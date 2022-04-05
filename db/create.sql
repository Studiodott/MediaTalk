create table "tag"
(
	id serial not null,
	handle character varying(36) not null,
	created_at timestamp not null,
	note character varying(1024),
	primary key(id)
);
create unique index tag_handle_idx on tag (handle);
