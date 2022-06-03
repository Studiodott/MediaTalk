from flask import g
import psycopg2
import psycopg2.extras
from pprint import pprint as D
from cs import app
from cs.model.setup import key

F = [ 'id', 'upstream_handle', 'media_type_id', 'handle', 'filename',
	'path', 'size_bytes', 'checksum', 'description', 'url_original',
	'url_description', 'created_at' ]

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

def find_by_tag_handle(tag_handle):
	q = """
		SELECT
			mt.name as media_type,
			""" + ', '.join([ f'm.{f} {f}' for f in F ]) + """
		FROM
			media m
			INNER JOIN media_type mt ON m.media_type_id = mt.id
			INNER JOIN tagging ti ON m.id = ti.media_id
			INNER JOIN tag t ON ti.tag_id = t.id
		WHERE
			t.handle = %(tag_handle)s;
		"""
	g.db_cur.execute(q, {
		'tag_handle' : tag_handle,
	})
	return g.db_cur.fetchall()

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
			"url_original",
			"url_description",
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
			%(url_original)s,
			%(url_description)s,
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
		'url_original' : args['url_original'],
		'url_description' : args['url_description'],
	})

	return handle
