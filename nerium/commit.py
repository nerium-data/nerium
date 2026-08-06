import os

UNKNOWN = "unknown"


def get_commit():
    """Return the git SHA of the running code, per `$GIT_COMMIT`

    The Dockerfile accepts the SHA as a build argument and bakes it into the
    image, so a deployed instance can report exactly what it is running. When
    the variable isn't set — a local checkout, say — there is nothing to
    report and the caller gets "unknown".
    """
    return os.getenv("GIT_COMMIT") or UNKNOWN
