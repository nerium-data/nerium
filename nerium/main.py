#!/usr/bin/env python
# -*- coding: utf-8 -*-
import abc
import os
from abc import ABC
from importlib import import_module
from pathlib import Path

# from . import config
import frontmatter
import yaml
from nerium import config, utils

# BASE CLASSES


# TODO: Refactor Query, Registry and Broker classes to a single Query class
#     : supporting all methods (or a more function-based module).
class Query():
    def __init__(self, name, metadata, path, result_cls, body):
        self.name = name
        self.metadata = metadata
        self.path = path
        self.result_cls = result_cls
        self.body = body

    def __str__(self):
        return self.body

    def __repr__(self):
        return 'nerium.Query ({})'.format(self.name)


class QueryRegistry():
    """ Creates a list of dictionaries, mapping query_name to file_system path,
    file extension, and ResultSet subclass that should be used for query
    submission.

    Holds Context invoked by Query class to choose a concrete ResultSet
    subclass to get results from.

    Provides a get_query method to retrieve Query object with path, metadata,
    and result_cls attributes from a query_name
    """

    # TODO: Provide for registration from frontmatter or direct config

    def __init__(self):
        pass

    def get_query(self, query_name):
        try:
            query = next(i for i in utils.register_paths()
                         if query_name == i['query_name'])
        except StopIteration:
            return None
        with open(query['query_path']) as f:
            metadata, query_body = frontmatter.parse(f.read())
        parsed_query = Query(
            name=query_name,
            metadata=metadata,
            path=query['query_path'],
            result_cls=query['result_cls'],
            body=query_body,
        )
        return parsed_query


class QueryBroker():
    """ Finds Query in registry by name, and looks up ResultSet subclass from
    path file extension. Submits Query to ResultSet and returns results
    """
    registry = QueryRegistry()

    def __init__(self, query_name, **kwargs):
        self.query_name = query_name
        self.kwargs = kwargs

    def result_set(self):
        query = self.registry.get_query(self.query_name)
        if not query:
            return [{
                'error':
                "No query found matching {}".format(self.query_name)
            }]
        else:
            result_mods = import_module('nerium.contrib.resultset')
            cls_name = query.result_cls
            result_cls = getattr(result_mods, cls_name)
            loader = result_cls(query, **self.kwargs)
            query_result = loader.result()
            return dict(metadata=query.metadata, data=query_result)


class ResultSet(ABC):
    """Generic result set class template.

    Loads data source and fetches results by submitting query to data source
    with expected bind parameters.


    Args:
        query: nerium.Query object fetched from registry by broker
        kwargs: Parameter keys and values to bind to query

    Usage:
        Subclass and provide a 'connection' property 'result' method
    """

    def __init__(self, query, **kwargs):
        self.query = query
        self.kwargs = kwargs

    def data_source(self):
        """ Get data source connection metadata based on config. Prefer, in order:
            - Query file frontmatter
            - Query subdirectory name
            - db.yaml file in query subdirectory
            - DATABASE_URL in environment

        To allow for possible non-SQL sources to be contributed, we only
        return a config value here, and leave connecting to concrete
        ResultSet subclass, as required values might change, as well as
        connection method
        """
        # *** GET CONNECTION PARAMS: ***
        # from frontmatter
        try:
            for db in config.databases:
                if db['name'] == self.query.metadata['database']:
                    return db
        except KeyError:
            pass
        try:
            return dict(url=self.query.metadata['database_url'])
        except KeyError:
            pass

        # from file in directory if present
        db_file = self.query.path.parent / 'db.yaml'
        if db_file.is_file():
            with open(db_file, 'r') as dbf:
                db_meta = yaml.load(dbf.read())
                try:
                    return db_meta['database']
                except KeyError:
                    try:
                        return dict(url=db_meta['database_url'])
                    except KeyError:
                        pass

        # from config match to subdirectory
        try:
            for db in config.databases:
                if db.name == self.query.path.parent.name:
                    return db
        except KeyError:
            pass

        # Use env['DATABASE_URL'] if nothing else is configured
        return dict(
                url=os.getenv('DATABASE_URL', '***No database configured***'))

    @property
    @abc.abstractmethod
    def connection(self):
        """ Return data source connection object, typically from data_source() method
        """
        return

    @abc.abstractmethod
    def result(self):
        """ Given a Query object and connection, return results as a
        serializable Python structure (generally a list of dictionaries)
        """
        return


class ResultFormat(ABC):
    def __init__(self, result, format_, **kwargs):
        self.result = result
        self.format_ = format_
        self.kwargs = kwargs

    def formatted_results(self):
        try:
            format_cls_name = config.formats[self.format_]
        except KeyError:
            format_cls_name = 'DefaultFormatter'
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
