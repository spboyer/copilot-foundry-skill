#!/usr/bin/env python3
"""
Call an existing Microsoft Foundry agent with a message.
Uses AzureDefaultCredential for authentication.

NOTE: This script automatically uses the .venv if it exists in the skill directory.
"""

import os
import sys

# Auto-activate venv if available
def _activate_venv():
    """Activate the skill's virtual environment if it exists."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)  # foundry-agent/
    project_root = os.path.dirname(skill_dir)  # copilot-foundry-skill/
    venv_python = os.path.join(project_root, '.venv', 'bin', 'python')
    
    # If we're not running from the venv and it exists, re-exec with venv python
    if os.path.exists(venv_python) and sys.executable != venv_python:
        os.execv(venv_python, [venv_python] + sys.argv)

_activate_venv()

import argparse
import os
import sys
from pathlib import Path


def load_env_file():
    """Load .env file from the script's directory or parent."""
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent  # foundry-agent/
    project_root = skill_dir.parent  # copilot-foundry-skill/
    
    # Look for .env in multiple locations
    env_locations = [
        project_root / ".env",        # copilot-foundry-skill/.env (project root)
        skill_dir / ".env",           # foundry-agent/.env
        script_dir / ".env",          # foundry-agent/scripts/.env
        Path.cwd() / ".env",          # current working directory
    ]
    
    for env_path in env_locations:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and value and key not in os.environ:
                            os.environ[key] = value
            return str(env_path)
    return None


# Load .env file before reading environment variables
_env_file = load_env_file()

# Configuration via environment variables (no defaults for sensitive values)
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_NAME = os.environ.get("AGENT_NAME", "ratemytask")


