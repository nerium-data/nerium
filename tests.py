import json
import os
import unittest
# from collections import OrderedDict
from tempfile import NamedTemporaryFile

import app
import nerium

# TODO: test moar methods

os.environ['LITESQL_BACKEND'] = 'sqlite:///'
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
    global report_name
    with NamedTemporaryFile(
            dir='query_files', suffix='.lite.sql', mode='w',
            delete=False) as _sql_file:
        sql_file = _sql_file
        sql_file.write(TEST_SQL)
        _report_name = os.path.basename(sql_file.name)
        report_name = os.path.splitext(_report_name)[0]


def tearDownModule():
    os.remove(sql_file.name)


class TestSQLResultSet(unittest.TestCase):
    def test_results_expected(self):
        loader = nerium.contrib.resultset.sql.SQLResultSet(report_name)
        result = loader.result()
        self.assertEqual(result, EXPECTED)


class TestSQLAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def test_response(self):
        endpoint = '/v1/sql/{}/'.format(report_name)
        response = self.app.get(endpoint)  # noqa F841

    def test_response_expected(self):
        endpoint = '/v1/sql/{}/'.format(report_name)
        response = self.app.get(endpoint)
        self.assertEqual(EXPECTED, json.loads(response.get_data()))


if __name__ == '__main__':
    unittest.main()
