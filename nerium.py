#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import decimal
import os
from abc import ABC
from datetime import datetime

import records
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request
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
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL',
                                       'sqlite:///?check_same_thread=False')
app.config['QUERY_PATH'] = os.getenv('QUERY_PATH', 'query_files')


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


# BASE CLASSES
class ResultSet(ABC):
    """Generic result set class template.

    Loads data source and query fetch query
    results by submitting query to data source with expected parameters.


    Args:
        report_name (str): Name of chosen query file, without the extension
        kwargs: Parameter keys and values to bind to query

    Usage:
        Subclass and override 'query_type' attribute with a file extension
        to seek in QUERY_PATH directory, and provide a 'result' method
    """

    def __init__(self, report_name, **kwargs):
        self.report_name = report_name
        self.kwargs = kwargs

    @property
    @abc.abstractmethod
    def query_type(self):
        return None

    def get_file(self):
        filename = '.'.join([self.report_name, self.query_type])
        query_file = os.path.join(app.config['QUERY_PATH'], filename)
        return query_file

    @abc.abstractmethod
    def result(self):
        """ Return query results as a JSON-serializable Python structure
        (generally a list of dictionaries)
        """
        return


class ResultFormatter(ABC):
    def __init__(self, result):
        self.result = result

    @abc.abstractmethod
    def format_results(self):
        """ Transform result set structure and return new structure
        """
        return


# `ResultSet` IMPLEMENTATION SUBCLASSES
class SQLResultSet(ResultSet):
    """ SQL database query implementation of ResultSet, using Records library
    to fetch a dataset from configured report_name
    """

    @property
    def query_type(self):
        return ('sql')

    query_db = records.Database(app.config['DATABASE_URL'])

    def result(self):
        try:
            rows = self.query_db.query_file(self.get_file(), **self.kwargs)
            result = rows.as_dict()
        except IOError as e:
            result = [{'error': repr(e)}, ]
        return result


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

    query_db = records.Database(app.config['DATABASE_URL'])
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


# `ResultFormatter` IMPLEMENTATION SUBCLASSES
class CompactFormatter(ResultFormatter):
    """ Returns dict in format
    {"columns": [<list of column names>], "data": [<array of row value arrays>]}
    """
    # TODO: some graceful error handling, in case of bad input format, etc.
    def format_results(self):
        raw = self.result
        columns = list(raw[0].keys())
        data = [tuple(row.values()) for row in raw]
        formatted = dict(columns=columns, data=data)
        return formatted


class AffixFormatter(ResultFormatter):
    """ Wrap default object array with error and metadata details
    """
    def format_results(self):
        if 'error' in self.result[0].keys():
            return self.result

        formatted = {}
        formatted['error'] = False
        formatted['response'] = self.result
        formatted['metadata'] = {}
        formatted['metadata']['executed'] = datetime.now().isoformat()
        formatted['metadata']['params'] = request.args.to_dict()
        return formatted


# LIL FLASK APP
class ReportAPI(Resource):
    """ Calls ResultSet.result() and returns JSON

        Given a report_name, query_type, and format_ (via URL routes), this
        Flask-RESTful Resource submits the query matching the report_name to
        the appropriate query_type subclass and optionally format results
        via the matching format_cls and let Resource do its JSON thing
    """
    # Poor man's plugin registration.
    # TODO: formalize this with `__subclasses__()` method
    # TODO: unless and until doing this dynamically with `__subclasses__()`
    #     let's move this to a separate config
    query_type_lookup = {'sql': SQLResultSet, 'takei': TakeiResultSet}
    format_lookup = {'compact': CompactFormatter, 'affix': AffixFormatter}

    def get(self, report_name, query_type='sql', format_='default'):
        # Lookup query_type and fetch result from corresponding class
        try:
            result_cls = self.query_type_lookup[query_type]
        except KeyError:
            result_cls = SQLResultSet
        loader = result_cls(report_name, **request.args.to_dict())
        query_result = loader.result()

        try:
            format_cls = self.format_lookup[format_]
            payload = format_cls(query_result).format_results()
        except KeyError:
            """ Return default serialization """
            # TODO: add logging and log a warning here
            #     and/or return format not found message to client(?)
            payload = query_result
        return payload


api.add_resource(
    ReportAPI,
    '/v1/<string:report_name>/',
    '/v1/<string:query_type>/<string:report_name>/',
    '/v1/<string:query_type>/<string:report_name>/<string:format_>/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
