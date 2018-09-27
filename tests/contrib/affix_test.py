import unittest
from nerium import query
from tests.test_setup import query_name


class TestContribAffixFormatter(unittest.TestCase):
    AFFIX_EXPECTED = {
        'error':
        False,
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
        'metadata': {
            'executed': 'N/A',
            'params': {}
        }
    }

    def test_results_affix(self):
        result = query.result_set(query_name)
        formatted_results = query.formatted_results(
            result, format_='affix')
        # match shape
        self.assertEqual(formatted_results.keys(), self.AFFIX_EXPECTED.keys())
        self.assertEqual(formatted_results['response'],
                         self.AFFIX_EXPECTED['response'])
        self.assertEqual(formatted_results['error'],
                         self.AFFIX_EXPECTED['error'])
        self.assertEqual(formatted_results['metadata']['params'],
                         self.AFFIX_EXPECTED['metadata']['params'])