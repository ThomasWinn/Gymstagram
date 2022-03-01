-- -- DROP TABLE user_responses;

-- create table user (
--   time_created TIMESTAMP without time zone DEFAULT CURRENT_TIMESTAMP,
--   person_id SERIAL PRIMARY KEY,
--   name varchar(255) NOT NULL,
--   summoner_name varchar(255) NOT NULL,
--   league_playrate char(4),
--   first_bought varchar(15),
--   summoner_rank varchar(10),
--   summoner_roles varchar(15),
--   reason_why varchar(255)
-- );

-- insert into user_responses (name, summoner_name, league_playrate, first_bought, summoner_rank, summoner_roles, reason_why) values ('test boy', 'test_name', '1to2', 'skin', 'Challenger', 'TopMid', '');
-- insert into user_responses (name, summoner_name, league_playrate, first_bought, summoner_rank, summoner_roles, reason_why) values ('test grill', 'test_grill_name', '3to4', 'champion', 'Bronze', 'Support', '');

-- A table to hold images.
create table images (
  image_id SERIAL PRIMARY KEY,
  filename text,
  data bytea
);