from app.models import Role, User, Stocker, ForkliftDriver, DropList, db, Item, Location

def droplist_setup():
    User.query.delete()
    ForkliftDriver.query.delete()
    Stocker.query.delete()
    Role.query.delete()
    DropList.query.delete()
    
    values = []

    role1 = Role(role="stocker")
    role2 = Role(role="forklift_driver")    
    db.session.add_all([role1, role2])
    db.session.commit()
   
    u1 = User.sign_up(
                        first_name="Test", last_name="Person", 
                        email="test@person.com", department="sundries", 
                        password="Qwerty123!", current_role_id=role1.id)   
    u2 = User.sign_up(
                        first_name="New", last_name="Person", 
                        email="new@person.com", department="sundries", 
                        password="Qwerty123!", current_role_id=role2.id)   
    u3 = User.sign_up(
                        first_name="New2", last_name="Person2", 
                        email="new@person2.com", department="hardlines", 
                        password="Qwerty123!", current_role_id=role1.id)   
    db.session.commit()

    values.extend([u1,u2,u3])

    s1 = Stocker(user_id=u1.id)
    s2 = Stocker(user_id=u3.id)
    f1 = ForkliftDriver(user_id=u2.id)    
    
    db.session.add_all([s1,s2, f1])
    db.session.commit()
    
    droplist = DropList(stocker_id=s1.id, description="Test Drop", department="hardlines", forklift_driver_id=f1.id)
    droplist_2 = DropList(stocker_id=s1.id, description="Test Droplist 2", department="hardlines")
    droplist_3 = DropList(stocker_id=s2.id, description="Test Droplist 3", department="sundries")
    
    values.extend([s1,s2,f1])

    db.session.add_all([droplist, droplist_2, droplist_3])
    db.session.commit()

    values.extend([droplist, droplist_2, droplist_3])

    loc = Location(name="S409")
    
    db.session.add(loc)
    db.session.commit()
    
    item_1 = Item(
                row_letter="a", 
                column_number=1, 
                location_id=loc.id, 
                description="Test Item 1", 
                droplist_id= droplist_2.id)
        
    db.session.add(item_1)
    db.session.commit()



    return values
