
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

# CREATE functions
def add_post(user_id, description, filename, data):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding post %s, %s, %s, %s", user_id, description, filename, data)
        cur.execute("INSERT INTO posts (user_id, description, filename, data) VALUES (%s, %s, %s, %s) RETURNING post_id", (user_id, description, filename, data))
        return cur.fetchone()

def add_exercise(post_id, exercise_name, num_sets, num_reps):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding exercise %s, %s, %s, %s", post_id, exercise_name, num_sets, num_reps)
        cur.execute("INSERT INTO exercises (post_id, time_based, exercise_name, num_sets, num_reps) VALUES (%s, false, %s, %s, %s)", (post_id, exercise_name, num_sets, num_reps))

def add_time_exercise(post_id, exercise_name, num_time, time_units):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding time based exercise %s, %s, %s, %s", post_id, exercise_name, num_time, time_units)
        cur.execute("INSERT INTO exercises (post_id, time_based, exercise_name, num_time, time_units) VALUES (%s, true, %s, %s, %s)", (post_id, exercise_name, num_time, time_units))

def add_user(user_id, fname, lname):
    with get_db_cursor(True) as cur:
        full_name = fname + ' ' + lname
        current_app.logger.info("Adding User %s, %s, %s, %s", user_id, fname, lname, full_name)
        cur.execute("INSERT INTO users (user_id, first_name, last_name, full_name) VALUES (%s, %s, %s, %s)", (user_id, fname, lname, full_name))

def like_post(post_id, user_id):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding Like %s, %s", post_id, user_id)
        cur.execute("INSERT INTO likes (post_id, user_id) VALUES (%s, %s)", (post_id, user_id))

def follow_user(followed_id, follower_id):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding Follower %s, %s", followed_id, follower_id)
        cur.execute("INSERT INTO followers (followed_id, follower_id) VALUES (%s, %s)", (followed_id, follower_id))

def add_comment(post_id, user_id, comment):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding Comment %s, %s, %s", post_id, user_id, comment)
        cur.execute("INSERT INTO comments (post_id, user_id, comment) VALUES (%s, %s, %s)", (post_id, user_id, comment))

# READ functions 

# Probably need to call this in conjunction with get_post_exercises... running an inner/natural join between the exercises
# and posts tables might work but will get really messy

def get_user_profile(user):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM users where user_id = %s", (user,))
        return cur.fetchall()

def get_all_posts():
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM posts ORDER BY tstamp DESC")
        return cur.fetchall()

def get_all_users():
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM users")
        return cur.fetchall()

def get_all_posts_reverse():
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM posts ORDER BY tstamp ASC")
        return cur.fetchall()

