#!/usr/bin/env python
from flask import Flask, g, render_template, send_from_directory, make_response
import flask.json
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse, fields, marshal_with
import psycopg2
import psycopg2.extras
import json
from datetime import datetime
from pprint import pprint as D

class DTJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, datetime):
			return obj.isoformat()
		return json.JSONEncoder.default(self, obj)

app = Flask(__name__)
app.json_encoder = DTJsonEncoder
socketio = SocketIO(app, cors_allowed_origins='*', logger=True, json=flask.json)
cors = CORS(app, resources={ r"/*" : { 'origins' : [ 'http://localhost:3000' ] } })
api = Api(app, errors={})

@api.representation('application/json')
def output_json(data, code, headers=None):
	resp = make_response(json.dumps(data, cls=DTJsonEncoder), code)
	resp.headers.extend(headers or {})
	return resp

from cs.model import setup, media, tag, tagging

media_fields = {
	'handle' : fields.String,
	'media_type' : fields.String,
	'filename' : fields.String,
	'description' : fields.String,
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

tagging_fields = {
	'handle' : fields.String,
	'media_handle' : fields.String,
	'tag_handle' : fields.String,
	'comment' : fields.String,
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
	@marshal_with(tagging_list_fields)
	def get(self):
		l = tagging.list()
		return { 'taggings' : l }, 200
	@marshal_with(tagging_fields)
	def post(self):
		args = tagging_parser.parse_args()
		handle = tagging.create(args['media_handle'], args['tag_handle'], args['position'], args['comment'])
		ti = tagging.get(handle)
		socketio.emit('tagging_created', ti)
		g.db_commit = True
		return ti, 200

api.add_resource(TaggingManagerResource, '/api/tagging')

class TaggingResource(Resource):
	@marshal_with(tagging_fields)
	def get(self, handle):
		return tagging.get(handle), 200
api.add_resource(TaggingResource, '/api/tagging/<handle>')

@app.route('/', methods=[ 'GET' ])
def push_index():
	D(f"staticindex")
	return send_from_directory('../../../frontend/dist', 'index.html')

@app.route('/<path:path>', methods=[ 'GET' ])
def push_static(path=None):
	D(f"static, path={path}")
	return send_from_directory('../../../frontend/dist', path)

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
