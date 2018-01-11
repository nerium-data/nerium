import os

# from app import app
import records
from nerium import ResultSet


# `ResultSet` IMPLEMENTATION SUBCLASSES
class SQLResultSet(ResultSet):
    """ SQL database query implementation of ResultSet, using Records library
    to fetch a dataset from configured report_name
    """

    @property
    def query_type(self):
        return ('sql')

    db = os.getenv('DATABASE_URL', 'sqlite:///?check_same_thread=False')
    query_db = records.Database(db)
    # query_db = records.Database(app.config['DATABASE_URL'])

    def result(self):
        try:
            rows = self.query_db.query_file(self.get_file(), **self.kwargs)
            result = rows.as_dict()
        except IOError as e:
            result = [{'error': repr(e)}, ]
        return result
