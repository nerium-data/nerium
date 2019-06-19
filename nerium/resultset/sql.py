# -*- coding: utf-8 -*-
"""SQL database query implementation of resultset, using Records library
to fetch a dataset from configured query_name
"""
from sqlalchemy import create_engine
from nerium.data_source import get_data_source


def connection(query):
    db_url = get_data_source(query)
    db = create_engine(db_url)
    conn = db.connect()
    return conn


def result(query, **kwargs):
    try:
        db = connection(query)
        sql = query.body
        cur = db.execute(sql, **kwargs)
        cols = cur.keys()
        result = cur.fetchall()
        rows = [dict(zip(cols, row)) for row in result]
    except Exception as e:
        rows = [{"error": repr(e)}]
    return rows
