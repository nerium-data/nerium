import json
import unittest
# from collections import OrderedDict

import aiohttp
from aiohttp.test_utils import AioHTTPTestCase
from nerium import Query, ResultFormat
from nerium.app import app
from tests.test_setup import query_name

# Fixtures
EXPECTED = [{
    'foo': 1.25,
    'bar': '2017-09-09',
    'quux': 'Hello',
    'quuux': 'Björk Guðmundsdóttir'
}, {
    'foo': 42,
    'bar': '2031-05-25',
    'quux': 'yo',
    'quuux': 'ƺƺƺƺ'
}]



class TestResults(unittest.TestCase):
    def test_results_expected(self):
        loader = Query(query_name)
        result = loader.result_set()
        self.assertEqual(result, EXPECTED)
        formatter = ResultFormat(result, format_='default')
        formatted_results = formatter.formatted_results()
        self.assertEqual(formatted_results, EXPECTED)


class TestAPI(AioHTTPTestCase):
    async def get_application(self):
        return app

    def test_response(self):
        async def test_get_query():
            url = "/v1/{}".format(query_name)
            resp = await self.client.request("GET", url)
            assert resp.status == 200
            text = await resp.text()
            self.assertEqual(EXPECTED, json.loads(text))

        self.loop.run_until_complete(test_get_query())


if __name__ == '__main__':
    unittest.main()
