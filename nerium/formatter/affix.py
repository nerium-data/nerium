import datetime

""" Wrap default object array with error and metadata details
"""


def format_results(result, **kwargs):
    formatted = {}
    formatted['error'] = False
    formatted['response'] = result['data']
    formatted['metadata'] = {}
    formatted['metadata']['executed'] = datetime.datetime.now().isoformat()
    formatted['metadata']['params'] = kwargs
    return formatted
