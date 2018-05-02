import json
import os
import unittest
# from collections import OrderedDict
from tempfile import NamedTemporaryFile

import aiohttp
from aiohttp.test_utils import AioHTTPTestCase
from nerium.app import app
from nerium import Query, ResultFormat

# TODO: tests for contrib modules

os.environ['DATABASE_URL'] = 'sqlite:///'

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

TEST_SQL = """select cast(1.25 as float) as foo  -- float check
                    -- timestamp check
                   , strftime('%Y-%m-%d', '2017-09-09') as bar
                   , 'Hello' as quux  -- ascii string check
                   , 'Björk Guðmundsdóttir' as quuux  -- unicode check
               union
              select 42
                   , strftime('%Y-%m-%d','2031-05-25')
                   , 'yo'
                   , 'ƺƺƺƺ';
           """


def setUpModule():
    global sql_file
    global query_name
    with NamedTemporaryFile(
            dir='query_files', suffix='.sql', mode='w',
            delete=False) as _sql_file:
        sql_file = _sql_file
        sql_file.write(TEST_SQL)
        _report_name = os.path.basename(sql_file.name)
        query_name = os.path.splitext(_report_name)[0]


def tearDownModule():
    os.remove(sql_file.name)


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
