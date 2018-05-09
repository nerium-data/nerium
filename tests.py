import datetime
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

class TestContribAffixFormatter(unittest.TestCase):
    AFFIX_EXPECTED = { 'error': False,
                       'response': [{
                                    'foo': 1.25,
                                    'bar': '2017-09-09',
                                    'quux': 'Hello',
                                    'quuux': 'Björk Guðmundsdóttir'
                                }, {
                                    'foo': 42,
                                    'bar': '2031-05-25',
                                    'quux': 'yo',
                                    'quuux': 'ƺƺƺƺ'
                                }],
                        'metadata': {'executed': 'N/A',  
                                     'params': {}}
                      }

    def test_results_affix(self):
        loader = Query(query_name)
        result = loader.result_set()
        formatter = ResultFormat(result, format_='affix')
        formatted_results = formatter.formatted_results()
        #match shape
        self.assertEqual(formatted_results.keys(), self.AFFIX_EXPECTED.keys())
        self.assertEqual(formatted_results['response'],
                         self.AFFIX_EXPECTED['response'])
        self.assertEqual(formatted_results['error'],
                         self.AFFIX_EXPECTED['error'])
        self.assertEqual(formatted_results['metadata']['params'],
                         self.AFFIX_EXPECTED['metadata']['params'])


class TestContribCompactFormatter(unittest.TestCase):
    COMPACT_EXPECTED = {
                        'columns': ['foo', 'bar', 'quux', 'quuux'],
                        'data': [
                             (1.25, '2017-09-09', 'Hello', 'Björk Guðmundsdóttir'),
                             (42, '2031-05-25', 'yo', 'ƺƺƺƺ')]
    }

    def test_results_compact(self):
        loader = Query(query_name)
        result = loader.result_set()
        formatter = ResultFormat(result, format_='compact')
        formatted_results = formatter.formatted_results()
        self.assertEqual(formatted_results, self.COMPACT_EXPECTED)

class TestContribCSVFormatter(unittest.TestCase):
    CSV_EXPECTED = 'foo,bar,quux,quuux\r\n1.25,2017-09-09,Hello,Björk Guðmundsdóttir\r\n42,2031-05-25,yo,ƺƺƺƺ\r\n'

    def test_results_csv(self):
        loader = Query(query_name)
        result = loader.result_set()
        formatter = ResultFormat(result, format_='csv')
        formatted_results = formatter.formatted_results()
        self.assertEqual(formatted_results, self.CSV_EXPECTED) 

class TestContribSumFormatter(unittest.TestCase):
    TEST_SUM_SQL = """select 0 as grouping,
                        'hello' as label,
                        100 as part
                union
                select 0 as grouping,
                        'hello' as label,
                        50 as part
                union
                select 0 as grouping,
                        'word' as label,
                        20 as part
                union 
                select 1 as grouping,
                    'hello' as label,
                    150 as part
                union
                select 1 as grouping,
                    'word' as label,
                    20 as part
                union
                select 3 as grouping,
                    NULL as label,
                    170 as part"""
    
    SUM_EXPECTED = {'error': False,
                    'response': {'summary': [{
                                                "label": "hello",
                                                "part": 150
                                             }, {
                                                "label": "word",
                                                "part": 20
                                             }, {
                                                "label": None,
                                                "part": 170
                                             }],
                                 'result':[{
                                        "label": "hello",
                                        "part": 50
                                        }, {
                                        "label": "hello",
                                        "part": 100
                                        }, {
                                        "label": "word",
                                        "part": 20
                                    }]
                                },
                     'metadata': {'executed': 'N/A',  
                                  'params': {}}
                      }
    NO_SUM_EXPECTED = { 'error': False,
                        'response': {'summary': [],
                                     'result':[{
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
                                    },
                        'metadata': {'executed': 'N/A',  
                                    'params': {}}
                      }
    
    def test_results_no_sum(self):
        loader = Query(query_name)
        result = loader.result_set()
        formatter = ResultFormat(result, format_='sum')
        formatted_results = formatter.formatted_results()
        self.assertEqual(formatted_results['response']['summary'],
                         self.NO_SUM_EXPECTED['response']['summary'])
        self.assertEqual(formatted_results['response']['result'],
                         self.NO_SUM_EXPECTED['response']['result'])
    
    def test_results_w_sum(self):
        with NamedTemporaryFile(
            dir='query_files', suffix='.sql', mode='w',
            delete=False) as _sql_sum_file:
            sql_sum_file = _sql_sum_file
            sql_sum_file.write(self.TEST_SUM_SQL)
            _report_name = os.path.basename(sql_sum_file.name)
            sum_query_name = os.path.splitext(_report_name)[0]

        loader = Query(sum_query_name)
        result = loader.result_set()
        formatter = ResultFormat(result, format_='sum')
        formatted_results = formatter.formatted_results()
        self.assertEqual(formatted_results['response']['summary'],
                         self.SUM_EXPECTED['response']['summary'])
        self.assertEqual(formatted_results['response']['result'],
                         self.SUM_EXPECTED['response']['result'])
        os.remove(sql_sum_file.name)
    

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
