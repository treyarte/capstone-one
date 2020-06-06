"""SLQAlchemy models for mydroplist"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """User model"""

    __tablename__ = "user"

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
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer, 
        db.ForeignKey("user.id"),
        unique=True,
        nullable=False
    )


class Stocker(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        unique=True,
        nullable=False
    )



def connect_db(app):
    """connect this database to the flask app"""
    db.app = app
    db.init_app(app)