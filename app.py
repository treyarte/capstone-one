import os
from flask import Flask, redirect, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Stocker, ForkliftDriver, DropList, Location, DropListItem, Item
from forms import SignUpForm
from sqlalchemy.exec import IntegrityError

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

@app.route("/sign-up", methods=["GET", "POST"])
def signUp():
    """Signs a user up to the system"""
    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.sign_up(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email = form.email.data,
                department = form.department.data,
                password = form.password.data,
                image_url = form.image_url.data
            )
            db.session.commit()
        except IntegrityError:
            flash("Email is already in use")
            return render_template("users/signup.html", form=form)
            

        return redirect("/")
    
    return render_template("users/signup.html", form=form)

# @app.after_request
# def add_header(req):
#     "make each request header non-caching."

#     req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     req.headers["Pragma"] = "no-cache"
#     req.headers["Expires"] = "0"
#     req.headers["Cache-Control"] = "public, max-age=0"
#     return req