# -*- coding: utf-8 -*-
"""SQL database query implementation of resultset, using Records library
to fetch a dataset from configured query_name
"""
import records
from nerium import data_source


def connection(query):
    db_url = data_source.get_data_source(query)['url']
    db = records.Database(db_url)
    return db


def result(query, **kwargs):
    try:
        rows = connection(query).query(query.body, **kwargs)
        rows = rows.as_dict()
    except Exception as e:
        rows = [{'error': repr(e)}, ]  # yapf: disable
    return rows
