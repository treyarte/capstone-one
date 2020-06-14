import os
from flask import Flask, redirect, render_template, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Stocker, ForkliftDriver, DropList, Location, DropListItem, Item
from sqlalchemy.exc import IntegrityError
from forms import SignUpForm, LoginForm, LocationForm, ItemForm, DropListForm
from functools import wraps

app = Flask(__name__)

#use the local db if environ DB_URI variable is not set
app.config["SQLALCHEMY_DATABASE_URI"] = ( os.environ.get("Database_URL", "postgres:///mydroplist"))

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "this is my secret")
#removes caching
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

toolbar = DebugToolbarExtension(app)

connect_db(app)

CURR_USER_KEY = "curr_user"

@app.before_request
def add_global_user():
    """Add logged in user to global"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    
    else:
        g.user = None

def authorize(func):
    """decorator that check if a user is authorize"""
    @wraps(func)
    def inner_function(*args, **kwargs):
        if not g.user:
            flash("Unauthorized Access", "danger")
            return redirect("/")
        return func(*args, **kwargs)
    #either use wraps or below to prevent overwritting of endpoints
    # inner_function.__name__ = func.__name__
    return inner_function

def check_owner(func):
    """decorator that check if a user is the owner of a droplist"""
    @wraps(func)
    def inner_function(droplist_id, *args,**kwargs):
        drop_list = DropList.query.get_or_404(droplist_id)

        if g.user.stocker.id != drop_list.stocker_id:
            flash("Unauthorized access")
            return redirect("/")
        return func(droplist_id, *args,**kwargs)
    return inner_function
    

def handle_login(user):
    """Log a user in"""
    session[CURR_USER_KEY] = user.id

def handle_logout():
    """Remove the user from the session to log them out"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def check_item_in_droplist(droplist_id, item_id):
    """check if an item is in the specified droplist"""
    droplist = DropList.query.get_or_404(droplist_id)
    #checking to see if the item even exists
    Item.query.get_or_404(item_id)

    item = db.session.query(Item).join(
                                DropListItem, Item.id==DropListItem.item_id).join(
                                DropList, DropList.id == DropListItem.drop_list_id).filter(
                                Item.id==item_id).filter(DropList.id==droplist_id).first()

    return [droplist, item]

@app.route("/")
def homepage():
    """Home page of the application"""
    return render_template("home.html")
