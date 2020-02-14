FROM alpine:3.10
LABEL maintainer='thomas@yager-madden.com'

# Install python3 and alpine packages for psycopg2 and gevent
RUN apk add --no-cache python3 py3-psycopg2 py3-gevent git

# Copy in the code
COPY . /app

WORKDIR /app

# install from code currently in repo
RUN pip3 install flask gunicorn==19.9.0
RUN python3 setup.py install


VOLUME /app/query_files
VOLUME /app/format_files
EXPOSE 5000 

CMD gunicorn -c gunicorn_conf.py nerium.app:app
