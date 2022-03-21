from functools import wraps
from werkzeug.utils import secure_filename
from os import environ as env
from werkzeug.exceptions import HTTPException
from authlib.integrations.flask_client import OAuth
from authlib.oauth2.rfc6749 import OAuth2Token
from six.moves.urllib.parse import urlencode
from flask import Flask, render_template, request, g, redirect, url_for, send_file, jsonify, session, current_app

from bs4 import BeautifulSoup
from scrape_quotes import *

import os
import db
import io
import json
import random

# import jinja2
# from jinja2.ext import Extension


# jinja_env = jinja2.Environment(
#     loader=jinja2.FileSystemLoader('.'),
#     extensions=['jinja2.ext.do']
# )
'''
Questions:
Liking/dislike button - IS there a way you can update likes and dislikes realtime if we have two buttons? How will the server know when the button is pressed and specific post id?
Searching - realtime searching after onpress of each letter ("autocomplete")? How do we pass the server the string we typed so far without pressing the search button or enter?
'''
# TODO: Test all functionality to connect to front end
# import psycopg2 #installed binary version # unable to use heroku psql #not able to understand how to access the db
app = Flask(__name__)
app.secret_key = env['CLIENT_SECRET']

# jinja_env = jinja2.Environment(
#     loader=jinja2.FileSystemLoader('.'),
#     extensions=['jinja2.ext.do']
# )

oauth = OAuth(app)

def fetch_token(name, request):
    token = OAuth2Token.find(
        name=name,
        user=request.user
    )
    return token.to_token()

auth0 = oauth.register('auth0',
    client_id=env['CLIENT_ID'],
    client_secret=env['CLIENT_SECRET'],
    api_base_url='https://' + env['DOMAIN'],
    access_token_url='https://' + env['DOMAIN'] + '/oauth/token',
    authorize_url='https://' + env['DOMAIN'] + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
    server_metadata_url='https://' + env['DOMAIN'] + '/.well-known'
                        '/openid-configuration',
    fetch_token=fetch_token,
    )

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)
  return decorated

@app.before_first_request
def initialize():
    db.setup()

    # check to see if there are already quotes in the db
    if (len(db.get_all_quotes()) == 0):
        # Scrape 
        quotes = generate_quotes()
        db.add_quotes(quotes)

@app.route('/')
def main_page():
    all_posts = db.get_all_posts()
    all_exercises = db.get_all_exercises()
    rand = random.randint(1, 49)
    chosen_quote = db.get_quote(rand)
    la_quote = chosen_quote[0][0]
    if 'Erin' in la_quote:
        la_quote.replace('- -', '-')

    return render_template('home.html', posts = all_posts, exercises=all_exercises, quote=la_quote)

########################## TAG ##################################
# @app.route('/tag/<int:tag_id>', methods=['GET'])
# def display_tag_posts(tag_id):
#     # get all posts from this 

# Get all hashtags from a sentence
def get_all_hashtag(text):
    ret = []

    splitter = text.split()
    
    for word in splitter:
        if word[0] == '#':
            ret.append(word[1:])
    
    return ret


########################## PROFILE #############################

# return data containing necessary things for a profile
@app.route('/profile/<string:id>')
def profile(id):
    data = {
        'username': '',
        'first_name': '',
        'last_name': '',
        'followers': 0,
        'following': 0,
    }
    # IF LOGGED IN return your profile page else return a blurred out page or soemthing where in middle says sign in / log in that directs to auth0
    if 'profile' in session:
        ####### maybe add in !!!!!
        # retrieve stuff from db about user
        # user_profile = db.get_user_profile(session['profile']['user_id'])
        # data['username'] = user_profile[1]
        # data['first_name'] = user_profile[2]
        # data['last_name'] = user_profile[3]
        # data['followers'] = user_profile[4]
        # data['following'] = user_profile[5]

        # user_posts = db.get_user_posts(session['profile']['user_id'])
        # data['posts'] = user_posts

        # return render_template('profile.html', data=data)
        return render_template('profile.html')
    # TODO: direct to new page
    else:
        # return render_template('no_profile.html', data=data)
        return render_template('profile.html')

########################## DM ######################################
@app.route('/messages')
def messages():
    return render_template('messages.html')

########################## LOGIN / LOGOUT ##################################

