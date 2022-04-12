from flask import g
import os
import psycopg2
import psycopg2.extras
from ulid import ULID
from pprint import pprint as D
from cs import app

@app.before_request
def db_setup():
	g.db_con = psycopg2.connect(dsn=os.getenv('DATABASE_URL'),
		cursor_factory = psycopg2.extras.RealDictCursor)

	g.db_con.autocommit = False
	g.db_cur = g.db_con.cursor()
	g.db_cur.execute('SET TIME ZONE \'UTC\';')

@app.teardown_request
def db_wrapup(error):
	db_con = getattr(g, 'db_con', None)
	db_commit = getattr(g, 'db_commit', None)

	if db_con:
		if db_commit and not error:
			db_con.commit()
		else:
			db_con.rollback()
		db_con.close()
	else:
		app.logger.error("can't find database connection")

def key():
	return str(ULID())
