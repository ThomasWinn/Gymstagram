DROP TABLE imagess;
create table imagess (
  image_id SERIAL PRIMARY KEY,
  filename text,
  data bytea
);

drop table exercises;
drop table images;
drop table posts;
create table posts (
  post_id SERIAL PRIMARY KEY,
  tstamp timestamp NOT NULL DEFAULT NOW(),
  post_title VARCHAR(255) NOT NULL,
  post_description text,
  user_id text
);

create table exercises (
    exercise_id SERIAL PRIMARY KEY,
    post_id INT,
    time_based boolean,
    exercise_name VARCHAR(255),
    num_sets INT,
    num_reps INT,
    num_time INT,
    time_units INT,
    CONSTRAINT fk_post
      FOREIGN KEY(post_id) 
	  REFERENCES posts(post_id)
	  ON DELETE CASCADE
);

create table images (
    img_id SERIAL PRIMARY KEY,
    post_id INT,
    filename text,
    data bytea,
    CONSTRAINT fk_post
      FOREIGN KEY(post_id) 
	  REFERENCES posts(post_id)
	  ON DELETE CASCADE
);

insert into posts (post_title, post_description, user_id) values ('My Workout', 'Insane Chest Workout 2/28/2022', '1');
insert into exercises (post_id, time_based, exercise_name, num_sets, num_reps) values (1, FALSE, 'Bench Press', 3, 8);

