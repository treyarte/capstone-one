"""droplist items routes test"""

import os
from unittest import TestCase
from models import db, User, Stocker, ForkliftDriver, DropList, Location, Item, Role
from test_utils import droplist_setup

os.environ["DATABASE_URL"] = "postgresql:///mydroplist-test"

from app import app, CURR_USER_KEY

app.config["SQLALCHEMY_ECHO"] = False

app.config["WTF_CSRF_ENABLED"] = False

db.create_all()

class DroplistItemsViewsTestCase(TestCase):
    """Test droplist items views"""

    def setUp(self):
        """Create test client and some sample data"""

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

       
        loc = Location(name="S409")
        loc_2 = Location(name="S408")
        loc_3 = Location(name="113")

        db.session.add_all([loc, loc_2, loc_3])
        db.session.commit()

        self.loc = loc
        self.loc_2 = loc_2
        self.loc_3 = loc_3
        
        item_1 = Item(
                            row_letter="a", 
                            column_number=1, 
                            location_id=self.loc.id, 
                            description="Test Item 1", 
                            droplist_id=self.droplist_2.id)

        item_2 = Item(
                            row_letter="a", 
                            column_number=2, 
                            location_id=self.loc_2.id, 
                            description="Test Item 2", 
                            droplist_id=self.droplist_2.id)

        item_3 = Item(
                            row_letter="c", 
                            column_number=3, 
                            location_id=self.loc_3.id, 
                            description="Test Item 3", 
                            droplist_id=self.droplist_2.id)
        
        db.session.add_all([item_1, item_2, item_3])
        db.session.commit()

        self.item_1 = item_1
        self.item_2 = item_2
        self.item_3 = item_3

    def tearDown(self):
        """Rollback transactions"""
        db.session.rollback()
        for model in [DropList, Item, Location, Stocker, ForkliftDriver, User, Role]:
            model.query.delete()

    def test_add_item_to_droplist(self):
        """check if items can be added to a droplist"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                self.droplist_id = self.droplist.id
                self.loc_id = self.loc.id
        
            resp = c.post(f"/droplists/{self.droplist_id}/items/add", 
                            data={"row_letter": "a", "column_number": 10, 
                                 "location_id": self.loc_id, "description": "test strawberries"})

            self.assertEqual(resp.status_code, 302)

            droplist = DropList.query.get(self.droplist_id)
            item = Item.query.filter(Item.description=="test strawberries").first()
            self.assertIn(item,droplist.droplist_items)

    def test_droplist_index(self):
        """Test if a user can view items in a droplist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                self.droplist_id = self.droplist_2.id

            resp = c.get(f"/droplists/{self.droplist_id}/items")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Item 1", html)
            self.assertIn("Test Item 2", html)
            self.assertIn("Test Item 3", html)

    def test_droplist_show_item(self):
        """Test if user can view a single item in a droplist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                self.droplist_id = self.droplist_2.id
                self.item_id = self.item_1.id
            
            resp = c.get(f"/droplists/{self.droplist_id}/items/{self.item_id}")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Item 1", html)

    def test_droplist_edit_item(self):
        """Test if a user can edit an item"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                self.droplist_id = self.droplist_2.id
                self.item_id = self.item_1.id
                self.loc_id = self.loc_2.id
            
            resp = c.post(f"/droplists/{self.droplist_id}/items/{self.item_id}/edit", 
                            data={"row_letter": "b", "column_number": 9, 
                                 "location_id": self.loc_id, "description": "updated item"})
            
            self.assertEqual(resp.status_code, 302)
            
            item = Item.query.get(self.item_id)
            self.assertEqual("updated item", item.description)
            self.assertEqual("b", item.row_letter)
            self.assertEqual(9, item.column_number)
            self.assertEqual(self.loc_id, item.location_id)


    def test_droplist_delete_item(self):
        """Test if a user can delete a item"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                self.droplist_id = self.droplist_2.id
                self.item_id = self.item_1.id
            
            resp = c.post(f"/droplists/{self.droplist_id}/items/{self.item_id}/delete")

            self.assertEqual(resp.status_code, 302)

            item = Item.query.get(self.item_id)

            self.assertIsNone(item)

