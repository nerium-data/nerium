#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import os
from abc import ABC
from importlib import import_module
from pathlib import Path

from dotenv import load_dotenv

# Provision environment as needed
# Load local .env first
load_dotenv(Path.cwd() / '.env')
# Load this one for use w/ Kubernetes secret mount
load_dotenv('/dotenv/.env')

# BASE CLASSES


class QueryRegistry():
    """ Creates a list of dictionaries, mapping query_name to file_system path,
    file extension, and ResultSet subclass that should be used for query
    submission.

    Holds Context invoked by Query class to choose a concrete ResultSet
    subclass to get results from.

    Provides a get_query method to retrieve path and result_cls attributes
    from a query_name
    """

    # TODO: Provide for registration from frontmatter or direct config

    def __init__(self):
        pass

    def lookup_extension(self, _key):
        # TODO: Define in external config file
        query_extension_lookup = {
            'sql': 'SQLResultSet',
        }
        try:
            return query_extension_lookup[_key]
        except KeyError:
            return 'SQLResultSet'

    def register_paths(self):
        query_directory = Path(os.getenv('QUERY_PATH', 'query_files'))
        flat_directory = list(query_directory.glob('**/*'))
        registry = [
            dict(
                query_name=i.stem,
                query_path=i,
                result_cls=self.lookup_extension(i.suffix))
            for i in flat_directory if i.is_file()
        ]
        return registry

    def get_query(self, query_name):
        try:
            query = next(
                i for i in self.register_paths()
                if query_name == i['query_name'])
            return query
        except StopIteration:
            return None


class Query():
    """ Finds query in registry, and looks up ResultSet subclass from
    path file extension. Submits query_path to ResultSet and returns results
    """

    def __init__(self, query_name, **kwargs):
        self.query_name = query_name
        self.kwargs = kwargs

    def result_set(self):
        registry = QueryRegistry()
        query = registry.get_query(self.query_name)
        if not query:
            return [{
                'error':
                "No query found matching {}".format(self.query_name)
            }]
        else:
            query_path = query['query_path']
            result_mods = import_module('nerium.contrib.resultset')
            result_cls = getattr(result_mods, query['result_cls'])
            loader = result_cls(query_path, **self.kwargs)
            query_result = loader.result()
            return query_result


class ResultSet(ABC):
    """Generic result set class template.

    Loads data source and fetches results by submitting query to data source
    with expected parameters.


    Args:
        query_path (path-like object): Path to query file
        kwargs: Parameter keys and values to bind to query

    Usage:
        Subclass and provide a 'result' method
    """

    def __init__(self, query_path, **kwargs):
        self.query_path = query_path
        self.kwargs = kwargs

    @abc.abstractmethod
    def result(self):
        """ Given a query_path, return results as a serializable Python structure
        (generally a list of dictionaries)
        """
        return


class ResultFormat(ABC):
    def __init__(self, result, format_, **kwargs):
        self.result = result
        self.format_ = format_
        self.kwargs = kwargs

    def formatted_results(self):
        format_lookup = {
            'affix': 'AffixFormatter',
            'compact': 'CompactFormatter',
            'csv': 'CsvFormatter',
            'default': 'DefaultFormatter',
        }
        format_cls_name = format_lookup[self.format_]
        format_mods = import_module('nerium.contrib.formatter')
        format_cls = getattr(format_mods, format_cls_name)
        return format_cls(self.result, **self.kwargs).format_results()


class ResultFormatter(ABC):
    def __init__(self, result, **kwargs):
        self.result = result
        self.kwargs = kwargs

    @abc.abstractmethod
    def format_results(self):
        """ Transform result set structure and return new structure
        """
        return
