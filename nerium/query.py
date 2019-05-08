import json
import os
from datetime import datetime
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import frontmatter
from jinja2.sandbox import SandboxedEnvironment
from tablib.formats._json import serialize_objects_handler as handler


def query_file(query_name):
    """Find file matching query_name and return Path object
    """
    flat_queries = list(Path(os.getenv("QUERY_PATH", "query_files")).glob("**/*"))
    query_file = None
    query_file_match = list(filter(lambda i: query_name == i.stem, flat_queries))
    if query_file_match:
        # TODO: Warn if more than one match
        query_file = query_file_match[0]
    return query_file


def parse_query_file(query_name):
    """Parse query file and return query object
    """
    query_obj = SimpleNamespace(
        name=query_name, executed=datetime.utcnow().isoformat(), error=False
    )

    query_path = query_file(query_name)

    try:
        with open(query_path) as f:
            metadata, query_body = frontmatter.parse(f.read())
            result_module = query_path.suffix.strip(".")

            query_obj.metadata = metadata
            query_obj.path = query_path
            query_obj.result_module = result_module
            query_obj.body = query_body

    except (FileNotFoundError, TypeError):
        query_obj.error = f"No query found matching '{query_name}'"
        query_obj.status_code = 404

    return query_obj


def process_template(body, **kwargs):
    """Render query body using jinja2 sandbox
    TODO: Prevent variable expansion
    """
    env = SandboxedEnvironment()
    template = env.from_string(body)
    return template.render(kwargs)


def plugin_module(name):
    """Load all modules named like `nerium_*` as plugin registry and return
    module matching query file stem if available, or default to sql built-in

    Besides being named like `nerium_*`, plugins are expected to accept a query object
    and provide a `result` method that returns an iterable dataset (list of dicts, e.g.)
    """
    from pkgutil import iter_modules

    plugins = {
        name: import_module(name)
        for finder, name, ispkg in iter_modules()
        if name.startswith("nerium_")
    }
    plugin_name = f"nerium_{name}"
    if plugin_name in plugins.keys():
        return plugins[plugin_name]
    else:
        return import_module("nerium.resultset.sql")


def assign_module(name="sql"):
    """Import resultset module matching query file stem from nerium.resultset or plugin
    """
    try:
        result_module = import_module(f"nerium.resultset.{name}")
    except ModuleNotFoundError:
        result_module = plugin_module(name)
    return result_module


def get_result_set(query_name, **kwargs):
    """Call parse_query_file, then submit query object to resultset module
    """
    query = parse_query_file(query_name)

    # Bail on 404:
    if query.error:
        return query

    result_module = assign_module(query.result_module)
    query.body = process_template(body=query.body, **kwargs)
    result = result_module.result(query, **kwargs)

    # Dumping and reloading via json here gets us datetime and decimal
    # serialization handling courtesy of `tablib`
    # TODO: tablib handler breaks on interval type; let's make our own handler
    query.result = json.loads(json.dumps(result, default=handler))

    # Set query.error in case of query excecption
    try:
        query.error = query.result[0]["error"]
    except (IndexError, KeyError, TypeError):
        pass

    return query
