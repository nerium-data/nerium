#!/usr/bin/env python
# -*- coding: utf-8 -*
from pathlib import Path

from flask import Flask, jsonify, make_response, request
from dotenv import load_dotenv
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
def base_route():
    return jsonify({"status": "ok", "version": __version__, "commit": commit})


@app.route("/v1/reports/")
@app.route("/v1/reports/list/")
def serve_report_list():
    return jsonify(discovery.list_reports())


@app.route("/v1/reports/<query_name>/")
def serve_report_description(query_name):
    report_descr = discovery.describe_report(query_name)
    if report_descr.error:
        status_code = getattr(report_descr, "status_code", 400)
        return jsonify(dict(error=report_descr.error)), status_code
    return jsonify(vars(report_descr))


@app.route("/v1/results/<query_name>/")
@app.route("/v1/results/<query_name>/<format_>")
def serve_query_result(query_name, format_="default"):
    params = convert_multidict(request.args.to_dict(flat=False))
    query_results = query.get_result_set(query_name, **params)
    if query_results.error:
        status_code = getattr(query_results, "status_code", 400)
        return jsonify(dict(error=query_results.error)), status_code

    format_schema = formatter.get_format(format_)
    formatted = format_schema.dump(query_results)
    return jsonify(formatted)


@app.route("/v1/results/<query_name>/csv")
def serve_csv_result(query_name):
    params = convert_multidict(request.args.to_dict(flat=False))
    query_results = csv_result.results_to_csv(query_name, **params)
    resp = make_response()
    resp.headers["content_type"] = "text/csv"
    resp.data = query_results
    return resp
