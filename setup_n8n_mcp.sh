#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${REPO_ROOT}/config/n8n_mcp.env"
MCP_TARGET="${HOME}/.cursor/mcp.json"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Run setup_n8n_mcp.py first to create the API key."
  exit 1
fi

# shellcheck disable=SC1090
set -a
source "${ENV_FILE}"
set +a

mkdir -p "${HOME}/.cursor"

python3 - <<'PY'
import json
import os
from pathlib import Path

home = Path(os.environ["HOME"])
target = home / ".cursor" / "mcp.json"
env_file = Path(os.environ["REPO_ROOT"]) / "config" / "n8n_mcp.env"

values = {}
for line in env_file.read_text().splitlines():
    if "=" in line:
        k, v = line.split("=", 1)
        values[k.strip()] = v.strip()

config = {"mcpServers": {}}
if target.exists():
    try:
        config = json.loads(target.read_text())
        config.setdefault("mcpServers", {})
    except json.JSONDecodeError:
        pass

config["mcpServers"]["n8n-mcp"] = {
    "command": "npx",
    "args": ["-y", "n8n-mcp"],
    "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": values["N8N_API_URL"],
        "N8N_API_KEY": values["N8N_API_KEY"],
    },
}

target.write_text(json.dumps(config, indent=2) + "\n")
print(f"Configured n8n-mcp in {target}")
PY

echo "Restart Cursor or reload MCP servers to apply."
