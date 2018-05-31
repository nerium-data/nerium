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
            try:
                jinja = JinjaSql(param_style='named')
            except NameError:
                raise Exception("jinjasql >= 0.1.7 required for use")
            qs, bind_params = jinja.prepare_query(self.query.body, self.kwargs)
            result = self.connection().query(qs, **bind_params)
            result = result.as_dict()
        except Exception as e:
            result = [
                {
                    'error': repr(e)
                },
            ]
        return result
