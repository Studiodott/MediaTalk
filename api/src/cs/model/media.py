from flask import g
import psycopg2
import psycopg2.extras
from ulid import ULID
from pprint import pprint as D
from cs import app

def list():
	q = """
		SELECT
			m.id id,
			mt.name media_type,
			m.handle handle,
			m.filename filename,
			m.path path,
			m.description description,
			m.created_at created_at
		FROM
			media m
			INNER JOIN media_type mt ON m.media_type_id = mt.id;
		"""
	
	g.db_cur.execute(q)
	return g.db_cur.fetchall()

def get(handle):
	q = """
		SELECT
			m.id id,
			mt.name media_type,
			m.handle handle,
			m.filename filename,
			m.path path,
			m.description description,
			m.created_at created_at
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

