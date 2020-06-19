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

        u1, u2, u3, s1, s2, f1, droplist = droplist_setup()

        self.u1 = u1
        self.u2 = u2
        self.u3 = u3
        self.s1 = s1
        self.s2 = s2
        self.f1 = f1
        self.droplist = droplist

       
        loc = Location(name="S409")

        db.session.add(loc)
        db.session.commit()

        self.loc = loc
        

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
