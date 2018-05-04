# Nerium

![small bicycle](https://dl.dropboxusercontent.com/s/7kba2cgrcvuj0hy/nerium-bicycle-sm.jpg "Keeping the 'micro' in microservices")

[![CircleCI](https://img.shields.io/circleci/project/github/OAODEV/nerium.svg)](https://circleci.com/gh/OAODEV/nerium)
[![Codecov](https://img.shields.io/codecov/c/github/OAODEV/nerium.svg)](https://codecov.io/gh/OAODEV/nerium)
[![PyPI - Version](https://img.shields.io/pypi/v/nerium.svg)](https://pypi.org/project/nerium/)
[![PyPI - License](https://img.shields.io/pypi/l/nerium.svg)](https://pypi.org/project/nerium/)

A simple [aiohttp](https://docs.aiohttp.org/) microservice that submits queries to a database and returns machine-readable serialized results (typically JSON). By analogy with static site generators, Nerium reads its queries from local files, stored in a (configurable) directory on the filesystem. The idea is that report analysts should be able to author queries in their preferred local editor, and upload them where Nerium can use them.

OAO uses Nerium to easily and quickly provide JSON APIs with report results from our PostgreSQL data warehouse.

Nerium features an extendable architecture, allowing support for multiple query types and output formats by registering subclasses of `ResultSet` and `ResultFormatter` template classes.

Currently supports SQL queries using the excellent [Records](https://github.com/kennethreitz/records) library. In keeping with Records usage, query parameters can be specified in `key=value` format, and (_safely_!) injected into your query in `:key` format. 

In theory, `ResultSet` subclasses can be added (under `contrib/resultset`) for non-SQL query languages. This is a promising area for future development.

Default JSON output is an array of objects, one per result row, with database column names as keys. A `compact` JSON output format may also be requested, with separate `column` (array of column names) and `data` (array of row value arrays) nodes for compactness. Additional formats (not necessarily JSON) can be added by subclassing `ResultFormatter`.

In theory, Nerium can already support any backend that SQLAlchemy can, but since none of these are hard dependencies, drivers aren't included in Pipfile, and the Dockerfile only supports PostgreSQL. If you want Nerium to work with other databases, you can install Python connectors with `pip`, either in a virtualenv or by creating your own Dockerfile using `FROM oaodev/nerium`.

Nerium is inspired in roughly equal measure by [SQueaLy](https://hashedin.com/2017/04/24/squealy-intro-how-to-build-customized-dashboard/) and [Pelican](https://blog.getpelican.com/). It hopes to be something like [Superset](https://superset.incubator.apache.org/) when it grows up.

## Install/Run

### Using Docker

```bash
$ docker run -d --name=nerium \
--envfile=.env \
-v /local/path/to/query_files:/app/query_files \
-p 8080:8080 oaodev/nerium

$ curl http://localhost:8081/v1/<query_name>?<params>
```

### Local install

```bash
pipenv install nerium[pg]
```

Then add a `query_files` directory to your project, write your queries, and configure the app as described in the next section. The command `nerium` starts a local `aiohttp` server running the app, listening on port 8080.

## Configuration

`DATABASE_URL` and optional `QUERY_PATH` (directory where query files reside, defaults to `query_files` in the working direcory) may be set in the environment, or in a local `.env` file.

In order to query multiple databases with a single instance of Nerium, create a subdirectory for each database under the `$QUERY_PATH`, place the related files under their respective directory, and include a separate `.env` file per subdirectory setting its `DATABASE_URL` value.

## API

### URLs

`/v1/<string:query_name>/?[ne_format=<formatter>]&<query_params>`

`query_name` should match the name of a given query script file, minus the file extension. Params are as specified in the queries themselves.

`ne_format` may be passed as in the query string as an optional formatter name, and defaults to 'default'. Other supported `contrib` options are described in Content section below.

Unknown values passed to `query_extension` or `format` will silently fall back to defaults.

### Method

`GET`

### Success Response

**Code**: 200

**Content**:  
'default': `[{<column_name>:<row_value>, etc..., }, {etc...}, ]`  
'compact': `{"columns": [<list of column names>], "data": [<array of row value arrays>]}`  
'affix': `{"error": false, "response": {<'default' array of result objects>}, "metadata":{"executed": <timestamp>, "params": {<array of name-value pairs submitted to query with request>}}}`

Of course, it is possible that a database query might return no results. In this case, Nerium will respond with and empty JSON array `[]` regardless of specified format. This is not considered an error, and clients should be prepared to handle it appropriately.

### Error Responses

**Code**: 400
**Content**: `{"error": <exception.repr from Python>}`

## Sketchy Roadmap/TODOs

(in no particular order)

- Parameter discovery endpoint
- Report listing endpoint
- ~~Plugin architecture~~
- Improve/mature plugin architecture
    - ~~Separate base classes to a library~~
    - ~~Implementation subclasses in `contrib` package~~
    - Subclass registration mechanism
- Configurable/flexible JSON output formatters (`AffixFormatter` could do with less hard-coding)
- Static output file generator (and other caching)
- Swagger docs
- ~~Health check/default query endpoint~~ (Own git commit hash report(?))
