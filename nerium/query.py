import os
from collections import namedtuple
from datetime import datetime
from pathlib import Path

import sqlparse
import yaml
from jinja2.sandbox import SandboxedEnvironment

from nerium import db


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


def init_query(query_name):
    """Initialize query namedtuple from file name
    """
    Query = namedtuple(
        "Query",
        [
            "name",
            "executed",
            "error",
            "metadata",
            "path",
            "body",
            "result",
            "status_code",
        ],
        defaults=(False, {}, "", "", "", 200),
    )
    query_obj = Query(
        name=query_name,
        executed=datetime.utcnow().isoformat(),
        path=query_file(query_name),
    )
    return query_obj


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


def process_template(body, **kwargs):
    """Render query body using jinja2 sandbox
    TODO: Prevent variable expansion
    """
    env = SandboxedEnvironment()
    template = env.from_string(body)
    return template.render(kwargs)


def parse_query_file(query_name):
    """Parse query file and add query body and metadata.
    """
    query_obj = init_query(query_name)
    try:
        with open(query_obj.path) as f:
            query_string = f.read()

        query_obj = query_obj._replace(
            metadata=extract_metadata(query_string), body=process_template(query_string)
        )

    # Set 404 if no file matches query_name
    except (FileNotFoundError, TypeError):
        query_obj = query_obj._replace(
            error=f"No query found matching '{query_name}'", status_code=404
        )

    return query_obj


def get_result_set(query_name, **kwargs):
    """Call parse_query_file, then submit query and add results to object
    """
    query = parse_query_file(query_name)

    # Bail if parser doesn't find query file:
    if query.error:
        return query

    query = query._replace(result=db.result(query, **kwargs))

    # Set query.error in case result_module captures an excecption
    if isinstance(query.result[0], dict) and "error" in query.result[0].keys():
        query = query._replace(error=query.result[0]["error"], status_code=400)

    return query
