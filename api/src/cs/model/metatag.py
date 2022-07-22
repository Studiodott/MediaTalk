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
			created_at
		FROM
			metatag;
		"""

	g.db_cur.execute(q)
	return g.db_cur.fetchall()

def get(handle):
	q = """
		SELECT
			id,
			handle,
			name,
			created_at
		FROM
			metatag
		WHERE
			handle=%(handle)s;
		"""

	g.db_cur.execute(q, {
		'handle' : handle,
	})
	return g.db_cur.fetchone()

def remove(handle):
	q = """
		DELETE FROM metatag
		WHERE handle = %(handle)s;"""

	g.db_cur.execute(q, {
		'handle' : handle,
	})

def create(name):
	handle = key()

	q = """
		INSERT INTO "metatag" (
			"handle",
			"name",
			"created_at"
		) VALUES (
			%(handle)s,
			%(name)s,
			NOW()
		);"""
	
	g.db_cur.execute(q, {
		'handle' : handle,
		'name' : name,
	})

	return handle

def has_tag(handle, tag_handle):

	q = """
		SELECT
			mtt.created_at
		FROM
			metatag_tag mtt
		INNER JOIN
			metatag mt ON mtt.metatag_id = mt.id
			tag t ON mtt.tag_id = t.id
		WHERE
			mt.handle = %(handle)s AND
			t.handle = %(tag_handle)s;
		"""

	g.db_cur.execute(q, {
		'handle' : handle,
	})
	return cursor.rowcount > 0

def add_tag(handle, tag_handle):

	q = """
		INSERT INTO "metatag_tag" (
			"metatag_id",
			"tag_id",
			"created_at"
		) VALUES (
			(SELECT id FROM metatag WHERE handle=%(handle)s),
			(SELECT id FROM tag WHERE handle=%(tag_handle)s),
			NOW()
		);"""
	
	g.db_cur.execute(q, {
		'handle' : handle,
		'tag_handle' : tag_handle,
	})

def remove_tag(handle, tag_handle):
	q = """
		DELETE FROM "metatag_tag"
		WHERE metatag_id = (SELECT
				id
			FROM
				"metatag"
			WHERE
				handle = %(handle)s)
		AND tag_id = (SELECT
				id
			FROM
				"tag"
			WHERE
				handle = %(tag_handle)s);
		"""
	g.db_cur.execute(q, {
		'handle' : handle,
		'tag_handle' : tag_handle,
	})
