from cs import app, celery_app, socketio
from cs.model import setup, media, tag, tagging, user, config
import time
import ffmpeg
import statistics
import struct
import png
import json
import os
import hashlib
import boto3
import shutil
from flask import g
from tempfile import NamedTemporaryFile
from os import path
from apiclient import discovery, http

PATH_ORIGINAL = 'original' 
PATH_GENERATED = 'generated' 

def hash_file(filepath):

	h = hashlib.new('sha256')
	R = 4096

	with open(filepath, 'rb') as f:
		done = False
		while not done:
			b = f.read(R)
			h.update(b)
			if len(b) < R:
				done = True
	
	return h.hexdigest()

def process_audio(in_file_name, out_file):

	try:
		P = int(os.environ['CONF_APP_SNAPSHOT_WIDTH'])
	except:
		P = 640

	# get ffmpeg to decode the audio (part) of the file to PCM
	out, _ = (ffmpeg
		.input(in_file_name)
		.output('-', format='s8', acodec='pcm_s8', ac=1, ar='8k')
		.overwrite_output()
		.run(capture_stdout=True)
	)
	n_bytes = len(out)

	# a stride is the number of PCM samples we summarize into one
	# value, to get one pixel in our output waveform
	stride = n_bytes // P

	stats = []
	for i in range(P):
		# note the stdev of each stride of samples, to get an idea of the
		# amplitude swing in this stride
		# the mean'll hover around 0, since this is signed PCM
		samples = struct.unpack(f'{stride}b', out[i*stride:(i+1)*stride])
		stats.append(statistics.stdev(samples))

	# we'll take the largest stdev as 100% pixel height
	stats_largest = max(stats)

	w = P
	h = P//8

	# set up the pixel plane, all zeroes, contents are palette entries
	pixels = [
		[ 0 for _ in range(w) ]
		for _ in range(h)
	]

	# determine pixel values
	for x in range(w):
		# for each column, determine how many pixels should be lit in this
		# column, and how far down to go to reach their top
		n_pixels = (stats[x] / stats_largest) * h
		top = h - n_pixels	# pixels count down from top
		for y in range(h):
			# everything above top stays blank, underneath gets color
			pixels[y][x] = 0 if y < top else 1

	# the palette
	palette = [
		(0xff, 0xff, 0xff),
		(0x90, 0x90, 0x90),
	]

	# and dish it out to a PNG file
	img = png.Writer(w, h, palette=palette, bitdepth=1)
	img.write(out_file, pixels)

@celery_app.task
def media_add_tags(media_handle, tags):

	from flask import g

	print(f"media_add_tags(media_handle={media_handle} tags={tags})")

	with app.app_context():
		setup.db_setup()
		media_add_tags_real(media_handle, tags)
		g.db_commit = True
		setup.db_wrapup(False)

@celery_app.task
def media_add_tags_real(media_handle, tags):

	print(f"media_add_tags_real(media_handle={media_handle}, tags={tags})")

	api_user_key = 'added_by_API'
	tagging_range = json.dumps({ 'what' : 'all' })

	u = user.get_by_key(api_user_key)
	if not u:
		new_user_handle = user.create(api_user_key)
		u = user.get_by_key(api_user_key)
		socketio.emit('user_created', u)
	user_handle = u['handle']

	for t in tags:
		existing_tag = tag.find(t)
		if not existing_tag:
			tag_handle = tag.create(t, '')
			socketio.emit('tag_created', tag.get(tag_handle), broadcast=True)
		else:
			tag_handle = existing_tag['handle']
		print(f"  media_handle={media_handle} tag_handle={tag_handle} user_handle={user_handle} tagging_range={tagging_range}")
		tagging_handle = tagging.create(media_handle, tag_handle, user_handle, tagging_range)
		socketio.emit('tagging_created', tagging.get(tagging_handle))

@celery_app.task
def sync_gdrive():

	from flask import g

	with app.app_context():
		setup.db_setup()
		sync_gdrive_real()
		g.db_commit = True
		setup.db_wrapup(False)

