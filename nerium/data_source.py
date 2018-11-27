import os

import yaml
from nerium import config


def get_data_source(query):
    """ Get data source connection metadata based on config. Prefer, in order:
        - Query file frontmatter
        - Query subdirectory name
        - db.yaml file in query subdirectory
        - DATABASE_URL in environment

    To allow for possible non-SQL sources to be contributed, we only
    return a config value here, and leave connecting to concrete
    ResultSet subclass, as required values might change, as well as
    connection method. (This is also why we return a dict, despite having
    a single value in the database case.)
    """
    # *** GET CONNECTION PARAMS: ***
    # from frontmatter
    try:
        for source in config.data_sources:
            if source['name'] == query.metadata['database']:
                return source
    except KeyError:
        pass
    try:
        return dict(url=query.metadata['database_url'])
    except KeyError:
        pass

    # from file in directory if present
    db_file = query.path.parent / 'db.yaml'
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
        for source in config.data_sources:
            if source.name == query.path.parent.name:
                return source
    except (KeyError, AttributeError):
        pass

    # Use env['DATABASE_URL']/sqlite if nothing else is configured
    return dict(
        url=os.getenv('DATABASE_URL', 'sqlite:///'))
