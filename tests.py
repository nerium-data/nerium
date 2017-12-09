import json
import os
import unittest
from tempfile import NamedTemporaryFile

import nerium

os.environ['DATABASE_URL'] = 'sqlite:///'

# Fixtures
EXPECTED = dict(
    columns=['foo', 'bar', 'quux', 'quuux'],
    data=[[1.25, '2017-09-09T00:00:00', 'Hello', 'Björk Guðmundsdóttir'],
          [42.0, '2031-05-25T00:00:00', 'Howdy', 'ƺƺƺƺ']])

TEST_SQL = """select cast(1.25 as float) as foo  -- float check
                    -- timestamp check
                   , strftime('%Y-%m-%dT%H:%M:%S', '2017-09-09') as bar
                   , 'Hello' as quux  -- ascii string check
                   , 'Björk Guðmundsdóttir' as quuux  -- unicode check
               union
              select 42
                   , strftime('%Y-%m-%dT%H:%M:%S','2031-05-25')
                   , 'Howdy'
                   , 'ƺƺƺƺ';
           """


def setUpModule():
    global sql_file
    global report_name
    with NamedTemporaryFile(
            dir='sqls', suffix='.sql', mode='w', delete=False) as _sql_file:
        sql_file = _sql_file
        sql_file.write(TEST_SQL)
        _report_name = os.path.basename(sql_file.name)
        report_name = os.path.splitext(_report_name)[0]


def tearDownModule():
    os.remove(sql_file.name)


class TestResultSet(unittest.TestCase):
    def test_results_expected(self):
        loader = nerium.ResultSet()
        result = loader.result(report_name)

        self.assertEqual(result, EXPECTED)


class Testnerium(unittest.TestCase):
    def setUp(self):
        self.app = nerium.app.test_client()

    def test_response(self):
        endpoint = '/{}'.format(report_name)
        response = self.app.get(endpoint)  # noqa F841

    def test_response_expected(self):
        endpoint = '/{}'.format(report_name)
        response = self.app.get(endpoint)
        self.assertEqual(EXPECTED, json.loads(response.get_data()))


if __name__ == '__main__':
    unittest.main()
