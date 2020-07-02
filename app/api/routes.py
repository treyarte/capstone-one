from flask import Blueprint, request, jsonify, send_file
import json
import requests
from app.helpers.decorators import authorize
from app.models import ForkliftDriver, db, DropList
from app.helpers.api_methods import send_data, create_chart

api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/forklift_drivers/droplists", methods=["POST"])
@authorize
def get_all_accepted_drivers_droplist():
    """Return the number of droplist completed for all drivers"""
    status_filter = request.json.get("status")
    chart_type = request.json.get("type")

    all_drivers = db.session.query(ForkliftDriver).all()

    drivers_names = [d.full_name for d in all_drivers]

    num_droplists = []

    for driver in all_drivers:
        droplist_count = db.session.query(DropList).join(
            ForkliftDriver, ForkliftDriver.id == DropList.forklift_driver_id).filter(DropList.status==status_filter).filter(
                ForkliftDriver.id == driver.id).count()
        num_droplists.append(droplist_count)

    chart_dict = {
        "type":chart_type,
        "options":{
        "title": {
            "display":"true",
            "text": f"Total Droplist {status_filter}",
            "fontColor": "gray",
            "fontsize": 100
            }
        },
        "data":{
            "labels":drivers_names,
            "datasets":[{
                "label":"Forklift Drivers",
                "data":num_droplists
            }]
        }
    }
    chart_data = json.dumps(chart_dict)
    resp = create_chart(400, 668, chart_type, chart_dict)

    return resp