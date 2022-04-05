#!/usr/bin/env python

from flask import Flask, g, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from pprint import pprint as D

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*', logger=True)
cors = CORS(app, resources={ r"/*" : { 'origins' : [ 'http://localhost:3000' ] } })

@app.route('/', methods=[ 'GET' ])
def push_index():
	D(f"staticindex")
	return send_from_directory('../../frontend/dist', 'index.html')

@app.route('/<path:path>', methods=[ 'GET' ])
def push_static(path=None):
	D(f"static, path={path}")
	return send_from_directory('../../frontend/dist', path)

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


if __name__ == '__main__':
	socketio.run(app)
