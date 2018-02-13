from nerium import ResultFormatter


class CompactFormatter(ResultFormatter):
    """ Returns dict in format
    {"columns": [<list of column names>], "data": [<array of row value arrays>]}
    """
    # TODO: some graceful error handling, in case of bad input format, etc.
    def format_results(self):
        raw = self.result
        columns = list(raw[0].keys())
        data = [tuple(row.values()) for row in raw]
        formatted = dict(columns=columns, data=data)
        return formatted
