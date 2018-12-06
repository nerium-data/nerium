import importlib.util
import os
from importlib import import_module


def get_format(format_):
    """ Find format schema in $FORMAT_PATH or nerium/schema
    """
    format_path = os.getenv('FORMAT_PATH', 'format_files')
    try:
        spec = importlib.util.spec_from_file_location(
            "format_mod", f"{format_path}/{format_}.py")
        format_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(format_mod)
    except FileNotFoundError:
        try:
            format_mod = import_module(f'nerium.schema.{format_}')
        except ModuleNotFoundError:
            format_mod = import_module('nerium.schema.default')
    schema = format_mod.ResultSchema()
    return schema
