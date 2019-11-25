import os
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import sqlparse
import yaml
from jinja2.sandbox import SandboxedEnvironment
from nerium.db import result


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


def extract_metadata(query_string):
    """ Find `:meta` labeled comment in query string and load yaml from it
    """
    tokens = sqlparse.parse(query_string)[0].tokens
    try:
        meta_comment = str(
            [
                token
                for token in tokens
                if type(token) == sqlparse.sql.Comment and ":meta" in str(token)
            ][0]
        )
    except IndexError:
        return {}
    meta_string = meta_comment.split("---")[1]
    metadata = yaml.safe_load(meta_string)
    return metadata


def parse_query_file(query_name):
    """Parse query file and return query object
    """
    # TODO: immutable named tuple
    query_obj = SimpleNamespace(
        name=query_name, executed=datetime.utcnow().isoformat(), error=False
    )

    query_path = query_file(query_name)

    try:
        with open(query_path) as f:
            query_string = f.read()

        query_obj.metadata = extract_metadata(query_string)
        query_obj.path = query_path
        query_obj.body = query_string

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


def get_result_set(query_name, **kwargs):
    """Call parse_query_file, then submit query object to resultset module
    """
    query = parse_query_file(query_name)

    # Bail if parser doesn't find query file:
    if query.error:
        return query

    # result_module = assign_module(query.result_module)

    # TODO: New resultset object here instead of mutating query object
    query.body = process_template(body=query.body, **kwargs)
    query.result = result(query, **kwargs)

    # Set query.error in case result_module captures an excecption
    if isinstance(query.result[0], dict) and "error" in query.result[0].keys():
        query.error = query.result[0]["error"]
        query.status_code = 400

    return query
