import os
from collections import namedtuple
from datetime import datetime
from pathlib import Path

import sqlparse
import yaml

# from jinja2.sandbox import SandboxedEnvironment

from raw import db


def query_file(query_name):
    """Find file matching query_name and return Path object"""
    flat_queries = list(Path(os.getenv("QUERY_PATH", "query_files")).glob("**/*"))
    query_file = None
    query_file_match = list(filter(lambda i: query_name == i.stem, flat_queries))
    if query_file_match:
        # TODO: Warn if more than one match
        query_file = query_file_match[0]
    return query_file


def init_query(query_name):
    """Initialize query namedtuple from file name"""
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
    )
    # `nametuple.defaults` option only available in >=3.7
    # .__new__.defaults__ works with older versions
    Query.__new__.__defaults__ = (False, {}, "", "", "", 200)
    query_obj = Query(
        name=query_name,
        executed=datetime.utcnow().isoformat(),
        path=query_file(query_name),
    )
    return query_obj


def extract_metadata(query_string):
    """Find `:meta` labeled comment in query string and load yaml from it"""
    tokens = sqlparse.parse(query_string)[0].tokens
    # Get comment with :meta label
    try:
        meta_comment = str(
            [
                token
                for token in tokens
                if isinstance(token, sqlparse.sql.Comment) and ":meta" in str(token)
            ][0]
        )
    except IndexError:
        return {}
    # Split YAML block out of :meta comment and load it
    meta_string = meta_comment.split("---")[1]
    metadata = yaml.safe_load(meta_string)
    return metadata


def parse_query_file(query_name):
    """Parse query file and add query body and metadata."""
    query_obj = init_query(query_name)
    try:
        with open(query_obj.path) as f:
            query_string = f.read()

        metadata = extract_metadata(query_string)
        body = sqlparse.format(query_string, strip_comments=True)

        query_obj = query_obj._replace(metadata=metadata, body=body)

    # Set 404 if no file matches query_name
    except (FileNotFoundError, TypeError):
        query_obj = query_obj._replace(
            error=f"No query found matching '{query_name}'", status_code=404
        )

    return query_obj


def get_result_set(query_name, **kwargs):
    """Call parse_query_file, then submit query and return new object with result"""
    query = parse_query_file(query_name)

    # Bail if parser captures error:
    if query.error:
        return query

    result = db.result(query.body, jinja=True, **kwargs)
    query = query._replace(result=result)

    # Set query.error in case db module captures an excecption
    if isinstance(query.result[0], dict) and "error" in query.result[0].keys():
        error = query.result[0]["error"]
        query = query._replace(error=error, status_code=400)

    return query
