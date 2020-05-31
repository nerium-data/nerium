# -*- coding: utf-8 -*-
"""Use SQLAlchemy engine to fetch a dataset from configured query_name
"""
import os
from sqlalchemy import create_engine, text


def get_data_source(query):
    """ Get data source connection metadata based on config. Prefer, in order:
        - Query file metadata
        - DATABASE_URL in environment
    """
    # from file metadata
    if "database_url" in query.metadata.keys():
        return query.metadata["database_url"]

    # Default to $DATABASE_URL (with sqlite fallback) if not set in frontmatter
    return os.getenv("DATABASE_URL", "sqlite:///")


def connection(query):
    db_url = get_data_source(query)
    db = create_engine(db_url)
    conn = db.connect()
    return conn


def result(query, **kwargs):
    try:
        db = connection(query)
        sql = query.body
        cur = db.execute(text(sql), **kwargs)
        cols = cur.keys()
        result = cur.fetchall()
        rows = [dict(zip(cols, row)) for row in result]
    except Exception as e:
        rows = [{"error": repr(e)}]
    return rows
