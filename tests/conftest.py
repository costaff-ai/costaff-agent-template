"""pytest fixtures for the Template agent.

The template's tools call out to the manager-core MCP via a plain
HTTP shim (`tools._http.call_shim`). Tests mock httpx so they never
hit a real network.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest


def make_response(status: int, json_body=None, *, text: str = ""):
    """Build a MagicMock that quacks like an httpx.Response."""
    r = MagicMock()
    r.status_code = status
    if json_body is not None:
        r.json = MagicMock(return_value=json_body)
        r.text = json.dumps(json_body)
    else:
        r.json = MagicMock(side_effect=ValueError("not JSON"))
        r.text = text
    return r


@pytest.fixture
def mock_httpx(mocker):
    """Patch httpx inside tools._http with a mock whose .post returns
    whatever the test stages via mock.return_value."""
    import tools._http as _http  # noqa: WPS433

    fake_httpx = MagicMock()
    fake_httpx.post = MagicMock()
    mocker.patch.object(_http, "httpx", new=fake_httpx)
    return fake_httpx
