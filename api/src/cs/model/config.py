from flask import g
import psycopg2
import psycopg2.extras
from ulid import ULID
from pprint import pprint as D
from cs import app
from cs.model.setup import key
from random import randint

def get_all():
	q = """
		SELECT
			"key",
			"value"
		FROM
			"config";
		"""

	g.db_cur.execute(q)
	return { row['key'] : row['value'] for row in g.db_cur.fetchall() }

def get(k):
	q = """
		SELECT
			"value"
		FROM
			"config"
		WHERE
			"key" = %(k)s;
		"""

	g.db_cur.execute(q, { 'k' : k })

	row = g.db_cur.fetchone()

	return row['value'] if row else None

def set(k, v):
	q = """
		UPDATE "config"
		SET "value" = %(v)s
		WHERE "key" = %(k)s;
		"""
	
	g.db_cur.execute(q, {
		'k' : k,
		'v' : v,
	})
