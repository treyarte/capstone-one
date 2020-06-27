import os
from flask import Flask, redirect, render_template, flash, session, g, Response, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from app.models import connect_db, User

from app.home.routes import home
from app.users.routes import users_route
from app.droplists.routes import droplist_routes
from app.droplist_items.routes import droplist_items_route
from app.locations.routes import locations
from app.api.routes import api

CURR_USER_KEY = "curr_user"

def create_app():
    app = Flask(__name__)

    #use the local db if environ DB_URI variable is not set
    app.config["SQLALCHEMY_DATABASE_URI"] = ( os.environ.get("DATABASE_URL", "postgres:///mydroplist"))

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "this is my secret")
    #removes caching
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    toolbar = DebugToolbarExtension(app)

    connect_db(app)

    @app.before_request
    def add_global_user():
        """Added logged in user to global"""

        if CURR_USER_KEY in session:
            g.user = User.query.get(session[CURR_USER_KEY])
        
        else:
            g.user = None

    @app.errorhandler(404)
    def not_found(e):

        return render_template("404.html"), 404

    app.register_blueprint(home)
    app.register_blueprint(users_route)
    app.register_blueprint(droplist_routes)
    app.register_blueprint(droplist_items_route)
    app.register_blueprint(locations)
    app.register_blueprint(api)

    return app

