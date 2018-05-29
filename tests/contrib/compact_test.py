import unittest
from nerium import QueryBroker, ResultFormat
from tests.test_setup import query_name


class TestContribCompactFormatter(unittest.TestCase):
    COMPACT_EXPECTED = {
        'columns': ['foo', 'bar', 'quux', 'quuux'],
        'data': [(1.25, '2017-09-09', 'Hello', 'Björk Guðmundsdóttir'),
                 (42, '2031-05-25', 'yo', 'ƺƺƺƺ')]
    }

    def test_results_compact(self):
        loader = QueryBroker(query_name)
        result = loader.result_set()
        formatter = ResultFormat(result, format_='compact')
        formatted_results = formatter.formatted_results()
        self.assertEqual(formatted_results, self.COMPACT_EXPECTED)