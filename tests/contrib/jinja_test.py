import unittest
from nerium import query
from tests.test_setup import jinja_query_name
try:
    # See tests/query/jinja.jinja for template format
    import jinjasql  # noqa401

    class TestJinjaTemplateResult(unittest.TestCase):
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
        DIFFERS = [{
            'foo': 1.25,
            'bar': '2017-09-09',
            'quuux': 'Björk Guðmundsdóttir'
        }, {
            'foo': 42,
            'bar': '2031-05-25',
            'quuux': 'ƺƺƺƺ'
        }]

        def test_jinja_results(self):
            result = query.result_set(jinja_query_name, hello="Hello")['data']
            formatted_results = query.formatted_results(
                result, format_='default')
            self.assertEqual(formatted_results, self.EXPECTED)

        def test_jinja_default(self):
            result = query.result_set(jinja_query_name)['data']
            formatted_results = query.formatted_results(
                result, format_='default')
            self.assertEqual(formatted_results, self.DIFFERS)
except ImportError:
    # can't test this module without jinjasql
    pass
