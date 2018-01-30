import sqlalchemy
from nerium import ResultSet
from nerium.contrib.queryable.record import RecordsQueryable


class SQLResultSet(ResultSet):
    """ SQL database query implementation of ResultSet, using Records library
    to fetch a dataset from configured report_name
    """

    @property
    def query_type(self):
        return ('sql')

    # TODO: abstract method of base class or concrete implementation here?
    def get_params(self):
        with open(self.get_file(), 'r') as qf:
            query_data = qf.read()
        query = sqlalchemy.text(query_data)
        # get_children will get all elements related to the query
        bind_parameters = query.get_children()
        needed_params = [bparam.key
                         for bparam in bind_parameters
                         if isinstance(bparam,
                                       sqlalchemy.sql.expression.BindParameter)
                         ]
        return needed_params

    def result(self):
        try:
            db = RecordsQueryable()
            params = self.get_params()
            kwarg_set = set(self.kwargs.keys())
            if set(params) != kwarg_set:
                excess = set(params).symmetric_difference(kwarg_set)
                result = [{'error': "required parameters: {params} --- "
                                    "excess/missing: {excess}"
                                    .format(params=params,
                                            excess=list(excess))}]
            else:
                result = db.results(self.get_file(), **self.kwargs)
        except IOError as e:
            result = [{'error': repr(e)}, ]
        except (sqlalchemy.exc.OperationalError,
                sqlalchemy.exc.InternalError) as e:
            result = [{'error': repr(e)}, ]
        return result
