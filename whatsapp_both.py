import requests
import json
import time

EVOLUTION_HOST = "http://10.147.18.204:8088"
API_KEY = "a8efc554faaf4b52ca1e3b7d05523903"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def generate_code(phone_number, instance_name):
    print(f"Borrando instancia anterior {instance_name}...")
    requests.delete(f"{EVOLUTION_HOST}/instance/delete/{instance_name}", headers=headers)
    
    print(f"Creando nueva instancia para {phone_number}...")
    create_url = f"{EVOLUTION_HOST}/instance/create"
    payload = {
        "instanceName": instance_name,
        "qrcode": False,
        "integration": "WHATSAPP-BAILEYS",
        "clientName": "Dario-VPN",
        "browser": "Chrome (Mac OS)"
    }
    requests.post(create_url, headers=headers, json=payload)
    
    time.sleep(2)
    
    connect_url = f"{EVOLUTION_HOST}/instance/connect/{instance_name}?number={phone_number}"
    response = requests.get(connect_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'code' in data and len(data['code']) < 20:
            return data['code']
        elif 'pairingCode' in data:
            return data['pairingCode']
    return None

print("\n--- GENERANDO CÓDIGOS PARA AMBOS NÚMEROS ---")

code_farmacia = generate_code("584127775239", "AMC_FARMACIA")
if code_farmacia:
    print(f"\n=> CÓDIGO FARMACIA (0412-7775239): {code_farmacia}")

code_dario = generate_code("584127754865", "AMC_DARIO")
if code_dario:
    print(f"\n=> CÓDIGO DARIO (0412-7754865): {code_dario}")
