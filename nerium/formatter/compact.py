# -*- coding: utf-8 -*-
"""Returns dict in format
{"columns": [<list of column names>],
"data": [<list of row value lists>]}
"""
# TODO: some graceful error handling, in case of bad input format, etc.


def format_results(result, **kwargs):
    raw = result['data']
    columns = list(raw[0].keys())
    data = [tuple(row.values()) for row in raw]
    formatted = dict(columns=columns, data=data)
    return formatted
