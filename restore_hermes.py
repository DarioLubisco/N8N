import paramiko

def restore_hermes():
    host = "10.147.18.204"
    port = 22
    username = "root"
    password = "Twinc3pt.2"

    config_content = """# Hermes Agent CLI Configuration - Arquitectura Hibrida Hermes + Gemini
model:
  default: "nousresearch/hermes-4-405b"
  subagent_worker: "google/gemini-2.0-flash-001"
  fallback_model: "google/gemini-2.0-flash-001"
  provider: "auto"
  base_url: "https://openrouter.ai/api/v1"

provider_routing:
  require_parameters: false
  allow_fallbacks: true

terminal:
  backend: "local"
  cwd: "."
  timeout: 180

agent:
  max_turns: 60
  reasoning_effort: "medium"

# Habilitar herramientas para Telegram
platform_toolsets:
  cli: [hermes-cli]
  telegram: [terminal, file, web, skills, todo]
  whatsapp: [hermes-whatsapp]

memory:
  memory_enabled: true
  user_profile_enabled: true

# Configuracion de voz
stt:
  enabled: true
  local:
    model: "base"
"""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port, username, password, timeout=10)
        sftp = ssh.open_sftp()
        with sftp.file("/root/.hermes/config.yaml", 'w') as f:
            f.write(config_content)
            
        # Limpiar LLM_MODEL de .env para que respete config.yaml
        with sftp.open('/root/.hermes/.env', 'r') as env_file:
            lines = env_file.readlines()
        with sftp.open('/root/.hermes/.env', 'w') as env_file:
            for line in lines:
                if not line.startswith('LLM_MODEL='):
                    env_file.write(line)
        sftp.close()
        
        print("Configuracion restaurada. Reiniciando hermes...")
        ssh.exec_command("docker restart hermes")
        print("Hecho.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    restore_hermes()
