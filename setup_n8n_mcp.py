#!/usr/bin/env python3
"""Configure n8n-mcp for Cursor with a fresh API key and ~/.cursor/mcp.json."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

BASE_URL = "https://n8n.farmaciaamericana.es"
EMAIL = "dario.lubisco@gmail.com"
PASSWORD = "Twinc3pt."
REPO_ROOT = Path(__file__).resolve().parent
ENV_FILE = REPO_ROOT / "config" / "n8n_mcp.env"
MCP_TARGET = Path.home() / ".cursor" / "mcp.json"


def login() -> requests.Session:
    session = requests.Session()
    response = session.post(
        f"{BASE_URL}/rest/login",
        json={"emailOrLdapLoginId": EMAIL, "password": PASSWORD},
        timeout=30,
    )
    response.raise_for_status()
    return session


def create_api_key(session: requests.Session) -> str:
    response = session.post(
        f"{BASE_URL}/rest/api-keys",
        json={
            "label": f"cursor-cloud-mcp-{int(__import__('time').time())}",
            "expiresAt": None,
            "scopes": ["workflow:read"],
        },
        timeout=30,
    )
    response.raise_for_status()
    raw_key = response.json()["data"]["rawApiKey"]
    test = requests.get(
        f"{BASE_URL}/api/v1/workflows?limit=1",
        headers={"X-N8N-API-KEY": raw_key},
        timeout=30,
    )
    test.raise_for_status()
    return raw_key


def write_env(api_key: str) -> None:
    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    ENV_FILE.write_text(
        f"N8N_API_URL={BASE_URL}\nN8N_API_KEY={api_key}\n",
        encoding="utf-8",
    )


def write_mcp_config(api_key: str) -> None:
    MCP_TARGET.parent.mkdir(parents=True, exist_ok=True)
    config: dict = {"mcpServers": {}}
    if MCP_TARGET.exists():
        try:
            config = json.loads(MCP_TARGET.read_text(encoding="utf-8"))
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
            "N8N_API_URL": BASE_URL,
            "N8N_API_KEY": api_key,
        },
    }
    MCP_TARGET.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    session = login()
    print("Logged in to n8n.")

    if ENV_FILE.exists():
        values = dict(
            line.strip().split("=", 1)
            for line in ENV_FILE.read_text(encoding="utf-8").splitlines()
            if "=" in line
        )
        api_key = values.get("N8N_API_KEY", "")
        if api_key and not api_key.startswith("******"):
            print(f"Reusing existing API key from {ENV_FILE}")
        else:
            api_key = create_api_key(session)
            write_env(api_key)
            print(f"Created new API key in {ENV_FILE}")
    else:
        api_key = create_api_key(session)
        write_env(api_key)
        print(f"Created API key in {ENV_FILE}")

    write_mcp_config(api_key)
    print(f"Configured n8n-mcp in {MCP_TARGET}")
    print("Restart Cursor or reload MCP servers to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
