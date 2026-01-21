#!/bin/bash
# Quick wrapper for calling a Foundry agent with minimal output
# Usage: quick_call.sh "your message here"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Check if .venv exists
if [ -d "$SKILL_DIR/../.venv" ]; then
    PYTHON="$SKILL_DIR/../.venv/bin/python"
elif [ -d "$SKILL_DIR/.venv" ]; then
    PYTHON="$SKILL_DIR/.venv/bin/python"
else
    PYTHON="python3"
fi

# Call the agent with quiet mode
exec "$PYTHON" "$SCRIPT_DIR/call_agent.py" --quiet "$@"
