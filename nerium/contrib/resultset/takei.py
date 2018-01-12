from nerium import ResultSet
from nerium.contrib.queryable.record import RecordsQueryable
from nerium.contrib.queryable.takei import TakeiQueryable


class TakeiResultSet(ResultSet):
    """ Handle table name substitution in takei queries

        **NOTE** Normally I (@tym-oao) am opposed to project names in code,
        and particularly in something like a class name. In this limited case
        it is acceptable and deliberate, because the table name substitution
        being done to set up the queries is gross, and it is fondly to be
        wished that this code will serve only as a legacy stopgap, and that we
        will soon burn this bridge behind us to light our way forward.

        TL;DR: let's not merge this to master in its present form, k?
    """
    # TODO: Factor this whole thing out. Stop using queries that conditionally
    #     access different tables for the same data. Stop using MySQL.

    @property
    def query_type(self):
        return('sql')

    @property
    def table_list(self):
        db = TakeiQueryable()
        return db.get_table_list(self.get_file())

    def result(self):
        if 'client_id' in self.kwargs.keys():
            tbl_name = "{}_daily".format(self.kwargs['client_id'])
            if tbl_name not in self.table_list:
                result = [{'error': 'Table {} not found in database'}, ]
                return result
            try:
                tbl_name = '`{}`'.format(tbl_name)
                with open(self.get_file(), 'r') as _query_file:
                    sql_query = _query_file.read()
                    sql_query = sql_query.replace('TABLE_NAME', tbl_name)
                    db = TakeiQueryable()
                    result = db.results(sql_query, **self.kwargs)
                return result
            except IOError as e:
                result = [{'error': repr(e)}, ]
                return result
        else:
            try:
                db = RecordsQueryable()
                result = db.results(self.get_file(), **self.kwargs)
            except IOError as e:
                result = [{'error': repr(e)}, ]
            return result
