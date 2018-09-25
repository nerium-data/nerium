#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from abc import ABC, abstractmethod

# from . import config
import yaml
from nerium import config


# BASE CLASSES

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
                db_meta = yaml.safe_load(dbf.read())
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
        except (KeyError, AttributeError):
            pass

        # Use env['DATABASE_URL'] if nothing else is configured
        return dict(
            url=os.getenv('DATABASE_URL', '***No database configured***'))

    @property
    @abstractmethod
    def connection(self):
        """ Return data source connection object, typically from data_source() method
        """
        return

    @abstractmethod
    def result(self):
        """ Given a Query object and connection, return results as a
        serializable Python structure (generally a list of dictionaries)
        """
        return


class ResultFormatter(ABC):
    def __init__(self, result, **kwargs):
        self.result = result
        self.kwargs = kwargs

    @abstractmethod
    def format_results(self):
        """ Transform result set structure and return new structure
        """
        return
