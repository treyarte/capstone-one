from flask import Blueprint, render_template, g, flash, redirect
from app.helpers.decorators import authorize

home = Blueprint("home", __name__, template_folder="templates")

@home.route("/")
def homepage():
    """Home page of the application"""
    if g.user:
        return redirect("/droplists")

    #if the user is not logged in show this 
    return render_template("landing-page.html")

@home.route("/statistics")
@authorize
def stats_page():
    """Page where user can create graphs"""

    return render_template("statistics-page.html")