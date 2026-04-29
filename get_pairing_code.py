import requests
import json

# --- Configuración ---
EVOLUTION_HOST = "http://10.147.18.204:8088"
INSTANCE_NAME = "AMC_WHATSAPP_V2"
API_KEY = "a8efc554faaf4b52ca1e3b7d05523903"
PHONE_NUMBER = "584127775239"  # Sin el símbolo '+'

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def get_pairing_code():
    # El endpoint correcto para pairing code en Evolution v2
    url = f"{EVOLUTION_HOST}/instance/connect/pairingCode/{INSTANCE_NAME}?number={PHONE_NUMBER}"
    
    print(f"Solicitando código de vinculación para {PHONE_NUMBER} en la instancia {INSTANCE_NAME}...")
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            code = data.get("code")
            if code:
                print("\n" + "="*40)
                print(f"TU CÓDIGO DE VINCULACIÓN ES: {code}")
                print("="*40)
                print("\nInstrucciones:")
                print("1. En tu celular, abre WhatsApp.")
                print("2. Ve a Dispositivos vinculados > Vincular un dispositivo.")
                print("3. Selecciona 'Vincular con el número de teléfono'.")
                print(f"4. Ingresa el código {code} cuando te lo pida.")
            else:
                print(f"No se recibió un código. Respuesta: {data}")
        else:
            print(f"Error del servidor (Status {response.status_code}): {response.text}")
    except Exception as e:
        print(f"Error de red: {e}")

if __name__ == "__main__":
    get_pairing_code()
