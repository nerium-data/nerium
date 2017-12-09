from flask import Flask, render_template, request
from flask_restful import Api, Resource
from nerium import ResultSet

# Instantiate app
app = Flask(__name__)
api = Api(app)


class ReportAPI(Resource):
    def get(self, report_name):
        loader = ResultSet()
        payload = loader.result(report_name, **request.args.to_dict())
        return payload


api.add_resource(ReportAPI, '/<string:report_name>',
                 '/report/<string:report_name>')


@app.route('/table/<string:report_name>')
def report_table(report_name):
    loader = ResultSet()
    payload = loader.result(report_name, **request.args.to_dict())
    return render_template(
        'table.html', columns=payload['columns'], data=payload['data'])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
