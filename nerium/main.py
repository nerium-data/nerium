#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import os
from abc import ABC

from dotenv import find_dotenv, load_dotenv
import sqlalchemy

# Provision environment as needed
if find_dotenv():
    load_dotenv(find_dotenv())
else:
    load_dotenv('/dotenv/.env')


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

        q_path = os.getenv('QUERY_PATH', 'query_files')
        query_file = os.path.join(q_path, filename)
        return query_file

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
