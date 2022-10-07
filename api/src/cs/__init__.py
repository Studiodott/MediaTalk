#!/usr/bin/env python
from flask import Flask, g, render_template, send_from_directory, make_response
import flask.json
import werkzeug.datastructures
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse, fields, marshal_with
from flask_jwt_extended import JWTManager
from flask_jwt_extended import ( create_access_token, set_access_cookies, jwt_required, get_jwt_identity )
from celery import Celery, chain
from celery.schedules import crontab
import psycopg2
import psycopg2.extras
import json
import os
from ulid import ULID
from datetime import datetime, timedelta
from pprint import pprint as D

class DTJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return obj.isoformat()
		return json.JSONEncoder.default(self, obj)

# oh ffsffs

app = Flask(__name__)
app.json_encoder = DTJsonEncoder
app.config['JWT_SECRET_KEY'] = os.environ['CONF_APP_SECRET']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=356)
app.config['UPLOAD_DIR'] = os.getenv('CONF_APP_UPLOAD_DIR', '/tmp')

socketio = SocketIO(app, cors_allowed_origins='*', logger=True, json=flask.json,
	message_queue=os.environ['REDIS_URL'])
cors = CORS(app, resources={ r"/*" : { 'origins' : [ 'http://localhost:3000' ] } })
api = Api(app, errors={})
celery_app = Celery(broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
jwt = JWTManager(app)

@api.representation('application/json')
def output_json(data, code, headers=None):
	resp = make_response(json.dumps(data, cls=DTJsonEncoder), code)
	resp.headers.extend(headers or {})
	return resp

from cs.model import setup, media, tag, tagging, logic, user, metatag, config
from cs.background import tasks

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

	sender.add_periodic_task(
		crontab(hour=0, minute=0),
		tasks.sync_gdrive.s()
	)

login_fields = {
	'access_token' : fields.String,
	'colour' : fields.String,
	'admin' : fields.Boolean,
}
login_parser = reqparse.RequestParser()
login_parser.add_argument('key', type=str, required=True)
class LoginResource(Resource):
	@marshal_with(login_fields)
	def post(self):
		args = login_parser.parse_args()
		u = user.get_by_key(args['key'])
		if not u:
			handle = user.create(args['key'], admin=True if user.count() == 0 else False)
			u = user.get_by_handle(handle)
			socketio.emit('user_created', u)
		print(f'got u={u}')
		access_token = create_access_token(identity=u['handle'])
		g.db_commit = True
		return {
			'access_token' : access_token,
			'colour' : u['colour'],
			'admin' : u['admin'],
		}, 200
api.add_resource(LoginResource, '/api/login')

user_fields = {
	'handle' : fields.String,
	'key' : fields.String,
	'colour' : fields.String,
	'admin' : fields.Boolean,
	'created_at' : fields.DateTime(dt_format='iso8601'),
}
user_list_fields = {
	'users' : fields.List(fields.Nested(user_fields)),
}

class UserManagerResource(Resource):
	decorators = [ jwt_required() ]

	@marshal_with(user_list_fields)
	def get(self):
		l = user.list()
		return { 'users' : l }, 200

api.add_resource(UserManagerResource, '/api/user')

media_fields = {
	'handle' : fields.String,
	'media_type' : fields.String,
	'filename' : fields.String,
	'description' : fields.String,
	'checksum' : fields.String,
	'url_original' : fields.String,
	'url_description' : fields.String,
	'created_at' : fields.DateTime(dt_format='iso8601'),
}
media_list_fields = {
	'media' : fields.List(fields.Nested(media_fields)),
}
class MediaManagerResource(Resource):
	@marshal_with(media_list_fields)
	def get(self):
		l = media.list()
		return { 'media' : l }, 200
api.add_resource(MediaManagerResource, '/api/media')

class MediaResource(Resource):
	@marshal_with(media_fields)
	def get(self, handle):
		return media.get(handle), 200
api.add_resource(MediaResource, '/api/media/<handle>')

metatag_fields = {
	'handle' : fields.String,
	'name' : fields.String,
	'created_at' : fields.DateTime(dt_format='iso8601'),
	'tag_handles' : fields.List(fields.String),
}
metatag_list_fields = {
	'metatags' : fields.List(fields.Nested(metatag_fields)),
}
metatag_parser = reqparse.RequestParser()
metatag_parser.add_argument('name', type=str, required=True)
class MetaTagManagerResource(Resource):
	@marshal_with(metatag_list_fields)
	def get(self):
		mts = metatag.list()
		for mt in mts:
			mt['tag_handles'] = [ t['handle'] for t in tag.list(metatag_handle=mt['handle']) ]
		return { 'metatags' : mts }, 200
	@marshal_with(metatag_fields)
	def post(self):
		args = metatag_parser.parse_args()
		handle = metatag.create(args['name'])
		mt = metatag.get(handle)
		mt['tag_handles'] = []
		socketio.emit('metatag_created', mt)
		g.db_commit = True
		return mt, 200
api.add_resource(MetaTagManagerResource, '/api/metatag')

class MetaTagResource(Resource):
	@marshal_with(metatag_fields)
	def get(self, handle):
		return metatag.get(handle), 200
	def delete(self, handle):
		metatag.remove(handle)
		socketio.emit('metatag_removed', handle)
		g.db_commit = True
		return '', 201
api.add_resource(MetaTagResource, '/api/metatag/<handle>')

class MetaTagTagResource(Resource):
	def post(self, metatag_handle, tag_handle):
		metatag.add_tag(metatag_handle, tag_handle)
		mt = metatag.get(metatag_handle)
		print(f'mt={mt}')
		mt['tag_handles'] = [ t['handle'] for t in tag.list(metatag_handle=metatag_handle) ]
		socketio.emit('metatag_changed', mt)
		g.db_commit = True
		return '', 201

	def delete(self, metatag_handle, tag_handle):
		metatag.remove_tag(metatag_handle, tag_handle)
		mt = metatag.get(metatag_handle)
		mt['tag_handles'] = [ t['handle'] for t in tag.list(metatag_handle=metatag_handle) ]
		socketio.emit('metatag_changed', mt)
		g.db_commit = True
		return '', 201
api.add_resource(MetaTagTagResource, '/api/metatag/<metatag_handle>/<tag_handle>')

tag_fields = {
	'handle' : fields.String,
	'name' : fields.String,
	'description' : fields.String,
	'created_at' : fields.DateTime(dt_format='iso8601'),
}
tag_list_fields = {
	'tags' : fields.List(fields.Nested(tag_fields)),
}
tag_parser = reqparse.RequestParser()
tag_parser.add_argument('name', type=str, required=True)
tag_parser.add_argument('description', type=str, required=True)
class TagManagerResource(Resource):
	@marshal_with(tag_list_fields)
	def get(self):
		l = tag.list()
		return { 'tags' : l }, 200
	@marshal_with(tag_fields)
	def post(self):
		args = tag_parser.parse_args()
		handle = tag.create(args['name'], args['description'])
		t = tag.get(handle)
		socketio.emit('tag_created', t)
		g.db_commit = True
		return t, 200

api.add_resource(TagManagerResource, '/api/tag')

class TagResource(Resource):
	@marshal_with(tag_fields)
	def get(self, handle):
		return tag.get(handle), 200
	def delete(self, handle):
		print(f'TAGREMOVE {handle}')
		print(f'TAGREMOVE {handle}')
		print(f'TAGREMOVE {handle}')
		print(f'TAGREMOVE {handle}')
		tag.remove(handle)
		socketio.emit('tag_removed', handle)
		g.db_commit = True
		return '', 201
api.add_resource(TagResource, '/api/tag/<handle>')


tagging_fields = {
	'handle' : fields.String,
	'media_handle' : fields.String,
	'tag_handle' : fields.String,
	'user_handle' : fields.String,
	'comment' : fields.String,
	'colour' : fields.String,
	'position' : fields.Raw,
	'created_at' : fields.DateTime(dt_format='iso8601'),
}
tagging_list_fields = {
	'taggings' : fields.List(fields.Nested(tagging_fields)),
}
tagging_parser = reqparse.RequestParser()
tagging_parser.add_argument('media_handle', type=str, required=True)
tagging_parser.add_argument('tag_handle', type=str, required=True)
tagging_parser.add_argument('position', type=str, required=True)
tagging_parser.add_argument('comment', type=str, required=False)
class TaggingManagerResource(Resource):
	decorators = [ jwt_required() ]

	@marshal_with(tagging_list_fields)
	def get(self):
		l = tagging.list()
		print(f'list={l}')
		return { 'taggings' : l }, 200
	@marshal_with(tagging_fields)
	def post(self):
		args = tagging_parser.parse_args()
		user_handle = get_jwt_identity()
		print(f'TAGGING CREATE THIS USER IS {user_handle}')
		print(f'TAGGING CREATE THIS USER IS {user_handle}')
		print(f'TAGGING CREATE THIS USER IS {user_handle}')
		print(f'TAGGING CREATE THIS USER IS {user_handle}')
		print(args)
		handle = tagging.create(args['media_handle'], args['tag_handle'], user_handle, args['position'], args['comment'])
		ti = tagging.get(handle)
		print(f'TAGGING CREATE THIS TAGGIN IS {ti}')

		socketio.emit('tagging_created', ti)
		g.db_commit = True
		return ti, 200

api.add_resource(TaggingManagerResource, '/api/tagging')

class TaggingResource(Resource):
	@marshal_with(tagging_fields)
	def get(self, handle):
		return tagging.get(handle), 200
	def delete(self, handle):
		print(f'TAGGING REMOVE {handle}')
		print(f'TAGGING REMOVE {handle}')
		print(f'TAGGING REMOVE {handle}')
		print(f'TAGGING REMOVE {handle}')
		tagging.remove(handle)
		socketio.emit('tagging_removed', handle)
		g.db_commit = True
		return '', 201
api.add_resource(TaggingResource, '/api/tagging/<handle>')

search_fields = {
	'media' : fields.List(fields.Nested(media_fields)),
	'tags' : fields.List(fields.Nested(tag_fields)),
	'users' : fields.List(fields.Nested(user_fields)),
	'taggings' : fields.List(fields.Nested(tagging_fields)),
}
search_parser = reqparse.RequestParser()
search_parser.add_argument('media_type', type=str, required=False, action='append')
search_parser.add_argument('tag_handle', type=str, required=False, action='append')
search_parser.add_argument('user_handle', type=str, required=False, action='append')
search_parser.add_argument('tag_handles_and', type=bool, required=False)
search_parser.add_argument('user_handles_and', type=bool, required=False)
class SearchResource(Resource):
	decorators = [ jwt_required() ]

	@marshal_with(search_fields)
	def get(self):
		args = search_parser.parse_args()
		return logic.search(
			media_types=args['media_type'],
			tag_handles=args['tag_handle'],
			user_handles=args['user_handle'],
			tag_handles_and=args['tag_handles_and'],
			user_handles_and=args['user_handles_and']), 200
api.add_resource(SearchResource, '/api/search')

config_parser = reqparse.RequestParser()
config_parser.add_argument('key', type=str, required=True)
config_parser.add_argument('value', type=str, required=True)
class ConfigResource(Resource):
	decorators = [ jwt_required() ]

	def get(self):
		return config.get_all(), 200

	def post(self):
		args = config_parser.parse_args()
		config.set(args['key'], args['value'])
		g.db_commit = True
		return config.get_all(), 200

api.add_resource(ConfigResource, '/api/admin/config')

integration_media_upload_parser = reqparse.RequestParser()
integration_media_upload_parser.add_argument('media', type=werkzeug.datastructures.FileStorage, location='files', required=True)
integration_media_upload_parser.add_argument('media_type', type=str, required=True)
integration_media_upload_parser.add_argument('handle', type=str, required=False)
integration_media_upload_parser.add_argument('description', type=str)
integration_media_upload_parser.add_argument('tag', type=str, action='append')
p = """
<html>
<body>
<pre>
{message}
</pre>
<form method="POST" enctype="multipart/form-data">
	<div><label for="media_type">Type:</label>
	<select name="media_type" id="media_type">
		<option value="TEXT">TEXT</option>
		<option value="IMAGE">IMAGE</option>
		<option value="AUDIO">AUDIO</option>
		<option value="VIDEO">VIDEO</option>
	</select></div>
	<p>The handle; You may supply a unique handle for this media, to check for future duplicates. If you supply one here, any future uploads with the same handle will not be processed. This allows the uploader to work in batches with possible repetitions, without duplicates on the server. If left blank, a unique handle will be generated.</p>
	<p>Tags; any given tags will be applied as entire-document tags to the uploaded media, reusing ones which exist already or creating them if not, as an API-specific user which will also be reused-or-created. This form has three tag inputs but there's no real limit under the hood.</p>
	<div><label for="handle">Your unique handle:</label>
	<input type="text" name="handle" id="handle"></div>
	<div><label for="description">Description:</label>
	<input type="text" name="description" id="description"></div>
	<div><label for="tag">Tags:</label></div>
	<div><input type="text" name="tag" id="tag"></div>
	<div><input type="text" name="tag" id="tag"></div>
	<div><input type="text" name="tag" id="tag"></div>
	<div><label for="media">Media file:</label>
	<input type="file" name="media" id="media"></div>
	<input type="submit" value="Upload">
</form>
<pre>
or with curl:

curl -X POST -F media_type=TEXT -F handle=your_handle -F description="a description" -F tag=first_tag -F tag=second_tag -F media=@your_file THIS_URL
</pre>
</body>
</html>
"""

class IntegrationMediaUploadResource(Resource):
	def get(self):
		msg = 'This is not a test, input will be processed and saved. On success 201 will be returned, processing is done asynchronously.'
		return make_response(p.format(message=msg), 200, { "Content-Type" : "text/html" })

	def post(self):
		args = integration_media_upload_parser.parse_args()
		handle = args['handle'] if ('handle' in args and args['handle'] and len(args['handle'])) else str(ULID())
		tag_list = list(filter(lambda t: len(t) > 0, args['tag']))
		dest = os.path.join(app.config['UPLOAD_DIR'], args['media'].filename)
		assert args['media_type'] in [ 'TEXT', 'IMAGE', 'AUDIO', 'VIDEO' ]
		D("saving to {}".format(dest))
		args['media'].save(dest)
		task_sync = tasks.sync_local_file.s(dest, args['media'].filename, args['media_type'], handle, args['description'])
		task_add_tags = tasks.media_add_tags.s(tag_list)
		chain(task_sync, task_add_tags)()

		return '', 201
api.add_resource(IntegrationMediaUploadResource, '/api/integration/media/upload')

class IntegrationMediaUploadTestResource(Resource):
	def get(self):
		msg = 'This is a test for development purposes, input is inspected but not processed/saved.'
		return make_response(p.format(message=msg), 200, { "Content-Type" : "text/html" })

	def post(self):
		args = integration_media_upload_parser.parse_args()
		tag_list = list(filter(lambda t: len(t) > 0, args['tag']))

		D(args)
		handle = args['handle'] if ('handle' in args and len(args['handle'])) else str(ULID())
		assert args['media_type'] in [ 'TEXT', 'IMAGE', 'AUDIO', 'VIDEO' ]
		dest = os.path.join(app.config['UPLOAD_DIR'], args['media'].filename)
		args['media'].save(dest)

		ret = {
			'status' : 'looks good!',
			'filename' : args['media'].filename,
			'media_type' : args['media_type'],
			'handle' : handle,
			'description' : args['description'],
			'filesize' : os.stat(dest).st_size,
			'tag' : args['tag'],
		}
		os.remove(dest)
		msg = 'Received:\n{}'.format(json.dumps(ret, indent=2))
		return make_response(p.format(message=msg), 200, { "Content-Type" : "text/html" })
api.add_resource(IntegrationMediaUploadTestResource, '/api/integration/test/media/upload')

class AdminSyncResource(Resource):
	decorators = [ jwt_required() ]

	def post(self):
		user_handle = get_jwt_identity()
		u = user.get_by_handle(user_handle)
		if u['admin']:
			tasks.sync_gdrive.apply_async()
		else:
			return '', 400
		return '', 201
api.add_resource(AdminSyncResource, '/api/admin/sync')

user_parser = reqparse.RequestParser()
user_parser.add_argument('admin', type=bool, required=True)
class AdminUserResource(Resource):
	decorators = [ jwt_required() ]

	@marshal_with(user_fields)
	def get(self, key):
		calling_user_handle = get_jwt_identity()
		calling_user = user.get_by_handle(calling_user_handle)
		if not calling_user['admin']:
			return '', 400
		dest_user = user.get_by_key(key)
		if not dest_user:
			return '', 404
		return dest_user, 200

	def post(self, key):
		calling_user_handle = get_jwt_identity()
		calling_user = user.get_by_handle(calling_user_handle)
		if not calling_user['admin']:
			return '', 400
		args = user_parser.parse_args()
		dest_user = user.get_by_key(key)
		if not dest_user:
			return '', 404
		user.update(dest_user['handle'], args['admin'])
		changed_user = user.get_by_key(key)
		socketio.emit('user_created', changed_user)
		return '', 201
api.add_resource(AdminUserResource, '/api/admin/user/<key>')

@app.route('/', methods=[ 'GET' ])
def push_index():
	D(f"staticindex")
	return send_from_directory('../../../frontend/dist', 'index.html')

@app.route('/<path:path>', methods=[ 'GET' ])
def push_static(path=None):
	D(f"static, path={path}")
	return send_from_directory('../../../frontend/dist', path)

@app.route('/bar', methods=[ 'GET' ])
def bar():
	tasks.sync_gdrive.apply_async()
	return "ok", 200

@app.route('/foo', methods=[ 'GET' ])
def hello():
	return """
<html>
	<head>
	</head>
	<body>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.4.1/socket.io.js"></script>
		<script type="text/javascript">
var socket = io(location.origin.replace(/^http/, 'ws'), {
	transports : [ 'websocket', 'polling' ],
});
socket.on('connect', function() {
	socket.emit('debug', 'hello');
});
		</script>
	</body>
</html>
""", 200

@socketio.on('debug')
def handle_debug(data):
	print(f"debug data={data}")
	if data == 'new_tag':
		emit('new_tag', 'ok', broadcast = True)
