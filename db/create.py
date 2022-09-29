#!/usr/bin/env python3
import os
import psycopg2
import psycopg2.extras

db_con = psycopg2.connect(dsn=os.getenv('DATABASE_URL'),
	cursor_factory = psycopg2.extras.RealDictCursor)
db_cur = db_con.cursor()

db_cur.execute(open('db/create.sql', 'r').read())

db_con.commit()
db_con.close()
