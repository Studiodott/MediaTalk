from cs import app, celery_app, socketio
from cs.model import setup, media, tag, tagging, user
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

def db_load(path):
	try:
		with open(path, 'r') as f:
			return json.loads(f.read())
	except:
		return { 'files' : [] }

def db_save(db, path):
	with open(path, 'w') as f:
		f.write(json.dumps(db, indent=2))

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
def sync_stub(_path, name, _type, upstream_handle, description):

	from flask import g

	with app.app_context():
		setup.db_setup()
		ret = sync_stub_real(_path, name, _type, upstream_handle, description)
		g.db_commit = True
		setup.db_wrapup(False)
		return ret

@celery_app.task
def sync_stub_real(_path, name, _type, upstream_handle, description):

	for i in range(3):
		print(f"naptime")
		time.sleep(1)

	print(f"wakeup")
	return "pony"

@celery_app.task
def sync_stubmore(a):

	from flask import g

	print(f"arg={a}")

	with app.app_context():
		setup.db_setup()
		sync_stubmore_real(a)
		g.db_commit = True
		setup.db_wrapup(False)

@celery_app.task
def sync_stubmore_real(a):

	print(f"sync_stubmore_real")
	print(f"arg={a}")
	for i in range(3):
		print(f"naptime")
		time.sleep(1)

	print(f"wakeup")
	return True


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

	path_original = path.join(os.environ['CONF_APP_MEDIA_PATH'], 'original')
	path_generated = path.join(os.environ['CONF_APP_MEDIA_PATH'], 'generated')

	api_key = os.environ['CONF_DRIVE_API_KEY']
	folder_id = os.environ['CONF_DRIVE_FOLDER_ID']

	aws_resource = boto3.resource('s3')
	aws_bucket = os.environ['CONF_AWS_BUCKET']
	aws_region = os.environ['CONF_AWS_REGION']

	print(f'talking to folder_id={folder_id} as api_key={api_key}')
	try:
		# set up the sync
		drive_service = discovery.build('drive', 'v3', developerKey=api_key)

		# get a remote file list
		param = {
			'q' : f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder'",
		}
		drive_result = drive_service.files().list(**param).execute()
		drive_files = drive_result.get('files')
		"""
		drive_files = [
			{
				'id' : '01G22CEZVY1NP1YS5V3J8SH1NK',
				'name' : 'image_koeln.jpg',
				'mimeType' : 'image/jpg',
			},
			{
				'id' : '01G22CF3D1T8YMA28HPTBRZYH2',
				'name' : 'text_lorem-ipsum.txt',
				'mimeType' : 'text/foo',
			},
			{
				'id' : '01G22CF4HPXPHCRMP2X4PW997W',
				'name' : 'audio_jazzy.mp4',
				'mimeType' : 'audio/mp4',
			},
			{
				'id' : '01G22CF6DY3PM86BT9J7385NXF',
				'name' : 'video_owl.mp4',
				'mimeType' : 'video/mp4',
			},
			{
				'id' : '01G22CF769DSC68ZKS8SK5SZGS',
				'name' : 'BoldDimIbis.mp4',
				'mimeType' : 'video/mp4',
			},
		]
		"""
	except Exception as e:
		print(f"error while setting up drive: {e}")
		return False

	print(f"found {len(drive_files)} on this drive")
	for f in drive_files:
		print(f"inspecting {f['name']}")
		existing_file = media.find_by_upstream_handle(f['id'])

		if existing_file:
			print(f"  already exists, skipping...")
			continue

		fdesc = {
			'filename' : f['name'],
			'path' : path.join(path_original, f['name']),
			'media_type' : 'unknown',
			'upstream_handle' : f['id'],
			'size_bytes' : None,
			'media_desc' : None,
			'status' : 'discovered',
			'error' : None,
			'description' : '',
		}

		temp_files = {}

		try:

			# figure out its type, trust upstream on this
			fdesc['media_type'] = f['mimeType'].split('/')[0].upper()

			# set up a temp file for this
			temp_files['original'] = NamedTemporaryFile(delete=False)

			print(f"handling as temp file {temp_files['original'].name}")

			# commence download
			fdesc['status'] = 'downloading'
			drive_req = drive_service.files().get_media(fileId=f['id'])

			drive_downloader = http.MediaIoBaseDownload(temp_files['original'], drive_req)
			done = False
			while not done:
				status, done = drive_downloader.next_chunk()
			temp_files['original'].close()
			"""
			shutil.copyfile(path.join('/tmp/in', f['name']), temp_files['original'].name)
			"""


			stats = os.stat(temp_files['original'].name)
			fdesc['size_bytes'] = stats.st_size
			print(f"  saved {stats.st_size} bytes")

			# hash it
			fdesc['status'] = 'hashing'
			fdesc['checksum'] = hash_file(temp_files['original'].name)

			# handle it
			try:
				fdesc['status'] = 'processing'
				if fdesc['media_type'] in [ 'AUDIO', 'VIDEO' ]:
					temp_files['waveform'] = NamedTemporaryFile(delete=False)
					process_audio(temp_files['original'].name, temp_files['waveform'])
					temp_files['waveform'].close()
			except Exception as e:
				print(f"error processing file: {e}")

			# upload the original
			with open(temp_files['original'].name, 'rb') as f:
				aws_path = path.join(
					os.environ['CONF_APP_MEDIA_PATH'],
					'original',
					fdesc['checksum']
				)
				aws_resource.Bucket(aws_bucket).put_object(
					Key=aws_path, Body=f)
				fdesc['url_original'] = f"https://{aws_bucket}.s3.{aws_region}.amazonaws.com/{aws_path}"

			# upload the waveform, if existing
			if 'waveform' in temp_files:
				with open(temp_files['waveform'].name, 'rb') as f:
					aws_path = path.join(
						os.environ['CONF_APP_MEDIA_PATH'],
						'generated',
						f"{fdesc['checksum']}_waveform"
					)
					aws_resource.Bucket(aws_bucket).put_object(
						Key=aws_path, Body=f)
					fdesc['url_description'] = f"https://{aws_bucket}.s3.{aws_region}.amazonaws.com/{aws_path}"
			else:
				fdesc['url_description'] = ''

			fdesc['status'] = 'ok'
		except IOError as e:
			print(f"ERROR {e}")
			fdesc['error'] = f"while {fdesc['status']}: {e}"
			fdesc['status'] = 'failed'
		else:
			handle = media.create(fdesc)
			g.db_con.commit()
			socketio.emit('media_created', media.get(handle), broadcast=True)
		finally:
			for what, where in temp_files.items():
				print(f"removing temp_file {where.name} for {what}")
				os.remove(where.name)

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

	path_original = path.join(os.environ['CONF_APP_MEDIA_PATH'], 'original')
	path_generated = path.join(os.environ['CONF_APP_MEDIA_PATH'], 'generated')

	aws_resource = boto3.resource('s3')
	aws_bucket = os.environ['CONF_AWS_BUCKET']
	aws_region = os.environ['CONF_AWS_REGION']

	existing_file = media.find_by_upstream_handle(upstream_handle)

	if existing_file:
		print(f"  already exists, skipping...")
		return

	fdesc = {
		'filename' : name,
		'hande' : None,
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
			aws_path = path.join(
				os.environ['CONF_APP_MEDIA_PATH'],
				'original',
				fdesc['checksum']
			)
			aws_resource.Bucket(aws_bucket).put_object(
				Key=aws_path, Body=f)
			fdesc['url_original'] = f"https://{aws_bucket}.s3.{aws_region}.amazonaws.com/{aws_path}"

		# upload the waveform, if existing
		if 'waveform' in temp_files:
			with open(temp_files['waveform'].name, 'rb') as f:
				aws_path = path.join(
					os.environ['CONF_APP_MEDIA_PATH'],
					'generated',
					f"{fdesc['checksum']}_waveform"
				)
				aws_resource.Bucket(aws_bucket).put_object(
					Key=aws_path, Body=f)
				fdesc['url_description'] = f"https://{aws_bucket}.s3.{aws_region}.amazonaws.com/{aws_path}"
		else:
			fdesc['url_description'] = ''

		fdesc['status'] = 'ok'

	except IOError as e:
		print(f"ERROR {e}")
		fdesc['error'] = f"while {fdesc['status']}: {e}"
		fdesc['status'] = 'failed'
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

	return fdesc['handle']
