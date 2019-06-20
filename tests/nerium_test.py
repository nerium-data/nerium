import os
from pathlib import Path

import pytest

# import nerium_mock
from nerium import query
from nerium.app import app

# Fixtures
EXPECTED = [
    {
        "foo": 1.25,
        "bar": "2019-09-09",
        "quux": "Hello",
        "quuux": "Björk Guðmundsdóttir",
    },
    {"foo": 42, "bar": "2031-05-25", "quux": "yo", "quuux": "ƺƺƺƺ"},
]

CSV_EXPECTED = "foo,bar,quux,quuux\r\n1.25,2019-09-09,Hello,Björk Guðmundsdóttir\r\n42,2031-05-25,yo,ƺƺƺƺ\r\n"  # noqa E501

COMPACT_EXPECTED = {
    "columns": ["foo", "bar", "quux", "quuux"],
    "data": [
        [1.25, "2019-09-09", "Hello", "Björk Guðmundsdóttir"],
        [42, "2031-05-25", "yo", "ƺƺƺƺ"],
    ],
}

DESCR_EXPECTED = {
    "columns": ["foo", "bar", "quux", "quuux"],
    "error": False,
    "metadata": {"foo": "bar"},
    "name": "test",
    "params": ["greeting"],
    "type": "sql",
}

query_name = "test"
query_path = Path(__file__).resolve().parent / "query"
os.environ["QUERY_PATH"] = str(query_path)
os.environ["DATABASE_URL"] = "sqlite:///"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    client = app.test_client()
    yield client


def test_results_expected():
    result = query.get_result_set(query_name)
    assert result.result == EXPECTED


def test_health_check(client):
    # with app.test_client() as client:
    resp = client.get("/")
    assert resp.status_code == 200
    text = resp.get_json()
    assert text["status"] == "ok"
    assert "commit" in text.keys()


def test_sql_error(client):
    url = "/v1/results/error_test"
    resp = client.get(url)
    assert resp.status_code == 400
    assert "error" in resp.get_json().keys()


def test_missing_query_error(client):
    url = "/v1/results/not_a_query"
    resp = client.get(url)
    assert resp.status_code == 404
    assert "error" in resp.get_json().keys()


def test_missing_report_error(client):
    url = "/v1/reports/not_a_query"
    resp = client.get(url)
    assert resp.status_code == 404
    assert "error" in resp.get_json().keys()


def test_get_query(client):
    url = f"/v1/results/{query_name}"
    resp = client.get(url)
    assert resp.status_code == 200
    assert EXPECTED == resp.get_json()[0]["data"]


def test_results_csv(client):
    url = f"/v1/results/{query_name}/csv"
    resp = client.get(url)
    assert resp.headers["content_type"] == "text/csv"
    assert str(resp.data, "utf-8") == CSV_EXPECTED


def test_results_compact(client):
    url = f"/v1/results/{query_name}/compact"
    resp = client.get(url)
    assert resp.status_code == 200
    assert COMPACT_EXPECTED == resp.get_json()[0]


def test_reports_list(client):
    url = "/v1/reports/list"
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.get_json() == {"reports": ["error_test", "mock", "test", "test_body"]}


def test_report_descr(client):
    url = f"/v1/reports/{query_name}"
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.get_json() == DESCR_EXPECTED


def test_report_descr_body(client):
    url = "/v1/reports/test_body"
    resp = client.get(url)
    assert resp.status_code == 200
    assert "columns" in resp.get_json().keys()


def test_load_plugin(client):
    url = "/v1/results/mock?foo=bar&baz=quux"
    resp = client.get(url)
    assert resp.status_code == 200
    assert "quux" in str(resp.data)


def test_report_descr_error(client):
    url = "/v1/reports/goo"
    resp = client.get(url)
    assert resp.status_code == 404
    assert ("error", "No query found matching 'goo'") in resp.get_json().items()
