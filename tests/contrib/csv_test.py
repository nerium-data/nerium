import unittest
from nerium import QueryBroker, ResultFormat
from tests.test_setup import query_name


class TestContribCSVFormatter(unittest.TestCase):
    CSV_EXPECTED = 'foo,bar,quux,quuux\r\n1.25,2017-09-09,Hello,Björk Guðmundsdóttir\r\n42,2031-05-25,yo,ƺƺƺƺ\r\n'

    def test_results_csv(self):
        loader = QueryBroker(query_name)
        result = loader.result_set()
        formatter = ResultFormat(result, format_='csv')
        formatted_results = formatter.formatted_results()
        self.assertEqual(formatted_results, self.CSV_EXPECTED)
