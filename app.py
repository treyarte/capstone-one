import os
from flask import Flask, redirect, render_template, flash, session, g, Response, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, Role, User, Stocker, ForkliftDriver, DropList, Location, Item
from sqlalchemy.exc import IntegrityError
from forms import SignUpForm, LoginForm, LocationForm, ItemForm, DropListForm, EditUserForm
from functools import wraps

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

def handle_login(user):
    """Log a user in"""
    session[CURR_USER_KEY] = user.id

def handle_logout():
    """Remove the user from the session to log them out"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

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

    form.user_role.choices = db.session.query(Role.id, Role.role).all()

    if form.validate_on_submit():
        try:
            user = User.sign_up(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email = form.email.data,
                department = form.department.data,
                password = form.password.data,
                image_url = form.image_url.data,
                current_role_id = form.user_role.data
            )
            
            db.session.commit()
        
            if user.current_role.role == "stocker":
                stocker = Stocker(user_id = user.id)
                db.session.add(stocker)
                db.session.commit()
            elif user.current_role.role == "forklift_driver":
                driver = ForkliftDriver(user_id = user.id)
                db.session.add(driver)
                db.session.commit()

        except IntegrityError:
            flash("Email is already in use", "danger")
            return redirect("/sign-up")
        
        handle_login(user)

        flash(f"Welcome {user.first_name}!")
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

@app.route("/users")
def get_users():
    """get users in the system"""

    users = User.query.all()
    return render_template("/users/index.html", users=users)

@app.route("/users/<int:user_id>")
@authorize
def show_user(user_id):
    """show user details"""

    user = User.query.get_or_404(user_id)

    return render_template("/users/show.html", user=user)

@app.route("/users/settings", methods=["GET", "POST"])
@authorize
def edit_user():
    """edit user information"""

    form = EditUserForm(obj=g.user)

    if form.validate_on_submit():
        
        user = User.authenticate(g.user.email, form.current_password.data)
        
        if user:
            
            
            try:
                user.first_name=form.first_name.data
                user.last_name=form.last_name.data
                user.email = form.email.data
                user.department = form.department.data
                user.image_url = form.image_url.data
                user.current_role_id = form.current_role_id.data
                
                if form.new_password.data:
                    
                    if user.check_password_reused(form.new_password.data):
                        flash("Password is already in use")
                        return redirect("/users/settings")

                    user.password = form.new_password.data

                db.session.commit()

                flash("Profile successfully updated", "success")
                return redirect(f"/users/{user.id}")
            except IntegrityError:
                flash("Email is already in use", "danger")
                return redirect("users/settings")
        else:
            flash("invalid password", "danger")
            return redirect("/users/settings")
    
    return render_template("/users/edit.html", form=form)

@app.route("/users/<int:user_id>/delete", methods=["POST"])
@authorize
@check_same_user
def delete_user(user_id):
    """Delete a user from the system"""
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect("/")

######################################################
# Droplist routes
@app.route("/droplists")
@authorize
def droplist_index():
    """show all the users droplist"""

    droplists = None

    department_filter = request.args.get("department",g.user.department)

    if g.user.current_role.role == "stocker":
        droplists = g.user.get_stocker.get_droplists_by_department(department_filter)
    elif g.user.current_role.role == "forklift_driver":
        droplists = g.user.get_driver.droplists


    return render_template("/droplists/index.html", droplists = droplists)


@app.route("/droplists/new", methods=["GET", "POST"])
@authorize
@check_stocker
def create_droplist():
    """create a new droplist"""

    form = DropListForm(department = g.user.department)

    if form.validate_on_submit():
        droplist = DropList(stocker_id=g.user.get_stocker.id, department=form.department.data, description=form.description.data)
        db.session.add(droplist)
        db.session.commit()
        
        flash("Droplist successfully created")
        return redirect(f"/droplists/{droplist.id}")
    
    return render_template("droplists/form.html", form=form)


@app.route("/droplists/<int:droplist_id>")
@authorize
@check_droplist_access
def show_drop_list(droplist_id):
    droplist = DropList.query.get_or_404(droplist_id)

    return render_template("droplists/show.html", droplist=droplist)

@app.route("/droplists/<int:droplist_id>/send", methods=["GET", "POST"])
@authorize
@check_stocker
@check_droplist_owner
def send_droplist(droplist_id):
    """connects a droplist to a driver"""
    droplist = DropList.query.get_or_404(droplist_id)
    forklift_driver_id = request.form.get("driverId", type=int)
    
    department = request.args.get("department", droplist.department)
    
    if forklift_driver_id:
        forklift_driver = ForkliftDriver.query.get_or_404(forklift_driver_id)
        
        droplist.forklift_driver_id = forklift_driver.id
        droplist.status="sent"    

        db.session.commit()

        flash("Droplist successfully sent")
        return redirect("/droplists")
    


    forklift_drivers = ForkliftDriver.get_drivers_by_department(department)

    return render_template("/droplists/send.html", drivers=forklift_drivers, droplist=droplist)

@app.route("/droplists/<int:droplist_id>/option", methods=["POST"])
@authorize
@check_driver
@check_droplist_access
def droplist_accept_decline(droplist_id):
    """driver accepts or declines a droplist"""
    droplist = DropList.query.get_or_404(droplist_id)
    
    choice = request.form.get("choice")
  
    if choice == "accepted" or choice == "declined":
        droplist.status = choice
        db.session.commit()

        flash(f"Successfully {choice} droplist", "success")
        return redirect("/droplists")
    
    else:
        flash("Not a valid choice", "danger")
        return redirect("/droplists")
    
    

@app.route("/droplists/<int:droplist_id>/edit", methods=["GET", "POST"])
@authorize
@check_stocker
@check_droplist_owner
def edit_drop_list(droplist_id):
    """Allow the user to edit their drop list"""
    droplist = DropList.query.get_or_404(droplist_id)
    
    form = DropListForm(obj=droplist)

    if form.validate_on_submit():
        droplist.description = form.description.data
        droplist.department = form.department.data

        db.session.commit()

        flash("Drop list successfully updated", "success")
        return redirect(f"/droplists/{droplist_id}")
    
    return render_template("/droplists/edit.html", form=form)

@app.route("/droplists/<int:droplist_id>/delete", methods=["POST"])
@authorize
@check_stocker
@check_droplist_owner
def delete_droplist(droplist_id):
    """Delete a droplist"""
    droplist = DropList.query.get_or_404(droplist_id)

    db.session.delete(droplist)
    db.session.commit()

    flash("droplist was successfully deleted", "success")
    return redirect("/")

#####################################################
# Droplist items routes

@app.route("/droplists/<int:droplist_id>/items")
@authorize
@check_droplist_access
def show_droplist_items(droplist_id):
    """Show items that are in the droplist"""
    droplist = DropList.query.get_or_404(droplist_id)

    return render_template("/droplist_items/index.html", droplist=droplist)

@app.route("/droplists/<int:droplist_id>/items/add", methods=["GET","POST"])
@authorize
@check_stocker
@check_droplist_owner
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
                description=form.description.data,
                droplist_id=droplist.id
        )

        db.session.add(item)
        db.session.commit()

        return redirect(f"/droplists/{droplist.id}/items")

    return render_template("/droplist_items/new.html", form=form)

@app.route("/droplists/<int:droplist_id>/items/<int:item_id>")
@authorize
@check_droplist_access
def show_item(droplist_id,item_id):
    """show a specific item in a droplist"""
    droplist = DropList.query.get_or_404(droplist_id)
    item = Item.query.get_or_404(item_id)

    if droplist.check_item(item) == False:
        return render_template("404.html"), 404

    return render_template("/droplist_items/show.html", item=item, droplist = droplist)

@app.route("/droplists/<int:droplist_id>/items/<int:item_id>/edit", methods=["GET", "POST"])
@authorize
@check_stocker
@check_droplist_owner
def edit_droplist_item(droplist_id, item_id):
    """edit a droplist item"""
    droplist = DropList.query.get_or_404(droplist_id)
    item = Item.query.get_or_404(item_id)

    if droplist.check_item(item) == False:
        return render_template("404.html"), 404

    form = ItemForm(obj=item)

    form.set_choices(db, Location)

    if form.validate_on_submit():
        item.description = form.description.data
        item.row_letter = form.row_letter.data
        item.column_number = form.column_number.data
        item.location_id = form.location_id.data

        db.session.commit()

        flash("Item successfully updated")
        return redirect(f"/droplists/{droplist_id}/items/{item_id}")

    return render_template("/droplist_items/edit.html", form=form)

@app.route("/droplists/<int:droplist_id>/items/<int:item_id>/delete", methods=["POST"])
@authorize
@check_stocker
@check_droplist_owner
def delete_droplist_item(droplist_id, item_id):
    """delete an item from a droplist"""
    droplist = DropList.query.get_or_404(droplist_id)
    item = Item.query.get_or_404(item_id)

    if droplist.check_item(item) == False:
        return render_template("404.html"), 404
    
    db.session.delete(item)
    db.session.commit()

    flash("successfully deleted the item", "success")
    return redirect(f"/droplists/{droplist.id}/items")



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

#################################################
#JSON routes

@app.route("/forklift_driver/droplist_chart")
@authorize
def get_all_accepted_drivers_droplist():
    """Return the number of droplist accepted for all drivers"""
    complete_filter = request.args.get("completed", "accepted")
    chart_type = request.args.get("type", "bar")

    all_drivers = db.session.query(ForkliftDriver).all()

    drivers_names = [d.full_name for d in all_drivers]

    num_droplists = []

    for driver in all_drivers:
        droplist_count = db.session.query(DropList).join(
            ForkliftDriver, ForkliftDriver.id == DropList.forklift_driver_id).filter(DropList.status==complete_filter).filter(
                ForkliftDriver.id == driver.id).count()
        num_droplists.append(droplist_count)

    chart_dict = {
        "type": chart_type,
        "data": {
            "labels": drivers_names,
            "datasets":[{
                "label": "Forklift Drivers",
                "data": num_droplists
            
            }]
        }
    }

    return jsonify(chart_dict)




#################################################
#error routes
@app.errorhandler(404)
def not_found(e):

    return render_template("404.html"), 404


# @app.after_request
# def add_header(req):
#     "make each request header non-caching."

#     req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     req.headers["Pragma"] = "no-cache"
#     req.headers["Expires"] = "0"
#     req.headers["Cache-Control"] = "public, max-age=0"
#     return req