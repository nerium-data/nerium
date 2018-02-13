#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import os
from abc import ABC
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

# Provision environment as needed
if find_dotenv():
    load_dotenv(find_dotenv())
else:
    load_dotenv('/dotenv/.env')


# BASE CLASSES
class ResultSet(ABC):
    """Generic result set class template.

    Loads data source and fetches results by submitting query to data source
    with expected parameters.


    Args:
        report_name (str): Name of chosen query file, without the extension
        kwargs: Parameter keys and values to bind to query

    Usage:
        Subclass and provide a 'result' method
    """

    def __init__(self, report_name, **kwargs):
        self.report_name = report_name
        self.kwargs = kwargs

    def get_query_path(self):
        query_directory = Path(os.getenv('QUERY_PATH', 'query_files'))
        flat_directory = list(query_directory.glob('**/*'))
        files = [i for i in flat_directory if i.is_file()]
        try:
            query_path = next(
                i for i in sorted(files) if i.stem == self.report_name)
            return query_path
        except StopIteration:
            return None

    def result_set(self):
        """ if your functionResultSet subclass needs no script,
            simply return self.result() here.
        """
        if not self.get_query_path():
            return [
                {
                    'error': "No query found matching {}".format(
                        self.report_name)
                },
            ]
        else:
            return self.result()

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
