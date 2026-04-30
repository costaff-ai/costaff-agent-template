"""MCP toolset loader for the template agent.

Loads:
    1. The agent's own MCP server (URL from MCP_TEMPLATE_URL env var).
    2. Any extra MCP servers configured via TEMPLATE_AGENT_MCP_URLS
       (set by the CoStaff dashboard at deploy time).

Usage:
    from mcp_toolsets import load_all_mcp_toolsets
    toolsets = load_all_mcp_toolsets()  # list of McpToolset

Notes
-----
TEMPLATE_AGENT_MCP_URLS format (JSON):
    {
        "name": {"url": "...", "headers": {...}, "enabled": true},
        ...
    }
"""
import json
import logging
import os
from typing import List

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

logger = logging.getLogger(__name__)

# TODO: Replace with your MCP service URL when forking this template
DEFAULT_MCP_URL = "http://costaff-mcp-template:8082/mcp"


def _connection_params(entry):
    """Coerce an entry (string URL or dict) into StreamableHTTPServerParams."""
    if isinstance(entry, str):
        url, headers = entry, None
    else:
        url = entry.get("url", "")
        headers = entry.get("headers") or None
    if not url:
        raise ValueError("MCP entry has no URL")
    return StreamableHTTPServerParams(url=url, headers=headers or {})


def load_all_mcp_toolsets() -> List[McpToolset]:
    """Build the agent's MCP toolset list from env configuration."""
    toolsets: List[McpToolset] = []

    # Own MCP — always connected
    own_url = os.getenv("MCP_TEMPLATE_URL", DEFAULT_MCP_URL)
    toolsets.append(McpToolset(connection_params=StreamableHTTPServerParams(url=own_url)))
    logger.info(f"Template MCP URL: {own_url}")

    # Extra MCPs from CoStaff dashboard (e.g. costaff core MCP)
    raw_extra = os.getenv("TEMPLATE_AGENT_MCP_URLS", "")
    if raw_extra:
        try:
            extra_config = json.loads(raw_extra)
        except json.JSONDecodeError:
            logger.error("TEMPLATE_AGENT_MCP_URLS is not valid JSON, skipping extra MCPs")
            return toolsets

        for name, entry in extra_config.items():
            if isinstance(entry, dict) and not entry.get("enabled", True):
                logger.info(f"Skipping disabled extra MCP: {name}")
                continue
            try:
                toolsets.append(McpToolset(connection_params=_connection_params(entry)))
                logger.info(f"Added extra MCP: {name}")
            except Exception as e:
                logger.error(f"Failed to load extra MCP '{name}': {e}")

    return toolsets
