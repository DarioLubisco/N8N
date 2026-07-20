#!/usr/bin/env python3
"""Despliega el workflow External Error Reporter y copia el módulo Python al scraper."""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import requests

BASE_URL = os.getenv("N8N_REST_URL", "https://n8n.farmaciaamericana.es/rest")
EMAIL = os.getenv("N8N_EMAIL", "dario.lubisco@gmail.com")
PASSWORD = os.getenv("N8N_PASSWORD", "Twinc3pt.")

WORKFLOW_ID = "Kp8mScRpErr01"
WORKFLOW_FILE = Path(__file__).resolve().parent / "workflows" / f"{WORKFLOW_ID}.json"
MODULE_SOURCE = Path(__file__).resolve().parent / "scraper_integrations" / "n8n_error_reporter.py"
SCRAPER_REPO = Path(os.getenv(
    "SCRAPER_REPO_PATH",
    "/home/synapse/source/repos/Clasificacion Medicamentos",
))


def login() -> requests.Session:
    session = requests.Session()
    resp = session.post(
        f"{BASE_URL}/login",
        json={"emailOrLdapLoginId": EMAIL, "password": PASSWORD},
        timeout=30,
    )
    resp.raise_for_status()
    return session


def deploy_workflow(session: requests.Session) -> None:
    with WORKFLOW_FILE.open(encoding="utf-8") as handle:
        workflow = json.load(handle)

    wf_id = workflow["id"]
    resp = session.get(f"{BASE_URL}/workflows/{wf_id}", timeout=30)
    if resp.status_code == 200:
        print(f"Actualizando workflow existente {wf_id}...")
        payload = workflow
        update = session.patch(f"{BASE_URL}/workflows/{wf_id}", json=payload, timeout=60)
        update.raise_for_status()
    else:
        print(f"Creando workflow {wf_id}...")
        create = session.post(f"{BASE_URL}/workflows", json=workflow, timeout=60)
        create.raise_for_status()

    activate = session.patch(
        f"{BASE_URL}/workflows/{wf_id}",
        json={"active": True},
        timeout=30,
    )
    activate.raise_for_status()
    print(f"Workflow {wf_id} activo en n8n.")


def copy_module_to_scraper() -> None:
    if not SCRAPER_REPO.exists():
        print(f"Repo scraper no encontrado en {SCRAPER_REPO}; omitiendo copia local.")
        return
    dest = SCRAPER_REPO / "n8n_error_reporter.py"
    shutil.copy2(MODULE_SOURCE, dest)
    print(f"Módulo copiado a {dest}")


def main() -> int:
    session = login()
    deploy_workflow(session)
    copy_module_to_scraper()
    print("Listo. Configurar en Debian:")
    print("  export N8N_SCRAPER_ERROR_WEBHOOK_URL=https://n8n.farmaciaamericana.es/webhook/scraper-error-report")
    print("  export N8N_SCRAPER_ERROR_TOKEN=<mismo valor que SCRAPER_ERROR_WEBHOOK_TOKEN en n8n>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
