#!/bin/bash
# Quick wrapper for calling a Foundry agent
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/call_agent.py" --quiet "$@"
