"""Test droplist routes"""

import os
from unittest import TestCase
from models import Role, User, Stocker, ForkliftDriver, DropList, db

os.environ["DATABASE_URL"] = "postgresql:///mydroplist-test"

from app import app, CURR_USER_KEY

app.config["SQLALCHEMY_ECHO"] = False


app.config["WTF_CSRF_ENABLED"] = False

db.create_all()
class DroplistTestCase(TestCase):
    """Tests for droplist routes"""

    def setUp(self):
        """create a test client and sample data"""

        User.query.delete()
        ForkliftDriver.query.delete()
        Stocker.query.delete()
        Role.query.delete()
        DropList.query.delete()
        
        self.client = app.test_client()

        role1 = Role(role="stocker")
        role2 = Role(role="forklift_driver")

        db.session.add_all([role1, role2])
        db.session.commit()

        self.role1 = role1
        self.role2 = role2

        self.u1 = User.sign_up(
                            first_name="Test", last_name="Person", 
                            email="test@person.com", department="sundrys", 
                            password="Qwerty123!", current_role_id=self.role1.id)

        self.u2 = User.sign_up(
                            first_name="New", last_name="Person", 
                            email="new@person.com", department="sundrys", 
                            password="Qwerty123!", current_role_id=self.role2.id)

        self.u3 = User.sign_up(
                            first_name="New2", last_name="Person2", 
                            email="new@person2.com", department="hardlines", 
                            password="Qwerty123!", current_role_id=self.role1.id)

        db.session.commit()

        stocker = Stocker(user_id=self.u1.id)
        stocker2 = Stocker(user_id=self.u3.id)
        forklift_driver = ForkliftDriver(user_id=self.u2.id)

        db.session.add_all([stocker,stocker2, forklift_driver])
        db.session.commit()

        self.s1 = stocker
        self.f1 = forklift_driver

        droplist = DropList(stocker_id=self.s1.id, description="Test Drop", department="hardlines", forklift_driver_id=self.f1.id)
        db.session.add(droplist)
        db.session.commit()

        self.droplist = droplist

    
    def tearDown(self):
        """rollback db transactions"""
        db.session.rollback()
        User.query.delete()
        ForkliftDriver.query.delete()
        Stocker.query.delete()
        Role.query.delete()
        DropList.query.delete()
    
    def test_create_droplist(self):
        """Test is a droplist can be created"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                self.stocker_id = self.s1.id
        
            resp = c.post("/droplists/new", data={"description": "Test droplist","department": "sundries"})
            self.assertEqual(resp.status_code, 302)
            droplist = DropList.query.filter(DropList.description=="Test droplist").first()
            self.assertEqual(droplist.description, "Test droplist")

    def test_driver_create_droplist(self):
        """check if an driver can create a droplist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id
            
            resp = c.post("/droplists/new", data={"description": "Test droplist","department": "sundries"})
            self.assertEqual(resp.status_code, 302)
            droplist = DropList.query.filter(DropList.description=="Test droplist").first()
            self.assertIsNone(droplist)

    def test_view_wrong_user_droplist(self):
        """test if an unauthorized user can view a droplist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u3.id
                self.droplist_id = self.droplist.id
            
            resp = c.get(f"/droplists/{self.droplist.id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Unauthorized access",html)
        
    def test_driver_view_droplist(self):
        """Test if an authorized driver can view a users droplist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id
                self.droplist_id = self.droplist.id
        
            resp = c.get(f"/droplists/{self.droplist_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Drop",html)
            self.assertNotIn("Unauthorized access", html)

    def test_droplist_edit(self):
        """Test if a user can edit their droplist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                self.droplist_id = self.droplist.id
            
            resp = c.post(f"/droplists/{self.droplist_id}/edit", 
                        data={"description": "Edit List","department": "sundries"})
            
            self.assertEqual(resp.status_code, 302)
            droplist = DropList.query.get(self.droplist_id)
            self.assertEqual(droplist.description, "Edit List")
    
    def test_not_stocker_edit(self):
        """Test if a user that is not a stocker can edit a droplit"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id
                self.droplist_id = self.droplist.id
            
            resp = c.post(f"/droplists/{self.droplist_id}/edit", 
                        data={"description": "Edit List2","department": "sundries"})
            
            self.assertEqual(resp.status_code, 302)
            droplist = DropList.query.get(self.droplist_id)
            self.assertNotEqual(droplist.description, "Edit List2")

    def test_droplist_delete(self):
        """Test if user can delete their droplist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                self.droplist_id = self.droplist.id

            resp = c.post(f"/droplists/{self.droplist_id}/delete")

            self.assertEqual(resp.status_code, 302)
            droplist = DropList.query.get(self.droplist_id)
            self.assertIsNone(droplist)
    
    def test_unauthorized_droplist_delete(self):
        """Test if an user can delete someone elses droplist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u3.id
                self.droplist_id = self.droplist.id
            
            resp = c.post(f"/droplists/{self.droplist_id}/delete")

            self.assertEqual(resp.status_code, 302)
            droplist = DropList.query.get(self.droplist_id)
            self.assertEqual(droplist.description, "Test Drop")