@celery_app.task
def sync_gdrive_real():

	c = config.get_all()

	# don't do this if there's no config
	try:
		for k in [ 'S3_URL', 'S3_BUCKET', 'S3_ACCESS_KEY_ID', 'S3_SECRET_ACCESS_KEY', 'DRIVE_API_KEY', 'DRIVE_FOLDER_ID' ]:
			assert c[k] and len(c[k]) > 0
	except Exception as e:
		socketio.emit('sync_status', { 'error' : True, 'message' : 'configuration not complete' }, broadcast=True)
		return False

	# try to open up S3
	try:
		s3_client = boto3.client(
			's3',
			endpoint_url = c['S3_URL'],
			aws_access_key_id = c['S3_ACCESS_KEY_ID'],
			aws_secret_access_key = c['S3_SECRET_ACCESS_KEY']
		)
	except Exception as e:
		socketio.emit('sync_status', { 'error' : True, 'message' : 'could not talk to S3' }, broadcast=True)
		return False

	"""
	try to open up the Drive, and get a list of files we can find there
	"""
	try:
		# set up the sync
		drive_service = discovery.build('drive', 'v3', developerKey=c['DRIVE_API_KEY'])

		# collection of all pages
		all_drive_files = []

		# general query options, all non-directory files parented by _FOLDER_ID
		param = {
			'q' : f"'{c['DRIVE_FOLDER_ID']}' in parents and mimeType != 'application/vnd.google-apps.folder'",
			'fields' : f"nextPageToken, files(id, name, mimeType)",
			'pageSize' : 100,
		}

		pageToken = None

		while True:

			param['pageToken'] = pageToken

			drive_result = drive_service.files().list(**param).execute()
			drive_files = drive_result.get('files')

			all_drive_files.extend(drive_files)

			pageToken = drive_result.get('nextPageToken', None)
			if not pageToken:
				# no more results, done here
				break
	except Exception as e:
		socketio.emit('sync_status', { 'error' : True, 'message' : 'could not connect to Drive' }, broadcast=True)
		return False

	"""
	loop over the found files, checking if we know them already, processing if not
	"""
	for f in all_drive_files:
		print(f"inspecting {f['name']}")

		# do we have this file already?
		existing_file = media.find_by_upstream_handle(f['id'])
		if existing_file:
			print(f"  already exists, skipping...")
			continue

		# block of file info we want to keep
		fdesc = {
			'filename' : f['name'],
			'path' : path.join(PATH_ORIGINAL, f['name']),
			'media_type' : 'unknown',
			'upstream_handle' : f['id'],
			'size_bytes' : None,
			'media_desc' : None,
			'status' : 'discovered',
			'error' : None,
			'description' : f['name'],
		}

		temp_files = {}

		# try to download the file from Drive, process if (if needed),
		# and push it to S3
		try:

			# not a fan of this, but we must appease the Google, lest we
			# get ratelimited
			time.sleep(1)

			# figure out its type, trust upstream on this
			fdesc['media_type'] = f['mimeType'].split('/')[0].upper()

			# set up a temp file for this
			temp_files['original'] = NamedTemporaryFile(delete=False)

			# commence download
			fdesc['status'] = 'downloading'
			drive_req = drive_service.files().get_media(fileId=f['id'])
			drive_downloader = http.MediaIoBaseDownload(temp_files['original'], drive_req)
			done = False
			while not done:
				# download next chunk
				status, done = drive_downloader.next_chunk()

			# downloaded, close it up
			temp_files['original'].close()

			# find out and remember its size
			stats = os.stat(temp_files['original'].name)
			fdesc['size_bytes'] = stats.st_size
			print(f"  saved {stats.st_size} bytes")

			# hash it
			fdesc['status'] = 'hashing'
			fdesc['checksum'] = hash_file(temp_files['original'].name)

			# if it is a file we need to process (generate a waveform),
			# attempt to do so now, adding any generated files to temp_files
			try:
				fdesc['status'] = 'processing'
				# only do this for files with audio data
				if fdesc['media_type'] in [ 'AUDIO', 'VIDEO' ]:
					temp_files['waveform'] = NamedTemporaryFile(delete=False)
					process_audio(temp_files['original'].name, temp_files['waveform'])
					temp_files['waveform'].close()
			except Exception as e:
				print(f"error processing file: {e}")

			# upload the original to S3
			with open(temp_files['original'].name, 'rb') as f:
				s3_path = path.join(
					'original',
					fdesc['checksum']
				)
				s3_client.put_object(
					Body=f,
					Bucket=c['S3_BUCKET'],
					Key=s3_path
				)
				fdesc['url_original'] = f"{c['S3_URL']}/{c['S3_BUCKET']}/{s3_path}"

				"""
				aws_path = path.join(
					'original',
					fdesc['checksum']
				)
				aws_resource.Bucket(aws_bucket).put_object(
					Key=aws_path, Body=f)
				fdesc['url_original'] = f"https://{aws_bucket}.s3.{aws_region}.amazonaws.com/{aws_path}"a
				"""

			# upload the waveform, if existing
			if 'waveform' in temp_files:
				with open(temp_files['waveform'].name, 'rb') as f:
					s3_path = path.join(
						'generated',
						f"{fdesc['checksum']}_waveform"
					)
					s3_client.put_object(
						Body=f,
						Bucket=c['S3_BUCKET'],
						Key=s3_path
					)
					fdesc['url_description'] = f"{c['S3_URL']}/{c['S3_BUCKET']}/{s3_path}"

					"""
					aws_path = path.join(
						'generated',
						f"{fdesc['checksum']}_waveform"
					)
					aws_resource.Bucket(aws_bucket).put_object(
						Key=aws_path, Body=f)
					fdesc['url_description'] = f"https://{aws_bucket}.s3.{aws_region}.amazonaws.com/{aws_path}"
					"""
			else:
				fdesc['url_description'] = ''

			# finally done
			fdesc['status'] = 'ok'

		except IOError as e:
			socketio.emit('sync_status', { 'error' : True, 'message' : str(e) }, broadcast=True)
			fdesc['error'] = f"while {fdesc['status']}: {e}"
			fdesc['status'] = 'failed'
		else:
			# all went well, save  it database and broadcast this new file
			handle = media.create(fdesc)
			g.db_con.commit()
			socketio.emit('media_created', media.get(handle), broadcast=True)
		finally:
			# in any case, clean up
			for what, where in temp_files.items():
				print(f"removing temp_file {where.name} for {what}")
				os.remove(where.name)

	socketio.emit('sync_status', { 'error' : False, 'message' : f"synced {len(all_drive_files)} files" }, broadcast=True)

	return True

