"""Seed the database with sample data"""

from app import db
from models import User, Stocker, ForkliftDriver

db.drop_all()
db.create_all()

