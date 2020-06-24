from flask import Blueprint, redirect, flash, render_template
from app.models import Location, db
from app.forms import LocationForm
from app.helpers.decorators import authorize


locations = Blueprint("locations", __name__, url_prefix="/locations", template_folder="templates")

@locations.route("/")
@authorize
def location_index():
    """show multiple locations"""
    locations = Location.query.all()

    return render_template("/locations_index.html", locations=locations)

@locations.route("/new", methods=["GET", "POST"])
@authorize
def create_location():
    """Creates a location for a drop list item"""
    form = LocationForm()

    if form.validate_on_submit():
        location = Location(name=form.name.data)
        db.session.add(location)
        db.session.commit()
        flash("Location has been successfully created", "success")
        return redirect(f"/locations/{location.id}")
    
    return render_template("locations_new.html", form=form)

@locations.route("/<int:location_id>")
@authorize
def show_location(location_id):
    """Show a location"""
    location = Location.query.get_or_404(location_id)
    return render_template("/locations_show.html", location=location)

@locations.route("/<int:location_id>/edit", methods=["GET", "POST"])
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
    
    return render_template("/locations_edit.html", form=form)

@locations.route("/<int:location_id>/delete", methods=["POST"])
@authorize
def delete_location(location_id):
    """delete a location"""
    location = Location.query.get_or_404(location_id)

    db.session.delete(location)
    db.session.commit()

    flash("Location successfully deleted")
    return redirect("/")
