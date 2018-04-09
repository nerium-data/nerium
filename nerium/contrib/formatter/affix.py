import datetime

from flask import request
from nerium import ResultFormatter


class AffixFormatter(ResultFormatter):
    """ Wrap default object array with error and metadata details
    """
    def format_results(self):
        formatted = {}
        formatted['error'] = False
        formatted['response'] = self.result
        formatted['metadata'] = {}
        formatted['metadata']['executed'] = datetime.datetime.now().isoformat()
        # TODO: Lib shouldn't depend on Flask. Get these params another way
        formatted['metadata']['params'] = request.args.to_dict()
        return formatted
