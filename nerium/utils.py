"""Helper functions for app"""
import os
from pathlib import Path

from nerium import config


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


def extension_lookup(_key):
    try:
        return config.query_extensions[_key]
    except KeyError:
        return 'SQLResultSet'


def register_paths():
    query_directory = Path(os.getenv('QUERY_PATH', 'query_files'))
    flat_directory = list(query_directory.glob('**/*'))
    registry = [
        dict(
            query_name=i.stem,
            query_path=i,
            result_cls=extension_lookup(i.suffix.strip('.')))
        for i in flat_directory if i.is_file()
    ]
    # TODO: Don't return the whole registry here. We're doing this on
    #     : every call, so build the registry and filter to query_name
    #     : in a single step. (Or cache the registry on app start.)
    return registry