######################################################
# Login and sign-up routes 

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
        
            if form.user_type.data == "stocker":
                stocker = Stocker(user_id = user.id)
                db.session.add(stocker)
                db.session.commit()
            elif form.user_type.data == "driver":
                driver = ForkliftDriver(user_id = user.id)
                db.session.add(stocker)
                db.session.commit()

        except IntegrityError:
            flash("Email is already in use", "danger")
            return render_template("users/signup.html", form=form)
        
        handle_login(user)

        return redirect("/")
    
    return render_template("users/signup.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate a user"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(email=form.email.data, password=form.password.data)

        if user:
            flash("Successfully signed in", "success")
            handle_login(user)
            return redirect("/")
        else:
            flash("Invalid Login/Password combination")
        

    return render_template("users/login.html", form=form)

@app.route("/logout", methods=["POST"])
def logout():
    """log out a user"""

    handle_logout()
    flash("Successfully logged out", "success")
    return redirect("/")

######################################################
# Droplist routes
@app.route("/droplist/new", methods=["GET", "POST"])
@authorize
def create_droplist():
    """create a new droplist"""
    form = DropListForm()

    form.set_choices(db, ForkliftDriver, User)

    if form.validate_on_submit():
        drop_list = DropList(stocker_id=g.user.stocker.id, notes=form.notes.data, forklift_driver_id = form.forklift_driver_id.data)
        db.session.add(drop_list)
        db.session.commit()
        
        flash("Droplist successfully created")
        return redirect(f"/droplist/{drop_list.id}")
    
    return render_template("droplists/form.html", form=form)


@app.route("/droplist/<int:drop_list_id>")
@authorize
def show_drop_list(drop_list_id):
    drop_list = DropList.query.get_or_404(drop_list_id)

    return render_template("droplists/show.html", drop_list=drop_list)

@app.route("/droplist/<int:droplist_id>/edit", methods=["GET", "POST"])
@authorize
@check_owner
def edit_drop_list(droplist_id):
    """Allow the user to edit their drop list"""
    droplist = DropList.query.get_or_404(droplist_id)
    
    form = DropListForm(obj=droplist)

    form.set_choices(db, ForkliftDriver, User)

    if form.validate_on_submit():
        droplist.notes = form.notes.data
        droplist.forklift_driver_id = form.forklift_driver_id.data

        db.session.commit()

        flash("Drop list successfully updated")
        return redirect(f"/droplist/{droplist_id}")
    
    return render_template("/droplists/edit.html", form=form)

@app.route("/droplist/<int:droplist_id>/delete")
@authorize
@check_owner
def delete_droplist(droplist_id):
    """Delete a droplist"""
    droplist = DropList.query.get_or_404(droplist_id)

    db.session.delete(droplist)
    db.session.commit()

    flash("droplist was successfully deleted", "success")
    return redirect("/")

#####################################################
# Droplist items routes

@app.route("/droplist/<int:droplist_id>/items")
@authorize
def show_droplist_items(droplist_id):
    """Show items that are in the droplist"""
    droplist = DropList.query.get_or_404(droplist_id)

    return render_template("/droplist_items/index.html", droplist=droplist)

@app.route("/droplist/<int:droplist_id>/items/add", methods=["GET","POST"])
@authorize
@check_owner
def add_item_to_drop_list(droplist_id):
    """Add an item to the drop list"""
    droplist = DropList.query.get_or_404(droplist_id)
    
    form = ItemForm()

    form.set_choices(db, Location)

    if form.validate_on_submit():
        item = Item(
                row_letter=form.row_letter.data,
                column_number=form.column_number.data,
                location_id=form.location_id.data,
                description=form.description.data
        )

        db.session.add(item)
        db.session.commit()

        droplist.items.append(item)

        db.session.commit()

        return redirect(f"/droplist/{droplist.id}")

    return render_template("/droplist_items/new.html", form=form)

@app.route("/droplist/<int:droplist_id>/items/<int:item_id>")
@authorize
def show_item(droplist_id,item_id):
    """show a specific item in a droplist"""
    droplist, item = check_item_in_droplist(droplist_id, item_id)

    if item == None:
        #for now
        return redirect(404)

    return render_template("/droplist_items/show.html", item=item)

@app.route("/droplist/<int:droplist_id>/items/<int:item_id>/edit", methods=["GET", "POST"])
@authorize
@check_owner
def edit_droplist_item(droplist_id, item_id):
    """edit a droplist item"""
    droplist, item = check_item_in_droplist(droplist_id, item_id)

    if item == None:
        #for now
        return redirect(404)

    form = ItemForm(obj=item)

    form.set_choices(db, Location)

    if form.validate_on_submit():
        item.description = form.description.data
        item.row_letter = form.row_letter.data
        item.column_number = form.column_number.data
        item.location_id = form.location_id.data

        db.session.commit()

        flash("Item successfully updated")
        return redirect(f"/droplist/{droplist_id}/items/{item_id}")

    return render_template("/droplist_items/edit.html", form=form)

@app.route("/droplist/<int:droplist_id>/items/<int:item_id>/delete")
@authorize
@check_owner
def delete_droplist_item(droplist_id, item_id):
    """delete an item from a droplist"""
    droplist, item = check_item_in_droplist(droplist_id, item_id)

    if item == None:
        #for now
        return redirect(404)
    
    db.session.delete(item)
    db.session.commit()

    flash("successfully deleted the item", "success")
    return redirect(f"/droplist/{droplist.id}/items")



#####################################################
# Location routes

@app.route("/locations/new", methods=["GET", "POST"])
@authorize
def create_location():
    """Creates a location for a drop list item"""
    form = LocationForm()

    if form.validate_on_submit():
        location = Location(name=form.location.data)
        db.session.add(location)
        db.session.commit()
        return redirect(f"/locations/{location.id}")
    
    return render_template("locations/new.html", form=form)

@app.route("/locations/<int:location_id>")
@authorize
def show_location(location_id):
    """Show a location"""
    location = Location.query.get_or_404(location_id)
    return render_template("/locations/show.html", location=location)

@app.route("/locations/<int:location_id>/edit", methods=["GET", "POST"])
@authorize
def edit_location(location_id):
    """edit a location"""
    location = Location.query.get_or_404(location_id)

    form = LocationForm(obj=location)

    if form.validate_on_submit():
        location.name = form.name.data

        db.session.commit()
        
        flash("Location successfully updated")
        return redirect(f"/locations/{location.id}")
    
    return render_template("/locations/edit.html", form=form)

@app.route("/locations/<int:location_id>/delete", methods=["POST"])
@authorize
def delete_location(location_id):
    """delete a location"""
    location = Location.query.get_or_404(location_id)

    db.session.delete(location)
    db.session.commit()

    flash("Location successfully deleted")
    return redirect("/")



# @app.after_request
# def add_header(req):
#     "make each request header non-caching."

#     req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     req.headers["Pragma"] = "no-cache"
#     req.headers["Expires"] = "0"
#     req.headers["Cache-Control"] = "public, max-age=0"
#     return req