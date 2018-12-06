def unwrap_querystring_lists(obj):
    """Convert responder querystring params, pulling values out of list
    if there's only one.
    """
    new_dict = {
        key: (obj[key][0]
              if len(obj[key]) == 1 else obj[key])
        for key in obj.keys()
        }
    return new_dict
