"""Request model tests"""

import os
from unittest import TestCase

from models import db, Role, User, ForkliftDriver, Stocker, Item, Location, DropList
from sqlalchemy.exc import IntegrityError

os.environ["DATABASE_URL"] = "postgresql:///mydroplist-test"

from app import app

app.config["SQLALCHEMY_ECHO"] = False

from utils import create_sample_data

db.drop_all()
db.create_all()

class DropListModelTestCase(TestCase):
    """Test cases for the request model"""

    def setUp(self):
        """Adding sample data"""

        for model in [DropList,Item, Location, Stocker, ForkliftDriver, User, Role]:
            model.query.delete()
        
        self.client = app.test_client()

        #destructing off the values we need and skipping the ones we don't 
        _, _, s1, d1, _, _, droplist_1, *items  = create_sample_data(db, Role, User, Location, Stocker, 
                                                                        ForkliftDriver, Item,DropList)

        self.s1 = s1
        self.d1 = d1
        self.droplist_1 = droplist_1
        self.items=items

    def tearDown(self):
        """Rolling back any bad transactions"""
        db.session.rollback()
        for model in [DropList,Item, Location, Stocker, ForkliftDriver, User, Role]:
            model.query.delete()


    def test_droplist_creation(self):
        """Testing if request can be created"""
        test_droplist = DropList(stocker_id=self.s1.id, forklift_driver_id=self.d1.id, department=self.s1.user.department)
        
        db.session.add(test_droplist)
        db.session.commit()

        #no items should be created for this droplist yet
        self.assertEqual(len(test_droplist.items), 0)
        self.assertEqual(test_droplist.forklift_driver_id, self.d1.id)

    def test_invalid_user_droplist(self):
        """check if an invalid stocker can create a droplist"""

        #check if can create a droplist with an invalid user
        with self.assertRaises(IntegrityError):
            test_drop_list = DropList(stocker_id=112, forklift_driver_id=self.d1.id, department="hardlines")
            db.session.add(test_drop_list) 
            db.session.commit()
    
    def test_invalid_driver_droplist(self):
        """check if a valid stocker can assign an invalid driver to a droplist"""

        with self.assertRaises(IntegrityError):
            test_drop_list2 = DropList(stocker_id=self.s1.id, department=self.s1.user.department)
            db.session.add(test_drop_list2)
            db.session.commit()
            test_drop_list2.forklift_driver_id = 1
            db.session.commit()
