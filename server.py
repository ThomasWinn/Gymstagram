from functools import wraps
from werkzeug.utils import secure_filename
from os import environ as env
from werkzeug.exceptions import HTTPException
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from flask import Flask, render_template, request, g, redirect, url_for, send_file, jsonify, session
import os
import db
import io
import json

# import psycopg2 #installed binary version # unable to use heroku psql #not able to understand how to access the db
app = Flask(__name__)
app.secret_key = env['CLIENT_SECRET']

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=env['CLIENT_ID'],
    client_secret=env['CLIENT_SECRET'],
    api_base_url='https://' + env['DOMAIN'],
    access_token_url='https://' + env['DOMAIN'] + '/oauth/token',
    authorize_url='https://' + env['DOMAIN'] + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

@app.before_first_request
def initialize():
    db.setup()

@app.route('/')
def main_page():
    return render_template('home.html')

@app.route('/create_post', methods=["GET"])
def create_post():

    status = request.args.get("status", "")
    
    with db.get_db_cursor() as cur:
        image_ids = db.get_image_ids()
        return render_template("create_post.html", image_ids = image_ids)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', "gif"]

### IMAGES
@app.route('/image/<int:img_id>')
def view_image(img_id):
    image_row = db.get_image(img_id)
    stream = io.BytesIO(image_row["data"])
         
    # use special "send_file" function
    return send_file(stream, attachment_filename=image_row["filename"])    

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', "gif"]

@app.route('/create_post', methods=['POST'])
def upload_post():
    if 'image' not in request.files:
        return redirect(url_for("main_page", status="Image Upload Failed: No selected file"))
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for("main_page", status="Image Upload Failed: No selected file"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        data = file.read()
        db.upload_image(data, filename)

    return redirect(url_for("main_page", status="Image Uploaded Successfully"))
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
    return redirect('/')

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri='http://localhost:5000/callback')

@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('main_page', _external=True), 'client_id': env['CLIENT_ID']}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated
