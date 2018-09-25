import unittest
from nerium import query
from tests.test_setup import query_name, sum_query_name

SUM_EXPECTED = {
    'error': False,
    'response': {
        'summary': [{
            "label": "hello",
            "part": 150
        }, {
            "label": "word",
            "part": 20
        }, {
            "label": None,
            "part": 170
        }],
        'result': [{
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
    'metadata': {
        'executed': 'N/A',
        'params': {}
    }
}

NO_SUM_EXPECTED = {
    'error': False,
    'response': {
        'summary': [],
        'result': [{
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
    'metadata': {
        'executed': 'N/A',
        'params': {}
    }
}


class TestContribSumFormatter(unittest.TestCase):
    def test_results_no_sum(self):
        result = query.result_set(query_name)
        formatted_results = query.formatted_results(result, format_='sum')
        self.assertEqual(formatted_results['response']['summary'],
                         NO_SUM_EXPECTED['response']['summary'])
        self.assertEqual(formatted_results['response']['result'],
                         NO_SUM_EXPECTED['response']['result'])

    def test_results_w_sum(self):
        result = query.result_set(sum_query_name)
        formatted_results = query.formatted_results(result, format_='sum')
        self.assertEqual(formatted_results['response']['summary'],
                         SUM_EXPECTED['response']['summary'])
        self.assertEqual(formatted_results['response']['result'],
                         SUM_EXPECTED['response']['result'])