#!/usr/bin/env python3
"""Deploy paginated SQL fix for [PROD] [Finanzas] - Reporte de Compras Diarias."""

import json
import sys

import requests

BASE_URL = "https://n8n.farmaciaamericana.es/rest"
EMAIL = "dario.lubisco@gmail.com"
PASSWORD = "Twinc3pt."
WORKFLOW_ID = "QnqtF6NCBgqsRBSw"
WORKFLOW_PATH = "/workspace/workflows/QnqtF6NCBgqsRBSw.json"


def login() -> requests.Session:
    session = requests.Session()
    resp = session.post(
        f"{BASE_URL}/login",
        json={"emailOrLdapLoginId": EMAIL, "password": PASSWORD},
        timeout=30,
    )
    resp.raise_for_status()
    return session


def main() -> int:
    session = login()
    print("Logged in to n8n.")

    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        local_workflow = json.load(f)

    resp = session.get(f"{BASE_URL}/workflows/{WORKFLOW_ID}", timeout=30)
    resp.raise_for_status()
    remote_workflow = resp.json()["data"]

    remote_workflow["nodes"] = local_workflow["nodes"]
    remote_workflow["connections"] = local_workflow["connections"]
    remote_workflow["settings"] = local_workflow.get("settings", remote_workflow.get("settings", {}))
    remote_workflow["staticData"] = local_workflow.get("staticData", remote_workflow.get("staticData", {}))

    patch_resp = session.patch(
        f"{BASE_URL}/workflows/{WORKFLOW_ID}",
        json=remote_workflow,
        timeout=60,
    )
    if patch_resp.status_code != 200:
        print(f"Failed to update workflow: {patch_resp.status_code}")
        print(patch_resp.text)
        return 1

    print(f"Workflow {WORKFLOW_ID} updated successfully with paginated SQL reads.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
