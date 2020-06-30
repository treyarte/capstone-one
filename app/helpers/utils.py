def tuple_convertor(db_tup):
    """Converts a tuple to a dictionary"""
    new_dict = {}
    for a, b in db_tup:
        new_dict.setdefault(a, []).append(b)
    
    return new_dict