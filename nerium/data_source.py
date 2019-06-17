import os


def get_data_source(query):
    """ Get data source connection metadata based on config. Prefer, in order:
        - Query file frontmatter
        - DATABASE_URL in environment
    """
    # from frontmatter
    # TODO: try `database_url` key first, return as string if present
    # TODO: factor out try/except block
    try:
        return query.metadata["database_url"]
    except KeyError:
        pass

    # Use env['DATABASE_URL']/sqlite if not set in frontmatter
    return os.getenv("DATABASE_URL", "sqlite:///")
