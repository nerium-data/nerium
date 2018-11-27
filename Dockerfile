FROM alpine:3.8
LABEL maintainer='thomas.yager-madden@adops.com'
# Install python3
# Not using python:3-alpine to avoid
#   psycopg2 starting a separate python3 install
RUN apk add --no-cache python3 py3-psycopg2
# Copy in the code
COPY . /app

WORKDIR /app

# install from code currently in repo
RUN pip3 install --upgrade pip \
    && pip3 install -e .
VOLUME /app/query_files
EXPOSE 8080

CMD nerium
