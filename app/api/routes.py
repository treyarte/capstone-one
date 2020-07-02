from flask import Blueprint, request, jsonify, send_file
import json
import requests
from app.helpers.decorators import authorize
from app.models import ForkliftDriver, db, DropList
from app.helpers.api_methods import send_data, create_chart

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/forklift_drivers/droplists")
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
        "type":chart_type,
        "data":{
            "labels":drivers_names,
            "datasets":[{
                "label":"Forklift Drivers",
                "data":num_droplists
            }]
        }
    }
    chart_data = json.dumps(chart_dict)
    resp = create_chart(300, 668, chart_type, chart_dict)

    return resp