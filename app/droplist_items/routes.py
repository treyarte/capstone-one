from flask import Blueprint, render_template, flash, redirect
from app.models import DropList, Item, Location, db
from app.forms import ItemForm
from app.helpers.decorators import authorize, check_droplist_access, check_driver, check_stocker, check_droplist_owner


droplist_items_route = Blueprint("droplist_items", __name__, url_prefix="/droplists", template_folder="templates")

@droplist_items_route.route("/<int:droplist_id>/items")
@authorize
@check_droplist_access
def show_droplist_items(droplist_id):
    """Show items that are in the droplist"""
    droplist = DropList.query.get_or_404(droplist_id)

    return render_template("/droplist_items_index.html", droplist=droplist)

@droplist_items_route.route("/<int:droplist_id>/items/new", methods=["GET","POST"])
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

        return redirect(f"/droplists/{droplist.id}")

    return render_template("/droplist_items_new.html", form=form)

@droplist_items_route.route("/<int:droplist_id>/items/<int:item_id>")
@authorize
@check_droplist_access
def show_item(droplist_id,item_id):
    """show a specific item in a droplist"""
    droplist = DropList.query.get_or_404(droplist_id)
    item = Item.query.get_or_404(item_id)

    if droplist.check_item(item) == False:
        return render_template("404.html"), 404

    return render_template("/droplist_items_show.html", item=item, droplist = droplist)

@droplist_items_route.route("/<int:droplist_id>/items/<int:item_id>/edit", methods=["GET", "POST"])
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

        flash("Item successfully updated", "success")
        return redirect(f"/droplists/{droplist_id}")

    return render_template("/droplist_items_edit.html", form=form)

@droplist_items_route.route("/<int:droplist_id>/items/<int:item_id>/delete", methods=["POST"])
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