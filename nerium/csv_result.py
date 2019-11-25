from csv import DictWriter
from io import StringIO
from nerium.query import get_result_set


def results_to_csv(query_name, **kwargs):
    """ Generate CSV from result data
    """
    query = get_result_set(query_name, **kwargs)
    result = query.result
    stream = StringIO()
    headers = list(result[0].keys())
    dw = DictWriter(stream, fieldnames=headers)
    dw.writeheader()
    for row in result:
        dw.writerow(row)
    csv = stream.getvalue()
    return csv
