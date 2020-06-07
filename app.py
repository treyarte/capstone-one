import os
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Stocker, ForkliftDriver, Request, Location, RequestItem, Item

app = Flask(__name__)

#use the local db if environ DB_URI variable is not set
app.config["SQLALCHEMY_DATABASE_URI"] = ( os.environ.get("Database_URL", "postgres:///mydroplist"))

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "this is my secret")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.route("/")
def homepage():
    """Home page of the application"""
    return("Hello World")

# @app.after_request
# def add_header(req):
#     "make each request header non-caching."

#     req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     req.headers["Pragma"] = "no-cache"
#     req.headers["Expires"] = "0"
#     req.headers["Cache-Control"] = "public, max-age=0"
#     return req