@celery_app.task
def sync_local_file(_path, name, _type, upstream_handle, description):

	from flask import g

	with app.app_context():
		setup.db_setup()
		ret = sync_local_file_real(_path, name, _type, upstream_handle, description)
		g.db_commit = True
		setup.db_wrapup(False)
		return ret

@celery_app.task
def sync_local_file_real(_path, name, _type, upstream_handle, description):

	c = config.get_all()

	# don't do this if there's no config
	try:
		for k in [ 'S3_URL', 'S3_BUCKET', 'S3_ACCESS_KEY_ID', 'S3_SECRET_ACCESS_KEY', 'DRIVE_API_KEY', 'DRIVE_FOLDER_ID' ]:
			assert c[k] and len(c[k]) > 0
	except Exception as e:
		print(f"error talking to S3: {e}")
		socketio.emit('sync_status', { 'error' : True, 'message' : 'configuration not complete' }, broadcast=True)
		return False

	try:
		s3_client = boto3.client(
			's3',
			endpoint_url = c['S3_URL'],
			aws_access_key_id = c['S3_ACCESS_KEY_ID'],
			aws_secret_access_key = c['S3_SECRET_ACCESS_KEY']
		)
	except Exception as e:
		socketio.emit('sync_status', { 'error' : True, 'message' : 'could not talk to S3' }, broadcast=True)
		return False

	existing_file = media.find_by_upstream_handle(upstream_handle)
	if existing_file:
		print(f"  already exists, skipping...")
		return

	fdesc = {
		'filename' : name,
		'handle' : None,
		'path' : _path,
		'media_type' : _type,
		'upstream_handle' : upstream_handle,
		'size_bytes' : None,
		'media_desc' : None,
		'status' : 'discovered',
		'error' : None,
		'description' : description,
	}

	temp_files = {}

	try:

		stats = os.stat(_path)
		fdesc['size_bytes'] = stats.st_size
		print(f"  saved {stats.st_size} bytes")

		# hash it
		fdesc['status'] = 'hashing'
		fdesc['checksum'] = hash_file(_path)

		# handle it
		try:
			fdesc['status'] = 'processing'
			if fdesc['media_type'] in [ 'AUDIO', 'VIDEO' ]:
				temp_files['waveform'] = NamedTemporaryFile(delete=False)
				process_audio(_path, temp_files['waveform'])
				temp_files['waveform'].close()
		except Exception as e:
			print(f"error processing file: {e}")

		# upload the original
		with open(_path, 'rb') as f:
			s3_path = path.join(
				'original',
				fdesc['checksum']
			)
			s3_client.put_object(
				Body=f,
				Bucket=c['S3_BUCKET'],
				Key=s3_path
			)
			fdesc['url_original'] = f"{c['S3_URL']}/{c['S3_BUCKET']}/{s3_path}"

		# upload the waveform, if existing
		if 'waveform' in temp_files:
			with open(temp_files['waveform'].name, 'rb') as f:
				s3_path = path.join(
					'generated',
					f"{fdesc['checksum']}_waveform"
				)
				s3_client.put_object(
					Body=f,
					Bucket=c['S3_BUCKET'],
					Key=s3_path
				)
				fdesc['url_description'] = f"{c['S3_URL']}/{c['S3_BUCKET']}/{s3_path}"
		else:
			fdesc['url_description'] = ''

		fdesc['status'] = 'ok'

	except IOError as e:
		socketio.emit('sync_status', { 'error' : True, 'message' : str(e) }, broadcast=True)
		fdesc['error'] = f"while {fdesc['status']}: {e}"
		fdesc['status'] = 'failed'
		print(f"error! fdesc={fdesc}")
		raise e
	else:
		fdesc['handle'] = media.create(fdesc)
		g.db_con.commit()
		socketio.emit('media_created', media.get(fdesc['handle']), broadcast=True)
	finally:
		os.remove(_path)
		for what, where in temp_files.items():
			print(f"removing temp_file {where.name} for {what}")
			os.remove(where.name)

	socketio.emit('sync_status', { 'error' : False, 'message' : f"synced 1 file" }, broadcast=True)
	return fdesc['handle']
