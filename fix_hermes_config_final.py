import paramiko

def deploy_config():
    host = "10.147.18.204"
    port = 22
    username = "root"
    password = "Twinc3pt.2"

    clean_config = """# Hermes Agent CLI Configuration - Optimized for Gemma 3 27B
model:
  default: "google/gemma-3-27b-it"
  subagent_worker: "google/gemma-3-27b-it"
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

# Configuración de voz
stt:
  enabled: true
  local:
    model: "base"
"""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"Conectando a {host}...")
        ssh.connect(host, port, username, password, timeout=10)
        
        sftp = ssh.open_sftp()
        config_path = "/root/.hermes/config.yaml"
        with sftp.file(config_path, 'w') as f:
            f.write(clean_config)
        sftp.close()
        
        print("Configuración limpia desplegada. Reiniciando hermes...")
        ssh.exec_command("docker restart hermes")
        print("Hecho.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_config()
