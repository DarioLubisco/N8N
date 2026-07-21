#!/usr/bin/env python3
"""Switch the n8n [PROD] MSSQL - Saint Enterprise credential to the active network."""

from __future__ import annotations

import argparse
import os
import sys

import requests

BASE_URL = os.getenv("N8N_REST_URL", "https://n8n.farmaciaamericana.es/rest")
CREDENTIAL_ID = "oCKBzGZBl1xETeZa"
CREDENTIAL_NAME = "[PROD] MSSQL - Saint Enterprise"

NETWORKS = {
    "ZT": {"server": "10.147.18.192", "port": 49751},
    "TS": {"server": "100.94.5.108", "port": 49751},
    "LAN": {"server": "10.200.8.5", "port": 49751},
}


def login(session: requests.Session) -> None:
    email = os.getenv("N8N_EMAIL", "dario.lubisco@gmail.com")
    password = os.getenv("N8N_PASSWORD")
    if not password:
        raise SystemExit("Set N8N_PASSWORD before running this script.")

    response = session.post(
        f"{BASE_URL}/login",
        json={"email": email, "password": password},
        timeout=30,
    )
    response.raise_for_status()


def get_credential(session: requests.Session) -> dict:
    response = session.get(f"{BASE_URL}/credentials?includeData=true", timeout=30)
    response.raise_for_status()
    for credential in response.json()["data"]:
        if credential["id"] == CREDENTIAL_ID:
            return credential
    raise SystemExit(f"Credential {CREDENTIAL_ID} not found.")


def update_credential(session: requests.Session, network: str) -> dict:
    credential = get_credential(session)
    target = NETWORKS[network.upper()]
    current = credential.get("data") or {}

    if current.get("server") == target["server"] and current.get("port") == target["port"]:
        print(f"Credential already points to {network}: {target['server']}:{target['port']}")
        return credential

    payload = {
        "name": credential["name"],
        "type": credential["type"],
        "data": {**current, **target},
    }
    response = session.patch(
        f"{BASE_URL}/credentials/{CREDENTIAL_ID}",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    print(
        f"Updated {CREDENTIAL_NAME} from "
        f"{current.get('server')}:{current.get('port')} to "
        f"{target['server']}:{target['port']} ({network})"
    )
    return response.json()["data"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "network",
        choices=sorted(NETWORKS),
        help="Target network profile for the SQL credential.",
    )
    args = parser.parse_args()

    session = requests.Session()
    login(session)
    update_credential(session, args.network)


if __name__ == "__main__":
    main()
