# Mateclaw Agent Template

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-latest-orange.svg)](https://github.com/google/adk-python)
[![MCP](https://img.shields.io/badge/MCP-enabled-green.svg)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![A2A Protocol](https://img.shields.io/badge/A2A-protocol-violet.svg)](https://github.com/google/A2A)
[![mateclaw.agent.json](https://img.shields.io/badge/mateclaw-compatible-blue.svg)](https://github.com/MateClawAI/mateclaw)

[繁體中文](./README_zhtw.md) | **English**

**Mateclaw Agent Template** is a starting point for building external agents on the [Mateclaw](https://github.com/MateClawAI/mateclaw) platform. It follows the same architecture as first-party agents (`mateclaw-coding-agent`, `mateclaw-viz-report-agent`) and is ready to deploy with Docker Compose or the Mateclaw CLI.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Customisation Guide](#customisation-guide)
- [Environment Variables](#environment-variables)
- [MCP Extensions](#mcp-extensions)
- [mateclaw.agent.json](#mateclawagentjson)
- [License](#license)

---

## How It Works

```
Mateclaw Agent
     │
     │  A2A Protocol (/.well-known/agent.json)
     ▼
Template Agent  ──►  MCP Template Server  ──►  Your tools / data / APIs
```

1. The Mateclaw Agent delegates tasks via **A2A protocol**
2. The agent reasons using its system prompt and calls tools via the **MCP server**
3. Results are saved to a shared volume and returned to the calling agent

---

## Architecture

```
mateclaw-agent-template/
├── agent/                        # ADK agent definition
│   ├── agent.py                  # LlmAgent with dynamic MCP loading
│   ├── agent_a2a.py              # A2A server entrypoint
│   ├── requirements.txt
│   └── utils/
│       └── instructions/
│           └── agent_instruction.md   # System prompt (edit this)
├── mcp/                          # MCP server
│   ├── server.py                 # FastMCP server — add your tools here
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yaml           # Standalone deployment
├── mateclaw.agent.json           # Mateclaw platform manifest
└── .gitignore
```

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Google Gemini API Key **or** LiteLLM-compatible provider

### Standalone

```bash
git clone https://github.com/MateClawAI/mateclaw-agent-template.git
cd mateclaw-agent-template

# Set your API key
export GOOGLE_API_KEY=your_key_here

# Start
docker compose up -d --build
```

The agent will be available at `http://localhost:8081`.

### Via Mateclaw Platform

```bash
mateclaw agent deploy --local /path/to/your-agent
```

Mateclaw reads `mateclaw.agent.json`, builds and starts the containers, and registers the agent automatically.

---

## Customisation Guide

Search for all `TODO` comments across the project — each marks a decision point specific to your agent:

### 1. Rename identifiers

| Find | Replace with |
|------|--------------|
| `template_agent` | `your_agent_name` (snake_case, in Python files) |
| `template-agent` | `your-agent-name` (kebab-case, in YAML / JSON) |
| `mcp-template` | `mcp-your-agent` (kebab-case) |
| `TEMPLATE_` | `YOUR_AGENT_` (SCREAMING_SNAKE_CASE, env var prefix) |
| `template_data` | `your_agent_data` (Docker volume name) |

### 2. Write your MCP tools (`mcp/server.py`)

- Remove or rename the `example_*` tools
- Add tools that give the agent access to the data, APIs, or capabilities it needs
- Every tool must have a clear docstring — the LLM reads it to decide when to call the tool

### 3. Write your system prompt (`agent/utils/instructions/agent_instruction.md`)

- Replace the placeholder content with your agent's identity, role, and workflow
- Reference your actual tool names in the Tool Usage Guide table

### 4. Update manifests

- `mateclaw.agent.json` — update `name`, `description`, env var names
- `docker-compose.yaml` — update service names, env vars, volume name

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | ✅ | — | Google Gemini API key |
| `TEMPLATE_AGENT_MODEL` | ❌ | `gemini-2.5-flash` | Model name for Gemini provider |
| `MATECLAW_AGENT_MODEL_PROVIDER` | ❌ | `gemini` | `gemini` or `litellm` |
| `LITELLM_MODEL_NAME` | ❌ | — | Model name for LiteLLM provider |
| `LITELLM_API_BASE` | ❌ | — | LiteLLM API base URL |
| `LITELLM_API_KEY` | ❌ | — | LiteLLM API key |
| `MCP_TEMPLATE_URL` | ❌ | `http://mcp-template:8082/sse` | Internal MCP server URL |
| `TEMPLATE_WORKSPACE_DIR` | ❌ | `/app/data/workspace` | Shared data directory |
| `TEMPLATE_AGENT_MCP_URLS` | ❌ | — | JSON dict of extra MCP servers |

---

## MCP Extensions

Additional MCPs (databases, search APIs, internal tools) can be assigned dynamically from the **Mateclaw dashboard** under `Agents → your-agent → MCP Extensions → Apply & Restart` — no redeployment needed.

Extra MCPs are passed via the `TEMPLATE_AGENT_MCP_URLS` environment variable as a JSON dict:

```json
{
  "my-db-mcp": {
    "url": "https://my-db-mcp.internal/mcp",
    "transport": "streamable",
    "headers": { "Authorization": "Bearer ..." }
  }
}
```

Supported transports: `sse` (URL contains `/sse`) and `streamable` (default).

---

## mateclaw.agent.json

This manifest declares the agent's identity and capabilities to the Mateclaw platform:

```json
{
  "name": "your-agent-name",
  "version": "1.0.0",
  "description": "One-sentence description of what this agent does.",
  "a2a_service": "your-agent-name",
  "port": 8081,
  "env_required": ["GOOGLE_API_KEY"],
  "mcp_configurable": true,
  "mcp_env_var": "YOUR_AGENT_MCP_URLS"
}
```

---

## License

Distributed under the MIT License. See `LICENSE` for details.
