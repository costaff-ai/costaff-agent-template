import os
import sys
import inspect
import importlib
import pkgutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-template")

sys.path.insert(0, str(Path(__file__).parent))
# Allow tool files to import from each other (e.g. `from _shared import ...`)
# WARNING: This also puts tools/ at the TOP of Python's module search path.
# NEVER name a tool file the same as an installed package — it will shadow it and
# crash the server at startup (e.g. dotenv.py shadows python-dotenv).
# Dangerous names: dotenv.py, json.py, os.py, re.py, logging.py, requests.py
# Safe pattern: describe the CATEGORY, not the library → env_file.py, http_client.py
sys.path.insert(0, str(Path(__file__).parent / "tools"))

WORKSPACE = os.getenv("WORKSPACE_DIR", "/app/data/costaff-agent-template")
os.makedirs(WORKSPACE, exist_ok=True)

# TODO: Rename "Template" to your MCP server's name
# TODO: Replace MCP_TEMPLATE_PORT with your agent's MCP port env var
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Template", host="0.0.0.0", port=int(os.getenv("MCP_TEMPLATE_PORT", "8082")))


# ---------------------------------------------------------------------------
# Auto-discover and register tools from the tools/ subdirectory.
#
# HOW TO ADD TOOLS:
#   1. Create a new .py file inside tools/  (e.g. tools/my_tools.py)
#   2. Define plain Python functions with typed parameters and a docstring.
#   3. Functions whose names start with "_" are skipped (private helpers).
#   4. No extra wiring needed — they are picked up automatically on startup.
#
# Example (tools/my_tools.py):
#
#   import os
#   from pathlib import Path
#
#   def my_tool(input: str) -> str:
#       """Short description the LLM reads to decide when to call this."""
#       ...
# ---------------------------------------------------------------------------

def _register_tools(mcp_instance):
    tools_pkg_dir = Path(__file__).parent / "tools"
    for finder, module_name, _ in pkgutil.iter_modules([str(tools_pkg_dir)]):
        full_name = f"tools.{module_name}"
        try:
            module = importlib.import_module(full_name)
        except Exception as e:
            logger.error(f"Failed to import tool module '{full_name}': {e}")
            continue

        registered = 0
        for name, fn in inspect.getmembers(module, inspect.isfunction):
            # Only pick up functions defined in this module (not imported ones)
            if fn.__module__ != full_name:
                continue
            if name.startswith("_"):
                continue
            mcp_instance.tool()(fn)
            registered += 1

        logger.info(f"Registered {registered} tool(s) from tools/{module_name}.py")


_register_tools(mcp)


# ---------------------------------------------------------------------------
# Add inline tools here if you prefer not to use the tools/ subdirectory.
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # Transport env-selectable. Default SSE: race-free under to_a2a()+
    # ADK1.33 (streamable-http anyio CancelScope race google/adk-python
    # #4454 does NOT occur on SSE — verified 2026-05-16). New agents
    # forked from this template inherit the safe SSE default. Set
    # MCP_TRANSPORT=streamable-http to switch back once ADK fixes #4454.
    _t = os.getenv("MCP_TRANSPORT", "streamable-http")
    logger.info(f"Starting Template MCP server (transport={_t}, workspace={WORKSPACE})")
    mcp.run(transport=_t)
