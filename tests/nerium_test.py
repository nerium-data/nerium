#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path

import pytest

from nerium import query
from nerium.app import app

# Environment config
query_name = "test"
query_path = Path(__file__).resolve().parent / "query"
os.environ["QUERY_PATH"] = str(query_path)
os.environ["DATABASE_URL"] = "sqlite:///"
os.environ["API_KEY"] = TEST_API_KEY = "foo-bar-baz-quux"

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

CSV_EXPECTED = (
    "foo,bar,quux,quuux\r\n"
    "1.25,2019-09-09,Hello,Björk Guðmundsdóttir\r\n42,2031-05-25,yo,ƺƺƺƺ\r\n"
)

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
    "metadata": {"database_url": "sqlite:///", "foo": "bar"},
    "name": "test",
    "params": ["greeting"],
}


@pytest.fixture
def client():
    app.config["TESTING"] = True
    client = app.test_client()
    yield client


@pytest.fixture
def test_dir(monkeypatch):
    test_path = Path(__file__).resolve().parent
    monkeypatch.syspath_prepend(test_path)


def test_results_expected():
    result = query.get_result_set(query_name)
    assert result.result == EXPECTED


def test_health_check(client):
    resp = client.get("/", headers={"X-API-Key": TEST_API_KEY})
    assert resp.status_code == 200
    text = resp.get_json()
    assert text["status"] == "ok"
    assert "commit" in text.keys()


def test_sql_error(client):
    url = "/v1/error_test"
    resp = client.get(url, headers={"X-API-Key": TEST_API_KEY})
    assert resp.status_code == 400
    assert "error" in resp.get_json().keys()


def test_missing_query_error(client):
    url = "/v1/not_a_query"
    resp = client.get(url, headers={"X-API-Key": TEST_API_KEY})
    assert resp.status_code == 404
    assert "error" in resp.get_json().keys()


def test_missing_report_error(client):
    url = "/v1/not_a_query/docs"
    resp = client.get(url, headers={"X-API-Key": TEST_API_KEY})
    assert resp.status_code == 404
    assert "error" in resp.get_json().keys()


def test_missing_auth_header(client):
    url = "/"
    resp = client.get(url)
    assert resp.status_code == 400
    assert "error" in resp.get_json().keys()


def test_bad_auth_header(client):
    url = "/"
    resp = client.get(url, headers={"X-API-Key": "invalid-key-value"})
    assert resp.status_code == 403
    assert "error" in resp.get_json().keys()


def test_auth_header_not_required(client):
    os.environ["API_KEY"] = ""
    url = "/"
    resp = client.get(url, headers={"X-API-Key": "invalid-key-value"})
    assert resp.status_code == 200
    text = resp.get_json()
    assert text["status"] == "ok"
    assert "commit" in text.keys()


def test_get_query(client):
    url = f"/v1/{query_name}"
    resp = client.get(url, headers={"X-API-Key": TEST_API_KEY})
    assert resp.status_code == 200
    assert EXPECTED == resp.get_json()["data"]


def test_results_csv(client):
    url = f"/v1/{query_name}/csv"
    resp = client.get(url, headers={"X-API-Key": TEST_API_KEY})
    assert "text/csv" in resp.headers["content-type"]
    assert str(resp.data, "utf-8") == CSV_EXPECTED


def test_results_csv_error(client):
    url = "/v1/error_test/csv"
    resp = client.get(url, headers={"X-API-Key": TEST_API_KEY})
    assert resp.status_code == 400
    assert "no such table: not_a_table" in str(resp.data, "utf-8")


def test_results_compact(client):
    url = f"/v1/{query_name}/compact"
    resp = client.get(url, headers={"X-API-Key": TEST_API_KEY})
    assert resp.status_code == 200
    assert COMPACT_EXPECTED == resp.get_json()


def test_result_json(client):
    url = "/v1/test"
    data = dict(query_name="test", format="compact")
    resp = client.get(url, json=data, headers={"X-API-Key": TEST_API_KEY})
    assert resp.status_code == 200
    assert COMPACT_EXPECTED == resp.get_json()


def test_reports_list(client):
    url = "/v1/docs/"
    resp = client.get(url, headers={"X-API-Key": TEST_API_KEY})
    assert resp.status_code == 200
    assert resp.get_json() == {"reports": ["error_test", "test", "test_body"]}


def test_report_descr(client):
    url = f"/v1/{query_name}/docs"
    resp = client.get(url, headers={"X-API-Key": TEST_API_KEY})
    assert resp.status_code == 200
    assert resp.get_json() == DESCR_EXPECTED


def test_report_descr_body(client):
    url = "/v1/test_body/docs"
    resp = client.get(url, headers={"X-API-Key": TEST_API_KEY})
    assert resp.status_code == 200
    assert "columns" in resp.get_json().keys()


def test_report_descr_error(client):
    url = "/v1/goo/docs"
    resp = client.get(url, headers={"X-API-Key": TEST_API_KEY})
    assert resp.status_code == 404
    assert ("error", "No query found matching 'goo'") in resp.get_json().items()
