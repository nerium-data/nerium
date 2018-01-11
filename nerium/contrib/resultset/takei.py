import os

import records
# from app import app
from nerium import ResultSet


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

    # Also TODO: In the meantime, at least get this into its own "contrib"
    #     implementation

    @property
    def query_type(self):
        return('sql')

    db = os.getenv('DATABASE_URL', 'sqlite:///?check_same_thread=False')
    query_db = records.Database(db)
    # query_db = records.Database(app.config['DATABASE_URL'])
    table_list = query_db.get_table_names()

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
                    rows = self.query_db.query(sql_query, **self.kwargs)
                    result = rows.as_dict()
                return result
            except IOError as e:
                result = [{'error': repr(e)}, ]
                return result
        else:
            try:
                rows = self.query_db.query_file(self.get_file(), **self.kwargs)
                result = rows.as_dict()
            except IOError as e:
                result = [{'error': repr(e)}, ]
            return result
