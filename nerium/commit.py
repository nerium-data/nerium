import requests
from requests.exceptions import ConnectionError

from .version import __version__


def get_commit_for_version(version=__version__):
    v = f'v{version}'

    try:
        resp = requests.get('https://api.github.com/repos/OAODEV/nerium/tags')
        tags = resp.json()
        vtag = list(filter(lambda t: v == t['name'], tags))
        vtag = vtag[0]
        commit_url = vtag['commit']['url']
        resp = requests.get(commit_url)
        commit = resp.json()['url']
    except (IndexError, KeyError, TypeError, ConnectionError, ValueError):
        commit = 'Not found'
    return commit


if __name__ == "__main__":
    commit = get_commit_for_version()
    print(commit)
