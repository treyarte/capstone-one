from flask import Blueprint, redirect, render_template, flash, session
from app.forms import SignUpForm
from app.models import Role, User, Stocker, ForkliftDriver, db
from app.helpers.decorators import check_logged
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

        flash(f"Welcome {user.first_name}!")
        return redirect("/")
    
    return render_template("/signup.html", form=form)