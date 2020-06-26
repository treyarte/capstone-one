from flask import Blueprint, render_template, g, flash

home = Blueprint("home", __name__, template_folder="templates")

@home.route("/")
def homepage():
    """Home page of the application"""
    if g.user:
        return render_template("home.html")

    #if the user is not logged in show this 
    return render_template("landing-page.html")


