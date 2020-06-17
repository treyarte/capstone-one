"""Seed the database with sample data"""

from app import db
from models import Role, User, Stocker, ForkliftDriver, DropList, Location, Item

db.drop_all()
db.create_all()

role1 = Role(role="stocker")
role2 = Role(role="forklift_driver")

db.session.add_all([role1, role2])
db.session.commit()

user1 = User.sign_up("Andrew", "Thomas", "123@gmail.com", "hardlines", "Qwerty123!",role1.id,"https://i.ytimg.com/vi/7lg0ZnDxoJ4/maxresdefault.jpg")
user2 = User.sign_up("Roy", "Ourboy", "321@gmail.com", "hardlines", "123Qwerty!", role2.id)

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

droplist_1 = DropList(stocker_id = stocker1.id, forklift_driver_id=driver1.id, department=user1.department)

db.session.add(droplist_1)
db.session.commit()

item1 = Item(description="gold potatoes", row_letter="B", column_number=3, location_id=location1.id, droplist_id=droplist_1.id)
item2 = Item(description="onions", row_letter="C", column_number=1, location_id=location1.id, droplist_id=droplist_1.id)
item3 = Item(description="Dates", row_letter="B", column_number=10, location_id=location2.id, droplist_id=droplist_1.id)

db.session.add_all([item1, item2, item3])
db.session.commit()
