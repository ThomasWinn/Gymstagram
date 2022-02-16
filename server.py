from flask import Flask, render_template, request, g
import os
# import psycopg2 #installed binary version # unable to use heroku psql #not able to understand how to access the db
app = Flask(__name__)

@app.route('/')
def main_page():
    return render_template('home.html')