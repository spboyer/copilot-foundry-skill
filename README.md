# Copilot Foundry Skill

A skill for GitHub Copilot CLI and VS Code that calls Microsoft Foundry agents. This skill enables you to interact with AI agents deployed in Microsoft Foundry directly from your development environment.

## What It Does

This skill provides a bridge between Copilot and Microsoft Foundry agents. When you ask Copilot to rate a task, call an agent, or interact with Foundry, it automatically:

1. Checks your Azure authentication status
2. Connects to your Foundry project
3. Calls the specified agent with your message
4. Returns the agent's response

The default agent is `ratemytask`, which analyzes tasks and assigns priority levels based on urgency, impact, and business value.

## Prerequisites

- Python 3.9+
- **Azure CLI** (required for authentication)
- Access to a Microsoft Foundry project with deployed agents

### Installing Azure CLI

The Azure CLI is **required** for authentication. Install it for your platform:

| Platform | Command |
|----------|---------|
| **macOS** | `brew install azure-cli` |
| **Windows** | `winget install Microsoft.AzureCLI` |
| **Ubuntu/Debian** | `curl -sL https://aka.ms/InstallAzureCLIDeb \| sudo bash` |
| **Other Linux** | See [official docs](https://docs.microsoft.com/cli/azure/install-azure-cli) |

Verify installation:

```bash
az --version
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/shboyer/copilot-foundry-skill.git
cd copilot-foundry-skill
```

### 2. Run Setup

```bash
# Run the interactive setup script
python .github/skills/foundry-agent/scripts/setup.py
```

The setup script will:
- Check Python version (3.9+ required)
- Create a virtual environment
- Install required Azure packages
- Verify Azure CLI is installed
- Log you into Azure if needed
- Create your `.env` configuration file

### 3. Configure Environment

Edit `.github/skills/foundry-agent/.env` with your Foundry project details:

```bash
# Required: Your Foundry project endpoint
PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project

# Optional: Default agent name
AGENT_NAME=ratemytask
```

## Installing the Skill

### For GitHub Copilot CLI (Recommended)

GitHub Copilot CLI discovers skills from `.github/skills/` in your repository:

```
your-repo/
└── .github/
    └── skills/
        └── foundry-agent/
            ├── SKILL.md           # Skill definition
            ├── requirements.txt   # Dependencies
            ├── .env              # Your configuration (gitignored)
            └── scripts/
                ├── setup.py       # Interactive setup
                ├── call_agent.py  # Main script
                └── check_auth.py  # Auth verification
```

**Option A: Use in this repo**

The skill is already set up at `.github/skills/foundry-agent/`. Just run setup and use Copilot CLI:

```bash
# 1. Run setup
python .github/skills/foundry-agent/scripts/setup.py

# 2. Start Copilot CLI in this directory
copilot

# 3. Ask Copilot to rate your task
> rate my task: fix the login bug
```

**Option B: Copy to another repo**

Copy the skill to any repository you want to use it in:

```bash
# Copy skill directory to your project
cp -r .github/skills/foundry-agent /path/to/your-project/.github/skills/

# Run setup in the new location
python /path/to/your-project/.github/skills/foundry-agent/scripts/setup.py
```

**Option C: Global installation (VS Code)**

For use across all VS Code workspaces:

```bash
mkdir -p ~/.copilot/skills
cp -r .github/skills/foundry-agent ~/.copilot/skills/
python ~/.copilot/skills/foundry-agent/scripts/setup.py
```

## Usage

### In GitHub Copilot CLI

Start Copilot CLI in a directory containing the skill:

```bash
copilot
```

Then ask naturally:

- `rate my task: deploy the new feature to production`
- `call the ratemytask agent to prioritize this: customer data export is failing`
- `use foundry to rate this task: add dark mode to the dashboard`

### Command Line (Direct)

```bash
# Basic usage
python .github/skills/foundry-agent/scripts/call_agent.py "Rate my task: fix the login bug"

# Call a specific agent
python .github/skills/foundry-agent/scripts/call_agent.py --agent ratemytask "Update the docs"

# List available agents
python .github/skills/foundry-agent/scripts/call_agent.py --list

# Interactive conversation
python .github/skills/foundry-agent/scripts/call_agent.py --interactive
```

## Sample Phrases for Testing

### HIGH Priority (Urgent/Emergency)

These should be rated as high priority due to immediate business impact:

```
"Rate my task: Production database is completely down. Customers cannot login or access their accounts. Estimated revenue loss $50K/hour."

"Rate my task: Security breach detected - unauthorized access to customer payment data. Need immediate incident response."

"Rate my task: Main website returning 500 errors for all users. E-commerce checkout completely broken."

"Rate my task: Payment processing system is rejecting all credit cards. Orders are being abandoned."

"Rate my task: Critical memory leak causing servers to crash every 30 minutes. Auto-scaling cannot keep up."
```

### MEDIUM Priority (Important but not emergency)

These should be rated as medium priority - important but not blocking:

```
"Rate my task: The weekly sales report is taking 3x longer than usual to generate. Not blocking anything but should be fixed before next Monday's board meeting."

"Rate my task: Search results are showing some outdated products. Customers are complaining but can still complete purchases."

"Rate my task: Need to upgrade the authentication library before the deprecation date in 2 weeks."

"Rate my task: Mobile app performance has degraded by 20% after the last update. Users are noticing but app is functional."

"Rate my task: Email notifications are delayed by 2-3 hours. Not critical but affecting user experience."
```

### LOW Priority (Nice-to-have/Backlog)

These should be rated as low priority - improvements for when time permits:

```
"Rate my task: Update the footer copyright year from 2025 to 2026 when someone has time."

"Rate my task: The internal admin dashboard could use a dark mode option for the team."

"Rate my task: Consider adding a 'favorite' button to the product listing page for future enhancement."

"Rate my task: Refactor the legacy utility functions to use modern JavaScript syntax."

"Rate my task: Add more unit tests to the user service module for better coverage."
```

### Edge Cases for Testing

```
"Rate my task: I need to do something but I'm not sure what it is yet."

"Rate my task: Fix everything."

"Rate my task: The CEO wants this done yesterday but it's just changing a button color."

"Rate my task: Minor bug that affects 0.01% of users but those users are our biggest enterprise clients."
```

## Project Structure

```
copilot-foundry-skill/
├── README.md                              # This file
├── .gitignore                             # Excludes .env and secrets
└── .github/
    ├── copilot-instructions.md            # Copilot context for this repo
    └── skills/
        └── foundry-agent/
            ├── SKILL.md                   # Skill definition (name, description, instructions)
            ├── requirements.txt           # Python dependencies
            ├── .env.example               # Environment template
            └── scripts/
                ├── setup.py               # Interactive setup wizard
                ├── call_agent.py          # Main agent caller
                └── check_auth.py          # Azure auth verification
```

## How It Works

### Skill Discovery

GitHub Copilot CLI automatically discovers skills from `.github/skills/` directories. Each skill must have:

1. **SKILL.md** - Contains:
   - `name`: Unique identifier
   - `description`: When to use this skill (triggers invocation)
   - Instructions for how to use the skill

2. **Supporting files** - Scripts, configs, and resources the skill needs

### API Pattern

The skill uses the `azure-ai-projects` SDK (v2 beta) with the OpenAI responses API:

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Connect to Foundry
client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

# Get existing agent
agent = client.agents.get(agent_name="ratemytask")

# Call via OpenAI responses API
openai_client = client.get_openai_client()
response = openai_client.responses.create(
    input=[{"role": "user", "content": "Your message"}],
    extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
)
print(response.output_text)
```

## Troubleshooting

### "Azure CLI is not installed" error

The skill requires Azure CLI for authentication. Install it:

```bash
# macOS
brew install azure-cli

# Windows
winget install Microsoft.AzureCLI

# Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

Then verify with `az --version`.

### "Not authenticated" error

```bash
# Re-authenticate with Azure
az login

# Verify authentication
python scripts/check_auth.py
```

### "Agent not found" error

```bash
# List available agents
python scripts/call_agent.py --list

# Check you're using the correct endpoint
echo $PROJECT_ENDPOINT
```

### SDK/Import errors

```bash
# Ensure you have the pre-release SDK
pip install --pre "azure-ai-projects>=2.0.0b1" azure-identity
```

### Timeout or connection errors

- Verify your network can reach Azure services
- Check if you're behind a corporate proxy
- Ensure the Foundry project endpoint is correct

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the sample phrases above
5. Submit a pull request

## License

MIT
