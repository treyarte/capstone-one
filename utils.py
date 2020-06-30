def create_sample_data(db,Role, User, Location, Stocker, ForkliftDriver, Item, DropList):
    role1 = Role(role="stocker")
    role2 = Role(role="forklift_driver")

    db.session.add_all([role1, role2])
    db.session.commit()

    u1 = User.sign_up(first_name="Test", last_name="Person", 
                    email="test@person.com", department="hardlines", 
                    password="1234person",current_role_id=role1.id)

    u2 = User.sign_up(first_name="Test2", last_name="Person2", 
                    email="test@person2.com", department="hardlines", 
                    password="1234person2", current_role_id=role2.id)
    
    loc1 = Location(name="S409") 
    loc2 = Location(name="S408")
    
    db.session.add_all([loc1,loc2])
    db.session.commit()
    
    s1 = Stocker(user_id = u1.id)
    d1 = ForkliftDriver(user_id = u2.id)  

    db.session.add_all([s1, d1])
    db.session.commit()

    droplist_1 = DropList(stocker_id = s1.id, forklift_driver_id=d1.id, department=u1.department)

    db.session.add(droplist_1)
    db.session.commit()

    item1 = Item(description="gold potatoes", row_letter="B", column_number=3, location_id=loc1.id, droplist_id = droplist_1.id)
    item2 = Item(description="onions", row_letter="C", column_number=1, location_id=loc1.id, droplist_id=droplist_1.id)
    item3 = Item(description="Dates", row_letter="B", column_number=10, location_id=loc2.id, droplist_id=droplist_1.id)

    db.session.add_all([item1, item2, item3])
    db.session.commit()


    #req_items is a list of request item objects
    return [u1, u2, s1, d1, loc1, loc2, droplist_1, item1, item2, item3]

