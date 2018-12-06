from pathlib import Path

import responder
from dotenv import load_dotenv
from nerium import __version__, commit, formatter, query
from nerium.utils import unwrap_querystring_lists

# Provision environment as needed
# Load local .env first
load_dotenv(Path.cwd() / '.env')
# Load this one for use w/ Kubernetes secret mount
load_dotenv('/dotenv/.env')

api = responder.API(
    cors=True,
    cors_params={
        'allow_credentials': True,
        'expose_headers': ["*"],
        'allow_headers': ["*"],
        'allow_methods': ["*"]
    },
    title='Nerium',
    version='1.0',
    openapi='3.0.0',
    docs_route="/docs")


@api.route("/")
@api.route("/v1")
async def base_route(req, resp):
    resp.media = {"status": "ok", "version": __version__, "commit": commit}


@api.route("/v1/{query_name}")
@api.route("/v1/{query_name}/{format_}")
async def serve_query_result(req, resp, *, query_name, format_='default'):
    params = unwrap_querystring_lists(req.params)
    query_results = query.get_result_set(query_name, **params)
    if query_results['error']:
        resp.status_code = 400
        resp.media = dict(error=query_results['error'])
    else:
        format_schema = formatter.get_format(format_)
        resp.media = format_schema.dump(query_results)


@api.route("/v1/{query_name}/csv")
async def serve_csv_result(req, resp, *, query_name):
    params = unwrap_querystring_lists(req.params)
    query_results = query.results_to_csv(query_name, **params)
    resp.headers = {'content_type': 'text/csv'}
    resp.text = query_results


def main():
    api.run()


if __name__ == "__main__":
    main()
