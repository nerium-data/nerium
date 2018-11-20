import json
import os
import unittest
from datetime import datetime

from aiohttp.test_utils import AioHTTPTestCase
from nerium import query
from nerium.app import app
from nerium.utils import serial_date
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
        result = query.result_set(query_name)['data']
        self.assertEqual(result, EXPECTED)
        formatted_results = query.formatted_results(result, format_='default')
        self.assertEqual(formatted_results, EXPECTED)


class TestSerialDate(unittest.TestCase):
    def test_date_serialization(self):
        the_date = datetime(2019, 9, 9)
        serialize_this = json.dumps(
            dict(the_date=the_date, stringy='hey'), default=serial_date)
        serialized = '{"the_date": "2019-09-09T00:00:00", "stringy": "hey"}'
        self.assertEqual(serialize_this, serialized)


class TestAPI(AioHTTPTestCase):
    async def get_application(self):
        return app

    def test_response(self):
        async def test_health_check():
            resp = await self.client.request("GET", "/")
            assert resp.status == 200
            text = await resp.text()
            self.assertIn("ok", text)

        async def test_get_query():
            await test_health_check()
            url = "/v1/{}".format(query_name)
            resp = await self.client.request("GET", url)
            assert resp.status == 200
            text = await resp.text()
            self.assertEqual(EXPECTED, json.loads(text)['data'])

        self.loop.run_until_complete(test_get_query())


if __name__ == '__main__':
    unittest.main()
