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
  filename text,
  data bytea
);

create table followers (
  user_id text,
  follower_id text,
  UNIQUE (user_id, follower_id)
);

create table posts (
  post_id SERIAL PRIMARY KEY,
  tstamp timestamp NOT NULL DEFAULT NOW(),
  description text NOT NULL,
  filename text,
  data bytea,
  user_id text
  -- CONSTRAINT fk_user
  --   FOREIGN KEY(user_id)
  -- REFERENCES users(user_id)
  -- ON DELETE CASCADE
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
  tstamp timestamp NOT NULL DEFAULT NOW(),
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
  UNIQUE (post_id, tag_id)
);


-- why can't i add anything to anon
insert into users (user_id, username, first_name, last_name, full_name) values ('lKsjf23Dlds12', 'Anonyomous', 'hughdan', 'liu', 'hughdan liu');
insert into users (user_id, username, first_name, last_name, full_name) values ('lKsjkd', 'Anon', 'thom', 'liu', 'thom liu');
insert into users (user_id, username, first_name, last_name, full_name) values ('lKsjf23Dfj2', 'anon', 't', 'liu', 't liu');
insert into users (user_id, username, first_name, last_name, full_name) values ('lKsalfkjsaf12', 'JEFF', 'jeff', 'liu', 'jeff liu');
insert into users (user_id, username, first_name, last_name, full_name) values ('lKla3Dlds12', 'Calvinliu', 'calvin', 'liu', 'calvin liu');

-- insert into tags (tag) values ('LOL');
-- insert into tags (tag) values ('lol');
-- insert into tags (tag) values ('lolita');
-- insert into tags (tag) values ('lolz');
-- insert into tags (tag) values ('lolly');


-- insert into posts (post_title, post_description, user_id) values ('My Workout', 'Insane Chest Workout 2/28/2022', 'lKsjf23Dlds12') RETURNING post_id;

