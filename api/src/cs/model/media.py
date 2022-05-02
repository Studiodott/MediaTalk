from flask import g
import psycopg2
import psycopg2.extras
from pprint import pprint as D
from cs import app
from cs.model.setup import key

F = [ 'id', 'upstream_handle', 'media_type_id', 'handle', 'filename',
	'path', 'size_bytes', 'checksum', 'description', 'created_at' ]

def list():
	q = """
		SELECT
			mt.name media_type,
			""" + ', '.join([ f'm.{f} {f}' for f in F ]) + """
		FROM
			media m
			INNER JOIN media_type mt ON m.media_type_id = mt.id;
		"""
	
	g.db_cur.execute(q)
	return g.db_cur.fetchall()

def get(handle):
	q = """
		SELECT
			mt.name media_type,
			""" + ', '.join([ f'm.{f} {f}' for f in F ]) + """
		FROM
			media m
			INNER JOIN media_type mt ON m.media_type_id = mt.id
		WHERE
			m.handle = %(handle)s;
		"""
	
	g.db_cur.execute(q, {
		'handle' : handle,
	})
	return g.db_cur.fetchone()

def find_by_upstream_handle(upstream_handle):
	q = """
		SELECT
			mt.name media_type,
			""" + ', '.join([ f'm.{f} {f}' for f in F ]) + """
		FROM
			media m
			INNER JOIN media_type mt ON m.media_type_id = mt.id
		WHERE
			m.upstream_handle = %(upstream_handle)s;
		"""
	
	g.db_cur.execute(q, {
		'upstream_handle' : upstream_handle,
	})
	return g.db_cur.fetchone() or None

def create(args):
	handle = key()

	q = """
		INSERT INTO "media" (
			"handle",
			"media_type_id",
			"upstream_handle",
			"filename",
			"path",
			"size_bytes",
			"checksum",
			"description",
			"created_at"
		) VALUES (
			%(handle)s,
			(
				SELECT id FROM media_type WHERE name= %(media_type)s
			),
			%(upstream_handle)s,
			%(filename)s,
			%(path)s,
			%(size_bytes)s,
			%(checksum)s,
			%(description)s,
			NOW()
		);"""

	g.db_cur.execute(q, {
		'handle' : handle,
		'media_type' : args['media_type'],
		'upstream_handle' : args['upstream_handle'],
		'filename' : args['filename'],
		'path' : args['path'],
		'size_bytes' : args['size_bytes'],
		'checksum' : args['checksum'],
		'description' : args['description'],
	})

	return handle
