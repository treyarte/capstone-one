"""Request model tests"""

import os
from unittest import TestCase

from models import db, User, ForkliftDriver, Stocker, Item, Location, DropListItem, DropList
from sqlalchemy.exc import IntegrityError

os.environ["DATABASE_URL"] = "postgresql:///mydroplist-test"

from app import app

app.config["SQLALCHEMY_ECHO"] = False

from utils import create_sample_data

db.create_all()

class DropListModelTestCase(TestCase):
    """Test cases for the request model"""

    def setUp(self):
        """Adding sample data"""

        for model in [DropListItem, DropList, Item, Location, Stocker, ForkliftDriver, User]:
            model.query.delete()

        self.client = app.test_client()

        #destructing off the values we need and skipping the ones we don't 
        _, _, s1, d1, _, _, drop_list_1, *items, _  = create_sample_data(db, User, Location, Stocker, ForkliftDriver, Item, 
                                                                DropListItem, DropList)

        self.s1 = s1
        self.d1 = d1
        self.drop_list_1 = drop_list_1
        self.items=items

    def tearDown(self):
        """Rolling back any bad transactions"""
        db.session.rollback()
        
    def test_droplist_creation(self):
        """Testing if request can be created"""
        test_drop_list = DropList(stocker_id=self.s1.id, notes="Test notes")
        
        db.session.add(test_drop_list)
        db.session.commit()

        test_drop_list.forklift_driver_id = self.d1.id

        #no items should be created for this droplist yet
        self.assertEqual(len(test_drop_list.items), 0)
        self.assertEqual(test_drop_list.forklift_driver_id, self.d1.id)

    def test_invalid_user_droplist(self):
        """check if an invalid stocker can create a droplist"""

        #check if can create a droplist with an invalid user
        with self.assertRaises(IntegrityError):
            test_drop_list = DropList(stocker_id=112, forklift_driver_id=self.d1.id, notes="Error hopefully")
            db.session.add(test_drop_list) 
            db.session.commit()
    
    def test_invalid_driver_droplist(self):
        """check if a valid stocker can assign an invalid driver to a droplist"""

        with self.assertRaises(IntegrityError):
            test_drop_list2 = DropList(stocker_id=self.s1.id, notes="Test Invalid driver")
            db.session.add(test_drop_list2)
            db.session.commit()
            test_drop_list2.forklift_driver_id = 112
            db.session.commit()

    def test_droplist_add_items(self):
        """check if items can be added to a drop list"""
        for item in self.items:
            drop_list_item = self.drop_list_1.add_item(item.id)
            db.session.add(drop_list_item)
            db.session.commit()
        
        self.assertEqual(len(self.drop_list_1.items), 3)
