from nerium import ResultSet
from nerium.contrib.queryable.record import RecordsQueryable


class SQLResultSet(ResultSet):
    """ SQL database query implementation of ResultSet, using Records library
    to fetch a dataset from configured report_name
    """

    @property
    def query_type(self):
        return ('sql')

    def result(self):
        try:
            db = RecordsQueryable()
            result = db.results(self.get_file(), **self.kwargs)
        except IOError as e:
            result = [{'error': repr(e)}, ]
        return result
