import records
from nerium import ResultSet


class SQLResultSet(ResultSet):
    """ SQL database query implementation of ResultSet, using Records library
    to fetch a dataset from configured report_name
    """

    def backend_lookup(self, backend_name):
        # TODO: this.
        pass

    def result(self):
        try:
            backend_name = self.get_query_path().parent.name
            backend = self.backend_lookup(backend_name)
            db = records.Database(backend)
            result = db.query_file(self.get_query_path(), **self.kwargs)
            result = result.as_dict()
        except Exception as e:
            result = [{'error': repr(e)}, ]
        return result
