"""Tests for tools.costaff_api — the 4 manager-core wrapper tools that
every template-forked agent inherits.

Verifies each wrapper:
- Calls call_shim with the right tool name + base URL
- Passes the documented kwargs correctly
- Returns whatever call_shim returned (no transformation)
"""
from __future__ import annotations

from unittest.mock import patch

from tools.costaff_api import (
    add_task_comment,
    list_data_files,
    load_costaff_api_tools,
    move_to_shared,
    send_message_now,
)


# ----------------------------------------------------- send_message_now

def test_send_message_now_dispatches_to_shim():
    with patch("tools.costaff_api.call_shim", return_value="sent") as m:
        out = send_message_now(
            channel="telegram",
            recipient="user-123",
            body="[Agent] hello",
            user_id="user-123",
            session_id="sess-abc",
        )
        assert out == "sent"
        args, kwargs = m.call_args
        assert args[1] == "send_message_now"
        assert kwargs["channel"] == "telegram"
        assert kwargs["recipient"] == "user-123"
        assert kwargs["body"] == "[Agent] hello"
        assert kwargs["user_id"] == "user-123"
        assert kwargs["session_id"] == "sess-abc"


def test_send_message_now_default_app_name():
    with patch("tools.costaff_api.call_shim", return_value="") as m:
        send_message_now(channel="tg", recipient="r")
        _, kwargs = m.call_args
        assert kwargs["app_name"] == "costaff_agent"


# ----------------------------------------------------- add_task_comment

def test_add_task_comment_dispatches_to_shim():
    with patch("tools.costaff_api.call_shim", return_value="added") as m:
        out = add_task_comment(
            task_id="task-1",
            user_id="u",
            author="user",
            content="this is a note",
            comment_type="result",
        )
        assert out == "added"
        args, kwargs = m.call_args
        assert args[1] == "add_task_comment"
        assert kwargs["task_id"] == "task-1"
        assert kwargs["author"] == "user"
        assert kwargs["comment_type"] == "result"


def test_add_task_comment_default_comment_type():
    with patch("tools.costaff_api.call_shim", return_value="") as m:
        add_task_comment(task_id="t", user_id="u", author="a", content="c")
        _, kwargs = m.call_args
        assert kwargs["comment_type"] == "note"


# ----------------------------------------------------- move_to_shared

def test_move_to_shared_dispatches_to_shim():
    with patch("tools.costaff_api.call_shim", return_value="moved") as m:
        out = move_to_shared(src_path="/app/data/agent-x/foo.csv", overwrite=True)
        assert out == "moved"
        args, kwargs = m.call_args
        assert args[1] == "move_to_shared"
        assert kwargs["src_path"] == "/app/data/agent-x/foo.csv"
        assert kwargs["overwrite"] is True


def test_move_to_shared_default_overwrite_false():
    with patch("tools.costaff_api.call_shim", return_value="") as m:
        move_to_shared(src_path="/app/data/x.csv")
        _, kwargs = m.call_args
        assert kwargs["overwrite"] is False


# ----------------------------------------------------- list_data_files

def test_list_data_files_dispatches_to_shim():
    with patch("tools.costaff_api.call_shim", return_value="a.csv\nb.csv") as m:
        out = list_data_files(path="/app/data/shared/x", pattern="*.csv")
        assert out == "a.csv\nb.csv"
        args, kwargs = m.call_args
        assert args[1] == "list_data_files"
        assert kwargs["path"] == "/app/data/shared/x"
        assert kwargs["pattern"] == "*.csv"


def test_list_data_files_default_pattern_none():
    with patch("tools.costaff_api.call_shim", return_value="") as m:
        list_data_files(path="/app/data")
        _, kwargs = m.call_args
        assert kwargs["pattern"] is None


# ----------------------------------------------------- entry point

def test_load_costaff_api_tools_returns_four_callables():
    tools = load_costaff_api_tools()
    assert len(tools) == 4
    names = {t.__name__ for t in tools}
    assert names == {
        "send_message_now",
        "add_task_comment",
        "move_to_shared",
        "list_data_files",
    }


def test_all_wrappers_use_default_base_url():
    """The template's _BASE should default to costaff-mcp-costaff:8081
    (the well-known manager core URL)."""
    import tools.costaff_api as ca
    assert ca._BASE.startswith("http://")
    assert "8081" in ca._BASE


# ----------------------------------------------------- contract

def test_all_wrappers_return_strings():
    """ADK contract: function tool returns string, never raises."""
    with patch("tools.costaff_api.call_shim", return_value=""):
        assert isinstance(send_message_now(channel="tg", recipient="r"), str)
        assert isinstance(add_task_comment(task_id="t", user_id="u", author="a", content="c"), str)
        assert isinstance(move_to_shared(src_path="/x"), str)
        assert isinstance(list_data_files(path="/x"), str)
