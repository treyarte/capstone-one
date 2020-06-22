"""Test droplist routes"""

import os
from unittest import TestCase
from models import Role, User, Stocker, ForkliftDriver, DropList, db
from test_utils import droplist_setup

os.environ["DATABASE_URL"] = "postgresql:///mydroplist-test"

from app import app, CURR_USER_KEY

app.config["SQLALCHEMY_ECHO"] = False


app.config["WTF_CSRF_ENABLED"] = False

db.create_all()
class DroplistTestCase(TestCase):
    """Tests for droplist routes"""

    def setUp(self):
        """create a test client and sample data"""

        self.client = app.test_client()

        u1, u2, u3, s1, s2, f1, droplist, droplist_2, droplist_3 = droplist_setup()

        self.u1 = u1
        self.u2 = u2
        self.u3 = u3
        self.s1 = s1
        self.s2 = s2
        self.f1 = f1
        self.droplist = droplist
        self.droplist_2 = droplist_2
        self.droplist_3 = droplist_3
       

    
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
        
    def test_droplist_index(self):
        """test if users droplist are displayed"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            
            resp = c.get("/droplists", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertIn("Test Drop", html)

    def test_droplist_send(self):
        """Test if a user can send their droplist to a driver"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                self.droplist_2_id = self.droplist_2.id
                self.driver_id = self.f1.id
            
            resp = c.post(f"/droplists/{self.droplist_2_id}/send",
                     data={"driverId": self.driver_id}, 
                     follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            
            droplist = DropList.query.get(self.droplist_2_id)
            
            self.assertEqual(self.driver_id, droplist.forklift_driver_id)

            self.assertIn("sent",html)
    
    def test_send_wrong_droplist(self):
        """Test if a user can send another users droplist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                self.droplist_3_id = self.droplist_3.id
                self.driver_id = self.f1.id

            resp = c.post(f"/droplists/{self.droplist_3_id}/send", data={"driverId": self.driver_id}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Unauthorized access", html)
            
            droplist = DropList.query.get(self.droplist_3_id)
            #check if the droplist forklift driver key has been set
            self.assertIsNone(droplist.forklift_driver_id)

    def test_droplist_option_accepted(self):
        """Test if a driver can accept or decline a request"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id
                self.droplist_id = self.droplist.id 

            resp = c.post(f"/droplists/{self.droplist_id}/option", data={"choice": "accepted"})      

            self.assertEqual(resp.status_code, 302)
            droplist = DropList.query.get(self.droplist_id)
            self.assertEqual(droplist.status, "accepted")
            