def get_user_posts(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM posts where user_id = %s ORDER BY tstamp DESC", (user_id,))
        return cur.fetchall()

def get_post(post_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM posts where post_id = %s", (post_id,))
        return cur.fetchall()

# retrieve all exercises associated with a post
def get_post_exercises(post_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM exercises WHERE post_id = %s", (post_id,))
        return cur.fetchall()

def get_all_exercises():
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM exercises")
        return cur.fetchall()

def get_all_likes():
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM likes")
        return cur.fetchall()

def get_num_likes(post_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS num_likes FROM likes where post_id = %s", (post_id,))
        return cur.fetchone()

def get_post_likes(post_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM likes where post_id = %s", (post_id,))
        return cur.fetchall()

# Get Followers
def get_num_followers(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS num_followers FROM followers where followed_id = %s", (user_id,))
        return cur.fetchone()

def get_followers(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT user_id, username, full_name, bio FROM followers INNER JOIN users ON users.user_id = followers.follower_id WHERE followed_id = %s", (user_id,))
        return cur.fetchall()

def get_num_followed(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS num_followed FROM followers where follower_id = %s", (user_id,))
        return cur.fetchone()

def get_followed(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT user_id, username, full_name, bio FROM followers INNER JOIN users ON users.user_id = followers.followed_id WHERE follower_id = %s", (user_id,))
        return cur.fetchall()

def get_num_posts(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS num_posts FROM posts where user_id = %s", (user_id,))
        return cur.fetchone()

def get_profile_pic_text(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT filename FROM users where user_id = %s", (user_id,))
        return cur.fetchall()

def get_profile_pic_bytea(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT data FROM users where user_id = %s", (user_id,))
        return cur.fetchall()

def get_first_name(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT first_name FROM users where user_id = %s", (user_id,))
        return cur.fetchall()

def get_last_name(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT last_name FROM users where user_id = %s", (user_id,))
        return cur.fetchall()

def get_username(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT username FROM users where user_id = %s", (user_id,))
        return cur.fetchall()

def get_bio(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT bio FROM users where user_id = %s", (user_id,))
        return cur.fetchall()

# Get Comments
def get_post_comments(post_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM comments where post_id = %s ORDER BY tstamp DESC", (post_id,))
        return cur.fetchall()

def get_user_comments(user_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM comments where user_id = %s", (user_id,))
        return cur.fetchall()

def get_all_comments():
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM comments")
        return cur.fetchall()

# UPDATE functions
# Maybe we update the exercises associated with a post by deleting all of the posts exercises and just re-saving them?
# Manually updating/deleting each exercise when a user 

def update_post(post_id, description):
    with get_db_cursor(True) as cur:
        cur.execute("UPDATE posts SET description = %s WHERE post_id = %s", (description, post_id))

def update_comment(comment_id, edited_comment):
    with get_db_cursor(True) as cur:
        cur.execute("UPDATE comments SET comment = %s WHERE comment_id = %s", (edited_comment, comment_id))

def update_user(user_id, username, first_name, last_name, bio):
    with get_db_cursor(True) as cur:
        fullname = first_name + " " + last_name
        cur.execute("UPDATE users SET username = %s, first_name = %s, last_name = %s, full_name = %s, bio = %s WHERE user_id = %s", 
        (username, first_name, last_name, fullname, bio, user_id))

def update_user_picture(user_id, filename, data):
    with get_db_cursor(True) as cur:
        cur.execute("UPDATE users SET filename = %s, data = %s WHERE user_id = %s", (filename, data, user_id))

# DELETE functions

# post deletion will cascade and delete associated exercises
def delete_post(post_id):
    with get_db_cursor(True) as cur:
        cur.execute("DELETE FROM posts WHERE post_id = %s", (post_id,))

def delete_exercise(exercise_id):
    with get_db_cursor(True) as cur:
        cur.execute("DELETE FROM exercises WHERE exercise_id = %s", (exercise_id,))

# delete all exercises associated with a post
def delete_exercises_by_post(post_id):
    with get_db_cursor(True) as cur:
        cur.execute("DELETE FROM exercises WHERE post_id = %s", (post_id,))

def unlike_post(post_id, user_id):
    with get_db_cursor(True) as cur:
        cur.execute("DELETE FROM likes WHERE post_id = %s and user_id = %s", (post_id, user_id))

def unfollow(follower_id, followed_id):
    with get_db_cursor(True) as cur:
        cur.execute("DELETE FROM followers WHERE follower_id = %s and followed_id = %s", (follower_id, followed_id))

def delete_comment(comment_id):
    with get_db_cursor(True) as cur:
        cur.execute("DELETE FROM comments WHERE comment_id = %s", (comment_id,))

########################## SEARCH #############################
def search_user(text):
    with get_db_cursor() as cur:
        # same thing as select all users where text in username HAVENT TRIED YET
        # text = text.lower()
        query = "%" + text + "%"
        cur.execute('SELECT * FROM users WHERE username ilike %s', (query,))
        return cur.fetchall()

# full_name search
def search_name(text):
    with get_db_cursor() as cur:
        # text = text.lower()
        query = "%" + text + "%"
        cur.execute('SELECT * FROM users WHERE full_name ilike %s', (query,))
        return cur.fetchall()

# Search for tags which start from the tag
def search_tag(text):
    with get_db_cursor() as cur:
        text = text.lower()
        query = text + "%"
        cur.execute('SELECT * FROM tags WHERE tag like %s', (query,))
        return cur.fetchall()

########################## TAGS #############################

def get_hashtag_by_id(id):
    with get_db_cursor() as cur:
        cur.execute('SELECT * FROM tags WHERE tag_id=%s', (id,))
        return cur.fetchall()

def get_hashtag_by_text(text):
    with get_db_cursor() as cur:
        query = text.lower()
        cur.execute('SELECT * FROM tags WHERE tag=%s', (query,))
        return cur.fetchall()

# def get_hashtag_by_text(text):
#     with get_db_cursor() as cur:
#         query = text
#         cur.execute('SELECT * FROM tags WHERE tag ilike %s', (query,))
#         return cur.fetchall()

def add_post_to_tag(post_id, tag_id):
    with get_db_cursor(True) as cur:
        cur.execute('INSERT INTO post_tags (post_id, tag_id) VALUES (%s,%s)', (post_id, tag_id))


def add_hashtag(text):
    with get_db_cursor(True) as cur:
        text = text.lower()
        cur.execute("INSERT INTO tags (tag) VALUES (%s) RETURNING tag_id", (text,))
        return cur.fetchone()

def get_post_id_from_tag(t_id):
    with get_db_cursor() as cur:
        cur.execute('SELECT post_id FROM post_tags WHERE tag_id=%s', (t_id,))
        return cur.fetchall()

# def add_post_to_tag(tag_id, post_id):
#     with get_db_cursor(True) as cur:
#         current_app.logger.info("Adding Tag %s, %s", tag_id, post_id)
#         cur.execute("INSERT INTO tags (post_id, user_id, comment) VALUES (%s, %s, %s)", (post_id, user_id, comment))

########################## QUOTES #############################
def add_quotes(quotes):
    with get_db_cursor(True) as cur:
        for quote in quotes:
            cur.execute('INSERT into quotes_table (the_quote) VALUES (%s)', (quote,))

def get_all_quotes():
    with get_db_cursor() as cur:
        cur.execute('SELECT * FROM quotes_table')
        return cur.fetchall()

def get_quote(id):
    with get_db_cursor() as cur:
        cur.execute('SELECT the_quote FROM quotes_table WHERE quote_id=%s', (id,))
        return cur.fetchall()