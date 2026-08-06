# Welcome

Thank you very kindly for your interest in Nerium! We would love to get pull requests from everyone to help this project along. 🙂

## Getting set up

Nerium uses [`uv`](https://docs.astral.sh/uv/). `uv sync` will install the
pinned dependencies (including test tools) into `.venv`; run commands with
`uv run`, e.g. `uv run pytest`. Add or change a dependency with
`uv add`/`uv remove` rather than editing `pyproject.toml` by hand, and commit
the resulting `uv.lock`.

Releases are cut with `uv build && uv publish`, after bumping
`nerium/__version__.py` and tagging the commit `v<version>`.

## Guidelines

With a few exceptions we generally use [`black`](https://pypi.org/project/black/) and [`isort`](https://pypi.org/project/isort/) to format our Python code, and in any case expect/prefer things to pass [`flake8`](https://pypi.org/project/flake8/) linting.

Tests are good, and any pull requests will be expected to include them.

Thanks again for your consideration.
