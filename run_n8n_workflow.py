#!/usr/bin/env python3
"""Execute an n8n workflow with a manual trigger via REST API."""

from __future__ import annotations

import argparse
import json
import sys
import time

import requests

BASE_URL = "https://n8n.farmaciaamericana.es"
EMAIL = "dario.lubisco@gmail.com"
PASSWORD = "Twinc3pt."


def login() -> requests.Session:
    session = requests.Session()
    response = session.post(
        f"{BASE_URL}/rest/login",
        json={"emailOrLdapLoginId": EMAIL, "password": PASSWORD},
        timeout=30,
    )
    response.raise_for_status()
    return session


def run_workflow(session: requests.Session, workflow_id: str, trigger_name: str = "Disparador Manual") -> str:
    workflow = session.get(f"{BASE_URL}/rest/workflows/{workflow_id}", timeout=30).json()["data"]
    payload = {
        "workflowData": workflow,
        "triggerToStartFrom": {"name": trigger_name},
    }
    response = session.post(
        f"{BASE_URL}/rest/workflows/{workflow_id}/run",
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["data"]["executionId"]


def wait_for_execution(session: requests.Session, execution_id: str, poll_seconds: int = 15, max_polls: int = 40) -> dict:
    for _ in range(max_polls):
        response = session.get(f"{BASE_URL}/rest/executions/{execution_id}", timeout=30)
        response.raise_for_status()
        data = response.json()["data"]
        if data.get("finished"):
            return data
        time.sleep(poll_seconds)
    raise TimeoutError(f"Execution {execution_id} did not finish in time")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an n8n workflow with a manual trigger")
    parser.add_argument("workflow_id", help="Workflow ID, e.g. QnqtF6NCBgqsRBSw")
    parser.add_argument("--trigger", default="Disparador Manual", help="Manual trigger node name")
    parser.add_argument("--no-wait", action="store_true", help="Return execution ID without waiting")
    args = parser.parse_args()

    session = login()
    execution_id = run_workflow(session, args.workflow_id, args.trigger)
    print(json.dumps({"executionId": execution_id, "url": f"{BASE_URL}/workflow/{args.workflow_id}/executions/{execution_id}"}, indent=2))

    if args.no_wait:
        return 0

    result = wait_for_execution(session, execution_id)
    print(json.dumps({
        "status": result.get("status"),
        "finished": result.get("finished"),
        "startedAt": result.get("startedAt"),
        "stoppedAt": result.get("stoppedAt"),
        "url": f"{BASE_URL}/workflow/{args.workflow_id}/executions/{execution_id}",
    }, indent=2))
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
