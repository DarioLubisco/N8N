import requests
import json
import sys

BASE_URL = "https://n8n.farmaciaamericana.es/rest"
EMAIL = "dario.lubisco@gmail.com"
PASSWORD = "Twinc3pt."

file_path = '/home/synapse/source/N8N/workflows/fDCuAMGVUsXPdmXp.json'

def login():
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/login", json={
        "emailOrLdapLoginId": EMAIL,
        "password": PASSWORD
    })
    resp.raise_for_status()
    print("Logged in successfully.")
    return session

def update_workflow(session, wf_id, payload):
    # En n8n, actualizar un workflow requiere enviar el JSON completo
    resp = session.put(f"{BASE_URL}/workflows/{wf_id}", json=payload)
    if resp.status_code != 200:
        print(f"Error updating workflow: {resp.text}")
        sys.exit(1)
    print("Workflow updated successfully in live n8n instance.")

if __name__ == "__main__":
    session = login()
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    update_workflow(session, data["id"], data)
