---
name: foundry-agent
description: Call Microsoft Foundry agents. Use when user asks to rate a task or call a Foundry agent. Just run the Python script with --quiet flag.
license: MIT
---

# Microsoft Foundry Agent Skill

Call AI agents deployed in Microsoft Foundry from Copilot CLI.

## Prerequisites

```bash
pip install azure-ai-projects azure-identity
az login
export PROJECT_ENDPOINT="https://your-resource.services.ai.azure.com/api/projects/your-project"
```

## Usage

Call agent:
```bash
python scripts/call_agent.py --quiet "Rate my task: fix the bug"
```

List agents:
```bash
python scripts/call_agent.py --list
```

## Configuration

Set `PROJECT_ENDPOINT` environment variable or create `.env` file:
```
PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
AGENT_NAME=ratemytask
```
