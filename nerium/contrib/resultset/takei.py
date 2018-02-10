import re
import records

from nerium.contrib.resultset.sql import SQLResultSet


class TakeiResultSet(SQLResultSet):
    """ Handle table name substitution in takei queries
    """
    # TODO: Remove this module as soon as we can
    # replace legacy 'takei-web-app' MySQL instance

    def table_substitution(self, db, client_id):
        table_list = db.get_table_list()
        with open(self.get_file(), 'r') as _query_file:
            sql_query = _query_file.read()
        if '_TABLE' not in sql_query:
            return sql_query
        table_tokens = re.findall(r'\w+_TABLE\b', sql_query)
        table_norm = [i.lower().replace('_table', '') for i in table_tokens]
        table_sub = ['`{}_{}`'.format(client_id, i) for i in table_norm]
        for table in table_sub:
            if table not in table_list:
                return ('missing', table)
        table_map = list(zip(table_tokens, table_sub))
        for map in table_map:
            sql_query = sql_query.replace(map[0], map[1])
        return sql_query

    def result(self):
        backend_name = self.get_query_path().parent.name
        backend = self.backend_lookup(backend_name)
        db = records.Database(backend)

        if 'client_id' in self.kwargs.keys():
            sql_query = self.table_substitution(db, self.kwargs['client_id'])
            if sql_query[0] == 'missing':
                tbl_name = sql_query[1]
                result = [
                    {
                        'error':
                        'Table {} not found in database'.format(tbl_name)
                    },
                ]
                return result
            try:
                result = db.query(sql_query, **self.kwargs)
            except Exception as e:
                result = [{'error': repr(e)}, ]
        else:
            try:
                result = db.query_file(self.get_query_path(), **self.kwargs)
            except Exception as e:
                result = [{'error': repr(e)}, ]
        result = result.as_dict()
        return result
