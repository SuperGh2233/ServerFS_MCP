#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
BRIDGE_BIN=${SERVERFS_AGENT_BRIDGE_BIN:-"$REPO_ROOT/agent_bridge/.venv/bin/serverfs-agent-bridge"}
CONFIG=${1:-"$HOME/.config/serverfs-agent-bridge/config.json"}

if [ "$(uname -s)" != "Darwin" ]; then
  echo "run_macos_bridge.sh is only for macOS" >&2
  exit 2
fi
if [ ! -x "$BRIDGE_BIN" ]; then
  echo "Agent Bridge executable is missing; create agent_bridge/.venv and install the locked dependencies" >&2
  exit 2
fi
if [ ! -f "$CONFIG" ]; then
  echo "Agent Bridge config file does not exist" >&2
  exit 2
fi

exec "$BRIDGE_BIN" --config "$CONFIG"
