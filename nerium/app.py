#!/usr/bin/env python
# -*- coding: utf-8 -*
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request
from marshmallow import INCLUDE, Schema, fields
from marshmallow.exceptions import ValidationError

from nerium import __version__, commit, csv_result, discovery, formatter, query
from nerium.utils import convert_multidict

# Provision environment as needed
# Load local .env first
load_dotenv(Path.cwd() / ".env")
# Load this one for use w/ Kubernetes secret mount
load_dotenv("/dotenv/.env")

app = Flask(__name__)
app.url_map.strict_slashes = False


@app.route("/")
@app.route("/v1/")
@app.route("/v2/")
def base_route():
    return jsonify({"status": "ok", "version": __version__, "commit": commit})


@app.route("/v2/reports/")
@app.route("/v2/reports/list/")
def serve_report_list():
    return jsonify(discovery.list_reports())


@app.route("/v2/reports/<query_name>/")
def serve_report_description(query_name):
    report_descr = discovery.describe_report(query_name)
    if report_descr.error:
        status_code = getattr(report_descr, "status_code", 400)
        return jsonify(dict(error=report_descr.error)), status_code
    return jsonify(vars(report_descr))


@app.route("/v1/<query_name>/", methods=["GET"])
@app.route("/v1/<query_name>/<format_>", methods=["GET"])
@app.route("/v2/results/<query_name>/", methods=["GET", "POST"])
@app.route("/v2/results/<query_name>/<format_>", methods=["GET", "POST"])
def serve_query_result(query_name, format_="default"):
    if request.method == "POST":
        params = request.json
    else:
        params = convert_multidict(request.args.to_dict(flat=False))
    query_results = query.get_result_set(query_name, **params)
    if query_results.error:
        status_code = getattr(query_results, "status_code", 400)
        return jsonify(dict(error=query_results.error)), status_code

    format_schema = formatter.get_format(format_)
    formatted = format_schema.dump(query_results)
    return jsonify(formatted)


class ResultRequestSchema(Schema):
    class Meta:
        unknown = INCLUDE

    query_name = fields.String(required=True)
    format_ = fields.String(missing="default", data_key="format")


@app.route("/v2/result", methods=["POST"])
def serve_query_result_json():
    if request.method != "POST":
        return jsonify(dict(error=f"Method not allowed ({request.method})")), 405
    try:
        params = ResultRequestSchema().load(request.json)
    except ValidationError as e:
        return jsonify(e.normalized_messages()), 400
    query_name = params.pop("query_name")
    format_ = params.pop("format_")
    query_results = query.get_result_set(query_name, **params)
    if query_results.error:
        status_code = getattr(query_results, "status_code", 400)
        return jsonify(dict(error=query_results.error)), status_code

    format_schema = formatter.get_format(format_)
    formatted = format_schema.dump(query_results)
    return jsonify(formatted)


@app.route("/v1/<query_name>/csv")
@app.route("/v2/results/<query_name>/csv")
def serve_csv_result(query_name):
    params = convert_multidict(request.args.to_dict(flat=False))
    query_results = csv_result.results_to_csv(query_name, **params)
    resp = make_response()
    resp.headers["content_type"] = "text/csv"
    resp.data = query_results
    return resp
