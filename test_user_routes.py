"""Test for user routes"""

import os
from unittest import TestCase
from models import db, connect_db, User, Stocker, ForkliftDriver

os.environ["DATABASE_URL"] = "postgresql:///mydroplist-test"

from app import app, CURR_USER_KEY

app.config["SQLALCHEMY_ECHO"] = False

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False

class UserRoutesTestCase(TestCase):
    """Contains test for user routes"""

    def setUp(self):
        """create a test client and sample data"""

        User.query.delete()
        ForkliftDriver.query.delete()
        Stocker.query.delete()

        self.client = app.test_client()
    
    def tearDown(self):
        """rollback db transactions"""
        db.session.rollback()

