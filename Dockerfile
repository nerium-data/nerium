FROM alpine
# Install python3 & pipenv
# Not using python:3-alpine to avoid installing separarate python3
#   for psycopg2 install
# Symlinking python3 to /bin/python helps pipenv find it below
RUN apk add --no-cache python3 py3-psycopg2 py3-gevent\
    && ln -s /usr/bin/python3 /bin/python
RUN set -ex && pip3 install pipenv --upgrade

# Copy in the code
COPY *.py /app/
COPY nerium/ /app/nerium/
COPY Pipfile* /app/
WORKDIR /app
RUN pipenv install --system
VOLUME /app/query_files
# Install requirements (includes local setup.py)

CMD gunicorn -c gunicorn-conf.py app:app 
