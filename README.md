# Nerium

![small bicycle](https://dl.dropboxusercontent.com/s/7kba2cgrcvuj0hy/nerium-bicycle-sm.jpg "Keeping the 'micro' in microservices")

[![CircleCI](https://img.shields.io/circleci/project/github/OAODEV/nerium.svg)](https://circleci.com/gh/OAODEV/nerium)
[![Codecov](https://img.shields.io/codecov/c/github/OAODEV/nerium.svg)](https://codecov.io/gh/OAODEV/nerium)
[![PyPI - Version](https://img.shields.io/pypi/v/nerium.svg)](https://pypi.org/project/nerium/)
[![PyPI - License](https://img.shields.io/pypi/l/nerium.svg)](https://pypi.org/project/nerium/)
[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/OAODEV/nerium)


A simple [aiohttp](https://docs.aiohttp.org/) microservice that submits queries to a database and returns machine-readable serialized results (typically JSON). By analogy with static site generators, Nerium reads its queries from local files, stored in a (configurable) directory on the filesystem. The idea is that report analysts should be able to author queries in their preferred local editor, and upload or mount them where Nerium can use them.

OAO uses Nerium to easily and quickly provide JSON APIs with report results from our PostgreSQL data warehouse.

Nerium features an extendable architecture, allowing support for multiple query types and output formats.

Currently supports SQL queries using the excellent [Records](https://github.com/kennethreitz/records) library. In keeping with Records usage, query parameters can be specified in `key=value` format, and (_safely_!) injected into your query in `:key` format. 

In theory, other query types can be added (under `nerium/resultset`) for non-SQL query languages. This is a promising area for future development.

Default JSON output is an array of objects, one per result row, with database column names as keys. A `compact` JSON output format may also be requested, with separate `column` (array of column names) and `data` (array of row value arrays) nodes for compactness. Additional formats (not necessarily JSON) can be added with new plugin modules under `nerium/formatter`.

Nerium supports any backend that SQLAlchemy can, but since none of these are hard dependencies, drivers aren't included in Pipfile, and the Dockerfile only supports PostgreSQL. If you want Nerium to work with other databases, you can install Python connectors with `pip`, either in a virtualenv or by creating your own Dockerfile using `FROM oaodev/nerium`. (To ease installation, options for `nerium[mysql]` and `nerium[pg]` are provided in `setup.py`)

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

`DATABASE_URL` and optional `QUERY_PATH` (directory where query files reside, defaults to `query_files` in the working directory) may be set in the environment, or in a local `.env` file. This is the simplest configuration option.

In order to query multiple databases with a single instance of Nerium, create a subdirectory for each database under the `$QUERY_PATH`, place the related files under their respective directory, and include a separate `db.yaml` file per subdirectory, which may define a `database` or `database_url` key. (The method of naming the subdirectories to match database names still works for now, but should be considered deprecated.)

Separate database connections can also be specified directly in individual query files, by defining a `database` or `database_url` key in the YAML front matter (see below).

## Query files and front matter

As indicated above, queries are simply text files placed in local `query_files` directory, or an other arbitrary file system location specified by `QUERY_PATH` in the environment.

Query files can optionally include a [YAML](http://yaml.org/) front matter block. The front matter goes at the top of the file, set off by triple-dashed lines, as in this example:

```yaml
---
Author: Joelle van Dyne
Description: Returns all active usernames in the system
---
```

At present, the Nerium service doesn't do much with the front matter. As noted, it can be used to specify a database connection for the query. For other keys, the default response format simply passes the keys and values along in a `metadata` object. (All other current formatters simply ignore the metadata.) This mechanism can theoretically be used to pass relevant information about the query along to any clients of the service: for example, the data types of the columns in the results or what have you. Possibilities include whatever a reporting service and front end developer want to coordinate on. Front matter could also be used in more detailed ways in formatters yet to be devised.

## Plugin Architecture

As of v0.3, Nerium no longer includes `ResultSet` and `ResultFormatter` abstract base classes, nor a `contrib` package, as the project has been refactored to use a more functional style. Additional (non-SQL) query types and formats can still be added, by putting new modules under `nerium/resultset` and `nerium/formatter`, respectively.

### `resultset`

A `resultset` module is expected to have a `result` method that takes a `query` object and optional keyword argument (`kwargs`) dictionary, connects to a data source, and returns tabular results as a serializable Python structure (most typically a list of dictionaries). A Nerium `query` object is a [munchified](TK) dictionary, with elements found in [`get_query()`](TK).  Query files to be passed to this module should be named with a file extension that matches the module name (for example, `foo.sql` will be handed to the `resultset/sql.py` module).

### `formatter`

A `formatter` module requires a `format_results` method that takes a `result` object, rearranges or supplements the original structure as desired, and returns the new structure for serialization to the web service output. Formatter objects are invoked at runtime by passing a `ne_format` parameter to the Nerium URL, which should match the name of the formatter module (see API below).

## API

### URLs

`/v1/<string:query_name>/?[ne_format=<formatter>]&<query_params>`

`query_name` should match the name of a given query script file, minus the file extension. Params are as specified in the queries themselves.

`ne_format` may be passed as in the query string as an optional formatter name, and defaults to 'default'. Other supported `formatter` options are described in Content section below.

Unknown values passed to `query_extension` or `format` will silently fall back to defaults.

### Method

`GET`

### Success Response

**Code**: 200

**Content**:  
'default': `{"query_name": "<query_name>", "data": [{<column_name>:<row_value>, etc..., }, {etc...}, ], "metadata": {<key>: <value>, etc..., }}`  
'compact': `{"columns": [<list of column names>], "data": [<array of row value arrays>]}`  
'affix': `{"error": false, "response": {<'default' array of result objects>}, "metadata":{"executed": <timestamp>, "params": {<array of name-value pairs submitted to query with request>}}}`
'csv': `<csv formatted string (w \r\n newline)>`  
'sum': `{"error": false, "response": {"summary": <array of row dicts having grouping > 0>, "result": <array of row dicts having grouping = 0>}, "metadata":{"executed": <timestamp>, "params": {<array of name-value pairs submitted to query with request>}}}`

Of course, it is possible that a database query might return no results. In this case, Nerium will respond with an empty JSON array `[]` regardless of specified format. This is not considered an error, and clients should be prepared to handle it appropriately.

### Error Responses

**Code**: 400  
**Content**: `{"error": <exception.repr from Python>}`

## Sketchy Roadmap/TODOs

(in no particular order)

- More detailed documentation, especially about usage
- Parameter discovery endpoint
- Report listing endpoint
- ~~Plugin architecture~~
- Dynamic filtering without jinja-sql
- ~~Improve/mature plugin architecture~~
  - ~~Separate base classes to a library~~
  - ~~Implementation subclasses in `contrib` package~~
  - ~~Refactor plugin approach to use modules with an interface standard, instead of abstract class inheritance~~
- ~~Configurable/flexible JSON output formatters (`AffixFormatter` could do with less hard-coding)~~ [WONTFIX]
- Static output file generator (and other caching)
- Swagger docs
- ~~Health check/default query endpoint~~ (Own git commit hash report(?))
- Convert app.py to [Responder](https://python-responder.org)
