import decimal
import logging

from flask import Flask, jsonify, request
from flask.json import JSONEncoder
from flask_restful import Api, Resource
from nerium.contrib.formatter import (AffixFormatter, CompactFormatter,
                                      CsvFormatter)
from nerium.contrib.resultset import SQLResultSet
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

        Given a query_name, query_extension, and format_ (via URL routes),
        this Flask-RESTful Resource submits the query matching the query_name
        to the appropriate query_extension subclass and optionally format
        results via the matching format_cls and let Resource do its JSON thing
    """
    # Poor man's plugin registration.
    # TODO: formalize this with `__subclasses__()` method
    # TODO: unless and until doing this dynamically with `__subclasses__()`
    #     let's move this to a separate config
    query_extension_lookup = {
        'sql': SQLResultSet,
    }
    format_lookup = {
        'compact': CompactFormatter,
        'affix': AffixFormatter,
        'csv': CsvFormatter,
    }

    def get(self, query_name, query_extension='sql', format_='default'):
        # Lookup query_extension and fetch result from corresponding class
        # TODO: Consider adding this to query subdirectory dotenv
        #      (or something) - With backend_lookup and unique report names,
        #      this doesn't need to be in url pattern.
        try:
            result_cls = self.query_extension_lookup[query_extension]
        except KeyError:
            result_cls = SQLResultSet

        loader = result_cls(query_name, **request.args.to_dict())
        query_result = loader.result_set()

        ne_format = request.args.get("ne_format")
        if ne_format:
            format_ = ne_format

        if format_ in self.format_lookup.keys():
            format_cls = self.format_lookup[format_]
            payload = format_cls(query_result).formatted_results()
        else:
            """ Return default serialization """
            # TODO: return format not found message to client(?)
            if format_:
                logging.warning(
                    'format "{}" not found. Using default result ˝format.')
            if 'error' in query_result[0].keys():
                # Add 400 code to default-format error messages
                payload = query_result, 400
            else:
                payload = query_result
        return payload


api.add_resource(
    ReportAPI,
    '/v1/<string:query_name>/',
    strict_slashes=False)
api.add_resource(BaseRoute, '/', '/v1/', strict_slashes=False)


@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
