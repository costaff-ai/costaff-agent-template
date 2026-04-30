import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from google.adk.agents import LlmAgent

from instruction import build_instruction
from mcp_toolsets import load_all_mcp_toolsets
from models import selected_model
from skills import load_all_skills
from sub_agents import load_all_sub_agents

# Tools = MCP toolsets + Skill toolset
tools = list(load_all_mcp_toolsets())
tools.append(load_all_skills())

# Sub-agents (file-based discovery from sub_agents/ folder)
sub_agents = load_all_sub_agents()

# Instruction (placeholders resolved here)
instruction = build_instruction()

# TODO: Rename `template_agent` to your agent's name (snake_case)
# TODO: Update `name`, `description` to match your agent's role
# Note: sub_agents must be a list (possibly empty) — to_a2a serving requires
# `sub_agents=[]` and rejects None.
template_agent = LlmAgent(
    name="template_agent",
    model=selected_model,
    description="TODO: Describe what this agent does in one sentence.",
    instruction=instruction,
    tools=tools,
    sub_agents=sub_agents,
)
