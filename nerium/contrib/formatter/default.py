from nerium import ResultFormatter


class DefaultFormatter(ResultFormatter):
    """ No-op default
    """
    def format_results(self):
        return self.result
