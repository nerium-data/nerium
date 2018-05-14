import os

import records
from dotenv import load_dotenv
from nerium import ResultSet
try:
    from jinjasql import JinjaSql
except ImportError:
    # jinjasql > 0.1.6 required for use with repeat param def in template
    pass


class JinjaSQLResultSet(ResultSet):
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
            jinja = JinjaSql(param_style='named')
            with open(self.query_path, 'r') as query_file:
                query = query_file.readlines()
                query_text = ''.join(query)
            qs, bind_params = jinja.prepare_query(query_text, self.kwargs)
            result = db.query(qs, **bind_params)
            result = result.as_dict()
        except Exception as e:
            result = [{'error': repr(e)}, ]
        return result
