#!/usr/bin/env python

from flask import Flask, g, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/', methods=[ 'GET' ])
def hello():
	return """
<html>
	<head>
	</head>
	<body>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
		<script type="text/javascript">
let ws_proto = 'wss:';
if (window.location.protocol == 'http:') {
	ws_proto = 'ws:';
}
let ws_host = window.location.host;

var socket = io(ws_proto + '//' + ws_host + '/');
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

if __name__ == '__main__':
	socketio.run(app)
