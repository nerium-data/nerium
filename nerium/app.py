#!/usr/bin/env python
# -*- coding: utf-8 -*
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from marshmallow import INCLUDE, Schema, fields
from marshmallow.exceptions import ValidationError
from nerium import __version__, commit, csv_result, discovery, formatter, query
from nerium.utils import convert_multidict

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)


@app.route("/")
@app.route("/v1/")
@app.route("/v2/")
def base_route():
    """Health check route; returns OK with version and git commit detail"""
    return jsonify({"status": "ok", "version": __version__, "commit": commit})


@app.route("/v2/reports/")
def serve_report_list():
    """Discovery route; returns a list of available reports known to the service"""
    return jsonify(discovery.list_reports())


@app.route("/v2/reports/<query_name>/")
def serve_report_description(query_name):
    """Discovery route; returns details and metadata about a report by name"""
    report_descr = discovery.describe_report(query_name)
    if report_descr.error:
        status_code = getattr(report_descr, "status_code", 400)
        return jsonify(dict(error=report_descr.error)), status_code
    return jsonify(vars(report_descr))


class ResultRequestSchema(Schema):
    """Require query_name in valid results request, set format to "default" if
    not supplied
    """

    class Meta:
        unknown = INCLUDE

    query_name = fields.String(required=True)
    format_ = fields.String(missing="default", data_key="format")


def get_query_result(params):
    """Get query results from set of request parameters
    Return tuple with formatted results and status code
    """
    # load against schema, return with error message unless valid
    try:
        params = ResultRequestSchema().load(params)
    except ValidationError as e:
        return (e.normalized_messages(), 400)

    # Separate query_name and format from other parameters
    query_name = params.pop("query_name")
    format_ = params.pop("format_")

    # Fetch results from nerium.query
    query_results = query.get_result_set(query_name, **params)

    # Handle error from query submission
    if query_results.error:
        status_code = getattr(query_results, "status_code", 400)
        return (dict(error=query_results.error), status_code)

    # Format results before returning to view
    format_schema = formatter.get_format(format_)
    formatted = format_schema.dump(query_results)
    return (formatted, 200)


@app.route("/v1/<query_name>/")
@app.route("/v1/<query_name>/<format_>")
@app.route("/v2/results")
@app.route("/v2/results/<query_name>/")
@app.route("/v2/results/<query_name>/<format_>")
def serve_query_result(query_name="", format_=""):
    """Parse request and hand params to get_query_result"""
    params = request.json or convert_multidict(request.args.to_dict(flat=False))
    if query_name:
        params["query_name"] = query_name
    if format_:
        params["format_"] = format_

    query_result = get_query_result(params)

    result = query_result[0]
    status_code = query_result[1]

    return jsonify(result), status_code


@app.route("/v1/<query_name>/csv")
@app.route("/v2/results/<query_name>/csv")
def serve_csv_result(query_name):
    params = convert_multidict(request.args.to_dict(flat=False))
    query_results = csv_result.results_to_csv(query_name, **params)
    resp = make_response()
    resp.headers["content_type"] = "text/csv"
    resp.data = query_results
    return resp
