import os
import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard

# TODO: Update the import to match your agent variable name in agent.py
from agent import template_agent

PORT = int(os.getenv("PORT", "8081"))
PUBLIC_HOST = os.getenv("PUBLIC_HOST", "localhost")

# Provide a minimal agent card with only the agent-level description.
# Omitting individual tool skills prevents the parent agent from seeing
# sub-agent tools as directly callable, which would cause 500 errors.
# TODO: Replace `template_agent` with your agent variable name
agent_card = AgentCard(
    name=template_agent.name,
    url=f"http://{PUBLIC_HOST}:{PORT}",
    description=template_agent.description,
    version="1.0.0",
    capabilities={},
    skills=[],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    supports_authenticated_extended_card=False,
)

app = to_a2a(template_agent, host=PUBLIC_HOST, port=PORT, protocol="http", agent_card=agent_card)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
