import json
from pathlib import Path

import aiohttp_cors
from aiohttp import web
from dotenv import load_dotenv
from nerium import query, __version__
from nerium.utils import multi_to_dict, serial_date
from webargs import fields
from webargs.aiohttpparser import use_kwargs

# Provision environment as needed
# Load local .env first
load_dotenv(Path.cwd() / '.env')
# Load this one for use w/ Kubernetes secret mount
load_dotenv('/dotenv/.env')


async def base_route(request):
    data = {"status": "ok", "nerium-version": __version__}
    return web.json_response(data)


async def resultset(request):
    """Calls nerium.query.result_set() to fetch results from ResultSet()
    """
    request['querystring'] = multi_to_dict(request.rel_url.query)
    query_result = query.result_set(request.match_info['query_name'],
                                    **request['querystring'])
    # Using json.dumps instead of json_response for serialized datetimes
    return web.Response(
        text=json.dumps(query_result, default=serial_date),
        content_type='application/json')


@web.middleware
@use_kwargs({'ne_format': fields.Str(missing='default')})
async def formatter(request, handler, ne_format):
    """Pass resultset through formatter
    """
    # TODO: Following functional refactor, we can probably go to the formatter
    # directly, and have it call the resultset
    resp = await handler(request)
    result = json.loads(resp.text)

    # Remaining query string params are for the database query
    # Take out 'ne_format' and pass the rest along to the formatter
    try:
        params = request['querystring']
    except KeyError:
        params = {}
    params.pop('ne_format', None)
    payload = query.formatted_results(result, ne_format, **params)
    if isinstance(payload, str):
        return web.Response(text=payload, content_type='text/csv')
    else:
        # we can use json_response here because dates are already serialized
        return web.json_response(payload)


@web.middleware
async def result_status(request, handler):
    """Check if result_set returned an error
    """
    resp = await handler(request)
    result = json.loads(resp.text)
    try:
        if 'error' in result[0].keys():
            raise web.HTTPBadRequest(body=resp.text)
        else:
            return web.json_response(result)
    # exception for health check OK method
    except KeyError:
        return web.json_response(result)
    # empty result set
    except IndexError:
        # TODO: pass info once formatters better handle empty column sets
        raise web.HTTPOk(text=resp.text)


app = web.Application(middlewares=[formatter, result_status])
app.router.add_get('/v1/{query_name}/', resultset)
app.router.add_get('/v1/{query_name}', resultset)
app.router.add_get('/', base_route)
app.router.add_get('/v1/', base_route)

# Configure default CORS settings.
cors = aiohttp_cors.setup(
    app,
    defaults={
        "*":
        aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*",
        )
    })

# Configure CORS on all routes.
for route in list(app.router.routes()):
    cors.add(route)


def main():
    web.run_app(app)


if __name__ == '__main__':
    main()
