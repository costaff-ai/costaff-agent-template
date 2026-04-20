import os
import sys
import json
import importlib
import pkgutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from utils.instructions import AGENT_INSTRUCTION

# TODO: Replace with your agent's workspace directory env var and default path
WORKSPACE_DIR = os.getenv("AGENT_TEMPLATE_WORKSPACE_DIR", "/app/data/agent-template")


def get_connection_params(entry):
    if isinstance(entry, str):
        url, headers = entry, None
    else:
        url     = entry.get("url", "")
        headers = entry.get("headers") or None
    if not url:
        raise ValueError("MCP entry has no URL")
    return StreamableHTTPServerParams(url=url, headers=headers or {})


# TODO: Replace MCP_TEMPLATE_URL with your own MCP env var and service name
MCP_TEMPLATE_URL = os.getenv("MCP_TEMPLATE_URL", "http://costaff-mcp-template:8082/mcp")
tools = [McpToolset(connection_params=StreamableHTTPServerParams(url=MCP_TEMPLATE_URL))]
logger.info(f"Template MCP URL: {MCP_TEMPLATE_URL}")

# Additional MCPs configured via CoStaff dashboard
# TODO: Replace TEMPLATE_AGENT_MCP_URLS with your agent-specific env var name
raw_extra = os.getenv("TEMPLATE_AGENT_MCP_URLS", "")
if raw_extra:
    try:
        extra_config = json.loads(raw_extra)
        for mcp_name, entry in extra_config.items():
            if isinstance(entry, dict) and not entry.get("enabled", True):
                logger.info(f"Skipping disabled extra MCP: {mcp_name}")
                continue
            try:
                tools.append(McpToolset(connection_params=get_connection_params(entry)))
                logger.info(f"Added extra MCP: {mcp_name}")
            except Exception as e:
                logger.error(f"Failed to load extra MCP '{mcp_name}': {e}")
    except json.JSONDecodeError:
        logger.error("TEMPLATE_AGENT_MCP_URLS is not valid JSON, skipping extra MCPs")

model_provider = os.getenv("COSTAFF_AGENT_MODEL_PROVIDER", "gemini").lower()
# TODO: Replace TEMPLATE_AGENT_MODEL with your agent-specific env var name
model_name = os.getenv("TEMPLATE_AGENT_MODEL", "gemini-2.5-flash")

if model_provider == "litellm":
    from google.adk.models.lite_llm import LiteLlm
    selected_model = LiteLlm(
        model=os.getenv("LITELLM_MODEL_NAME"),
        api_base=os.getenv("LITELLM_API_BASE"),
        api_key=os.getenv("LITELLM_API_KEY"),
    )
    logger.info("Template Agent using LiteLLM model provider")
else:
    selected_model = model_name
    logger.info(f"Template Agent using model: {selected_model}")

preferred_lang = os.getenv("COSTAFF_PREFERRED_LANGUAGE", "Traditional Chinese (繁體中文)")
instruction = (
    AGENT_INSTRUCTION
    .replace("{WORKSPACE_DIR}", WORKSPACE_DIR)
    .replace("{user_id}", "shared")
    .replace("{PREFERRED_LANGUAGE}", preferred_lang)
)


# ---------------------------------------------------------------------------
# Auto-discover sub-agents from sub_agents/ subdirectory.
#
# HOW TO ADD A SUB-AGENT:
#   1. Create a new .py file inside sub_agents/  (e.g. sub_agents/search_agent.py)
#   2. Define a module-level variable named `agent` (an LlmAgent instance).
#   3. It is automatically included in the parent agent's sub_agents list.
#
# Example (sub_agents/search_agent.py):
#
#   from google.adk.agents import LlmAgent
#   agent = LlmAgent(name="search_agent", model="gemini-2.5-flash",
#                    description="...", instruction="...")
# ---------------------------------------------------------------------------

def _load_sub_agents():
    sub_agents = []
    pkg_dir = Path(__file__).parent / "sub_agents"
    for _, module_name, _ in pkgutil.iter_modules([str(pkg_dir)]):
        full_name = f"sub_agents.{module_name}"
        try:
            module = importlib.import_module(full_name)
            if hasattr(module, "agent"):
                sub_agents.append(module.agent)
                logger.info(f"Loaded sub-agent from sub_agents/{module_name}.py")
            else:
                logger.warning(f"sub_agents/{module_name}.py has no `agent` variable, skipping")
        except Exception as e:
            logger.error(f"Failed to load sub-agent '{full_name}': {e}")
    return sub_agents


sub_agents = _load_sub_agents()

# TODO: Rename `template_agent` to your agent's name (snake_case)
# TODO: Update `name`, `description`, and `instruction` to match your agent's role
template_agent = LlmAgent(
    name="template_agent",
    model=selected_model,
    description="TODO: Describe what this agent does in one sentence (Traditional Chinese preferred).",
    instruction=instruction,
    tools=tools,
    sub_agents=sub_agents if sub_agents else None,
)
