# TODO

Deferred items, mostly noticed in passing during the 0.15.0 release work.
Nothing here is urgent; none of it blocks a release.

## Dependencies

- [ ] **Drop `requests`.** Nothing imports it any more. It existed for the
  version-to-commit lookup that went away when `/` started reporting a
  baked-in `$GIT_COMMIT` build arg. Same situation `gitpython` was in.

## Docker image

- [ ] **Move to a slim base image.** `python:3.11-bullseye` is roughly 350MB
  compressed per architecture; `python:3.11-slim-bookworm` is closer to 45MB.
  Nothing obviously needs the full image now that the `git` install is gone —
  `psycopg[binary]` bundles its own libpq and `gevent` ships wheels. The
  Dockerfile was on slim as of v0.9.0 and drifted back at some point. This
  matters most when pushing multi-arch over a slow connection.
- [ ] **Add `.git` to `.dockerignore`.** ~1.5MB of history gets copied into
  the image by `COPY . /app`. It was arguably justified while the commit
  lookup read local git; it isn't now.
- [ ] **Fix the last line of `.dockerignore`.** It reads `.coverage*htmlcov/`
  — a missing newline joined two patterns into one that matches nothing, so
  `.coverage` and `htmlcov/` are both still copied in.
- [ ] **Use JSON array form for `CMD`.** buildx emits
  `JSONArgsRecommended`; the shell form doesn't forward OS signals to
  gunicorn, which matters for clean container shutdown.
- [ ] **Keep publishing multi-arch.** `v0.15.0` is the first `linux/arm64`
  image; everything before it was amd64-only. Worth making routine rather
  than remembering to pass `--platform`.

## Code

- [ ] **Resolve the `nerium.commit` name shadowing.** `nerium/__init__.py`
  does `commit = get_commit()`, which rebinds the name over the
  `nerium.commit` submodule — so `from nerium import commit` yields a string,
  not the module. Tests import `get_commit` directly to sidestep it. Renaming
  either the attribute or the module would clear it up.

## Docs

- [ ] **`.env` is documented but never loaded.** The README says config can
  live in "a local `.env` file", and `.env.example` implies the same, but
  nothing reads one: `python-dotenv` isn't a dependency and nothing imports
  it, so `flask run` silently ignores `.env`. (Docker is unaffected — it uses
  `--envfile`.)

  Resolution: docs, not code. Revise the `### Local install` section to show
  sourcing the file before starting the dev server, which is how this is
  handled in practice:

  ```sh
  set -a; source .env; set +a
  ```

  No `python-dotenv` dependency needed.

## Upstream, in sqla-raw

- [ ] **An empty `QUERY_PATH` globs the working directory.**
  `list_queries()` uses `os.getenv("QUERY_PATH", "query_files")`, and
  `os.getenv` only falls back when the variable is *absent*. `QUERY_PATH=`
  returns `""`, `Path("")` is `.`, and the recursive `**/*.sql` then sweeps
  up every query below the cwd — test fixtures included. `os.getenv(...) or
  "query_files"` would fix it.
- [ ] **Flattened subdirectories can collide.** Queries are matched on
  filename stem, so `a/summary.sql` and `b/summary.sql` both answer to
  `/v1/summary`, decided by glob order. There's already a `# TODO: Warn if
  more than one match` at that spot.

## Release housekeeping

- [ ] **Re-check Dependabot alerts.** There were 92 on `main` (26 high)
  before the dependency upgrade; confirm how many actually cleared.
- [ ] **Decide what CI does with coverage.** It still runs under `coverage`
  and stores `.coverage` as a build artifact, but nothing consumes that now
  that Codecov is gone. Either keep it as an on-demand artifact or simplify
  to plain `pytest`.
- [ ] **Note the PyPI version gap.** 0.14.0 was never published, so 0.15.0
  follows 0.13.2 on PyPI.
