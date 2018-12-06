FROM alpine:3.8
LABEL maintainer='thomas.yager-madden@adops.com'
# Install python3
# Not using python:3-alpine to avoid
#   psycopg2 starting a separate python3 install
ENV PORT 5000
RUN apk add --no-cache python3 py3-psycopg2 python3-dev build-base
# Copy in the code
COPY . /app

WORKDIR /app

# install from code currently in repo
RUN pip3 install --upgrade pip \
    && pip3 install --pre -e .

# responder is installing the wrong starlette
# TODO: Take this out when responder deps are sorted
RUN pip3 uninstall -y starlette && pip3 install 'starlette<0.9'

VOLUME /app/query_files
VOLUME /app/format_files
EXPOSE 5000 

CMD nerium
