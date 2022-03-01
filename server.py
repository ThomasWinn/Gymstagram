from crypt import methods
from telnetlib import STATUS
from flask import Flask, render_template, request, g, redirect, url_for
import os
import db
import io
from werkzeug.utils import secure_filename
# import psycopg2 #installed binary version # unable to use heroku psql #not able to understand how to access the db
app = Flask(__name__)

@app.before_first_request
def initialize():
    db.setup()

@app.route('/')
def main_page():
    return render_template('home.html')

@app.route('/create_post')
def create_post():
    return render_template('create_post.html')

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