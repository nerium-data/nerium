import importlib.util
import os
from importlib import import_module


def get_format(format_="default"):
    """ Find format schema in $FORMAT_PATH or nerium/schema
        NOTE: if `format_` is not found, this falls back to "default"
    """
    # Load format from builtin schema if exists
    try:
        format_mod = import_module(f"nerium.schema.{format_}")
    except ModuleNotFoundError:
        # Attempt to load custom format from $FORMAT_PATH
        try:
            format_path = os.getenv("FORMAT_PATH", "format_files")
            spec = importlib.util.spec_from_file_location(
                "format_mod", f"{format_path}/{format_}.py"
            )
            format_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(format_mod)
        # Fallback to default schema if no other match
        except FileNotFoundError:
            format_mod = import_module("nerium.schema.default")
    schema = format_mod.ResultSchema()
    return schema


# TODO: dump from format schema here(?)
