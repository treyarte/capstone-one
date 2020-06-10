def create_sample_data(db, User, Location, Stocker, ForkliftDriver, Item, DropListItem, DropList):
    u1 = User.sign_up(first_name="Test", last_name="Person", email="test@person.com", department="hardlines", password="1234person")
    u2 = User.sign_up(first_name="Test2", last_name="Person2", email="test@person2.com", department="hardlines", password="1234person2")
    
    loc1 = Location(name="S409") 
    loc2 = Location(name="S408")
    
    db.session.add_all([loc1,loc2])
    db.session.commit()
    
    s1 = Stocker(user_id = u1.id)
    d1 = ForkliftDriver(user_id = u2.id)  

    db.session.add_all([s1, d1])
    db.session.commit()

    drop_list_1 = DropList(stocker_id = s1.id, forklift_driver_id=d1.id)

    item1 = Item(description="gold potatoes", row_letter="B", column_number=3, location_id=loc1.id)
    item2 = Item(description="onions", row_letter="C", column_number=1, location_id=loc1.id)
    item3 = Item(description="Dates", row_letter="B", column_number=10, location_id=loc2.id)

    db.session.add_all([drop_list_1, item1, item2, item3])
    db.session.commit()

    drop_items1 = []
    drop_items1.append(DropListItem(drop_list_id = drop_list_1.id, item_id=item1.id))
    drop_items1.append(DropListItem(drop_list_id = drop_list_1.id, item_id=item2.id))
    drop_items1.append(DropListItem(drop_list_id = drop_list_1.id, item_id=item3.id))

    db.session.add_all(drop_items1)
    db.session.commit()

    #req_items is a list of request item objects
    return [u1, u2, s1, d1, loc1, loc2, drop_list_1, item1, item2, item3, drop_items1]