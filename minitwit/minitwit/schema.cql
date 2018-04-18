drop table if exists mt_db;
CREATE KEYSPACE mt_db
WITH REPLICATION = { 'class' : 'SimpleStrategy',
'replication_factor' : 1};

USE mt_db;

drop table if exists mt_db.user
CREATE TABLE user(
  user_id integer,
  username text,
  email text,
  password text,
  PRIMARY KEY (user_id)

);


drop table if exists follower;
CREATE TABLE follower (
  who_id integer,
  whom_id integer,
  PRIMARY KEY (who_id,whom_id)
);



drop table if exists mt_db.message
CREATE TABLE message(
  message_id integer,
  author_id integer,
  text text,
  pub_date int,
  PRIMARY KEY (message_id)

);
