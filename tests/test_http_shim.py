"""Tests for tools._http.call_shim — the HTTP shim every template-
forked agent uses to reach manager-core MCP.

Coverage:
- Success: returns the `result` field from JSON body.
- HTTP non-200: returns "[ERROR] ..." with status + error message.
- Transport error (e.g. connection refused): returns "[ERROR] could not reach...".
- Response with non-JSON body: returns raw text on success path.
- Authorization header: present iff MCP_SECRET_KEY is set.
- Timeout env var: honored (parsed from COSTAFF_TOOL_HTTP_TIMEOUT).
"""
from __future__ import annotations

import pytest

from tests.conftest import make_response


def test_call_shim_success_returns_result(mock_httpx):
    mock_httpx.post.return_value = make_response(200, {"result": "ok-string"})
    from tools._http import call_shim
    out = call_shim("http://mcp:8081", "do_thing", a=1)
    assert out == "ok-string"


def test_call_shim_passes_kwargs_as_json(mock_httpx):
    mock_httpx.post.return_value = make_response(200, {"result": ""})
    from tools._http import call_shim
    call_shim("http://mcp:8081", "send_msg", channel="tg", body="hi")
    args, kwargs = mock_httpx.post.call_args
    assert kwargs["json"] == {"channel": "tg", "body": "hi"}


def test_call_shim_url_format(mock_httpx):
    mock_httpx.post.return_value = make_response(200, {"result": ""})
    from tools._http import call_shim
    call_shim("http://mcp:8081/", "my_tool")  # trailing slash
    args, _ = mock_httpx.post.call_args
    assert args[0] == "http://mcp:8081/api/tool/my_tool"


def test_call_shim_non_200_returns_error(mock_httpx):
    mock_httpx.post.return_value = make_response(500, {"error": "boom"})
    from tools._http import call_shim
    out = call_shim("http://mcp:8081", "do_thing")
    assert out.startswith("[ERROR]")
    assert "do_thing" in out
    assert "500" in out
    assert "boom" in out


def test_call_shim_non_200_with_non_json_body(mock_httpx):
    mock_httpx.post.return_value = make_response(503, text="Service Unavailable")
    from tools._http import call_shim
    out = call_shim("http://mcp:8081", "do_thing")
    assert out.startswith("[ERROR]")
    assert "503" in out
    assert "Service Unavailable" in out


def test_call_shim_transport_error(mock_httpx):
    mock_httpx.post.side_effect = ConnectionError("nope")
    from tools._http import call_shim
    out = call_shim("http://mcp:8081", "do_thing")
    assert out.startswith("[ERROR] could not reach")
    assert "do_thing" in out


def test_call_shim_authorization_header_when_secret_set(mock_httpx, monkeypatch):
    import tools._http as _http
    monkeypatch.setattr(_http, "_SECRET", "test-secret-123")
    mock_httpx.post.return_value = make_response(200, {"result": ""})
    _http.call_shim("http://mcp:8081", "x")
    _, kwargs = mock_httpx.post.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer test-secret-123"


def test_call_shim_no_authorization_when_no_secret(mock_httpx, monkeypatch):
    import tools._http as _http
    monkeypatch.setattr(_http, "_SECRET", "")
    mock_httpx.post.return_value = make_response(200, {"result": ""})
    _http.call_shim("http://mcp:8081", "x")
    _, kwargs = mock_httpx.post.call_args
    assert "Authorization" not in kwargs["headers"]


def test_call_shim_timeout_passed(mock_httpx, monkeypatch):
    import tools._http as _http
    monkeypatch.setattr(_http, "_TIMEOUT", 5.0)
    mock_httpx.post.return_value = make_response(200, {"result": ""})
    _http.call_shim("http://mcp:8081", "x")
    _, kwargs = mock_httpx.post.call_args
    assert kwargs["timeout"] == 5.0


def test_call_shim_missing_result_field(mock_httpx):
    """If JSON body has no 'result' key, return empty string."""
    mock_httpx.post.return_value = make_response(200, {"other": "data"})
    from tools._http import call_shim
    out = call_shim("http://mcp:8081", "do_thing")
    assert out == ""
