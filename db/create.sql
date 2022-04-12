drop table if exists "tagging";
drop table if exists "tag";
drop table if exists "media";
drop table if exists "media_type";

create table "media_type" (
	id serial not null,
	handle character varying(26) not null,
	name character varying(64) not null,
	created_at timestamp not null,
	primary key (id)
);
create unique index media_type_handle_idx on media_type (handle);
insert into "media_type" ("handle", "name", "created_at") values ('01G04Z81VE46440V5BS0Q3HA3P', 'TEXT', now());
insert into "media_type" ("handle", "name", "created_at") values ('01G04ZB3G5SZF4CPNXB703ESXE', 'IMAGE', now());
insert into "media_type" ("handle", "name", "created_at") values ('01G04ZB3QM1AWYGZAXEXDHJDSH', 'AUDIO', now());
insert into "media_type" ("handle", "name", "created_at") values ('01G04ZB3YDKQZ5SWQE2TNHJ0Y9', 'VIDEO', now());

create table "media"
(
	id serial not null,
	media_type_id int,
	handle character varying(26) not null,
	filename character varying(256) not null,
	path character varying(1024) not null,
	description character varying(256),
	created_at timestamp not null,
	primary key(id),
	constraint media_media_type_fk foreign key (media_type_id) references media_type (id)
);
create unique index media_handle_idx on media (handle);

insert into "media" ("handle", "media_type_id", "filename", "path", "description", "created_at") values (
	'01G0D3V26XMAZ8PV6C5SDXPKXV',
	(select id from media_type where name='TEXT'),
	'text_lorem-ipsum.txt',
	'/demo/text_lorem-ipsum.txt',
	'Lorem Ipsum text',
	NOW()
);
insert into "media" ("handle", "media_type_id", "filename", "path", "description", "created_at") values (
	'01G0D3Z1AM40A1W3Y9MZAD0A43',
	(select id from media_type where name='IMAGE'),
	'image_koeln.jpg',
	'/demo/image_koeln.jpg',
	'Colognian street image',
	NOW()
);
insert into "media" ("handle", "media_type_id", "filename", "path", "description", "created_at") values (
	'01G0D40HQXEPM80J6T4VAE6WD5',
	(select id from media_type where name='AUDIO'),
	'audio_jazzy.mp4',
	'/demo/audio_jazzy.mp4',
	'Jazzy music',
	NOW()
);
insert into "media" ("handle", "media_type_id", "filename", "path", "description", "created_at") values (
	'01G0D41KDYXVCA69NNHR7C0EE1',
	(select id from media_type where name='VIDEO'),
	'video_owl.mp4',
	'/demo/video_owl.mp4',
	'Video of an owl',
	NOW()
);

create table "tag"
(
	id serial not null,
	handle character varying(26) not null,
	name character varying(128) not null,
	description character varying(256),
	created_at timestamp not null,
	primary key (id)
);
create unique index tag_handle_idx on tag (handle);

insert into "tag" ("handle", "name", "description", "created_at") values
	('01G0D43XSHJE6VGWNX2WA45MEH', 'Happy', 'Happiness', NOW() );
insert into "tag" ("handle", "name", "description", "created_at") values
	('01G0D456YBF5G1C9CHGTHS52JQ', 'Sad', 'Sadness', NOW() );
insert into "tag" ("handle", "name", "description", "created_at") values
	('01G0D4DDEN4J0M8MC44QHGHF3P', 'Mamihlapinatapai', 'self-explanatory', NOW() );
insert into "tag" ("handle", "name", "description", "created_at") values
	('01G0D4DXTW3SFV54V2WB5TCQE7', 'Toska', 'self-explanatory', NOW() );

create table "tagging"
(
	id serial not null,
	media_id int,
	tag_id int,
	handle character varying(26) not null,
	comment character varying (256),
	created_at timestamp not null,
	primary key (id),
	constraint tagging_media_fk foreign key (media_id) references media (id),
	constraint tagging_tag_fk foreign key (tag_id) references tag (id)
);
create unique index tagging_handle_idx on tagging (handle);

