
from contextlib import contextmanager
import logging
import os

from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None

def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    current_app.logger.info(f"creating db connection pool")
    pool = ThreadedConnectionPool(1, 4, dsn=DATABASE_URL, sslmode='require')


@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
      cursor = connection.cursor(cursor_factory=DictCursor)
      try:
          yield cursor
          if commit:
              connection.commit()
      finally:
          cursor.close()

def get_image(img_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM imagess where image_id=%s", (img_id,))
        return cur.fetchone()

def upload_image(data, filename):
    with get_db_cursor(True) as cur:
        cur.execute("insert into imagess (filename, data) values (%s, %s)", (filename, data))

def get_image_ids():
    with get_db_cursor() as cur:
        cur.execute("select image_id from imagess;")
        return [r['image_id'] for r in cur]

# CREATE functions
def add_post(title, description, user_id):
    with get_db_cursor() as cur:
        current_app.logger.info("Adding post %s, %s, %s", title, description, user_id)
        cur.execute("INSERT INTO posts (post_title, post_description, user_id) VALUES (%s, %s, %s)", (title, description, user_id))

# This is tricky, idk how we're gonna retrive the post_id associated with the exercise in order to establish the foreign
# key relationship
def add_exercise(post_id, time_based, exercise_name, num_sets, num_reps, num_time, time_units):
    with get_db_cursor() as cur:
        current_app.logger.info("Adding exercise %s, %s, %s, %s, %s, %s, %s", post_id, time_based, exercise_name, num_sets, num_reps, num_time, time_units)
        cur.execute("INSERT INTO exercises (post_id, time_based, exercise_name, num_sets, num_reps, num_time, time_units) VALUES (%s, %s, %s, %s, %s, %s, %s)", (post_id, time_based, exercise_name, num_sets, num_reps, num_time, time_units))


# READ functions 

# Probably need to call this in conjunction with get_post_exercises... running an inner/natural join between the exercises
# and posts tables might work but will get really messy
def get_all_posts():
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM posts")
        return cur.fetchall()

def get_user_posts(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM posts where user_id = %s", (user_id,))
        return cur.fetchall()

# retrieve all exercises associated with a post
def get_post_exercises(post_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM exercises WHERE post_id = %s", (post_id,))
        return cur.fetchall()

# UPDATE functions
# Maybe we update the exercises associated with a post by deleting all of the posts exercises and just re-saving them?
# Manually updating/deleting each exercise when a user 
def update_post(post_id, title, description):
    with get_db_cursor() as cur:
        cur.execute("UPDATE posts SET post_title = %s, post_description = %s WHERE post_id = %s", (post_id,))


# DELETE functions

# post deletion will cascade and delete associated exercises and image
def delete_post(post_id):
    with get_db_cursor() as cur:
        cur.execute("DELETE FROM posts WHERE post_id = %s", (post_id,))

def delete_exercise(exercise_id):
    with get_db_cursor() as cur:
        cur.execute("DELETE FROM exercises WHERE exercise_id = %s", (exercise_id,))

# delete all exercises associated with a post
def delete_exercises_by_post(post_id):
    with get_db_cursor() as cur:
        cur.execute("DELETE FROM exercises WHERE post_id = %s", (post_id,))
