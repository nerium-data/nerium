def serial_date(obj):
    """Convert dates/times to isoformat, for use by JSON formatter"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return str(obj)


def multi_to_dict(obj):
    """Convert multidict to dict, consolidating values
    into list for repeated keys
    """
    if hasattr(obj, 'getall'):
        new_dict = {
            key: (obj.getall(key)
                  if len(obj.getall(key)) > 1 else obj.get(key))
            for key in obj.keys()
        }
        return new_dict
    else:
        return dict(obj)
