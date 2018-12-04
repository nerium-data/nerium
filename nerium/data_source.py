import os

import yaml


def get_data_source(query):
    """ Get data source connection metadata based on config. Prefer, in order:
        - Query file frontmatter
        - `db.yaml` file in query subdirectory
        - DATABASE_URL in environment

    To allow for possible non-SQL sources to be contributed, we only
    return a config value here, and leave connecting to concrete
    resultset module, as required values and connection method might change.
    (This is also why we return a dict, despite having a single value in the
    SQL case.)
    """
    # *** GET CONNECTION PARAMS: ***
    # from frontmatter
    try:
        return query.metadata['data_source']
    except KeyError:
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
                return db_meta['data_source']
            except KeyError:
                try:
                    return dict(url=db_meta['database_url'])
                except KeyError:
                    pass

    # Use env['DATABASE_URL']/sqlite if nothing else is configured
    return dict(
        url=os.getenv('DATABASE_URL', 'sqlite:///'))
