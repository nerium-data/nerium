#!/usr/bin/env python
# -*- coding: utf-8 -*-
import decimal
import os

import records
from dotenv import find_dotenv, load_dotenv
from flask import Flask, current_app, render_template, request
from flask.json import JSONEncoder
from flask_restful import Api, Resource

# Provision environment as needed
if find_dotenv():
    load_dotenv(find_dotenv())
else:
    load_dotenv('/dotenv/.env')

# Instantiate and configure app
app = Flask(__name__)
api = Api(app)
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///')
app.config['SQL_PATH'] = os.getenv('SQL_PATH', 'sqls')


class ResultJSONEncoder(JSONEncoder):
    """ Add simple default encodings for Decimals and Datetimes.
    Why `json` doesn't do this out of the box is beyond me. >:(
    """
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return obj
        return JSONEncoder.default(self, obj)


app.config['RESTFUL_JSON'] = {'cls': ResultJSONEncoder}


class ResultSet:
    """Finds SQL query file, and executes query against database configured
    in $DATABASE_URL. Returns results as dict formatted like

    `{"columns": [<list of column names>], "data": [<list of rows as lists>]}`

    Args:
        report_name (str): Name of chosen query file, without the .sql extension
    """
    # Find SQL file matching report_name
    def get_sql(self, report_name):
        try:
            sql_dir = current_app.config['SQL_PATH']
        except RuntimeError:  # so this works outside requests for testing
            sql_dir = os.getenv('SQL_PATH', 'sqls')
        filename = '{}.sql'.format(report_name)
        sql_file = os.path.join(sql_dir, filename)
        return sql_file

    # Submit query, apply serialization cleaner method to data values,
    #    return results in dict
    def result(self, report_name, **kwargs):
        try:
            query_db = records.Database(current_app.config['DATABASE_URL'])
        except RuntimeError:
            query_db = records.Database(os.getenv('DATABASE_URL', 'sqlite:///'))
        result = query_db.query_file(self.get_sql(report_name), **kwargs)
        cols = result.dataset.headers
        rows = [list(row.values()) for row in result.all(as_ordereddict=True)]
        format_dict = dict(columns=cols, data=rows)
        return format_dict


class ReportAPI(Resource):
    """ Calls ResultSet.result() and returns JSON in compact format like

    `{"columns": [<list of column names>],
      "data": [<array of row value arrays>]}`
    """
    def get(self, report_name):
        loader = ResultSet()
        payload = loader.result(report_name, **request.args.to_dict())
        return payload


api.add_resource(ReportAPI, '/<string:report_name>',
                 '/report/<string:report_name>')


@app.route('/table/<string:report_name>')
def report_table(report_name):
    loader = ResultSet()
    payload = loader.result(report_name, **request.args.to_dict())
    return render_template(
        'table.html', columns=payload['columns'], data=payload['data'])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
