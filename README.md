# Nerium

A simple [Flask](http://flask.pocoo.org/) service that submits queries to a database and returns machine-readable serialized results. By analogy with static site generators, Nerium reads its queries from local files, stored in a configurable directory on the filesystem.

Nerium features an extensible architecture, allowing support for multiple query types and output formats by registering subclasses of `ResultSet` and `ResultFormatter` template classes.

Currently supports SQL queries via [Records](https://github.com/kennethreitz/records). In keeping with Records usage, query parameters can be specified in `key=value` format, and (_safely_!) injected into your query in `:key` format.

Default JSON output is an array of objects, one per result row, with database column names as keys. A `compact` JSON output format may also be requested, with separate `column` (array of column names) and `data` (array of row value arrays) nodes for compactness.

Docker image may be specified to include Python driver for Postgres or MySQL with `--build-arg db_driver=[ postgres | mysql ]` at build time.

Nerium is inspired in roughly equal measure by [SQueaLy](https://hashedin.com/2017/04/24/squealy-intro-how-to-build-customized-dashboard/) and [Pelican](https://blog.getpelican.com/). It hopes to be something like [Superset](https://superset.incubator.apache.org/) when it grows up.

## Install/Run

```
$ docker build --rm [ --build-arg db_driver={ postgres | mysql } ] -t nerium .

$ docker run -d --name=nerium_svc \
--envfile=.env \
-v /local/path/to/query_files:/app/query_files \
-p 8081:8081 nerium

$ curl http://localhost:8081/<report_name>?<params>
```

## Configuration

`DATABASE_URL` and `SQL_PATH` (directory where SQL files reside) may be set in the environment, or in a local `.env` file.

## API

### URLs

`/v1/<string:report_name>/?<params>`
`/v1/<string:query_type>/<string:report_name>/?<params>`
`/v1/sql/<string:report_name>/<string:format>/?<params>`
`/v1/sql/<string:report_name>/compact/?<params>`

`report_name` should match the name of a given SQL file, minus the `.sql` extension. Params are as specified in the queries themselves.

`query_type` is an optional file extension string and defaults to 'sql'
`format` is an optional formatter name, and defaults to 'default'. 'compact' is also available, as noted above. (Note that while optional, if you wish to specify a format, you must include the query_type also.)

Unknown values passed to `query_type` or `format` will silently fall back to defaults.

### Method

`GET`

### Success Response

**Code**: 200

**Content**:
'default': `[{<column_name>:<row_value>, etc..., }, {etc...}, ]`  
'compact': `{"columns": [<list of column names>], "data": [<array of row value arrays>]}`

## Sketchy Roadmap/TODOs

(in no particular order)
- Parameter discovery endpoint
- Report listing endpoint
- ~~Plugin architecture~~
- Improve/mature plugin architecture
- Configurable JSON output formatters
- More data visualization formats, semantic tagging in table template; move template/viz logic to separate client app
- Static output file generator (another client app)
- Swagger docs
- Health check/default query endpoint
