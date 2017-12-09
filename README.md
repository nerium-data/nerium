# Nerium

A simple service using [Flask](http://flask.pocoo.org/) and [Records](https://github.com/kennethreitz/records) to submit queries to a database and get results as JSON or bare HTML tables. Sources queries from local files, stored in a configurable directory on the filesystem. In keeping with Records usage, query parameters can be specified in `key=value` format, and (_safely_!) injected into your query in `:key` format.

Docker image may be specified to include Python driver for Postgres or MySQL with `--build-arg db_driver=[ postgres | mysql ]` at build time.

Inspired in roughly equal measure by [SQueaLy](https://hashedin.com/2017/04/24/squealy-intro-how-to-build-customized-dashboard/) and [Pelican](https://blog.getpelican.com/).

## Install/Run

```
$ docker build --rm [ --build-arg db_driver={ postgres | mysql } ] -t nerium .

$ docker run -d --name=nerium_svc \
--envfile=.env \
-v /local/path/to/sqls:/sqls \
-p 8081:8081 nerium

$ curl http://localhost:8081/<report_name>?<params>
```

## Configuration

`DATABASE_URL` and `SQL_PATH` (directory where SQL files reside) may be set in the environment, or in a local `.env` file.

## API

### URL

`/<string:report_name>?<params>` or `/report/<string:report_name>?<params>`

HTML table representation of report at `/table/<string:report_name>?<params>`

`report_name` should match the name of a given SQL file, minus the `.sql` extension. Params are as specified in the queries themselves.

### Method

`GET`

### Success Response

**Code**: 201

**Content**: `{"columns": [<list of column names>], "data": [<array of rows as arrays>]}`

## Sketchy Roadmap/TODOs

- Parameter discovery endpoint
- Static output file generator
- Fuller semantic tagging in table template
- JWT authentication
- Granular permissions settings
- Swagger docs for endpoints
- Health check/default query endpoint
