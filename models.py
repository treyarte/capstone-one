"""SLQAlchemy models for mydroplist"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()


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

    @property
    def get_stocker(self):
        stocker = db.session.query(Stocker).join(
                    User, User.id==Stocker.user_id).filter(
                    Stocker.user_id == self.id).first()

        return stocker
    @property
    def get_driver(self):
        driver = db.session.query(ForkliftDriver).join(
                    User, User.id==ForkliftDriver.user_id).filter(
                    ForkliftDriver.user_id == self.id).first()

        return driver

    def __repr__(self):
        return f"<User #{self.id}: {self.first_name} {self.last_name} {self.email}>"

    @classmethod
    def sign_up(cls, first_name, last_name, email, department, password, image_url=None):
        """Sign users up and hash passwords"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            department=department,
            password=hashed_pwd,
            image_url=image_url
        )

        db.session.add(user)
        return user


    @classmethod
    def authenticate(cls, email, password):
        """Finds and returns the user if their password hash match"""

        #The reason for using first over one is because first will return none if not found.
        #One would return an exception if not found.
        user = cls.query.filter_by(email=email).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)

            if is_auth:
                return user
        
        return False
class ForkliftDriver(db.Model):
    """A user that receives and completes a drop list"""

    @property
    def full_name(self):
        full_name = db.session.query(User.first_name, User.last_name).join(ForkliftDriver, User.id == ForkliftDriver.user_id).first()
        return " ".join(full_name)

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

    drop_list = db.relationship("DropList", backref="forklift_driver")


class Stocker(db.Model):
    """A user that makes a drop list"""

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

    drop_list = db.relationship("DropList", backref="stocker")


class DropList(db.Model):
    """A droplist created by a stocker and sent to a driver"""

    __tablename__= "drop_lists"

    id = db.Column(db.Integer, primary_key=True)
    
    notes = db.Column(db.Text, nullable=True)
    
    is_complete = db.Column(db.Boolean, nullable=False, default=False)
    
    stocker_id = db.Column(db.Integer, db.ForeignKey("stockers.id"), nullable=False)

    forklift_driver_id = db.Column(db.Integer, db.ForeignKey("forklift_drivers.id"), nullable=True)

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    items = db.relationship("Item", secondary="drop_list_items", cascade="all,delete", backref="drop_list")

    def add_item(self, item_id):
        """add an item to the droplist"""
        drop_list_item = DropListItem(drop_list_id=self.id, item_id=item_id)
        return drop_list_item

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
    """Items that is that will be on the droplist"""

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)

    description = db.Column(db.String(200))

    row_letter = db.Column(db.String(2), nullable=False)

    column_number = db.Column(db.Integer, nullable=False)

    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    

class DropListItem(db.Model):
    """Connects the drop list to Items"""

    __tablename__ = "drop_list_items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    drop_list_id = db.Column(
        db.Integer,
        db.ForeignKey("drop_lists.id") 
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id")
    )



def connect_db(app):
    """connect this database to the flask app"""
    db.app = app
    db.init_app(app)