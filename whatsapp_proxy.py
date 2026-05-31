import requests
import json
import time

EVOLUTION_HOST = "http://10.147.18.204:8088"
API_KEY = "a8efc554faaf4b52ca1e3b7d05523903"
PHONE_NUMBER = "584127775239"
INSTANCE_NAME = "AMC_WA_PROXY"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def delete_instance(name):
    url = f"{EVOLUTION_HOST}/instance/delete/{name}"
    requests.delete(url, headers=headers)
    
def create_instance():
    url = f"{EVOLUTION_HOST}/instance/create"
    payload = {
        "instanceName": INSTANCE_NAME,
        "qrcode": False,
        "integration": "WHATSAPP-BAILEYS",
        "clientName": "Proxy-Device",
        "browser": "Chrome (Mac OS)",
        "proxy": {
            "host": "172.17.0.3",
            "port": 8888,
            "protocol": "http"
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        return True
    else:
        print("Create failed:", response.text)
        return False

def get_pairing_code():
    url = f"{EVOLUTION_HOST}/instance/connect/{INSTANCE_NAME}?number={PHONE_NUMBER}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            if 'code' in data and len(data['code']) < 20:
                return data['code']
            elif 'pairingCode' in data:
                return data['pairingCode']
        except Exception:
            print("Response was not JSON. Text:")
            print(response.text)
    print("Pairing code failed with status:", response.status_code, response.text)
    return None

delete_instance(INSTANCE_NAME)

print(f"Creando instancia con proxy Surfshark para {PHONE_NUMBER}...")
if create_instance():
    time.sleep(2)
    print("Solicitando código...")
    code = get_pairing_code()
    if code:
        print(f"=== PAIRING_CODE: {code} ===")
    else:
        print("No se recibió código de vinculación.")
