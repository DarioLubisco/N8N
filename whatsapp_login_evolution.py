import requests
import json
import base64
import os
import time

# --- Configuración ---
EVOLUTION_HOST = "http://10.147.18.204:8088"
INSTANCE_NAME = "AMC_WHATSAPP_V2"
# Reemplaza 'tu_global_api_key' por la clave API real de Evolution
API_KEY = "a8efc554faaf4b52ca1e3b7d05523903"  

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def check_instance_status():
    url = f"{EVOLUTION_HOST}/instance/connectionState/{INSTANCE_NAME}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("instance", {}).get("state")
        elif response.status_code == 404:
            return "not_found"
        else:
            print(f"Error comprobando estado: {response.text}")
            return None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def create_instance():
    url = f"{EVOLUTION_HOST}/instance/create"
    payload = {
        "instanceName": INSTANCE_NAME,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS",
        # Disfrazando la conexión según las instrucciones del Handover
        "clientName": "AMC-System",
        "browser": "Safari"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        print(f"Instancia {INSTANCE_NAME} creada correctamente.")
        return response.json()
    else:
        print(f"Error creando instancia: {response.text}")
        return None

def connect_instance():
    url = f"{EVOLUTION_HOST}/instance/connect/{INSTANCE_NAME}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "base64" in data:
            base64_data = data["base64"].split(",")[1] if "," in data["base64"] else data["base64"]
            with open("qr_code.png", "wb") as f:
                f.write(base64.b64decode(base64_data))
            print("✅ QR generado con éxito. Abre el archivo 'qr_code.png' y escanéalo con WhatsApp.")
            return True
        elif data.get("instance", {}).get("state") == "open":
            print("✅ La instancia ya está conectada.")
            return True
    print(f"Respuesta inesperada al conectar: {response.text}")
    return False

def main():
    print(f"--- Iniciando conexión con Evolution API en {EVOLUTION_HOST} ---")
    
    state = check_instance_status()
    print(f"Estado de la instancia '{INSTANCE_NAME}': {state}")
    
    if state == "not_found":
        print("La instancia no existe. Creando...")
        create_instance()
        time.sleep(2)
        connect_instance()
    elif state in ["close", "connecting"]:
        print("Obteniendo QR de conexión...")
        connect_instance()
    elif state == "open":
        print("✅ La conexión de WhatsApp está activa y funcionando.")
    else:
        print("Estado desconocido. Intentando obtener QR por si acaso...")
        connect_instance()

if __name__ == "__main__":
    main()
