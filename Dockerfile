FROM python:3.15-slim-trixie
LABEL maintainer='Thomas Yager-Madden <thomas@yager-madden.com>'

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Bake the commit being built into the image, so a running instance can
# report it at `/`. Pass with `--build-arg GIT_COMMIT=$(git rev-parse HEAD)`.
ARG GIT_COMMIT=""
ENV GIT_COMMIT=${GIT_COMMIT}

# Copy in the code
COPY . /app

WORKDIR /app

# install from locked dependencies, including gunicorn/gevent server and
# psycopg Postgres database driver, into the base image's own interpreter
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/usr/local \
    UV_PYTHON_DOWNLOADS=never
RUN uv sync --locked --no-dev --extra serve --extra pg-binary

VOLUME /app/query_files
VOLUME /app/format_files
EXPOSE 5000

CMD ["gunicorn", "-c", "gunicorn_conf.py", "nerium.app:app"]
