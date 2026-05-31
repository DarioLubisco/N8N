import paramiko

def update_full_config():
    host = "10.147.18.204"
    port = 22
    username = "root"
    password = "Twinc3pt.2"

    config_content = """# Hermes Agent CLI Configuration - Optimized for Gemini 2.0 Flash
model:
  default: "google/gemini-2.0-flash-001"
  subagent_worker: "google/gemini-2.0-flash-001"
  fallback_model: "google/gemini-2.0-flash-001"
  provider: "auto"
  base_url: "https://openrouter.ai/api/v1"

provider_routing:
  require_parameters: false

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
        sftp.close()
        
        print("config.yaml actualizado. Reiniciando hermes...")
        ssh.exec_command("docker restart hermes")
        print("Hecho.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    update_full_config()
