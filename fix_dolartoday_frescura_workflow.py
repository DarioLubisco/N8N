#!/usr/bin/env python3
"""Deploy resilience fixes for [PROD] [Finanzas] - Monitorear Frescura DolarToday."""

import json
import sys
from pathlib import Path

import requests

BASE_URL = "https://n8n.farmaciaamericana.es/rest"
EMAIL = "dario.lubisco@gmail.com"
PASSWORD = "Twinc3pt."
WORKFLOW_ID = "MGuM78qi3IWrDWOt"
CREDENTIAL_ID = "oCKBzGZBl1xETeZa"
WORKFLOW_FILE = Path(__file__).parent / "workflows" / f"{WORKFLOW_ID}.json"

# ZeroTier is the stable path from Debian n8n to SRV-DC-AMC in production scripts.
SQL_HOST_ZT = "10.147.18.192"
SQL_PORT = 49751


def login() -> requests.Session:
    session = requests.Session()
    response = session.post(
        f"{BASE_URL}/login",
        json={"email": EMAIL, "password": PASSWORD},
        timeout=30,
    )
    response.raise_for_status()
    return session


def patch_sql_node(nodes: list[dict]) -> bool:
    changed = False
    for node in nodes:
        if node.get("name") != "Check DolarToday de Hoy":
            continue
        desired = {
            "retryOnFail": True,
            "maxTries": 5,
            "waitBetweenTries": 15000,
        }
        for key, value in desired.items():
            if node.get(key) != value:
                node[key] = value
                changed = True
    return changed


def update_workflow(session: requests.Session, workflow: dict) -> None:
    response = session.patch(
        f"{BASE_URL}/workflows/{WORKFLOW_ID}",
        json=workflow,
        timeout=30,
    )
    response.raise_for_status()
    print(f"Updated workflow {WORKFLOW_ID}")


def update_mssql_credential(session: requests.Session) -> None:
    response = session.get(f"{BASE_URL}/credentials/{CREDENTIAL_ID}", timeout=30)
    response.raise_for_status()
    credential = response.json()["data"]

    payload = {
        "name": credential["name"],
        "type": credential["type"],
        "data": {
            "server": SQL_HOST_ZT,
            "port": SQL_PORT,
            "database": "EnterpriseAdmin_AMC",
            "user": "sa",
            "password": "Twinc3pt.",
            "tls": False,
            "domain": "",
        },
    }

    response = session.patch(
        f"{BASE_URL}/credentials/{CREDENTIAL_ID}",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    print(
        f"Updated credential {CREDENTIAL_ID} to ZeroTier host "
        f"{SQL_HOST_ZT}:{SQL_PORT}"
    )


def main() -> int:
    session = login()

    with WORKFLOW_FILE.open(encoding="utf-8") as handle:
        workflow = json.load(handle)

    changed = patch_sql_node(workflow.get("nodes", []))
    if "activeVersion" in workflow and workflow["activeVersion"]:
        changed = patch_sql_node(workflow["activeVersion"].get("nodes", [])) or changed

    if not changed:
        print("Workflow already has retry settings.")
    else:
        with WORKFLOW_FILE.open("w", encoding="utf-8") as handle:
            json.dump(workflow, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        update_workflow(session, workflow)

    try:
        update_mssql_credential(session)
    except requests.HTTPError as exc:
        print(
            "Warning: could not update MSSQL credential automatically. "
            f"Set host to {SQL_HOST_ZT},{SQL_PORT} in n8n UI. "
            f"Details: {exc.response.text[:300]}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
