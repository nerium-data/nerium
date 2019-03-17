import os
import unittest
from pathlib import Path

# from munch import unmunchify
from nerium import app, query

# Fixtures
EXPECTED = [{
    'foo': 1.25,
    'bar': '2019-09-09',
    'quux': 'Hello',
    'quuux': 'Björk Guðmundsdóttir'
}, {
    'foo': 42,
    'bar': '2031-05-25',
    'quux': 'yo',
    'quuux': 'ƺƺƺƺ'
}]

CSV_EXPECTED = 'foo,bar,quux,quuux\r\n1.25,2019-09-09,Hello,Björk Guðmundsdóttir\r\n42,2031-05-25,yo,ƺƺƺƺ\r\n'  # noqa E501

COMPACT_EXPECTED = {
    'columns': ['foo', 'bar', 'quux', 'quuux'],
    'data': [[1.25, '2019-09-09', 'Hello', 'Björk Guðmundsdóttir'],
             [42, '2031-05-25', 'yo', 'ƺƺƺƺ']]
}

DESCR_EXPECTED = {
    "columns": ["foo", "bar", "quux", "quuux"],
    "error": False,
    "metadata": {
        "foo": "bar"
    },
    "name": "test",
    "params": [],
    "type": "sql"
}

query_name = 'test'


def api():
    return app.api


class TestQueryResults(unittest.TestCase):
    query_path = Path(__file__).resolve().parent / 'query'
    os.environ['QUERY_PATH'] = str(query_path)

    def test_results_expected(self):
        result = query.get_result_set(query_name)
        self.assertEqual(result.result, EXPECTED)


class TestEndpointMessages(unittest.TestCase):
    def test_health_check(self):
        resp = api().requests.get(url='/v1')
        assert resp.status_code == 200
        text = resp.text
        self.assertIn("ok", text)
        self.assertIn("commit", text)

    def test_sql_error(self):
        url = "/v1/results/error_test"
        resp = api().requests.get(url=url)
        assert resp.status_code == 400
        self.assertIn('error', resp.json())

    def test_missing_query_error(self):
        url = '/v1/results/not_a_query'
        resp = api().requests.get(url=url)
        assert resp.status_code == 404
        self.assertIn('error', resp.json())

    def test_missing_report_error(self):
        url = '/v1/reports/not_a_query'
        resp = api().requests.get(url=url)
        assert resp.status_code == 404
        self.assertIn('error', resp.json())


class TestResultsEndpoint(unittest.TestCase):
    def test_get_query(self):
        url = f"/v1/results/{query_name}"
        resp = api().requests.get(url=url)
        assert resp.status_code == 200
        self.assertEqual(EXPECTED, resp.json()['data'])

    def test_results_csv(self):
        url = f"/v1/results/{query_name}/csv"
        resp = api().requests.get(url=url)
        assert resp.headers['content_type'] == 'text/csv'
        self.assertEqual(resp.text, CSV_EXPECTED)

    def test_results_compact(self):
        url = f"/v1/results/{query_name}/compact"
        resp = api().requests.get(url=url)
        assert resp.status_code == 200
        self.assertEqual(
            COMPACT_EXPECTED, resp.json())


class TestReportsEndpoint(unittest.TestCase):
    def test_reports_list(self):
        url = "/v1/reports/list"
        resp = api().requests.get(url=url)
        assert resp.status_code == 200
        self.assertEqual(resp.json(), {'reports': ['error_test', 'test']})

    def test_report_descr(self):
        url = f"/v1/reports/{query_name}"
        resp = api().requests.get(url=url)
        assert resp.status_code == 200
        self.assertEqual(resp.json(), DESCR_EXPECTED)


if __name__ == '__main__':
    unittest.main()
