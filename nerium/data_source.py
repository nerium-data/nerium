import os


def get_data_source(query):
    """ Get data source connection metadata based on config. Prefer, in order:
        - Query file frontmatter
        - DATABASE_URL in environment
    """
    # from frontmatter
    if "database_url" in query.metadata.keys():
        return query.metadata["database_url"]

    # Default to $DATABASE_URL with sqlite fallback if not set in frontmatter
    return os.getenv("DATABASE_URL", "sqlite:///")
