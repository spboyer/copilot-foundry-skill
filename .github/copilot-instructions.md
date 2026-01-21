# Copilot Foundry Skill

This repository contains a skill for GitHub Copilot CLI that calls Microsoft Foundry agents.

## Project Structure

```
copilot-foundry-skill/
├── README.md                              # Human documentation
└── .github/
    ├── copilot-instructions.md            # This file
    └── skills/
        └── foundry-agent/
            ├── SKILL.md                   # Skill definition
            ├── requirements.txt           # Python dependencies
            ├── .venv/                     # Virtual environment (created by setup.py)
            └── scripts/
                ├── setup.py               # Interactive setup
                ├── check_auth.py          # Verify Azure authentication
                └── call_agent.py          # Call Foundry agents
```

## Quick Start

```bash
# Run setup first (one-time)
python .github/skills/foundry-agent/scripts/setup.py

# Test the skill
python .github/skills/foundry-agent/scripts/call_agent.py "Rate my task: write unit tests"
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `PROJECT_ENDPOINT` | **Yes** | Foundry project endpoint URL |
| `AGENT_NAME` | No | Default agent to call (default: `ratemytask`) |

## API Pattern

The skill uses `azure-ai-projects>=2.0.0b1` with the OpenAI responses API:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

client = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
agent = client.agents.get(agent_name="ratemytask")
openai_client = client.get_openai_client()

response = openai_client.responses.create(
    input=[{"role": "user", "content": "Your message"}],
    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
)
print(response.output_text)
```

## Key Details

- **Azure CLI**: Required for authentication
- **Auth**: Uses `AzureDefaultCredential` (env vars → managed identity → Azure CLI → VS Code)
- **SDK**: Requires `azure-ai-projects>=2.0.0b1` (pre-release) for the responses API

## Sample Test Phrases

**HIGH Priority:**
- "Rate my task: Production database is completely down."
- "Rate my task: Security breach detected."

**MEDIUM Priority:**
- "Rate my task: Weekly sales report is taking 3x longer than usual."

**LOW Priority:**
- "Rate my task: Update footer copyright year from 2025 to 2026."
