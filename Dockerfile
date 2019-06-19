FROM alpine:3.8
LABEL maintainer='yagermadden@gmail.com'

ENV PORT 5000
# Install python3
# Not using python:3-alpine to avoid
#   psycopg2 starting a separate python3 install'
RUN apk add --no-cache python3 py3-psycopg2 py3-gevent

# Copy in the code
COPY . /app

WORKDIR /app

# install from code currently in repo
RUN pip3 install --upgrade gunicorn pipenv \
    && pipenv install --system

VOLUME /app/query_files
VOLUME /app/format_files
EXPOSE 5000 

CMD gunicorn -c gunicorn_conf.py nerium.app:app
