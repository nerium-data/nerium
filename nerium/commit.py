import requests
from nerium import __version__
from git import Repo
from pathlib import Path


def get_local_head_commit():
    workdir = Path(__file__).resolve().parents[1]
    repo = Repo(workdir)
    commit = repo.head.commit.hexsha
    return commit


def get_commit_for_version(version=__version__):
    v = f"v{version}"

    try:
        resp = requests.get("https://api.github.com/repos/OAODEV/nerium/tags")
        tags = resp.json()
        vtag = list(filter(lambda t: v == t["name"], tags))
        vtag = vtag[0]
        commit_url = vtag["commit"]["url"]
        resp = requests.get(commit_url)
        commit = resp.json()["url"]
    except (
        IndexError,
        KeyError,
        TypeError,
        requests.exceptions.ConnectionError,
        ValueError,
    ):
        commit = get_local_head_commit()
    return commit


if __name__ == "__main__":
    commit = get_commit_for_version()
    print(commit)
