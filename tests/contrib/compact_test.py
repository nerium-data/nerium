import unittest
from nerium import query
from tests.test_setup import query_name


class TestContribCompactFormatter(unittest.TestCase):
    COMPACT_EXPECTED = {
        'columns': ['foo', 'bar', 'quux', 'quuux'],
        'data': [(1.25, '2017-09-09', 'Hello', 'Björk Guðmundsdóttir'),
                 (42, '2031-05-25', 'yo', 'ƺƺƺƺ')]
    }

    def test_results_compact(self):
        result = query.result_set(query_name)
        formatted_results = query.formatted_results(result, format_='compact')
        self.assertEqual(formatted_results, self.COMPACT_EXPECTED)
