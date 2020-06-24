import os
from flask import Flask, redirect, render_template, flash, session, g, Response, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from app.models import connect_db, db, Role, User, Stocker, ForkliftDriver, DropList, Location, Item, get_droplists
from sqlalchemy.exc import IntegrityError
from forms import SignUpForm, LoginForm, LocationForm, ItemForm, DropListForm, EditUserForm
from functools import wraps

from app.home.routes import home
from app.users.routes import users_route
from app.droplists.routes import droplist_routes

CURR_USER_KEY = "curr_user"

def create_app():
    app = Flask(__name__)

    #use the local db if environ DB_URI variable is not set
    app.config["SQLALCHEMY_DATABASE_URI"] = ( os.environ.get("Database_URL", "postgres:///mydroplist"))

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "this is my secret")
    #removes caching
    # app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    toolbar = DebugToolbarExtension(app)

    connect_db(app)

    @app.before_request
    def add_global_user():
        """Add logged in user to global"""

        if CURR_USER_KEY in session:
            g.user = User.query.get(session[CURR_USER_KEY])
        
        else:
            g.user = None

    app.register_blueprint(home)
    app.register_blueprint(users_route)
    app.register_blueprint(droplist_routes)

    return app

