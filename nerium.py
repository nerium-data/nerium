import decimal
import json
import os

import records
from dotenv import find_dotenv, load_dotenv

if not os.getenv('DATABASE_URL'):
    load_dotenv(find_dotenv())


class ResultSet:
    """Finds SQL query file, and executes query against database configured
    in $DATABASE_URL. Returns results as dict formatted like

    `{"columns": [<list of column names>], "data": [<list of rows as lists>]}`

    Args:
        report_name (str): Name of chosen query file, without the .sql extension
    """
    # Ensure results are JSON serializeable
    def date_handler(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return obj

    # Get database connection
    def query_db(self):
        db_url = os.getenv('DATABASE_URL', 'sqlite:///')
        db = records.Database(db_url)
        return db

    # Find SQL file matching report_name
    def get_sql(self, report_name):
        sql_dir = os.getenv('SQL_PATH', 'sqls')
        filename = '{}.sql'.format(report_name)
        sql_file = os.path.join(sql_dir, filename)
        return sql_file

    # Submit query, apply serialization cleaner method to data values,
    #    return results in dict
    def result(self, report_name, **kwargs):
        query_db = self.query_db()
        result = query_db.query_file(self.get_sql(report_name), **kwargs)
        cols = result.dataset.headers
        rows = [list(row.values()) for row in result.all(as_ordereddict=True)]
        rows = [[self.date_handler(obj) for obj in row] for row in rows]
        format_dict = dict(columns=cols, data=rows)
        return format_dict


if __name__ == "__main__":
    loader = ResultSet()
    payload = loader.result('test')
    print(json.dumps(payload))
