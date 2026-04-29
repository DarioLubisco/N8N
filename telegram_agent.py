import requests
import logging
import time
import sys

# --- CONFIGURACIÓN DE ESTÉTICA ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

logging.basicConfig(
    level=logging.INFO,
    format=f'{Colors.OKBLUE}%(asctime)s{Colors.ENDC} [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("TelegramAgent")

# --- CLASE PRINCIPAL DEL BOT ---
class TelegramAgent:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.last_update_id = 0
        self._bot_info = self._validate_token()

    def _validate_token(self):
        """Verifica que el token sea válido y obtiene info del bot."""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                data = response.json()['result']
                print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ CONEXIÓN EXITOSA{Colors.ENDC}")
                print(f"{Colors.OKCYAN}Bot:{Colors.ENDC} {data['first_name']} (@{data['username']})")
                print(f"{Colors.OKCYAN}Estado:{Colors.ENDC} Escuchando mensajes...\n")
                return data
            else:
                print(f"{Colors.FAIL}❌ Error: El Token proporcionado no es válido.{Colors.ENDC}")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Error de red: {e}")
            sys.exit(1)

    def get_updates(self):
        """Escucha nuevos mensajes (Long Polling)."""
        params = {"offset": self.last_update_id + 1, "timeout": 20}
        try:
            response = requests.get(f"{self.base_url}/getUpdates", params=params, timeout=25)
            if response.status_code == 200:
                updates = response.json().get("result", [])
                if updates:
                    self.last_update_id = updates[-1]["update_id"]
                return updates
        except Exception as e:
            logger.warning(f"Reconectando... ({e})")
        return []

    def send_response(self, chat_id, text):
        """Envía la respuesta al usuario."""
        payload = {
            "chat_id": chat_id, 
            "text": text, 
            "parse_mode": "Markdown"
        }
        try:
            requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=10)
        except Exception as e:
            logger.error(f"No se pudo enviar el mensaje: {e}")

    def show_typing(self, chat_id):
        """Muestra 'escribiendo...' en la interfaz de Telegram."""
        requests.post(f"{bot.base_url}/sendChatAction", json={"chat_id": chat_id, "action": "typing"})

# --- LÓGICA DE INTERACCIÓN CON IA ---
def procesar_con_ia(texto_usuario, nombre_usuario):
    """
    Aquí es donde ocurre la 'magia'. 
    Para que este bot sea realmente YO (Antigravity), deberías conectar 
    la API de Gemini o OpenAI aquí.
    """
    # Respuesta simulada premium
    return (
        f"👋 ¡Hola *{nombre_usuario}*!\n\n"
        f"He recibido tu mensaje: _\"{texto_usuario}\"_\n\n"
        f"Actualmente estoy funcionando en modo 'Espejo'. Para que pueda responderte con mi "
        f"inteligencia completa de Agente, necesito que me proporciones una **API Key** "
        f"de Google AI Studio (Gemini). \n\n"
        f"¿Quieres que te ayude a configurar una ahora mismo? Es gratis."
    )

# --- EJECUCIÓN ---
if __name__ == "__main__":
    TOKEN = "8322313955:AAHwniwWZssrVuQBQGb1excjHKyZ2VQkkdE"
    bot = TelegramAgent(TOKEN)
    
    try:
        while True:
            updates = bot.get_updates()
            for update in updates:
                if "message" in update and "text" in update["message"]:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    user_text = msg["text"]
                    first_name = msg["from"].get("first_name", "Amigo")

                    print(f"{Colors.OKBLUE}💬 {first_name}:{Colors.ENDC} {user_text}")
                    
                    bot.show_typing(chat_id)
                    time.sleep(1.5) # Simula tiempo de procesamiento
                    
                    respuesta = procesar_con_ia(user_text, first_name)
                    bot.send_response(chat_id, respuesta)
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}🛑 Bot apagado por el usuario.{Colors.ENDC}")
    except Exception as e:
        logger.error(f"Error crítico: {e}")
