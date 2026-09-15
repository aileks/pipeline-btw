import httpx
import pytest

from pipeline_btw.client import api


def api_response(status_code=200, json_data=None):
    return httpx.Response(
        status_code,
        json=json_data,
        request=httpx.Request("GET", api.BREWERY_API_URL),
    )


def test_returns_parsed_json_on_success(monkeypatch):
    """A successful response returns its parsed JSON body from a single request."""
    calls = []

    def fake_get(url, params=None):
        calls.append((url, params))
        return api_response(json_data=[{"id": "1"}])

    monkeypatch.setattr(api.httpx, "get", fake_get)
    monkeypatch.setattr(api.time, "sleep", lambda seconds: None)

    result = api.fetch_data({"per_page": 50, "page": 1})

    assert result == [{"id": "1"}]
    assert calls == [(api.BREWERY_API_URL, {"per_page": 50, "page": 1})]


def test_retries_retryable_status_then_succeeds(monkeypatch):
    """A retryable status code retries once with backoff before succeeding."""
    responses = [api_response(503), api_response(json_data=[{"id": "1"}])]
    calls = []
    sleeps = []

    def fake_get(url, params=None):
        calls.append(url)
        return responses[len(calls) - 1]

    monkeypatch.setattr(api.httpx, "get", fake_get)
    monkeypatch.setattr(api.time, "sleep", sleeps.append)

    result = api.fetch_data({})

    assert result == [{"id": "1"}]
    assert len(calls) == 2
    assert sleeps == [1]


def test_raises_after_exhausting_retries_on_network_error(monkeypatch):
    """A network error is retried up to max_retries times, then re-raised."""
    calls = []
    sleeps = []

    def fake_get(url, params=None):
        calls.append(url)
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(api.httpx, "get", fake_get)
    monkeypatch.setattr(api.time, "sleep", sleeps.append)

    with pytest.raises(httpx.ConnectError):
        api.fetch_data({}, max_retries=2)

    assert len(calls) == 3
    assert sleeps == [1, 2]


def test_does_not_retry_non_retryable_status(monkeypatch):
    """A non-retryable status code raises immediately without retrying."""
    calls = []
    sleeps = []

    def fake_get(url, params=None):
        calls.append(url)
        return api_response(404)

    monkeypatch.setattr(api.httpx, "get", fake_get)
    monkeypatch.setattr(api.time, "sleep", sleeps.append)

    with pytest.raises(httpx.HTTPStatusError):
        api.fetch_data({})

    assert len(calls) == 1
    assert sleeps == []
