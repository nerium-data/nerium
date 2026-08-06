FROM python:3.11-bullseye
LABEL maintainer='Thomas Yager-Madden <thomas@yager-madden.com>'

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# install git to support Nerium commit endpoint
RUN apt-get update && apt-get install -y git
# Copy in the code
COPY . /app

WORKDIR /app

# install from locked dependencies, including gunicorn/gevent server and
# psycopg2 Postgres database driver
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/usr/local
RUN uv sync --locked --no-dev --extra serve --extra pg-binary

VOLUME /app/query_files
VOLUME /app/format_files
EXPOSE 5000

CMD gunicorn -c gunicorn_conf.py nerium.app:app
