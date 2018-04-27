from aiohttp import web
from nerium import Query, ResultFormat
import json


def serial_date(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return obj


async def base_route(request):
    data = {"status": "ok"}
    return web.json_response(data)


async def resultset(request):
    """ Calls nerium.Query() to fetch results from ResultSet()
    """
    query = Query(request.match_info['query_name'],
                  **dict(request.rel_url.query))
    query_result = query.result_set()
    # Using json.dumps instead of json_response for serialized datetimes
    return web.Response(
        text=json.dumps(query_result, default=serial_date),
        content_type='application/json')


@web.middleware
async def formatter(request, handler):
    """ Pass resultset through formatter
    """
    resp = await handler(request)

    # Get format from request query string or use default
    try:
        format_ = request.rel_url.query['ne_format']
    except KeyError:
        format_ = 'default'
    result = json.loads(resp.text)

    # Remaining query string params are for the database query
    # Take out 'ne_format' and pass the rest along to the formatter
    params = dict(request.rel_url.query)
    params.pop('ne_format', None)
    formatter = ResultFormat(
        result,
        format_,
        **params)

    payload = formatter.formatted_results()
    if isinstance(payload, str):
        return web.Response(text=payload, content_type='text/csv')
    else:
        return web.json_response(payload)


@web.middleware
async def result_status(request, handler):
    """ Check if result_set returned an error
    """
    resp = await handler(request)
    result = json.loads(resp.text)
    try:
        if 'error' in result[0].keys():
            return web.json_response(result, status=400)
    # exception for health check OK method
    except KeyError:
        return web.json_response(result)


app = web.Application(middlewares=[
    formatter,
])
app.router.add_get('/v1/{query_name}/', resultset)
app.router.add_get('/v1/{query_name}', resultset)
app.router.add_get('/', base_route)
app.router.add_get('/v1/', base_route)

if __name__ == '__main__':
    web.run_app(app)