### CHECK TO SEE IF USER IS FIRST TIME OR NOT
def first_time_user(session):
    # for some reason, it'll get a profile from the db, but when I look in the db, the user was never added...
    current_app.logger.info(db.get_user_profile(session['user_id']))
    if len(db.get_user_profile(session['user_id'])) == 0:
        full_name = session['name'].split(' ')
        fname = full_name[0]
        lname = full_name[1]
        db.add_user(session['user_id'], fname, lname)
        return True
    else:
        return False


@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }

    #### WON"T ADD TROLL
    if first_time_user(session['profile']):
        current_app.logger.info('FIRST TIMER')
    else:
        current_app.logger.info('NOT FIRST TIMER')
    
    ### TODO: make functionality if he/she is already a user in the db
    
    return redirect('/')

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=url_for('callback_handling', _external=True))

@app.route('/logout')
@requires_auth
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('main_page', _external=True), 'client_id': env['CLIENT_ID']}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

########################## CREATE POST ##################################

@app.route('/create_post', methods=["GET"])
@requires_auth
def create_post():
    
    # if logged in 
    # if 'profile' in session:
    #     status = request.args.get("status", "")
        
    #     with db.get_db_cursor() as cur:
    #         image_ids = db.get_image_ids()
    #         return render_template("create_post.html", image_ids = image_ids)

    # TODO: create html page that tells them to sign in to view this page basically
    # else:
    return render_template('create_post.html')

### IMAGES
@app.route('/post/<int:post_id>')
def view_post_image(post_id):
    image_row = db.get_post(post_id)[0]
    stream = io.BytesIO(image_row[4])
    # use special "send_file" function
    return send_file(stream, attachment_filename=image_row["filename"]) 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', "gif"]

@app.route('/create_post', methods=['POST'])
@requires_auth
def upload_post():
    if 'image' not in request.files:
        return redirect(url_for("main_page", status="Image Upload Failed: No selected file"))
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for("main_page", status="Image Upload Failed: No selected file"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        data = file.read()
        description = request.form.get("text")
        user_id = session['profile']['user_id']
        post_id = db.add_post(user_id, description, filename, data)[0]
        all_hash = get_all_hashtag(description)
        lower_hash = []
        for hash in all_hash:
            # 'lol', 'hype'
            # eliminates 'Lol', 'lol' dupes
            if hash.lower() not in lower_hash:
                lower_hash.append(hash.lower())
                # add post to hashtag list
                # How do I connect this post to THIS hashtag
                
                if not db.has_hashtag(hash):
                    db.add_hashtag(hash) # return tag ID like we do with post
                    #todo
                # if tag exists we do some kinda connection between tag id and postid
                else:
                    # todo
            
            # add this hashtag 
        
        # print(post_id)
        text = request.form.getlist("text[]")
        exercises = []
        for x in range(0, len(text), 3):
            exercises.append(text[x:x+3])
        for exercise in exercises:
            if exercise[2].isdigit():
                db.add_exercise(post_id, exercise[0], exercise[1], exercise[2])
            else:
                db.add_time_exercise(post_id, exercise[0], exercise[1], exercise[2])
    return redirect(url_for("main_page", status="Image Uploaded Successfully"))

########################## LIKE / DISLIKE ##################################
# I'm confused how the heck we are going to do this
# TODO: I need to understand and populate shit into the db first to test.

########################## SEARCH ##################################
@app.route('/search', methods=['POST'])
def search_text():

    # search through usernames
    # TODO: some button to check if we should search through username or hashtag
    to_search = request.form.get('search', '') # if there's nothing in search, it'll just search through all users
    search_type = request.form.get('search_type', '')
    if search_type == 'name':
        # full_name search
        found_search = db.search_name(to_search)
        return render_template('searched.html', users=found_search)
    elif search_type == 'username':
        found_search = db.search_user(to_search)
        return render_template('searched.html', users=found_search)
    elif search_type == 'tag':
        found_search = db.search_tag(to_search)
        return render_template('searched_tag.html', tags=found_search)

    
    # TODO: how to return back information without reloading the page?

    # print(found_search)
    # return render_template('searched.html', users=found_search)

# @app.route('/posts/<post_id>', methods=['GET'])
# def get_post_exercises(post_id):
#     exercises = db.get_post_exercises(post_id)
#     return render_template("home.html", exercises = exercises)
