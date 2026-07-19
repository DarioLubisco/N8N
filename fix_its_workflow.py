#!/usr/bin/env python3
"""
Deploy ITS ETL workflow fix using n8n Public API v1 (same interface as n8n-mcp).

Requires:
  export N8N_API_URL=https://n8n.farmaciaamericana.es
  export N8N_API_KEY=<key from n8n Settings > API>

Falls back to REST session auth if N8N_API_KEY is not set (legacy).
"""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any

import requests

WORKFLOW_ID = "iwGP7AAVElhWT4Ob"
WORKFLOW_PATH = os.path.join(os.path.dirname(__file__), "workflows", f"{WORKFLOW_ID}.json")
N8N_API_URL = os.environ.get("N8N_API_URL", "https://n8n.farmaciaamericana.es").rstrip("/")
N8N_API_KEY = os.environ.get("N8N_API_KEY", "")
REST_EMAIL = os.environ.get("N8N_REST_EMAIL", "dario.lubisco@gmail.com")
REST_PASSWORD = os.environ.get("N8N_REST_PASSWORD", "Twinc3pt.")


def _headers() -> dict[str, str]:
    if not N8N_API_KEY:
        raise RuntimeError(
            "N8N_API_KEY no configurada. Crear en n8n > Settings > API "
            "y exportarla, o usar el MCP n8n-mcp (ver config/mcp.json)."
        )
    return {"X-N8N-API-KEY": N8N_API_KEY, "Content-Type": "application/json"}


def get_workflow(session: requests.Session) -> dict[str, Any]:
    resp = session.get(f"{N8N_API_URL}/api/v1/workflows/{WORKFLOW_ID}", headers=_headers())
    resp.raise_for_status()
    return resp.json()


def update_workflow(session: requests.Session, payload: dict[str, Any]) -> dict[str, Any]:
    resp = session.put(
        f"{N8N_API_URL}/api/v1/workflows/{WORKFLOW_ID}",
        headers=_headers(),
        json=payload,
    )
    resp.raise_for_status()
    return resp.json()


def activate_workflow(session: requests.Session) -> None:
    resp = session.post(
        f"{N8N_API_URL}/api/v1/workflows/{WORKFLOW_ID}/activate",
        headers=_headers(),
    )
    resp.raise_for_status()


def load_local_workflow() -> dict[str, Any]:
    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        return json.load(f)


def build_payload(local: dict[str, Any], remote: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": local["name"],
        "nodes": local["nodes"],
        "connections": local["connections"],
        "settings": local.get("settings", {}),
        "staticData": local.get("staticData", remote.get("staticData")),
    }


def main() -> int:
    local = load_local_workflow()
    session = requests.Session()

    os.makedirs("backup_workflows", exist_ok=True)
    remote = get_workflow(session)
    backup_path = f"backup_workflows/before_its_fix_{WORKFLOW_ID}.json"
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(remote, f, indent=2, ensure_ascii=False)
    print(f"Backup guardado en {backup_path}")

    payload = build_payload(local, remote)
    updated = update_workflow(session, payload)
    print(f"Workflow actualizado vía API v1 (n8n-mcp compatible). Nodos: {len(updated.get('nodes', []))}")

    activate_workflow(session)
    print("Workflow activado correctamente.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except requests.HTTPError as exc:
        print(f"HTTP error: {exc.response.status_code} {exc.response.text[:500]}", file=sys.stderr)
        sys.exit(1)
