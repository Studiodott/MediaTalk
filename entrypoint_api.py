#!/usr/bin/env python

from flask import Flask, g, render_template

app = Flask(__name__)

@app.route('/', methods=[ 'GET' ])
def hello():
	return "hello there", 200

if __name__ == '__main__':
	app.run('0.0.0.0', port=5000, debug=True)
