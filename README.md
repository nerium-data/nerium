# Nerium

![small bicycle](https://dl.dropboxusercontent.com/s/7kba2cgrcvuj0hy/nerium-bicycle-sm.jpg "Keeping the 'micro' in microservices")

[![CircleCI](https://img.shields.io/circleci/project/github/tym-xqo/nerium.svg)](https://circleci.com/gh/tym-xqo/nerium)
[![Codecov](https://img.shields.io/codecov/c/github/tym-xqo/nerium.svg)](https://codecov.io/gh/tym-xqo/nerium)
[![PyPI - Version](https://img.shields.io/pypi/v/nerium.svg)](https://pypi.org/project/nerium/)
[![PyPI - License](https://img.shields.io/pypi/l/nerium.svg)](https://pypi.org/project/nerium/)

A lightweight [Flask](http://flask.pocoo.org/)-based microservice that submits queries to any [SQLAlchemy](https://www.sqlalchemy.org/)-supported database, and returns results as JSON or CSV. By analogy with static site generators, Nerium reads its queries and serialization formats from local files, stored on the filesystem. The idea is that report analysts should be able to write queries in their preferred local editor, and upload or mount them where Nerium can use them.

Nerium provides a quick, simple, and easy way to develop JSON APIs for use in reporting and analytic applications. In keeping with SQLAlchemy usage, query parameters can be specified in `key=value` format, and (_safely_!) injected into your query in `:key` format.

Default JSON output represents `data` as an array of objects, one per result row, with database column names as keys. The default schema also provides top-level nodes for `name`, `metadata`, and `params` (details below). A `compact` JSON output format may also be requested, with separate `column` (array of column names) and `data` (array of row value arrays) nodes for compactness. Additional formats can be added by adding [marshmallow](https://marshmallow.readthedocs.io) schema definitions to `format_files`.

Nerium supports any backend that SQLAlchemy can, but since none of these are hard dependencies, drivers aren't included in Pipfile, and the Dockerfile only supports PostgreSQL. If you want Nerium to work with other databases, you can install Python connectors with `pip`, either in a virtualenv or by creating your own Dockerfile using `FROM tymxqo/nerium`. (To ease installation, options for `nerium[mysql]` and `nerium[pg]` are provided in `setup.py`)

## Install/Run

### Using Docker

```bash
docker run -d --name=nerium \
--envfile=.env \
-v /local/path/to/query_files:/app/query_files
-v /local/path/to/format_files:/app/format_files \
-p 5000:5000 tymxqo/nerium

curl http://localhost:5000/v1/<query_name>?<params>
```

You might also want to use `tymxqo/nerium` as a base image for your own custom container, in order to add different database drivers, etc. Or you can build locally from the included Dockerfile. The base image includes `psycopg2` PostgreSQL adapter, along with `gunicorn` WSGI server for a production-ready service.

### Local install

```sh
pipenv install nerium[pg]
```

Or install latest source from Github:

```sh
git clone https://github.com/tym-xqo/nerium.git
cd nerium
pipenv install --dev
```

Then add a `query_files` (and, optionally, `format_files`) directory to your project, write your queries, and configure the app as described in the next section. The command `FLASK_APP=nerium/app.py flask run` starts a local development server running the app, listening on port 5000. For production use, you will want to add a proper WSGI server (we like [`gunicorn`](https://gunicorn.org/)).

## Configuration

`DATABASE_URL` for query connections must be set in the environment (or in a local `.env` file). This is the simplest configuration option.

### Script file paths

By default, Nerium looks for query and format schema files in `query_files` and `format_files` respectively, in the current working directory from which the service is launched. `QUERY_PATH` and `FORMAT_PATH` environment variables can optionally be set in order to use files from other locations on the filesystem, as desired.

### Multiple Data Sources

If you want to query multiple databases from a single Nerium installation, any individual query file can define its own `database_url` as a key in YAML front matter (see below). This will override the `$DATABASE_URL` setting in the environment for that query only. If you have a large number of queries across several databases, keep in mind that running a separate Nerium instance for each database is always an option.

## Usage

### Query files

As indicated above, queries are simply text files placed in a local `query_files` directory, or another arbitrary filesystem location specified by `QUERY_PATH` in the environment. The base name of the file (`stem` in Python `pathlib` parlance) will determine the `{query_name}` portion of the matching API endpoint.

### Query parameters

Use `:<param>` to specify bind parameters in your query text. Clients can then specify values for these bind parameters in their `results` request, passed either as JSON or query string arguments.

### Metadata

Query files can optionally include a [YAML](http://yaml.org/) metadata block. The use of a special comment for metadata allows for the SQL file to be used as-is in other SQL clients. To add this metadata, create a multiline comment surrounded by `\* ... */` markers, and include the label `:meta` at the top. Within this comment, surround the YAML document with standard triple-dashed lines, as in this example:

```sql
/* :meta
---
Author: Joelle van Dyne
Description: Returns all active usernames in the system
---*/
select username from user;

```

Metadata can generally be thought of as a way to pass arbitrary key-value pairs to a front-end client; in the default format, the metadata is simply returned in the results response. (The `compact` formatter drops the metadata.) Other possible use cases include whatever a reporting service and front-end developer want to coordinate on.

There are a couple of special-case metadata items:

1. As noted above, it can be used to specify a database connection for the query, overriding the main `DATABASE_URL` in the environment
2. If the metadata includes a `params` block, its contents are returned as the `params` object in the `v1/reports/` discovery response.
3. Similarly, metadata describing `columns` will populate that section of the `/reports/` response.

In the absence of explicit metadata, Nerium attempts to find column specifications and named parameters by inspecting the query text itself. Although it is more manual, a metadata comment can provide greater detail in these sections — a report developer might specify the data type of a column or parameter, for example, in addition to its name.

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

### Custom format files

For serialization formats besides the built-in default and `compact`, schema definitions can be added to your `format_files` directory, using the Python [marshmallow](https://marshmallow.readthedocs.io) library. Similarly to query files, the app will look for a format module name matching the `{format}` specified in the endpoint URL. The app expects a `marshmallow.Schema` subclass named `ResultSchema`. Available attributes passed to this schema are all found in the [original `query` object](nerium/query.py#L28). (See [`nerium/schema`](nerium/schema) for examples of how this is done by built-in formats.)

## API

### Report listing endpoint

#### URLs

- `/v2/reports`

#### Method

`GET`

#### Success Response

**Code**: 200

**Content**: `{"reports": [<an array of report names>]}`

### Report description endpoints

#### URLs

- `/v2/reports/{string:query_name}`

#### Method

`GET`

#### Success Response

`{"columns":[<list of columns from report>],"error":false,"metadata":{<report: metadata object>},"name":"<query_name>","params":[<array of parameterized keys in query>],"type":"sql"}`

### Results endpoints

#### URLs

- `/v1/<string:query_name>?<query_params>`  
- `/v1/<string:query_name>/<string:format>?<query_params>`
- `/v2/results/`
- `/v2/results/<string:query_name>?<query_params>`  
- `/v2/results/<string:query_name>/<string:format>?<query_params>`

[`v1` endpoints are deprecated and will be removed eventually]

As shown above `query_name` and `format` may be accessed as part of the URL structure, or can be passed as parameters to the request.

Because we're retrieving report results here, the request is a `GET` in any case, but parameters may be sent in a JSON body or as querystring parameters. Note that `query_name` and `format` from URL base path will be preferred, even if a request to such a path happens to include either key in the request body (client apps should avoid doing this to avoid confusion).

`query_name` should match the name of a given query script file, minus the file extension. URL querystring parameters (or JSON keys other than `query_string` and `format`) are passed to the invoked data source query, matched to any parameter keys specified in the query file. If any parameters expected by the query are missing, an error will be returned. Extra/unrecognized parameters are silently ignored (this might seem surprising, but it's standard SQLAlchemy behavior for parameter substitution).

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
