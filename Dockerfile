FROM alpine
# Install python3
# Not using python:3-alpine to avoid
#   psycopg2 starting a separate python3 install
RUN apk add --no-cache python3 py3-psycopg2

# Copy in the code
COPY *.py /app/
COPY nerium/ /app/nerium/

WORKDIR /app
RUN pip3 install -e .
VOLUME /app/query_files
EXPOSE 8080

CMD nerium