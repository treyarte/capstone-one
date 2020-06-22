"""Test for user routes"""

import os
from unittest import TestCase
from models import db, connect_db, Role, User, Stocker, ForkliftDriver

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
        Role.query.delete()
        
        self.client = app.test_client()

        role1 = Role(id = 1,role="stocker")
        role2 = Role(id = 2, role="forklift_driver")

        db.session.add_all([role1, role2])
        db.session.commit()

        self.role1 = role1
        self.role2 = role2

        self.u1 = User.sign_up(
                            first_name="Test", last_name="User", 
                            email="test@person.com", department="sundrys", 
                            password="Qwerty123!", current_role_id=self.role1.id)

        self.u2 = User.sign_up(
                            first_name="New", last_name="Person", 
                            email="new@person.com", department="sundrys", 
                            password="Qwerty123!", current_role_id=self.role1.id)

        db.session.commit()

    
    def tearDown(self):
        """rollback db transactions"""
        db.session.rollback()
        User.query.delete()
        ForkliftDriver.query.delete()
        Stocker.query.delete()
        Role.query.delete()

    def test_sign_up_route(self):
        """Test if a user can sign up"""
        with self.client as c:
            
            resp = c.post("/sign-up", data={"first_name":"Test2", "last_name":"Person2", 
                            "email":"test2@person.com", "department":"sundries", 
                            "password":"Qwerty123!","confirm":"Qwerty123!", "user_role":self.role1.id})
            
            self.assertEqual(resp.status_code, 302)
            user = User.query.filter(User.email=="test2@person.com").first()
            self.assertEqual(user.email, "test2@person.com")
        
    def test_login_route(self):
        """Test if a user can sign in"""
        with self.client as c:

            resp = c.post("/login", data={"email":"test@person.com", "password":"Qwerty123!"})

            self.assertEqual(resp.status_code, 302)
    
    def test_edit_user(self):
        """Test if a logged in user can edit their profile"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                self.role_id = self.role1.id
            
            resp = c.post(f"/users/settings", data={
                            "first_name":"Test", "last_name":"Person", 
                            "email":"person@test.net", "department":"sundries", 
                            "current_password": "Qwerty123!", "current_role_id":1})

            self.assertEqual(resp.status_code, 302)
            user = User.query.filter(User.first_name=="Test").first()
            self.assertEqual(user.email, "person@test.net")
        
    def test_wrong_user_password(self):
        """Test if flash if wrong password"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                self.role_id = self.role1.id
        
        resp = c.post(f"/users/settings", data={
                            "first_name":"Test", "last_name":"Person", 
                            "email":"person@test.net", "department":"sundries", 
                            "current_password": "wqq!", "current_role_id":1}, follow_redirects=True)
        
        html = resp.get_data(as_text=True)

        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("invalid password",html)

    def test_delete_user(self):
        """Test if the logged in user can delete their profile"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            
        resp = c.post(f"/users/{self.u1.id}/delete")

        self.assertEqual(resp.status_code, 302)
        user = User.query.filter(User.email == "test@person.com").first()
        self.assertIsNone(user)
    
    def test_user_settings(self):
        self.assertIsNone(None)