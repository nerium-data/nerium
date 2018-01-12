# build gcsfuse for alpine
FROM golang:1-alpine as gcsfuse-build
RUN apk add --no-cache git
RUN go get github.com/googlecloudplatform/gcsfuse
RUN chmod +x /go/bin/gcsfuse


FROM alpine:3.6
# Install python3 & pipenv
# Not using python:3-alpine to avoid installing separarate python3
#   for psycopg2 install
# Symlinking python3 to /bin/python helps pipenv find it below
RUN apk add --no-cache python3 fuse\
    && ln -s /usr/bin/python3 /bin/python
RUN set -ex && pip3 install pipenv --upgrade

# Copy in the code
COPY *.py /app/
COPY Pipfile /app/
WORKDIR /app
VOLUME /app/query_files
# Install requirements
COPY --from=gcsfuse-build  /go/bin/gcsfuse /usr/local/bin/
RUN pipenv install --system


apk add --no-cache py3-psycopg2
pipenv install --system pymysql

CMD gunicorn -b 0.0.0.0:8081 app:app --log-file=-
