drop table exercises;
drop table followers;
drop table likes;
drop table comments;
drop table posts;
drop table users;
drop table quotes_table;
drop table tags;
drop table post_tags;

create table users (
  user_id text PRIMARY KEY,
  username varchar(255) DEFAULT 'Anonymous',
  first_name varchar(255),
  last_name varchar(255),
  full_name varchar(255),
  bio text DEFAULT 'Please write a bit about yourself and your fitness goals :)',
  filename text DEFAULT 'Anonymous',
  data bytea
);

create table followers (
  followed_id text,
  follower_id text,
  UNIQUE (followed_id, follower_id)
);

create table posts (
  post_id SERIAL PRIMARY KEY,
  tstamp timestamp NOT NULL DEFAULT date_trunc('second', NOW() - interval '5 hours'),
  description text NOT NULL,
  filename text,
  data bytea,
  user_id text,
  CONSTRAINT fk_user
    FOREIGN KEY(user_id)
  REFERENCES users(user_id)
  ON DELETE CASCADE
);

create table exercises (
    exercise_id SERIAL PRIMARY KEY,
    post_id INT,
    time_based boolean,
    exercise_name VARCHAR(255),
    num_sets INT,
    num_reps INT,
    num_time INT,
    time_units text,
    CONSTRAINT fk_post
      FOREIGN KEY(post_id) 
	  REFERENCES posts(post_id)
	  ON DELETE CASCADE
);

create table likes (
  post_id INT,
  user_id text,
  UNIQUE (post_id, user_id),
  CONSTRAINT fk_post
    FOREIGN KEY(post_id) 
  REFERENCES posts(post_id)
  ON DELETE CASCADE
);

create table comments (
  comment_id SERIAL PRIMARY KEY,
  tstamp timestamp NOT NULL DEFAULT date_trunc('second', NOW() - interval '5 hours'),
  post_id INT,
  user_id text,
  comment text,
  CONSTRAINT fk_post
    FOREIGN KEY(post_id) 
  REFERENCES posts(post_id)
  ON DELETE CASCADE
);

create table quotes_table (
  quote_id SERIAL PRIMARY KEY,
  the_quote text
);

-- link tags with posts
create table tags (
  tag_id SERIAL PRIMARY KEY,
  tag text
);

create table post_tags (
  post_id INT,
  tag_id INT,
  UNIQUE (post_id, tag_id),
  CONSTRAINT fk_post
    FOREIGN KEY(post_id) 
  REFERENCES posts(post_id)
  ON DELETE CASCADE
);