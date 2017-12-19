#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import os
from abc import ABC

import records
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request
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
            result = [{'Error': e, }, ]
        return result


class ResultFormatter(ABC):
    def __init__(self, result):
        self.result = result

    @abc.abstractmethod
    def format_results(self):
        """ Transform result set structure and return new structure
        """
        return


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


class ReportAPI(Resource):
    """ Calls ResultSet.result() and returns JSON
    """
    # Poor man's plugin registration.
    # TODO: formalize this with `__subclasses__()` method
    query_type_lookup = {'sql': SQLResultSet, }
    format_lookup = {'compact': CompactFormatter, }

    def get(self, report_name, query_type='sql', format='default'):
        # Lookup query_type and fetch result from corresponding class
        try:
            result_cls = self.query_type_lookup[query_type]
        except KeyError:
            result_cls = SQLResultSet
        loader = result_cls(report_name, **request.args.to_dict())
        query_result = loader.result()

        try:
            format_cls = self.format_lookup[format]
            payload = format_cls(query_result).format_results()
        except KeyError:
            # TODO: add logging and log a warning here
            #     and/or return format not found message to client(?)
            payload = query_result
        return payload


api.add_resource(
    ReportAPI,
    '/v1/<string:report_name>/',
    '/v1/<string:query_type>/<string:report_name>/',
    '/v1/<string:query_type>/<string:report_name>/<string:format>/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
