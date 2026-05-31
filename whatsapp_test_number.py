import requests
import json
import time

EVOLUTION_HOST = "http://10.147.18.204:8088"
API_KEY = "a8efc554faaf4b52ca1e3b7d05523903"
PHONE_NUMBER = "584127754865"
INSTANCE_NAME = "AMC_WA_TEST"

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
        "clientName": "Test-Device",
        "browser": "Chrome"
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
        data = response.json()
        if 'code' in data and len(data['code']) < 20:
            return data['code']
        elif 'pairingCode' in data:
            return data['pairingCode']
    print("Pairing code failed:", response.text)
    return None

delete_instance(INSTANCE_NAME)

print(f"Creando instancia de prueba para {PHONE_NUMBER}...")
if create_instance():
    time.sleep(2)
    print("Solicitando código...")
    code = get_pairing_code()
    if code:
        print(f"=== PAIRING_CODE: {code} ===")
    else:
        print("No se recibió código de vinculación.")
