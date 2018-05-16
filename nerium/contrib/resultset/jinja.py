import os

import records
from dotenv import load_dotenv
from nerium.contrib.resultset.sql import SQLResultSet

try:
    from jinjasql import JinjaSql
except ImportError:
    # jinjasql >= 0.1.7 required for use with repeat param def in template
    pass


class JinjaSQLResultSet(SQLResultSet):
    """ Use jinjasql to process template for use against records db connection.
    Similar to a regular SQLResultSet, but preprocesses the query with jinjasql
    to allow for more complex conditional logic.

    NOTE: jinjasql>=0.1.7 required for module usage.
    """

    def result(self):
        try:
            backend_path = self.query_path.parent
            backend = self.backend_lookup(backend_path)
            db = records.Database(backend)
            try:
                jinja = JinjaSql(param_style='named')
            except NameError:
                raise Exception("jinjasql >= 0.1.7 required for use")
            with open(self.query_path, 'r') as query_file:
                query = query_file.readlines()
                query_text = ''.join(query)
            qs, bind_params = jinja.prepare_query(query_text, self.kwargs)
            result = db.query(qs, **bind_params)
            result = result.as_dict()
        except Exception as e:
            result = [{'error': repr(e)}, ]
        return result
