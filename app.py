import decimal
import os

from flask import Flask, request
from flask.json import JSONEncoder
from flask_restful import Api, Resource
from nerium.contrib.formatter import (affix,
                                      compact)
from nerium.contrib.resultset import (sql,
                                      takei)


# Query name registration system query_name -> (script, type)

# PgSqlQueryable.query(script, params) -> ResultSet
# BGSqlQueryable.Query(script, params)

# (query_name, [param,]) v
# {query_name: (script_file, instantiable_queryable)}

# Instantiate and configure app
app = Flask(__name__)
api = Api(app)
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL',
                                       'sqlite:///?check_same_thread=False')
app.config['QUERY_PATH'] = os.getenv('QUERY_PATH', 'query_files')


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


# LIL FLASK APP
class ReportAPI(Resource):
    """ Calls ResultSet.result() and returns JSON

        Given a report_name, query_type, and format_ (via URL routes), this
        Flask-RESTful Resource submits the query matching the report_name to
        the appropriate query_type subclass and optionally format results
        via the matching format_cls and let Resource do its JSON thing
    """
    # Poor man's plugin registration.
    # TODO: formalize this with `__subclasses__()` method
    # TODO: unless and until doing this dynamically with `__subclasses__()`
    #     let's move this to a separate config
    query_type_lookup = {'sql': sql.SQLResultSet,
                         'takei': takei.TakeiResultSet}
    format_lookup = {'compact': compact.CompactFormatter,
                     'affix': affix.AffixFormatter}

    def get(self, report_name, query_type='sql', format_='default'):
        # Lookup query_type and fetch result from corresponding class
        try:
            result_cls = self.query_type_lookup[query_type]
        except KeyError:
            result_cls = sql.SQLResultSet

        loader = result_cls(report_name,
                            **request.args.to_dict())
        query_result = loader.result()

        try:
            format_cls = self.format_lookup[format_]
            payload = format_cls(query_result).format_results()
        except KeyError:
            """ Return default serialization """
            # TODO: add logging and log a warning here
            #     and/or return format not found message to client(?)
            payload = query_result
        return payload


api.add_resource(
    ReportAPI,
    '/v1/<string:report_name>/',
    '/v1/<string:query_type>/<string:report_name>/',
    '/v1/<string:query_type>/<string:report_name>/<string:format_>/')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
