from flask import Blueprint, request, jsonify
from app.helpers.decorators import authorize
from app.models import ForkliftDriver, db, DropList

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/forklift_driver/droplist_chart")
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