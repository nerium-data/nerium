import os

import records
from dotenv import find_dotenv, load_dotenv
from nerium import ResultSet


class SQLResultSet(ResultSet):
    """ SQL database query implementation of ResultSet, using Records library
    to fetch a dataset from configured report_name
    """

    def backend_lookup(self, backend_path):
        env_location = backend_path / '.env'
        if env_location.is_file():
            load_dotenv(env_location, override=True)
        return os.getenv('DATABASE_URL', 'NOT_CONFIGURED')

    def result(self):
        try:
            backend_path = self.get_query_path().parent
            backend = self.backend_lookup(backend_path)
            db = records.Database(backend)
            result = db.query_file(self.get_query_path(), **self.kwargs)
            result = result.as_dict()
        except Exception as e:
            result = [{'error': repr(e)}, ]
        return result
