import os

import records
from dotenv import load_dotenv
from nerium import ResultSet


class SQLResultSet(ResultSet):
    """ SQL database query implementation of ResultSet, using Records library
    to fetch a dataset from configured query_name
    """

    def backend_lookup(self, backend_path):
        env_location = backend_path / '.env'
        load_dotenv(env_location, override=True)
        return os.getenv('DATABASE_URL', 'NOT_CONFIGURED')

    def result(self):
        try:
            backend_path = self.query_path.parent
            backend = self.backend_lookup(backend_path)
            db = records.Database(backend)
            result = db.query_file(self.query_path, **self.kwargs)
            result = result.as_dict()
        except Exception as e:
            result = [{'error': repr(e)}, ]
        return result
