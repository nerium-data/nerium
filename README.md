# Nerium

![small bicycle](https://dl.dropboxusercontent.com/s/7kba2cgrcvuj0hy/nerium-bicycle-sm.jpg "Keeping the 'micro' in microservices")

[![CircleCI](https://img.shields.io/circleci/project/github/tym-xqo/nerium.svg)](https://circleci.com/gh/tym-xqo/nerium)
[![Codecov](https://img.shields.io/codecov/c/github/tym-xqo/nerium.svg)](https://codecov.io/gh/tym-xqo/nerium)
[![PyPI - Version](https://img.shields.io/pypi/v/nerium.svg)](https://pypi.org/project/nerium/)
[![PyPI - License](https://img.shields.io/pypi/l/nerium.svg)](https://pypi.org/project/nerium/)

A lightweight [Flask](http://flask.pocoo.org/)-based microservice that submits queries to a database and returns machine-readable serialized results (typically JSON). By analogy with static site generators, Nerium reads its queries and serialization formats from local files, stored  on the filesystem. The idea is that report analysts should be able to write queries in their preferred local editor, and upload or mount them where Nerium can use them.

Nerium provides a quick, simple, and easy way to develop JSON APIs for use in reporting and analytic applications.

Nerium features an extendable architecture, allowing support for multiple query types and output formats.

Currently supports SQL queries using the fine [SQLAlchemy](https://www.sqlalchemy.org/) library. In keeping with SQLAlchemy usage, query parameters can be specified in `key=value` format, and (_safely_!) injected into your query in `:key` format.

Other query types can be added as plugins, for non-SQL query languages. (Documentation on plugins forthcoming. See [nerium.query.plugin_module](nerium/query.py#L60-L78) in the meantime.)

Default JSON output represents `data` as an array of objects, one per result row, with database column names as keys. The default schema also provides top-level nodes for `name`, `metadata`, and `params` (details below). A `compact` JSON output format may also be requested, with separate `column` (array of column names) and `data` (array of row value arrays) nodes for compactness. Additional formats can be added by adding [marshmallow](https://marshmallow.readthedocs.io) schema definitions to `format_files`.

Nerium supports any backend that SQLAlchemy can, but since none of these are hard dependencies, drivers aren't included in Pipfile, and the Dockerfile only supports PostgreSQL. If you want Nerium to work with other databases, you can install Python connectors with `pip`, either in a virtualenv or by creating your own Dockerfile using `FROM tymxqo/nerium`. (To ease installation, options for `nerium[mysql]` and `nerium[pg]` are provided in `setup.py`)

## Install/Run

### Using Docker

```bash
$ docker run -d --name=nerium \
--envfile=.env \
-v /local/path/to/query_files:/app/query_files 
-v /local/path/to/format_files:/app/format_files \
-p 5000:5000 tymxqo/nerium

$ curl http://localhost:5000/v1/<query_name>?<params>
```

You might also want to use `tymxqo/nerium` as a base image for your own custom container, in order to add different database drivers, etc. Or you can build locally from the included Dockerfile. The base image includes `psycopg2` PostgreSQL adapter, along with `gunicorn` WSGI server for a production-ready service.

### Local install

```bash
pipenv install nerium[pg]
```

Then add a `query_files` (and, optionally, `format_files`) directory to your project, write your queries, and configure the app as described in the next section. The command `FLASK_APP=nerium/app.py` starts a local development server running the app, listening on port 5000. For production use, you will want to add a proper WSGI server (we like `gunicorn`).

## Configuration

`DATABASE_URL` for query connections must be set in the environment (or in a local `.env` file). This is the simplest configuration option.

### Script file paths

By default, Nerium looks for query and format schema files in `query_files` and `format_files` respectively, in the current working directory from which the service is launched. `QUERY_PATH` and `FORMAT_PATH` environment variables can optionally be set in order to use files from other locations on the filesystem, as desired.

### Multiple Data Sources

If you want to query multiple databases from a single Nerium installation, any individual query file can define its own `database_url` as a key in YAML front matter (see below). This will override the `$DATABASE_URL` setting in the environment for that query only. If you have a large number of queries across several databases, keep in mind that running a separate Nerium instance for each database is always an option.

## Usage

## Query files

As indicated above, queries are simply text files placed in a local `query_files` directory, or another arbitrary filesystem location specified by `QUERY_PATH` in the environment. The base name of the file (`stem` in Python `pathlib` parlance) will determine the `{query_name}` portion of the matching API endpoint; the file extension (or `suffix`) maps to the query type (literally the name of the `nerium.resultset` module that will handle the query).

Note that Nerium loads the query files on server start; while adding additional query scripts does not require any code or config changes, the server needs to be restarted in order to use them.

### Query parameters

Use `:<param>` to specify bind parameters in your query text. These are given specific values in the URL query string by the results request.

### Front matter

Query files can optionally include a [YAML](http://yaml.org/) front matter block. The front matter goes at the top of the file, set off by triple-dashed lines, as in this example:

```yaml
---
Author: Joelle van Dyne
Description: Returns all active usernames in the system
---
select username from user;

```

Front matter can generally be thought of as a way to pass arbitrary key-value pairs to a front-end client; in the default format, the contents of front matter are returned under as a `metadata` object in the results response. (The `compact` formatter simply drops the metadata.) Possibilities include whatever a reporting service and front end developer want to coordinate on.

There are a couple of special-case front matter items:

1. As noted above, it can be used to specify a database connection for the query, overriding the main `DATABASE_URL` in the environment
2. If the front matter includes a `params` block, its contents are returned as the `params` object in the `v1/reports/` discovery response.
3. Similarly, front matter describing `columns` will populate that section of the `/reports/` response.

In the absence of front matter, Nerium attempts to find column specifications and named parameters by inspecting the query text itself. Although it is more manual, front matter can provide greater detail in these sections — a report developer might specify the data type of a column or parameter, for example, in addition to its name.

### Jinja templating

Nerium supports [Jinja](http://jinja.pocoo.org/docs/dev/templates/) templating syntax in queries. The most typical use case would be for adding optional filter clauses to a query so that the same `SELECT` statement can be reused without having to be repeated in multiple files, for example:

```sql
select username
     , user_id
     , display_name
  from user
{% if group %}
 where user.group = :group
{% endif %}
```

Jinja filters and other logic can be applied to inputs, as well.

---
***WARNING!***

The Jinja template is rendered in a `SandboxedEnvironment`, which should protect against [server-side template injection](https://portswigger.net/blog/server-side-template-injection) and most [SQL injection](https://en.wikipedia.org/wiki/SQL_injection) tactics. It should not be considered perfectly safe, however. Use this feature sparingly; stick with SQLAlchemy-style `:key` named parameters for bind value substitutions, and test your specific queries carefully. It should almost go without saying that database permission grants to the user Nerium connects as should be well-restricted, whether one is using Jinja syntax or not.

One known dangerous case is if your entire query file just does a Jinja variable expansion and nothing else: `{{ my_whole_query }}`. *This will allow execution of arbitrary SQL and you should **never** make a template like this available.*

---

## Custom format files

For serialization formats besides the built-in default and `compact`, schema definitions can be added to your `format_files` directory, using the Python [marshmallow](https://marshmallow.readthedocs.io) library. Similarly to query files, the app will look for a format module name matching the `{format}` specified in the endpoint URL. The app expects a `marshmallow.Schema` subclass named `ResultSchema`. Available attributes passed to this schema are all those in the [original `query` object](nerium/query.py#L29) with additional `result` and `params` attributes added. (See [`nerium/schema`](nerium/schema) for examples of how this is done by built-in formats.)

## Query type extensions

A `resultset` module is expected to have a `result` method that takes a `query` object and optional keyword argument (`kwargs`) dictionary, connects to a data source, and returns tabular results as a serializable Python structure (most typically a list of dictionaries).

A Nerium `query` object is a [`SimpleNamespace`](https://docs.python.org/3/library/types.html?highlight=types#types.SimpleNamespace), with elements found in [`get_query()`](nerium/query.py#L29).

Query files to be passed to this module should be named with a file extension that matches the module name (for example, `foo.sql` will be handed to the `resultset/sql.py` module).

## API

### Report listing endpoint

#### URLs

- `/v1/reports`
- `/v1/reports/list` - these are both equivalent; the `list` is optional

#### Method

`GET`

#### Success Response

**Code**: 200

**Content**: `{"reports": [<an array of report names>]}`

### Report description endpoints

#### URLs

- `/v1/reports/{string:query_name}`

#### Method

`GET`

#### Success Response

`{"columns":[<list of columns from report>],"error":false,"metadata":{<report: metadata object>},"name":"<query_name>","params":[<array of parameterized keys in query>],"type":"sql"}`

### Results endpoints

#### URLs

- `/v1/results/<string:query_name>?<query_params>`  
- `/v1/results/<string:query_name>/<string:format>?<query_params>`

`query_name` should match the name of a given query script file, minus the file extension. URL querystring parameters are passed to the invoked data source query, matched to any parameter keys specified in the query file. If any parameters expected by the query are missing, an error will be returned. Extra/unrecognized parameters are silently ignored (this might seem surprising, but it's standard SQLAlchemy behavior for parameter substitution).

`format` path may be included as an optional formatter name, and defaults to 'default'. Other supported `formatter` options are described in Content section below.

Unknown values of `format` will silently fall back to default.

#### Method

`GET`

#### Success Response

**Code**: 200

**Content**:  

'default': `{"name": "<query_name>", "data": [{<column_name>:<row_value>, etc..., }, {etc...}, ], "metadata": {<key>: <value>, etc..., }, "params": {<array of name-value pairs submitted to query with request>}}`  
'compact': `{"columns": [<list of column names>], "data": [<array of row value arrays>]}`
'csv': `<csv formatted string (with \r\n newline)>`
  
Of course, it is possible that a database query might return no results. In this case, Nerium will respond with an empty JSON array `[]` regardless of specified format. This is not considered an error, and clients should be prepared to handle it appropriately.

#### Error Responses

**Code**: 400

**Content**: `{"error": <exception.repr from Python>}`
