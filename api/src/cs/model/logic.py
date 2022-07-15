from flask import g
from pprint import pprint as D
from cs import app
from psycopg2 import sql

def search(media_types, tag_handles, user_handles, tag_handles_and=False, user_handles_and=False):

	"""
	media = []

	if len(tag_handles):
		for tag_handle in tag_handles:
			media.extend(media.find_by_tag_handle(tag_handle))
	else:
		media = media.list()

	if len(media_types):
		media = filter(lambda m: m.media_type in media_types, media)
	
	"""
	filters = []
	if media_types and len(media_types):
		filters.append("mt.name = ANY(%(media_types)s)")
	if tag_handles and len(tag_handles):
		if tag_handles_and:
			for h in tag_handles:
				subq = sql.SQL("SELECT DISTINCT ti.media_id FROM tagging ti INNER JOIN tag t ON ti.tag_id = t.id WHERE t.handle={handle}").format(
					handle=sql.Literal(h)
				)
				filters.append(f"m.id IN ({subq.as_string(g.db_con)})")
		else:
			filters.append("t.handle = ANY(%(tag_handles)s)")
	if user_handles and len(user_handles):
		if user_handles_and:
			for h in user_handles:
				subq = sql.SQL('SELECT DISTINCT ti.media_id FROM tagging ti INNER JOIN "user" u ON ti.user_id = u.id WHERE u.handle={handle}').format(
					handle=sql.Literal(h)
				)
				filters.append(f"m.id IN ({subq.as_string(g.db_con)})")
		else:
			filters.append("u.handle = ANY(%(user_handles)s)")
	if not len(filters):
		filters.append("1=1")

	q = """
		SELECT
			m.id as media_id,
			m.handle as media_handle,
			mt.name as media_type,
			m.filename as media_filename,
			m.description as media_description,
			m.checksum as media_checksum,
			m.url_original as media_url_original,
			m.url_description as media_url_description,
			m.created_at as media_created_at,
			ti.handle as tagging_handle,
			ti.position as tagging_position,
			ti.comment as tagging_comment,
			ti.created_at as tagging_created_at,
			t.name as tag_name,
			t.handle as tag_handle,
			t.description as tag_description,
			t.created_at as tag_created_at,
			u.handle as user_handle,
			u.key as user_key,
			u.colour as user_colour,
			u.created_at as user_created_at
		FROM
			media m
			INNER JOIN media_type mt ON m.media_type_id = mt.id
			INNER JOIN tagging ti ON m.id = ti.media_id
			INNER JOIN tag t ON ti.tag_id = t.id
			INNER JOIN "user" u ON ti.user_id = u.id
		WHERE
			""" + " AND ".join(filters) + """
		ORDER BY
			m.handle ASC,
			t.handle ASC,
			u.handle ASC;"""

	g.db_cur.execute(q, {
		'media_types' : media_types,
		'tag_handles' : tag_handles,
		'user_handles' : user_handles,
	})

	media, taggings, tags, users = [], [], [], []
	last_media_handle = None
	last_tag_handle = None
	last_user_handle = None

	for row in g.db_cur.fetchall():
		if row['media_handle'] != last_media_handle:
			media.append({
				'handle' : row['media_handle'],
				'media_type' : row['media_type'],
				'filename' : row['media_filename'],
				'description' : row['media_description'],
				'checksum' : row['media_checksum'],
				'url_original' : row['media_url_original'],
				'url_description' : row['media_url_description'],
				'created_at' : row['media_created_at'],
			})
			last_media_handle = row['media_handle']
		if row['tag_handle'] != last_tag_handle:
			tags.append({
				'handle' : row['tag_handle'],
				'name' : row['tag_name'],
				'description' : row['tag_description'],
				'created_at' : row['tag_created_at'],
			})
			last_tag_handle = row['tag_handle']
		if row['user_handle'] != last_user_handle:
			users.append({
				'handle' : row['user_handle'],
				'key' : row['user_key'],
				'created_at' : row['user_created_at'],
			})
			last_user_handle = row['user_handle']
		taggings.append({
			'user_handle' : row['user_handle'],
			'media_handle' : row['media_handle'],
			'tag_handle' : row['tag_handle'],
			'handle' : row['tagging_handle'],
			'position' : row['tagging_position'],
			'colour' : row['user_colour'],
			'comment' : row['tagging_comment'],
			'created_at' : row['tagging_created_at'],
		})

	return {
		'media' : media,
		'tags' : tags,
		'users' : users,
		'taggings' : taggings,
	}



