#!/usr/bin/env python3
"""Deploy ITS ETL fix: remove stale schedule trigger and refresh workflow activation."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

BASE_URL = "https://n8n.farmaciaamericana.es/rest"
EMAIL = "dario.lubisco@gmail.com"
PASSWORD = "Twinc3pt."
WORKFLOW_ID = "iwGP7AAVElhWT4Ob"
WORKFLOW_PATH = Path(__file__).resolve().parent / "workflows" / f"{WORKFLOW_ID}.json"


def login() -> requests.Session:
    session = requests.Session()
    response = session.post(
        f"{BASE_URL}/login",
        json={"emailOrLdapLoginId": EMAIL, "password": PASSWORD},
        timeout=30,
    )
    response.raise_for_status()
    return session


def deploy(session: requests.Session) -> None:
    with WORKFLOW_PATH.open(encoding="utf-8") as handle:
        local_workflow = json.load(handle)

    response = session.get(f"{BASE_URL}/workflows/{WORKFLOW_ID}", timeout=30)
    response.raise_for_status()
    remote_workflow = response.json()["data"]

    remote_workflow["nodes"] = local_workflow["nodes"]
    remote_workflow["connections"] = local_workflow["connections"]
    remote_workflow["settings"] = local_workflow.get("settings", remote_workflow.get("settings", {}))
    remote_workflow["staticData"] = local_workflow.get("staticData", {})

    patch = session.patch(f"{BASE_URL}/workflows/{WORKFLOW_ID}", json=remote_workflow, timeout=60)
    patch.raise_for_status()
    print("Workflow actualizado.")

    # Refresh scheduler to drop ghost trigger from legacy FTP workflow.
    deactivate = session.patch(
        f"{BASE_URL}/workflows/{WORKFLOW_ID}",
        json={"active": False},
        timeout=30,
    )
    deactivate.raise_for_status()
    print("Workflow desactivado.")
    time.sleep(3)

    activate = session.patch(
        f"{BASE_URL}/workflows/{WORKFLOW_ID}",
        json={"active": True},
        timeout=30,
    )
    activate.raise_for_status()
    print("Workflow reactivado con trigger limpio.")


def main() -> int:
    session = login()
    print("Logged in to n8n.")
    deploy(session)
    print(f"ITS ETL fix deployed for workflow {WORKFLOW_ID}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
