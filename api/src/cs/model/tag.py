from flask import g
import psycopg2
import psycopg2.extras
from ulid import ULID
from pprint import pprint as D
from cs import app
from cs.model.setup import key

def list():
	q = """
		SELECT
			id,
			handle,
			name,
			description,
			created_at
		FROM
			tag;
		"""

	g.db_cur.execute(q)
	return g.db_cur.fetchall()

def get(handle):
	q = """
		SELECT
			id,
			handle,
			name,
			description,
			created_at
		FROM
			tag
		WHERE
			handle=%(handle)s;
		"""

	g.db_cur.execute(q, {
		'handle' : handle,
	})
	return g.db_cur.fetchone()

def create(name, description):
	handle = key()

	q = """
		INSERT INTO "tag" (
			"handle",
			"name",
			"description",
			"created_at"
		) VALUES (
			%(handle)s,
			%(name)s,
			%(description)s,
			NOW()
		);"""
	
	g.db_cur.execute(q, {
		'handle' : handle,
		'name' : name,
		'description' : description,
	})

	return handle
