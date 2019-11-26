FROM alpine:3.10
LABEL maintainer='yagermadden@gmail.com'

# Install python3
# Not using python:3-alpine to avoid
#   psycopg2 starting a separate python3 install'
RUN apk add --no-cache git python3 py3-psycopg2 py3-gevent

# Copy in the code
COPY . /app

WORKDIR /app

# install from code currently in repo
RUN python3 setup.py install
RUN pip3 install gunicorn==19.9.0

VOLUME /app/query_files
VOLUME /app/format_files
EXPOSE 5000 

CMD gunicorn -c gunicorn_conf.py nerium.app:app
