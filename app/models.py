"""SLQAlchemy models for mydroplist"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

def get_droplists(model_instance, sql_model):
    """Pass in a model and instance of that model that have a relationship with the droplist table to retrieve its droplists."""
    droplists = db.session.query(DropList).join(
            sql_model, sql_model.id==DropList.stocker_id).filter(
                model_instance.id == sql_model.id
            ).all()
    return droplists

class Role(db.Model):
    """Role model"""

    __tablename__="roles"

    id = db.Column(db.Integer, primary_key=True)

    role = db.Column(db.Text, nullable=False)
    
    users = db.relationship("User", backref="current_role")

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

    current_role_id = db.Column(db.Integer, db.ForeignKey("roles.id", ondelete="SET NULL"), nullable=False)

    image_url = db.Column(
        db.Text,
        nullable=True,
        default="https://pixabay.com/get/57e5d2444352a514f6da8c7dda35367b1c3edae25751734a_1280.png"
    )

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
    def sign_up(cls, first_name, last_name, email, department, password, current_role_id, image_url=None):
        """Sign users up and hash passwords"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            department=department,
            password=hashed_pwd,
            image_url=image_url,
            current_role_id=current_role_id
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
        full_name = db.session.query(
            User.first_name, User.last_name).join(
                ForkliftDriver, User.id == ForkliftDriver.user_id).filter(
                    ForkliftDriver.id == self.id
                ).first()
        return " ".join(full_name)

    __tablename__ = "forklift_drivers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id",ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    droplists = db.relationship("DropList", backref=db.backref("forklift_driver", cascade="delete"))
    user = db.relationship("User", backref=db.backref("forklift_driver", cascade="all, delete"), uselist=False)

    def get_droplists_by_department(self, department):
        if department == "all":
            droplists = db.session.query(DropList).join(
                ForkliftDriver, ForkliftDriver.id == DropList.forklift_driver_id).filter(
                    ForkliftDriver.id==self.id)
        else:
            droplists = db.session.query(DropList).join(
                            ForkliftDriver, ForkliftDriver.id == DropList.forklift_driver_id).filter(
                                DropList.department == department).filter(
                                    ForkliftDriver.id==self.id)
        return droplists

    @classmethod
    def get_drivers_by_department(cls, department):
        if department != "all":
            forklift_drivers = db.session.query(ForkliftDriver).join(
                User, User.id == ForkliftDriver.user_id).filter(
                   User.department==department).filter(User.current_role_id==2).all()
        else:
            forklift_drivers = db.session.query(ForkliftDriver).join(
                User, User.id == ForkliftDriver.user_id).filter(User.current_role_id==2).all()
        
        return forklift_drivers
class Stocker(db.Model):
    """A user that makes a drop list"""

    __tablename__= "stockers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id",  ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    droplists = db.relationship("DropList", backref=db.backref("stocker"))
    user = db.relationship("User", backref=db.backref("stocker"), uselist=False)

    # def get_droplists_by_department(self, department):
    # """Get droplists by the department"""
    #     if department == "all":
    #         droplists = db.session.query(DropList).join(Stocker, Stocker.id == DropList.stocker_id).filter(Stocker.id==self.id)
    #     else:
    #         droplists = db.session.query(DropList).join(
    #                         Stocker, Stocker.id == DropList.stocker_id).filter(DropList.department == department).filter(Stocker.id==self.id)
    #     return droplists
class DropList(db.Model):
    """A droplist created by a stocker and sent to a driver"""

    __tablename__= "droplists"

    id = db.Column(db.Integer, primary_key=True)
    
    department = db.Column(db.Text, nullable=False)
    
    is_complete = db.Column(db.Boolean, nullable=False, default=False)
    
    stocker_id = db.Column(db.Integer, db.ForeignKey("stockers.id", ondelete="CASCADE"), nullable=False)

    forklift_driver_id = db.Column(db.Integer, db.ForeignKey("forklift_drivers.id", ondelete="SET NULL"), nullable=True)

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    status = db.Column(db.Text, nullable=False, default="not sent")

    description = db.Column(db.Text, nullable=False, default=f"My Drop List-{datetime.utcnow()}")

    @property
    def droplist_items(self):
        items = db.session.query(Item).join(DropList, Item.droplist_id==DropList.id).filter(DropList.id==self.id).all()
        return items
    
    def check_item(self, item):
        """Check if an item is in the droplist"""
        if item in self.droplist_items:
            return True
        else:
            return False
        

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

    droplist_id = db.Column(db.Integer, db.ForeignKey("droplists.id", ondelete="CASCADE"), nullable=False)

    droplist = db.relationship("DropList", backref=db.backref("items", cascade="all, delete"))

def connect_db(app):
    """connect this database to the flask app"""
    db.app = app
    db.init_app(app)