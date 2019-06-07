import tablib
from nerium.query import get_result_set


def results_to_csv(query_name, **kwargs):
    """ Generate CSV from result data
    """
    # TODO: separate module for this
    query = get_result_set(query_name, **kwargs)
    result = query.result
    frame = tablib.Dataset()
    if isinstance(result[0], dict):
        data = [tuple(row.values()) for row in result]
        frame.headers = list(result[0].keys())
    else:
        data = [tuple(row.split(",")) for row in result]
    for row in data:
        frame.append(row)
    csv = frame.export("csv")
    return csv
