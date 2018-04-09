import decimal
import logging

from flask import Flask, jsonify, request
from flask.json import JSONEncoder
from flask_restful import Api, Resource
from nerium import Query, ResultFormat
from nerium.contrib.formatter import (AffixFormatter, CompactFormatter,
                                      CsvFormatter)
from werkzeug.exceptions import HTTPException

# Instantiate and configure app
app = Flask(__name__)
api = Api(app)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


class ResultJSONEncoder(JSONEncoder):
    """ Add simple default encodings for Decimals and Datetimes.
    Why `json` doesn't do this out of the box is beyond me. >:(
    """

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return obj
        return JSONEncoder.default(self, obj)


app.config['RESTFUL_JSON'] = {'cls': ResultJSONEncoder}


class BaseRoute(Resource):
    def get(self):
        return {"status": "ok"}


# LIL FLASK APP
class ReportAPI(Resource):
    """ Calls ResultSet.result() and returns JSON

        Given a query_name, and format_ (via URL route/query string),
        this Flask-RESTful Resource submits the query matching the query_name
        and optionally formats results via the matching format_cls.

        Parent `Resource` class automatically serializes results to JSON
    """
    def get(self, query_name, format_='default'):
        # Hand off to Query for query_path resolution and bring back results
        query = Query(query_name, **request.args.to_dict())
        query_result = query.result_set()

        ne_format = request.args.get("ne_format")
        if ne_format:
            format_ = ne_format
        
        # Pass results through matching formatter
        formatter = ResultFormat(query_result, format_)
        payload = formatter.formatted_results()

        return payload


api.add_resource(ReportAPI, '/v1/<string:query_name>/', strict_slashes=False)
api.add_resource(BaseRoute, '/', '/v1/', strict_slashes=False)


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
