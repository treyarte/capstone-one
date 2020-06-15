"""droplist items routes test"""

import os
from unittest import TestCase
from models import db, connect_db, User, Stocker, ForkliftDriver, DropList, DropListItem, Location, Item
from utils import create_sample_data

os.environ["DATABASE_URL"] = "postgresql:///mydroplist-test"

from app import app, CURR_USER_KEY

app.config["SQLALCHEMY_ECHO"] = False

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False

class DroplistItemsViewsTestCase(TestCase):
    """Test droplist items views"""

    def setUp(self):
        """Create test client and some sample data"""
        
        for model in [DropListItem, DropList, Item, Location, Stocker, ForkliftDriver, User]:
            model.query.delete()

        self.client = app.test_client()

        self.u1 = User.sign_up(first_name="test", last_name="person", email="testperson@test.com",department="test",password="Qwerty123!")
        self.u2 = User.sign_up(first_name="test2", last_name="person2", email="testperson2@test.com",department="test",password="Qwerty123!")

        db.session.commit()

       
        

    def tearDown(self):
        """Rollback transactions"""
        db.session.rollback()

    def test_add_item_to_droplist(self):
        """check if items can be added to a droplist"""

        s1 = Stocker(user_id=self.u1.id)
        f1 = ForkliftDriver(user_id=self.u2.id)
        
        db.session.add_all([s1,f1])
        db.session.commit()

        loc = Location(name="S409")
        droplist = DropList(stocker_id=s1.id, forklift_driver_id=f1.id)

        db.session.add_all([loc, droplist])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
                
        
            resp = c.post(f"/droplist/{droplist.id}/items/add", 
                            data={"row_letter": "a", "column_number": 10, 
                                 "location_id": loc.id, "description": "test strawberries"})

            self.assertEqual(resp.status_code, 200)

            item = Item.query.filter(Item.description=="test strawberries").first()

            self.assertIn(self.droplist.items, item)