def check_azure_cli_installed() -> bool:
    """Check if Azure CLI is installed."""
    import subprocess
    try:
        result = subprocess.run(
            ["az", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_environment(quiet: bool = False) -> bool:
    """Verify required environment variables are set."""
    global PROJECT_ENDPOINT
    PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
    
    if not PROJECT_ENDPOINT:
        if not quiet:
            print("ERROR: PROJECT_ENDPOINT environment variable is required.")
            if _env_file:
                print(f"\nLoaded .env from: {_env_file}")
                print("But PROJECT_ENDPOINT was not found or is empty.")
            else:
                print("\nNo .env file found. Looked in:")
                print(f"  - {Path(__file__).parent.parent}/.env")
                print(f"  - {Path.cwd()}/.env")
            print("\nSet it with:")
            print('  export PROJECT_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/<project>"')
            print("\nOr add to your .env file:")
            print('  PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>')
        else:
            print("ERROR: PROJECT_ENDPOINT not configured", file=sys.stderr)
        return False
    
    if _env_file and not quiet:
        print(f"Loaded config from: {_env_file}")
    return True


def check_auth() -> bool:
    """Quick auth check before making API calls."""
    script_dir = Path(__file__).parent
    
    # First check if Azure CLI is installed
    if not check_azure_cli_installed():
        print("ERROR: Azure CLI is not installed.")
        print("\nInstall it:")
        print("  macOS:   brew install azure-cli")
        print("  Windows: winget install Microsoft.AzureCLI")
        print("  Linux:   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash")
        print(f"\nOr run setup: python {script_dir}/setup.py")
        return False
    
    try:
        from azure.identity import DefaultAzureCredential
        from azure.core.exceptions import ClientAuthenticationError
    except ImportError:
        print("ERROR: Required Python packages not installed.")
        print(f"\nRun setup: python {script_dir}/setup.py")
        print("\nOr install manually:")
        print("  pip install --pre 'azure-ai-projects>=2.0.0b1' azure-identity")
        return False
    
    try:
        credential = DefaultAzureCredential()
        credential.get_token("https://management.azure.com/.default")
        return True
    except ClientAuthenticationError:
        print("ERROR: Not authenticated with Azure.")
        print("\nRun: az login")
        print(f"\nOr run setup: python {script_dir}/setup.py")
        return False
    except Exception as e:
        print(f"ERROR: Authentication failed: {e}")
        return False


def call_agent(message: str, agent_name: str = None) -> str:
    """Call an existing Foundry agent and get a response."""
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    
    agent_name = agent_name or AGENT_NAME
    
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    
    # Get the existing agent
    agent = project_client.agents.get(agent_name=agent_name)
    
    # Get OpenAI client for responses API
    openai_client = project_client.get_openai_client()
    
    # Call the agent using responses.create with agent reference
    response = openai_client.responses.create(
        input=message,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )
    
    return response.output_text


def call_agent_streaming(message: str, agent_name: str = None):
    """Call an existing Foundry agent with streaming response."""
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    
    agent_name = agent_name or AGENT_NAME
    
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    
    # Get the existing agent
    agent = project_client.agents.get(agent_name=agent_name)
    
    # Get OpenAI client for responses API
    openai_client = project_client.get_openai_client()
    
    # Call the agent with streaming
    with openai_client.responses.stream(
        input=message,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    ) as stream:
        for event in stream:
            if hasattr(event, 'delta') and event.delta:
                yield event.delta


def interactive_mode(agent_name: str = None):
    """Run an interactive conversation with the agent."""
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    
    agent_name = agent_name or AGENT_NAME
    
    print(f"Starting interactive session with agent: {agent_name}")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    
    # Get the existing agent
    agent = project_client.agents.get(agent_name=agent_name)
    openai_client = project_client.get_openai_client()
    
    # Maintain conversation history
    conversation = []
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEnding session.")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ('exit', 'quit'):
            print("Ending session.")
            break
        
        # Add to conversation
        conversation.append({"role": "user", "content": user_input})
        
        # Get response
        response = openai_client.responses.create(
            input=conversation,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        
        # Add assistant response to history
        conversation.append({"role": "assistant", "content": response.output_text})
        
        print(f"\nAgent: {response.output_text}")


def list_agents():
    """List all available agents in the project."""
    from azure.identity import DefaultAzureCredential
    from azure.ai.projects import AIProjectClient
    
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=DefaultAzureCredential(),
    )
    
    print(f"Agents in {PROJECT_ENDPOINT}:\n")
    for agent in project_client.agents.list(limit=50):
        print(f"  - {agent.name}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Call an existing Microsoft Foundry agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python call_agent.py "Rate my task: write unit tests"
  python call_agent.py --agent ratemytask "Rate my task: refactor the auth module"
  python call_agent.py --list
  python call_agent.py --interactive
  python call_agent.py --stream "Tell me about yourself"

Environment Variables:
  PROJECT_ENDPOINT  - Foundry project endpoint (default: shboyer-copilot-proj)
  AGENT_NAME        - Default agent name (default: ratemytask)
        """
    )
    parser.add_argument(
        "message",
        nargs="*",
        help="Message to send to the agent"
    )
    parser.add_argument(
        "-a", "--agent",
        default=None,
        help=f"Agent name to call (default: {AGENT_NAME})"
    )
    parser.add_argument(
        "-s", "--stream",
        action="store_true",
        help="Stream the response as it's generated"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start an interactive conversation"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List available agents"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress diagnostic output, only show agent response"
    )
    
    args = parser.parse_args()
    
    # Check environment variables first
    if not check_environment(quiet=args.quiet):
        return 1
    
    # Check auth (silently if --quiet)
    if not args.quiet:
        if not check_auth():
            return 1
    else:
        # Quick silent auth check
        try:
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential()
            credential.get_token("https://management.azure.com/.default")
        except:
            print("ERROR: Authentication failed. Run: az login", file=sys.stderr)
            return 1
    
    try:
        if args.list:
            list_agents()
            return 0
        
        if args.interactive:
            interactive_mode(args.agent)
            return 0
        
        if not args.message:
            print("ERROR: Message is required. Use -h for help.")
            return 1
        
        message = " ".join(args.message)
        agent_name = args.agent or AGENT_NAME
        
        if not args.quiet:
            print(f"Agent: {agent_name}")
            print(f"Message: {message}\n")
        
        if args.stream:
            if not args.quiet:
                print("Response: ", end="", flush=True)
            for chunk in call_agent_streaming(message, agent_name):
                print(chunk, end="", flush=True)
            print()
        else:
            response = call_agent(message, agent_name)
            if args.quiet:
                print(response)
            else:
                print(f"Response:\n{response}")
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
