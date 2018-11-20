# -*- coding: utf-8 -*-
"""Returns results as CSV-formatted string
"""
import tablib


def format_results(result, **kwargs):
    # TODO: some graceful error handling, in case of bad input format, etc.
    raw = result['data']
    columns = list(raw[0].keys())
    data = [tuple(row.values()) for row in raw]
    frame = tablib.Dataset()
    frame.headers = columns
    for row in data:
        frame.append(row)
    formatted = frame.export('csv')
    return formatted
