import json
import unittest

from nerium import app, query
# from nerium.app import api
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

CSV_EXPECTED = 'foo,bar,quux,quuux\r\n1.25,2017-09-09,Hello,Björk Guðmundsdóttir\r\n42,2031-05-25,yo,ƺƺƺƺ\r\n'  # noqa E501

COMPACT_EXPECTED = {
    'columns': ['foo', 'bar', 'quux', 'quuux'],
    'data': [[1.25, '2017-09-09', 'Hello', 'Björk Guðmundsdóttir'],
             [42, '2031-05-25', 'yo', 'ƺƺƺƺ']]
}


class TestResults(unittest.TestCase):
    def test_results_expected(self):
        result = query.get_result_set(query_name, format_='default')
        self.assertEqual(result['data'], EXPECTED)


class TestAPI(unittest.TestCase):
    def api(self):
        return app.api

    # def test_response(self):
    def test_health_check(self):
        resp = self.api().requests.get(url='/')
        assert resp.status_code == 200
        text = resp.text
        self.assertIn("ok", text)

    def test_get_query(self):
        url = f"/v1/{query_name}"
        resp = self.api().requests.get(url=url)
        assert resp.status_code == 200
        self.assertEqual(EXPECTED, resp.json()['data'])

    def test_results_csv(self):
        url = f"/v1/{query_name}/csv"
        resp = self.api().requests.get(url=url)
        assert resp.headers['content_type'] == 'text/csv'
        # formatted_results = query.formatted_results(result, format_='csv')
        self.assertEqual(resp.text, CSV_EXPECTED)

    def test_get_compact(self):
        url = f"/v1/{query_name}/compact"
        resp = self.api().requests.get(url=url)
        assert resp.status_code == 200
        self.assertEqual(
            COMPACT_EXPECTED, resp.json())


if __name__ == '__main__':
    unittest.main()
