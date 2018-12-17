FROM alpine:3.8
LABEL maintainer='thomas.yager-madden@adops.com'
# Install python3
# Not using python:3-alpine to avoid
#   psycopg2 starting a separate python3 install
ENV PORT 5000
RUN apk add --no-cache python3 py3-psycopg2 python3-dev build-base git
# Copy in the code
COPY . /app

WORKDIR /app

# install from code currently in repo
RUN pip3 install --upgrade pip pipenv \
    && pipenv install --system
VOLUME /app/query_files
VOLUME /app/format_files
EXPOSE 5000 

CMD nerium
