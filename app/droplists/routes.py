from flask import Blueprint, render_template, g, flash, redirect, request
from app.models import ForkliftDriver, Stocker, get_droplists, db, DropList
from app.forms import DropListForm
from app.helpers.decorators import authorize, check_stocker, check_droplist_access, check_droplist_owner,check_driver

droplist_routes = Blueprint("droplists", __name__, url_prefix="/droplists", template_folder="templates")

@droplist_routes.route("/")
@authorize
def droplist_index():
    """show all the users droplist"""

    droplists = None

    #future implementation
    # department_filter = request.args.get("department",g.user.department)

    if g.user.current_role.role == "stocker":
        # droplists = g.user.get_stocker.get_droplists_by_department(department_filter)
        droplists =get_droplists(g.user.get_stocker, Stocker)
    elif g.user.current_role.role == "forklift_driver":
        droplists =get_droplists(g.user.get_driver, ForkliftDriver)


    return render_template("/droplist_index.html", droplists = droplists)

@droplist_routes.route("/new", methods=["GET", "POST"])
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
    
    return render_template("/droplist_form.html", form=form)

@droplist_routes.route("/<int:droplist_id>")
@authorize
@check_droplist_access
def show_drop_list(droplist_id):
    droplist = DropList.query.get_or_404(droplist_id)

    return render_template("/droplist_show.html", droplist=droplist)

@droplist_routes.route("/<int:droplist_id>/send", methods=["GET", "POST"])
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

        flash("Droplist successfully sent", "success")
        return redirect("/droplists")
    


    forklift_drivers = ForkliftDriver.get_drivers_by_department(department)

    return render_template("/droplist_send.html", drivers=forklift_drivers, droplist=droplist)

@droplist_routes.route("/<int:droplist_id>/option", methods=["POST"])
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

@droplist_routes.route("/<int:droplist_id>/edit", methods=["GET", "POST"])
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
    
    return render_template("/droplist_edit.html", form=form)

@droplist_routes.route("/<int:droplist_id>/delete", methods=["POST"])
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