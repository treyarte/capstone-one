from flask import session, flash, redirect, g
from app.models import User, DropList
from functools import wraps

def check_logged(func):
    """decorator that checks if an user is logged in"""
    @wraps(func)
    def inner_function(*args, **kwargs):
        if g.user:
            flash("You are already signed in", "warning")
            return redirect("/")
        return func(*args, **kwargs)
    return inner_function

def authorize(func):
    """decorator that check if an user is authorize"""
    @wraps(func)
    def inner_function(*args, **kwargs):
        if not g.user:
            flash("Please login to continue", "danger")
            return redirect("/")
        return func(*args, **kwargs)
    #either use wraps or below to prevent overwritting of endpoints
    # inner_function.__name__ = func.__name__
    return inner_function

def check_droplist_owner(func):
    """decorator that check if a user is the owner of a droplist"""
    @wraps(func)
    def inner_function(*args,**kwargs):
        droplist_id  = kwargs.get("droplist_id")
        droplist = DropList.query.get_or_404(droplist_id)

        if g.user.get_stocker.id != droplist.stocker_id: 
            flash("Unauthorized access", "danger")
            return redirect("/")
        return func(*args,**kwargs)
    return inner_function

def check_same_user(func):
    """check if the logged in user is the same user"""
    @wraps(func)
    def inner_function(*args, **kwargs):
        u_id = kwargs.get("user_id")
     
        u = User.query.get_or_404(u_id)

        if g.user.id != u.id:
            flash("Unauthorized access", "danger")
            return redirect("/")
        return func(*args, **kwargs)
    return inner_function

def check_droplist_access(func):
    """check if the current user have access to view the droplist"""
    @wraps(func)
    def inner_function(*args, **kwargs):
        droplist = DropList.query.get_or_404(kwargs.get("droplist_id"))
        if g.user.current_role.role == "stocker":
            if droplist.stocker.user_id != g.user.id:
                flash("Unauthorized access", "danger")
                return redirect("/droplists")

        elif g.user.current_role.role == "forklift_driver":
            if droplist.forklift_driver.user_id != g.user.id:
                flash("Unauthorized access", "danger")
                return redirect("/droplists")

        return func(*args, **kwargs)
    return inner_function

def check_stocker(func):
    """check if the current logged in user is a stocker"""
    @wraps(func)
    def inner_function(*args, **kwargs):
        if g.user.current_role.role != "stocker":
            flash("Only stockers can perform this action. Please change role in settings", "warning")
            return redirect("/")
        return func(*args, **kwargs)
    return inner_function

def check_driver(func):
    """check if the current logged in user is a driver"""
    @wraps(func)
    def inner_function(*args, **kwargs):
        if g.user.current_role.role != "forklift_driver":
            flash("Only drivers can perform this action. Please change role in settings", "warning")
            return redirect("/")
        return func(*args, **kwargs)
    return inner_function

def check_items(func):
    """check if a droplist have items"""
    @wraps(func)
    def inner_function(*args, **kwargs):
        droplist = DropList.query.get_or_404(kwargs.get("droplist_id"))

        if not droplist.droplist_items:
            flash("Droplist cannot be empty", "danger")
            return redirect("/")
        return func(*args, **kwargs)
    return inner_function

def check_complete(func):
    """check if a droplist is complete or not"""
    @wraps(func)
    def inner_function(*args, **kwargs):
        droplist = DropList.query.get_or_404(kwargs.get("droplist_id"))

        if droplist.status == "completed":
            flash("Droplist is already complete", "warning")
            return redirect("/")
        return func(*args, **kwargs)
    return inner_function

