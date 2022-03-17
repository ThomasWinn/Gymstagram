drop table exercises;
drop table following;
drop table images;
drop table likes;
drop table dislikes;
drop table posts;
drop table users;

create table users (
  user_id text PRIMARY KEY,
  username varchar(255),
  first_name varchar(255),
  last_name varchar(255)
);

create table following (
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
  user_liked text,
  UNIQUE (post_id, user_liked)
);

create table dislikes (
  post_id INT,
  user_disliked text,
  UNIQUE (post_id, user_disliked)
);

-- insert into users (user_id, username, first_name, last_name) values ('lKsjf23Dlds12', 'liux2789', 'Hughdan', 'Liu');
-- insert into posts (post_title, post_description, user_id) values ('My Workout', 'Insane Chest Workout 2/28/2022', 'lKsjf23Dlds12') RETURNING post_id;

