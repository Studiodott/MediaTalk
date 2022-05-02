from cs import app, celery_app, socketio
from cs.model import setup, media
import time
import ffmpeg
import statistics
import struct
import png
import json
import os
import hashlib
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

def process_audio(filename):

	try:
		P = int(os.environ['CONF_APP_SNAPSHOT_WIDTH'])
	except:
		P = 640

	filename_snapshot = f'{filename}_waveform.png'
	path_original = path.join(os.environ['CONF_APP_MEDIA_PATH'], 'original')
	path_generated = path.join(os.environ['CONF_APP_MEDIA_PATH'], 'generated')

	# get ffmpeg to decode the audio (part) of the file to PCM
	out, _ = (ffmpeg
		.input(path.join(path_original, filename))
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
	f = open(path.join(path_generated, filename_snapshot), 'wb')
	img.write(f, pixels)

	return {
		'waveform_name' : filename_snapshot,
		'waveform_path' : path.join(path_generated, filename_snapshot),
	}

@celery_app.task
def cookle():

	from flask import g

	with app.app_context():
		setup.db_setup()
		sync()
		g.db_commit = True
		setup.db_wrapup(False)

	for _ in range(5):
		time.sleep(1)
		socketio.emit('tag_created', 'yes', broadcast=True)


@celery_app.task
def sync():

	path_original = path.join(os.environ['CONF_APP_MEDIA_PATH'], 'original')
	path_generated = path.join(os.environ['CONF_APP_MEDIA_PATH'], 'generated')
	api_key = os.environ['CONF_DRIVE_API_KEY']
	folder_id = os.environ['CONF_DRIVE_FOLDER_ID']

	try:
		os.makedirs(path_original, exist_ok=True)
		os.makedirs(path_generated, exist_ok=True)
	except FileExistsError:
		pass

	try:
		# set up the sync
		drive_service = discovery.build('drive', 'v3', developerKey=api_key)

		# get a remote file list
		param = {
			'q' : f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder'",
		}
		drive_result = drive_service.files().list(**param).execute()
		drive_files = drive_result.get('files')
	except Exception as e:
		print(f"error while setting up drive: {e}")
		return False

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

		try:

			# figure out its type, trust upstream on this
			fdesc['media_type'] = f['mimeType'].split('/')[0].upper()

			# commence download
			fdesc['status'] = 'downloading'
			drive_req = drive_service.files().get_media(fileId=f['id'])
			with open(fdesc['path'], 'wb') as out:
				drive_downloader = http.MediaIoBaseDownload(out, drive_req)
				done = False
				while not done:
					status, done = drive_downloader.next_chunk()
			stats = os.stat(path.join(path_original, f['name']))
			fdesc['size_bytes'] = stats.st_size
			print(f"  saved {stats.st_size} bytes")

			# hash it
			fdesc['status'] = 'hashing'
			fdesc['checksum'] = hash_file(fdesc['path'])

			# handle it
			fdesc['status'] = 'processing'
			if fdesc['media_type'] in [ 'AUDIO', 'VIDEO' ]:
				fdesc['media_desc'] = process_audio(fdesc['name'])

			fdesc['status'] = 'ok'
		except Exception as e:
			fdesc['error'] = f"while {fdesc['status']}: {e}"
			fdesc['status'] = 'failed'

		handle = media.create(fdesc)
		socketio.emit('media_created', media.get(handle), broadcast=True)

	return True
