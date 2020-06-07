"""SLQAlchemy models for mydroplist"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """User model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    admin = db.Column(db.Boolean, nullable=False, default=False)

    first_name = db.Column(db.Text, nullable=False)

    last_name = db.Column(db.Text,nullable=False)

    email = db.Column(db.Text, nullable=False, unique=True)

    department = db.Column(db.Text, nullable=False)

    password = db.Column(db.Text,nullable=False)

    image_url = db.Column(
        db.Text,
        nullable=True,
        default="https://pixabay.com/get/57e5d2444352a514f6da8c7dda35367b1c3edae25751734a_1280.png"
    )

    forklift_driver = db.relationship("ForkliftDriver", backref="user", uselist=False)
    stocker = db.relationship("Stocker", backref="user", uselist=False)

class ForkliftDriver(db.Model):
    """A user that receives and completes a request"""

    __tablename__ = "forklift_drivers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    requests = db.relationship("Request", backref="forklift_driver")


class Stocker(db.Model):
    """A user that makes a request"""

    __tablename__= "stockers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    requests = db.relationship("Request", backref="stocker")


class Request(db.Model):
    """A request created by a stocker and sent to a driver"""

    __tablename__= "requests"

    id = db.Column(db.Integer, primary_key=True)
    
    request_type = db.Column(db.Text, nullable=False, default="droplist")
    
    description = db.Column(db.Text, nullable=True)
    
    is_complete = db.Column(db.Boolean, nullable=False, default=False)
    
    stocker_id = db.Column(db.Integer, db.ForeignKey("stockers.id"), nullable=False)

    forklift_driver_id = db.Column(db.Integer, db.ForeignKey("forklift_drivers.id"), nullable=True)

    items = db.relationship("Item", secondary="request_items", backref="request")

class Location(db.Model):
    """A place where items are located"""

    __tablename__ = "locations"

    id = db.Column(
        db.Integer, 
        primary_key=True
    )

    name = db.Column(
        db.Text,
        nullable=False
    )

    items = db.relationship("Item", backref="location")

class Item(db.Model):
    """Items the stocker is requesting for"""

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)

    description = db.Column(db.String(200))

    row_letter = db.Column(db.String(2), nullable=False)

    column_number = db.Column(db.Integer, nullable=False)

    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)

class RequestItem(db.Model):
    """Connects request to Items"""

    __tablename__ = "request_items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    request_id = db.Column(
        db.Integer,
        db.ForeignKey("requests.id") 
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id")
    )



def connect_db(app):
    """connect this database to the flask app"""
    db.app = app
    db.init_app(app)