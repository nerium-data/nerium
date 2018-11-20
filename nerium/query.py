import os
from datetime import datetime
from pathlib import Path

import frontmatter
from importlib import import_module
from munch import munchify

# Walking the query_files dir to get all the queries in a single list
# NOTE: this means query names should be unique across subdirectories,
#       *and* adding a new query file requires restart
FLAT_QUERIES = list(Path(os.getenv('QUERY_PATH', 'query_files')).glob('**/*'))


def get_query(query_name):
    """Find file matching query_name, read and return query object
    """
    query_file_match = list(
        filter(lambda i: query_name == i.stem, FLAT_QUERIES))
    if not query_file_match:
        return None
    # TODO: Log warning if more than one match
    query_file = query_file_match[0]
    with open(query_file) as f:
        metadata, query_body = frontmatter.parse(f.read())
    result_mod = query_file.suffix.strip('.')
    parsed_query = dict(
        name=query_name,
        metadata=metadata,
        path=query_file,
        result_mod=result_mod,
        body=query_body,
        error=False,
        executed=datetime.now())
    return munchify(parsed_query)


def result_set(query_name, **kwargs):
    """Call get_query, then submit query from file to resultset module
    """
    query = get_query(query_name)
    if not query:
        return [{'error': f"No query found matching '{query_name}'"}]
    try:
        result_mod = import_module(
            f'nerium.contrib.resultset.{query.result_mod}')
    except ModuleNotFoundError:
        result_mod = import_module('nerium.resultset.sql')
    query_result = result_mod.result(query, **kwargs)
    return dict(metadata=query.metadata, data=query_result)


def formatted_results(result, format_, **kwargs):
    try:
        format_mod = import_module(f'nerium.formatter.{format_}')
    except ModuleNotFoundError:
        format_mod = import_module('nerium.formatter.default')
    return format_mod.format_results(result, **kwargs)
