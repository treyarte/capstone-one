"""Seed the database with sample data"""

from app import db
from models import User, Stocker, ForkliftDriver, Request, RequestItem, Location, Item

db.drop_all()
db.create_all()

user1 = User.sign_up("Trey", "Akimoto", "123@gmail.com", "hardlines", "qwerty123","https://i.ytimg.com/vi/7lg0ZnDxoJ4/maxresdefault.jpg")
user2 = User.sign_up("Roy", "Ourboy", "321@gmail.com", "hardlines", "123qwerty")

location1 = Location(name="S409") 
location2 = Location(name="S408")

db.session.add_all([location1, location2])

db.session.commit()

user1.admin = True

db.session.commit()


stocker1 = Stocker(user_id = user1.id)
driver1 = ForkliftDriver(user_id = user2.id)  

db.session.add_all([stocker1, driver1])
db.session.commit()

request1 = Request(stocker_id = stocker1.id, forklift_driver_id=driver1.id)

item1 = Item(description="gold potatoes", row_letter="B", column_number=3, location_id=location1.id)
item2 = Item(description="onions", row_letter="C", column_number=1, location_id=location1.id)
item3 = Item(description="Dates", row_letter="B", column_number=10, location_id=location2.id)

db.session.add_all([request1, item1, item2, item3])
db.session.commit()

req_items1 = []
req_items1.append(RequestItem(request_id = request1.id, item_id=item1.id))
req_items1.append(RequestItem(request_id = request1.id, item_id=item2.id))
req_items1.append(RequestItem(request_id = request1.id, item_id=item3.id))

db.session.add_all(req_items1)
db.session.commit()