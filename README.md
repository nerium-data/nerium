# Nerium

![small bicycle](https://dl.dropboxusercontent.com/s/7kba2cgrcvuj0hy/nerium-bicycle-sm.jpg "Keeping the 'micro' in microservices")

[![CircleCI](https://img.shields.io/circleci/project/github/OAODEV/nerium.svg)](https://circleci.com/gh/OAODEV/nerium)
[![Codecov](https://img.shields.io/codecov/c/github/OAODEV/nerium.svg)](https://codecov.io/gh/OAODEV/nerium)
[![PyPI - Version](https://img.shields.io/pypi/v/nerium.svg)](https://pypi.org/project/nerium/)
[![PyPI - License](https://img.shields.io/pypi/l/nerium.svg)](https://pypi.org/project/nerium/)
[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/OAODEV/nerium)

A lightweight [responder](https://python-responder.org/)-based microservice that submits queries to a database and returns machine-readable serialized results (typically JSON). By analogy with static site generators, Nerium reads its queries and serialization formats from local files, stored  on the filesystem. The idea is that report analysts should be able to write queries in their preferred local editor, and upload or mount them where Nerium can use them.

OAO uses Nerium to easily and quickly provide JSON APIs with report results from our PostgreSQL data warehouse.

Nerium features an extendable architecture, allowing support for multiple query types and output formats.

Currently supports SQL queries using the excellent [Records](https://github.com/kennethreitz/records) library. In keeping with Records usage, query parameters can be specified in `key=value` format, and (_safely_!) injected into your query in `:key` format.

In theory, other query types can be added (under `nerium/resultset`) for non-SQL query languages. This is a promising area for future development.

Default JSON output represents `data` as an array of objects, one per result row, with database column names as keys. The default schema also provides top-level nodes for `name`, `metadata`, and `params` (details below). A `compact` JSON output format may also be requested, with separate `column` (array of column names) and `data` (array of row value arrays) nodes for compactness. Additional formats can be added by adding [marshmallow](https://marshmallow.readthedocs.io) schema definitions to `format_files`.

Nerium supports any backend that SQLAlchemy can, but since none of these are hard dependencies, drivers aren't included in Pipfile, and the Dockerfile only supports PostgreSQL. If you want Nerium to work with other databases, you can install Python connectors with `pip`, either in a virtualenv or by creating your own Dockerfile using `FROM oaodev/nerium`. (To ease installation, options for `nerium[mysql]` and `nerium[pg]` are provided in `setup.py`)

Nerium is inspired in roughly equal measure by [SQueaLy](https://hashedin.com/2017/04/24/squealy-intro-how-to-build-customized-dashboard/) and [Pelican](https://blog.getpelican.com/). It hopes to be something like [Superset](https://superset.incubator.apache.org/) when it grows up.

## Install/Run

### Using Docker

```bash
$ docker run -d --name=nerium \
--envfile=.env \
-v /local/path/to/query_files:/app/query_files \
-v /local/path/to/format_files:/app/format_files \
-p 5000:5000 oaodev/nerium

$ curl http://localhost:5000/v1/<query_name>?<params>
```

### Local install

```bash
pipenv install nerium[pg]
```

Then add a `query_files` (and, optionally, `format_files`) directory to your project, write your queries, and configure the app as described in the next section. The command `nerium` starts a local `uvicorn` server running the app, listening on port 5042.

## Configuration

`DATABASE_URL` for query connections must be set in the environment (or in a local `.env` file). This is the simplest configuration option.

Because the service uses `responder`, it will also respect `PORT` if set in the environment.

### Script file paths

By default, Nerium looks for query and format schema files in `query_files` and `format_files` respectively, in the current working directory from which the service is launched. `QUERY_PATH` and `FORMAT_PATH` environment variables can optionally be set in order to use files from other locations on the filesystem.

### Data Sources

If you want to query multiple databases from a single Nerium installation, any individual query file can define its own `database_url` as a key in YAML front matter (see below).

Alternatively, to handle multiple files with the same connection, create a subdirectory for each database under the `$QUERY_PATH`, place the related files under their respective directory, and include a separate `db.yaml` file per subdirectory, which defines the `database_url` key.

_NOTE_: A `database_url` setting in front matter of a particular will override subdirectory-level `db.yaml` setting as well as `DATABASE_URL` in the environment.

## Usage

## Query files and front matter

As indicated above, queries are simply text files placed in local `query_files` directory, or another arbitrary filesystem location specified by `QUERY_PATH` in the environment. The base name of the file (`stem` in Python `pathlib` parlance) will determine the `{query_name}` portion of the matching API endpoint; the file extension (or `suffix`) maps to the query type (literally the name of the `nerium.resultset` module that will handle the query).

Note that Nerium loads the query files on server start; while adding additional query scripts does not require any code or config changes, the server needs to be restarted in order to use them.

Query files can optionally include a [YAML](http://yaml.org/) front matter block. The front matter goes at the top of the file, set off by triple-dashed lines, as in this example:

```yaml
---
Author: Joelle van Dyne
Description: Returns all active usernames in the system
---
select username from user;

```

At present, the Nerium service doesn't do much with the front matter. As noted above, it can be used to specify a database connection for the query. For other keys, the default response format simply passes the keys and values along in a `metadata` object. (The `compact` formatter simply ignores the metadata.) This mechanism can theoretically be used to pass relevant information about the query along to any clients of the service: for example, the data types of the columns in the results or what have you. Possibilities include whatever a reporting service and front end developer want to coordinate on. Front matter could also be used in more detailed ways in formatters yet to be devised.

## Custom format files

For serialization formats besides the built-in default and `compact`, schema definitions can be added to your `format_files` directory, using the Python [marshmallow](https://marshmallow.readthedocs.io) library. Similarly to query files, the app will look for a format module name matching the `{format}` specified in the endpoint URL. The app expects a `marshmallow.Schema` subclass named `ResultSchema`. Available attributes passed to this schema are all those in the [original `query` object](nerium/query.py#L29) with additional `result` and `params` attributes added. (See [`nerium/schema`](nerium/schema) for examples of how this is done by built-in formats.)

## Query type extensions

A `resultset` module is expected to have a `result` method that takes a `query` object and optional keyword argument (`kwargs`) dictionary, connects to a data source, and returns tabular results as a serializable Python structure (most typically a list of dictionaries). 

A Nerium `query` object is a [munchified](https://github.com/Infinidat/munch) dictionary, with elements found in [`get_query()`](nerium/query.py#L29).

Query files to be passed to this module should be named with a file extension that matches the module name (for example, `foo.sql` will be handed to the `resultset/sql.py` module).

## API

### URLs

- `/v1/<string:query_name>?<query_params>`  
- `/v1/<string:query_name>/<string:format>?<query_params>`

`query_name` should match the name of a given query script file, minus the file extension. URL querystring parameters are passed to the invoked data source query, matched to any keys specified in the query file. If any parameters expected by the query are missing, an error will be returned. Extra/unrecognized parameters are silently ignored (this might seem surprising, but it's standard SQLAlchemy behavior for parameter substitution).

`format` path may be included as an optional formatter name, and defaults to 'default'. Other supported `formatter` options are described in Content section below.

Unknown values passed to `query_extension` or `format` will silently fall back to defaults.

### Method

`GET`

### Success Response

**Code**: 200

**Content**:  

'default': `{"name": "<query_name>", "data": [{<column_name>:<row_value>, etc..., }, {etc...}, ], "metadata": {<key>: <value>, etc..., }, "params": {<array of name-value pairs submitted to query with request>}}`  
'compact': `{"columns": [<list of column names>], "data": [<array of row value arrays>]}`  
  
Of course, it is possible that a database query might return no results. In this case, Nerium will respond with an empty JSON array `[]` regardless of specified format. This is not considered an error, and clients should be prepared to handle it appropriately.

- `/v1/<string:query_name>/csv`

### Method

`GET`

### Success Response

**Code**: 200  

**Content**:

`<csv formatted string (with \r\n newline)>`

### Error Responses

**Code**: 400

**Content**: `{"error": <exception.repr from Python>}`

## Sketchy Roadmap/TODOs

(in no particular order)

- More detailed documentation, especially about usage
- Parameter discovery endpoint
- Report listing endpoint
- Dynamic filtering
- ~~Improve/mature plugin architecture~~
  - ~~Separate base classes to a library~~
  - ~~Implementation subclasses in `contrib` package~~
  - ~~Refactor plugin approach to use modules with an interface standard, instead of abstract class inheritance~~
- ~~Configurable/flexible JSON output formatters (`AffixFormatter` could do with less hard-coding)~~ [Implemented via marshmallow schemas]
- Static output file generator (and other caching)
- Swagger docs
- ~~Health check/default query endpoint~~ ~~(Own git commit hash report(?))~~
- ~~Convert app.py to [Responder](https://python-responder.org)~~
