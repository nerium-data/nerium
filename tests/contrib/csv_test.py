import unittest
from nerium import query
from tests.test_setup import query_name


class TestContribCSVFormatter(unittest.TestCase):
    CSV_EXPECTED = 'foo,bar,quux,quuux\r\n1.25,2017-09-09,Hello,Björk Guðmundsdóttir\r\n42,2031-05-25,yo,ƺƺƺƺ\r\n'  # noqa E501

    def test_results_csv(self):
        result = query.result_set(query_name)
        formatted_results = query.formatted_results(result, format_='csv')
        self.assertEqual(formatted_results, self.CSV_EXPECTED)
