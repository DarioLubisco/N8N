import requests
import json
import time

EVOLUTION_HOST = "http://10.147.18.204:8088"
API_KEY = "a8efc554faaf4b52ca1e3b7d05523903"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def generate_code_with_plus(phone_number, instance_name):
    print(f"Borrando instancia anterior {instance_name}...")
    requests.delete(f"{EVOLUTION_HOST}/instance/delete/{instance_name}", headers=headers)
    
    print(f"Creando nueva instancia para {phone_number}...")
    create_url = f"{EVOLUTION_HOST}/instance/create"
    payload = {
        "instanceName": instance_name,
        "qrcode": False,
        "integration": "WHATSAPP-BAILEYS",
        "clientName": "Dario-VPN",
        "browser": "Chrome (Mac OS)",
        "number": phone_number
    }
    requests.post(create_url, headers=headers, json=payload)
    
    time.sleep(2)
    
    # Use %2B for the plus sign in the URL
    encoded_number = phone_number.replace("+", "%2B")
    connect_url = f"{EVOLUTION_HOST}/instance/connect/{instance_name}?number={encoded_number}"
    response = requests.get(connect_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'code' in data and len(data['code']) < 20:
            return data['code']
        elif 'pairingCode' in data:
            return data['pairingCode']
    else:
        print(response.status_code, response.text)
    return None

print("\n--- GENERANDO CÓDIGO CON FORMATO INTERNACIONAL ---")

code_farmacia = generate_code_with_plus("+584127775239", "AMC_FARMACIA_PLUS")
if code_farmacia:
    print(f"\n=> CÓDIGO FARMACIA (+584127775239): {code_farmacia}")
else:
    print("Fallo la generacion con el signo +")
