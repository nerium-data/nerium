import re
from collections import namedtuple
from datetime import datetime

import s3fs
import yaml
from raw import db
from nerium import streaming


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
            "statement",
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
        path=db.path_by_name(query_name),
    )
    return query_obj


def extract_metadata(query_string):
    """Find frontmatter comment in query string and load yaml from it if present"""
    metadata = {}
    meta_comment = re.search(r"---[\s\S]+?---", query_string, re.MULTILINE)
    if meta_comment:
        meta_string = meta_comment[0].strip("---")
        metadata = yaml.safe_load(meta_string)

    return metadata


def read_query_file(path):
    if path.startswith("s3://"):
        # Read file from S3 and convert to string with decode()
        fs = s3fs.S3FileSystem(anon=False)
        with fs.open(path, "rb") as f:
            statement = f.read().decode()
    else:
        # Read file as text from local filesystem
        with open(path, "rt") as f:
            statement = f.read()
    return statement


def parse_query_file(query_name):
    """Parse query file and add query statement and metadata."""
    query_obj = init_query(query_name)

    if not query_obj.path:
        query_obj = query_obj._replace(
            error=f"No query found matching '{query_name}'", status_code=404
        )
        return query_obj

    statement = read_query_file(query_obj.path)
    metadata = extract_metadata(statement)
    query_obj = query_obj._replace(metadata=metadata, statement=statement)
    return query_obj


def query_decorator(func):
    """Decorates a "result" query method, e.g. a sqla-raw method, in a
    Query for parsing and execution error handling.

    """

    def inner(query_name, *args, **kwargs):
        query = parse_query_file(query_name)

        # Bail if parser captures error:
        if query.error:
            return query

        try:
            result = func(query_name, *args, **kwargs)
            query = query._replace(result=result)
        except Exception as e:
            query = query._replace(error=repr(e), status_code=400)

        return query
    return inner


@query_decorator
def get_result_set(query_name, **kwargs):
    """Call parse_query_file, then submit query and return new object with result"""

    return db.result_by_name(query_name, **kwargs)


@query_decorator
def serialize_stream(query_name, writer_constructor, **kwargs):
    """Call parse_query_file, then submit query and return generator with result"""

    result = db.stream_result_by_name(query_name, **kwargs)
    # Initialization here (outside of a generator) allows for
    # exception handling in `query_decorator` and an HTTP error
    # return prior to starting a 200 streaming HTTP
    # response. Otherwise, an exception raised from within the
    # generator iteration would occur after the stream response is returned
    stream, writer = streaming.initialize_stream(result, writer_constructor)

    return streaming.yield_stream(result, stream, writer, **kwargs)
