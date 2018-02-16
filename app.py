import decimal
# import os

from flask import Flask, request
from flask.json import JSONEncoder
from flask_restful import Api, Resource
from nerium.contrib.formatter import (AffixFormatter, CompactFormatter)
from nerium.contrib.resultset import SQLResultSet

# Instantiate and configure app
app = Flask(__name__)
api = Api(app)


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

        Given a report_name, query_extension, and format_ (via URL routes),
        this Flask-RESTful Resource submits the query matching the report_name
        to the appropriate query_extension subclass and optionally format
        results via the matching format_cls and let Resource do its JSON thing
    """
    # Poor man's plugin registration.
    # TODO: formalize this with `__subclasses__()` method
    # TODO: unless and until doing this dynamically with `__subclasses__()`
    #     let's move this to a separate config
    query_extension_lookup = {'sql': SQLResultSet, }
    format_lookup = {'compact': CompactFormatter, 'affix': AffixFormatter}

    def get(self, report_name, query_extension='sql', format_='default'):
        # Lookup query_extension and fetch result from corresponding class
        # TODO: Consider adding this to query subdirectory dotenv
        #      (or something) - With backend_lookup and unique report names,
        #      this doesn't need to be in url pattern.
        try:
            result_cls = self.query_extension_lookup[query_extension]
        except KeyError:
            result_cls = SQLResultSet

        loader = result_cls(report_name, **request.args.to_dict())
        query_result = loader.result_set()

        if format_ in self.format_lookup.keys():
            format_cls = self.format_lookup[format_]
            payload = format_cls(query_result).format_results()
        else:
            """ Return default serialization """
            # TODO: add logging and log a warning here
            #     and/or return format not found message to client(?)
            payload = query_result
        return payload


api.add_resource(
    ReportAPI,
    '/v1/<string:report_name>/',
    '/v1/<string:query_extension>/<string:report_name>/',
    '/v1/<string:query_extension>/<string:report_name>/<string:format_>/',
    strict_slashes=False)

api.add_resource(BaseRoute, '/', '/v1/', strict_slashes=False)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
