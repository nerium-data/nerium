import os
import re
from pathlib import Path
from types import SimpleNamespace

from nerium.query import parse_query_file
from sqlparse import parse
from sqlparse.sql import IdentifierList, Identifier


def list_reports():
    flat_queries = list(Path(os.getenv("QUERY_PATH", "query_files")).glob("**/*"))
    """Return list of available report names from query dir
    """
    # Filter out docs and metadata
    query_paths = list(filter(lambda i: i.suffix not in [".md", ".yaml"], flat_queries))
    query_names = [i.stem for i in query_paths]
    query_names.sort()
    reports = dict(reports=query_names)
    return reports


def columns_from_metadata(query):
    """Return `columns` block from query front matter,
    if present
    """
    columns = None
    if "columns" in query.metadata.keys():
        columns = query.metadata["columns"]
    return columns


def columns_from_body(query):
    """Parse columns from SELECT statement
    """
    columns = []
    if query.result_module != "sql":
        columns = None
    parsed_query = parse(query.body)[0]
    for tkn in parsed_query.tokens:
        if isinstance(tkn, IdentifierList):
            for id_ in tkn:
                if isinstance(id_, Identifier):
                    columns.append(id_.get_name())
    if not columns:
        columns = "unknown"
    return columns


def params_from_metadata(query):
    params = None
    if "params" in query.metadata.keys():
        params = query.metadata["params"]
    return params


def params_from_body(query):
    param_regex = re.compile("(?<!\\w)\\:\\w+")
    param_list = [i.strip(":") for i in re.findall(param_regex, query.body)]
    return param_list


def get_report_query(query_name):
    query = parse_query_file(query_name)
    if not query:
        query = SimpleNamespace()
        query.error = f"No query found matching '{query_name}'"
        query.status_code = 404
    return query


def describe_report(query_name):
    report_query = get_report_query(query_name)
    if report_query.error:
        return report_query
    params = params_from_metadata(report_query) or params_from_body(report_query)
    columns = columns_from_metadata(report_query) or columns_from_body(report_query)
    report_description = SimpleNamespace(
        error=report_query.error,
        name=report_query.name,
        type=report_query.result_module,
        columns=columns,
        params=params,
        metadata=report_query.metadata,
    )
    return report_description


if __name__ == "__main__":
    q = describe_report("foo")
    # h = params_from_body(q)
    print(q)
