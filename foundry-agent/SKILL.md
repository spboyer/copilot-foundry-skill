---
name: foundry-agent
description: Call existing Microsoft Foundry agents from VS Code. Use this skill when: (1) User asks to call, invoke, or query a Foundry agent, (2) User mentions "ratemytask" or rating tasks, (3) User wants to interact with AI agents deployed in Microsoft Foundry or Azure AI, (4) User asks about Foundry agent capabilities, (5) User mentions "rate my task", "task rating", or productivity assessment. Handles Azure authentication automatically via AzureDefaultCredential, prompting for az login if needed. Keywords: foundry, agent, ratemytask, rate task, azure ai, microsoft foundry, call agent, invoke agent.
license: MIT
---

# Microsoft Foundry Agent Skill

This skill enables you to call existing AI agents deployed in Microsoft Foundry directly from Claude in VS Code.

## Skill Installation

**First-time setup (interactive):**
```bash
python scripts/setup.py
```

This will install dependencies, check Azure CLI, and configure your environment.

**Global (all workspaces):**
```bash
cp -r foundry-agent ~/.copilot/skills/
```

**Local (this workspace only):** The skill is auto-discovered from this folder.

## Authentication

Authentication uses `AzureDefaultCredential` which automatically tries:
1. Environment variables (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`)
2. Managed Identity (if running in Azure)
3. Azure CLI credentials (`az login`)
4. VS Code Azure extension credentials

**Before calling an agent**, run the auth check script to verify credentials:
```bash
python scripts/check_auth.py
```

If not authenticated, the script will prompt you to run `az login`.

## Environment Setup

Required environment variables:
- `PROJECT_ENDPOINT`: Your Foundry project endpoint (e.g., `https://<resource>.services.ai.azure.com/api/projects/<project>`)

Optional:
- `AGENT_NAME`: Name of the agent to call (default: `ratemytask`)

```bash
cp .env.example .env
# Edit .env with your PROJECT_ENDPOINT, then:
source .env
```

## Usage

### Check Authentication
```bash
python scripts/check_auth.py
```

### List Available Agents
```bash
python scripts/call_agent.py --list
```

### Call an Agent
```bash
python scripts/call_agent.py "Rate my task: write unit tests for auth module"
```

### Call a Specific Agent
```bash
python scripts/call_agent.py --agent ratemytask "Rate my task: refactor the login flow"
```

### Multi-Turn Conversation
```bash
python scripts/call_agent.py --interactive
```

### Stream Response
```bash
python scripts/call_agent.py --stream "Tell me about yourself"
```

## Script Reference

| Script | Purpose |
|--------|---------|
| `scripts/setup.py` | Interactive setup: install deps, verify Azure CLI, configure .env |
| `scripts/check_auth.py` | Verify Azure authentication, run `az login` if needed |
| `scripts/call_agent.py` | Send messages to an existing Foundry agent |

## API Pattern

The skill uses the `azure-ai-projects` SDK to call existing agents:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

project_client = AIProjectClient(
    endpoint="https://<resource>.services.ai.azure.com/api/projects/<project>",
    credential=DefaultAzureCredential(),
)

# Get existing agent
agent = project_client.agents.get(agent_name="your-agent-name")

# Call agent via OpenAI responses API
openai_client = project_client.get_openai_client()
response = openai_client.responses.create(
    input=[{"role": "user", "content": "Your message"}],
    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
)
print(response.output_text)
```

## Error Handling

The scripts handle common errors:
- **Authentication failure**: Prompts for `az login`
- **Agent not found**: Lists available agents
- **Network errors**: Shows clear error messages

## Dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

Or install directly:
```bash
pip install --pre "azure-ai-projects>=2.0.0b1" azure-identity
```
