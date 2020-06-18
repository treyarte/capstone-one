"""Test for the user model"""

import os
from unittest import TestCase

from models import db, User, ForkliftDriver, Stocker, Role


os.environ["DATABASE_URL"] = "postgresql:///mydroplist-test"

from app import app

app.config["SQLALCHEMY_ECHO"] = False


db.create_all()


class UserModelTestCase(TestCase):
    """Test cases for the user model"""

    def setUp(self):
        """create sample data"""
        db.session.rollback()

        User.query.delete()
        Stocker.query.delete()
        ForkliftDriver.query.delete()
        Role.query.delete()

        role1 = Role(role="stocker")
        role2 = Role(role="forklift_driver")

        db.session.add_all([role1,role2])
        db.session.commit()

        self.role1 = role1
        self.role2 = role2
        
        user = User.sign_up(
                            first_name="Test", last_name="Person", 
                            email="test@person.com", department="sundrys", 
                            password="Qwerty123!", current_role_id=role1.id)

        test_user = User.sign_up(
                            first_name="Test", last_name="User", 
                            email="test@user.com", department="sundrys", 
                            password="Qwerty123!", current_role_id=role2.id)

        db.session.commit()

        self.user = user
        self.test_user = test_user

        stocker = Stocker(user_id=self.user.id)
        forklift_driver = ForkliftDriver(user_id=self.test_user.id)

        db.session.add_all([stocker, forklift_driver])
        db.session.commit()
    
    def tearDown(self):
        """rollback db transactions"""
        db.session.rollback()
        User.query.delete()
        Stocker.query.delete()
        ForkliftDriver.query.delete()
        Role.query.delete()
    
    def test_user_sign_up(self):
        """Should return the newly created user"""
        
        user = User.sign_up(
                            first_name="Test2", last_name="Person2", 
                            email="test@person2.com", department="sundrys", 
                            password="Qwerty123!", current_role_id=self.role1.id)
        
        self.assertIsInstance(user,User)
        self.assertEqual(user.first_name, "Test2")
    
    def test_user_login(self):
        """should return a user or return false"""

        user = User.authenticate(email="test@person.com", password="Qwerty123!")

        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "test@person.com")

        user_2 = User.authenticate(email="worngEmail", password="Qwerty123!")
        self.assertEqual(user_2, False)
        
        user_2 = User.authenticate(email="test@person.com", password="wrongpassword")
        self.assertEqual(user_2, False)

    def test_get_stocker(self):
        """test if user is a stocker"""

        self.assertIsInstance(self.user.get_stocker, Stocker)
        self.assertIsNone(self.test_user.get_stocker)
    
    def test_get_driver(self):
        """test if user is a stocker"""

        self.assertIsInstance(self.test_user.get_driver, ForkliftDriver)
        self.assertIsNone(self.user.get_driver)
