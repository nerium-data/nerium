import tablib

""" Returns results as CSV-formatted string
"""
# TODO: some graceful error handling, in case of bad input format, etc.


def format_results(result, **kwargs):
    raw = result['data']
    columns = list(raw[0].keys())
    data = [tuple(row.values()) for row in raw]
    frame = tablib.Dataset()
    frame.headers = columns
    for row in data:
        frame.append(row)
    formatted = frame.export('csv')
    return formatted