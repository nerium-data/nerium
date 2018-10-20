import os
from pathlib import Path

import frontmatter
from importlib import import_module
from munch import munchify
from nerium import config

FLAT_QUERIES = list(Path(os.getenv('QUERY_PATH', 'query_files')).glob('**/*'))

FLAT_TEMPLATES = list(
    Path(os.getenv('TEMPLATE_PATH', 'templates')).glob('**/*'))


def get_query(query_name):
    query_file_match = list(
        filter(lambda i: query_name == i.stem, FLAT_QUERIES))
    if not query_file_match:
        return None
    query_file = query_file_match[0]
    with open(query_file) as f:
        metadata, query_body = frontmatter.parse(f.read())
    query_ext = query_file.suffix.strip('.')
    try:
        result_cls = config.query_extensions[query_ext]
    except KeyError:
        result_cls = 'SQLResultSet'
    parsed_query = dict(
        name=query_name,
        metadata=metadata,
        path=query_file,
        result_cls=result_cls,
        body=query_body,
    )
    return munchify(parsed_query)


def result_set(query_name, **kwargs):
    query = get_query(query_name)
    if not query:
        return [{'error': "No query found matching {}".format(query_name)}]
    result_mods = import_module('nerium.contrib.resultset')
    cls_name = query.result_cls
    result_cls = getattr(result_mods, cls_name)
    loader = result_cls(query, **kwargs)
    query_result = loader.result()
    return dict(metadata=query.metadata, data=query_result)


def formatted_results(result, format_, **kwargs):
    try:
        format_cls_name = config.formats[format_]
    except KeyError:
        format_cls_name = 'DefaultFormatter'
    format_mods = import_module('nerium.contrib.formatter')
    format_cls = getattr(format_mods, format_cls_name)
    return format_cls(result, **kwargs).format_results()
