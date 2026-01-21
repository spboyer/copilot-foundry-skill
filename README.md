# Copilot Foundry Skill

Call Microsoft Foundry agents from GitHub Copilot CLI.

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/spboyer/copilot-foundry-skill.git
cd copilot-foundry-skill/foundry-agent
python -m venv .venv
.venv/bin/pip install azure-ai-projects azure-identity

# 2. Configure
echo 'PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project' > .env

# 3. Login to Azure
az login

# 4. Run
python call_agent_simple.py "Rate my task: fix the login bug"
```

## Install as Global Skill

```bash
mkdir -p ~/.copilot/skills
cp -r foundry-agent ~/.copilot/skills/
```

## Usage

```bash
python call_agent_simple.py "Rate my task: deploy new feature"
```

The script automatically:
- Uses the `.venv` if it exists
- Reads config from `.env` file
- Calls the Foundry agent
- Prints the response

## Configuration

Create `.env` in the skill directory:
```
PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
AGENT_NAME=ratemytask
```

## License

MIT
