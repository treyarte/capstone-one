from flask import Blueprint, redirect, render_template, flash, session, g
from app.forms import SignUpForm, LoginForm,EditUserForm
from app.models import Role, User, Stocker, ForkliftDriver, db
from app.helpers.decorators import check_logged, authorize, check_same_user
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = "curr_user"

def handle_login(user):
    """Log a user in"""
    session[CURR_USER_KEY] = user.id

def handle_logout():
    """Remove the user from the session to log them out"""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

users_route = Blueprint("users", __name__, template_folder="templates") 

@users_route.route("/sign-up", methods=["GET", "POST"])
@check_logged
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

        flash(f"Welcome {user.first_name}!", "success")
        return redirect("/")
    
    return render_template("/signup.html", form=form)

@users_route.route("/login", methods=["GET", "POST"])
@check_logged
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
            flash("Invalid Login/Password combination", "danger")
    
    return render_template("/login.html", form=form)

@users_route.route("/logout", methods=["POST"])
def logout():
    """log out a user"""

    handle_logout()
    flash("Successfully logged out", "success")
    return redirect("/")

@users_route.route("/users")
@authorize
def get_users():
    """get users in the system"""

    users = User.query.all()
    return render_template("/index.html", users=users)

@users_route.route("/users/<int:user_id>")
@authorize
def show_user(user_id):
    """show user details"""

    user = User.query.get_or_404(user_id)

    return render_template("/show.html", user=user)

@users_route.route("/users/settings", methods=["GET", "POST"])
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
                db.session.commit()

                if user.current_role.role == "stocker":
                    if user.get_stocker is None:
                        stocker = Stocker(user_id=user.id)
                        db.session.add(stocker)
                        db.session.commit()

                elif user.current_role.role == "forklift_driver":
                    if user.get_driver is None:
                        forklift_driver = ForkliftDriver(user_id=user.id)
                        db.session.add(forklift_driver)
                        db.session.commit()
                        
                flash("Profile successfully updated", "success")
                return redirect(f"/users/{user.id}")
            except IntegrityError:
                flash("Email is already in use", "danger")
                return redirect("/users/settings")
        else:
            flash("invalid password", "danger")
            return redirect("/users/settings")
    
    return render_template("/edit.html", form=form)

@users_route.route("/users/<int:user_id>/delete", methods=["POST"])
@authorize
@check_same_user
def delete_user(user_id):
    """Delete a user from the system"""
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect("/")