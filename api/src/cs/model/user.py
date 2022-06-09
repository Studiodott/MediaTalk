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
			key,
			created_at
		FROM
			"user";
		"""

	g.db_cur.execute(q)
	return g.db_cur.fetchall()

def get_by_handle(handle):
	q = """
		SELECT
			id,
			handle,
			key,
			created_at
		FROM
			"user"
		WHERE
			handle=%(handle)s;
		"""

	g.db_cur.execute(q, {
		'handle' : handle,
	})
	return g.db_cur.fetchone()

def get_by_key(key):

	# the LOWER comparison ain't pretty, by the book emails
	# have a case-sensitive username in username@domain.tld,
	# but since we have a quite lax login scenario here it's
	# preferred to spawning x differently capitalized users
	q = """
		SELECT
			id,
			handle,
			key,
			created_at
		FROM
			"user"
		WHERE
			LOWER(key)=LOWER(%(key)s);
		"""

	g.db_cur.execute(q, {
		'key' : key,
	})
	return g.db_cur.fetchone()


def create(desired_key):
	handle = key()

	q = """
		INSERT INTO "user" (
			"handle",
			"key",
			"created_at"
		) VALUES (
			%(handle)s,
			%(key)s,
			NOW()
		);"""
	
	g.db_cur.execute(q, {
		'handle' : handle,
		'key' : desired_key,
	})

	return handle
