#!/usr/bin/env python3
"""Deploy ITS ETL workflow fix: remove Telegram spam on successful runs."""

import json
import os
import sys
import time

import requests

BASE_URL = "https://n8n.farmaciaamericana.es/rest"
EMAIL = "dario.lubisco@gmail.com"
PASSWORD = "Twinc3pt."
WORKFLOW_ID = "iwGP7AAVElhWT4Ob"
WORKFLOW_PATH = os.path.join(os.path.dirname(__file__), "workflows", f"{WORKFLOW_ID}.json")


def login(session: requests.Session) -> None:
    for attempt in range(5):
        resp = session.post(
            f"{BASE_URL}/login",
            json={"email": EMAIL, "password": PASSWORD},
        )
        if resp.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        resp.raise_for_status()
        return
    raise RuntimeError("No se pudo autenticar en n8n (rate limit).")


def main() -> int:
    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        workflow = json.load(f)

    session = requests.Session()
    login(session)

    os.makedirs("backup_workflows", exist_ok=True)
    current = session.get(f"{BASE_URL}/workflows/{WORKFLOW_ID}").json()["data"]
    backup_path = f"backup_workflows/before_its_fix_{WORKFLOW_ID}.json"
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
    print(f"Backup guardado en {backup_path}")

    payload = {
        "name": workflow["name"],
        "nodes": workflow["nodes"],
        "connections": workflow["connections"],
        "settings": workflow.get("settings", {}),
        "staticData": workflow.get("staticData"),
    }

    resp = session.patch(f"{BASE_URL}/workflows/{WORKFLOW_ID}", json=payload)
    resp.raise_for_status()
    print("Workflow ITS actualizado en n8n.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
