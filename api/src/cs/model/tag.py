from flask import g
import psycopg2
import psycopg2.extras
from ulid import ULID
from pprint import pprint as D
from cs import app
from cs.model.setup import key

def list(metatag_handle=None):

	if metatag_handle:
		q = """
			SELECT
				t.id as id,
				t.handle as handle,
				t.name as name,
				t.description as description,
				t.created_at as created_at
			FROM
				tag t
				INNER JOIN metatag_tag mtt ON t.id = mtt.tag_id
				INNER JOIN metatag mt ON mtt.metatag_id = mt.id
			WHERE
				mt.handle = %(metatag_handle)s;
			"""
	else:
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

	g.db_cur.execute(q, {
		'metatag_handle' : metatag_handle,
	})
	return g.db_cur.fetchall()

def find(name):

	name = name.lower()

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
			name=%(name)s;
		"""

	g.db_cur.execute(q, {
		'name' : name,
	})
	return g.db_cur.fetchone()

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

def remove(handle):
	q = """
		DELETE FROM tag
		WHERE handle = %(handle)s;"""

	g.db_cur.execute(q, {
		'handle' : handle,
	})

def create(name, description):
	handle = key()

	name = name.lower()

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
