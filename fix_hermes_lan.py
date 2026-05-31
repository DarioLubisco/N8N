import paramiko
import re

host = "10.200.8.204"
port = 22
username = "root"
password = "Twinc3pt.2"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Conectando a {host}...")
    ssh.connect(host, port, username, password, timeout=5)
    print("Conexión exitosa. Leyendo config.yaml...")
    
    config_path = "/root/.hermes/config.yaml"
    
    stdin, stdout, stderr = ssh.exec_command(f"cat {config_path}")
    config = stdout.read().decode('utf-8')
    
    if not config:
        print("Error: No se pudo leer el archivo de configuración.")
        exit(1)
        
    print("CONFIG ACTUAL (Fragmento Gemini):")
    # Imprimimos la parte de gemini para debug
    import textwrap
    lines = config.split("\n")
    for i, line in enumerate(lines):
        if "google/gemini" in line:
            print("\n".join(lines[max(0, i-2):min(len(lines), i+10)]))
            
    # Remove skills from any agent using gemini model
    # We will just replace skills: ["..."] with skills: [] for Gemini.
    new_config = re.sub(r'(model:\s*google/gemini[^\n]*\n(?:[^\n]*\n)*?\s*skills:\s*\[)([^\]]*?)(\])', r'\1\3', config, flags=re.MULTILINE|re.IGNORECASE)
    
    sftp = ssh.open_sftp()
    with sftp.file(config_path, 'w') as f:
        f.write(new_config)
    sftp.close()
    
    print("\n¡Opción 1 completada! Las skills han sido removidas del agente Gemini en config.yaml.")
    print("Reiniciando el contenedor hermes para aplicar cambios...")
    ssh.exec_command("docker restart hermes")
    
except Exception as e:
    print(f"Error de red o conexión: {e}")
finally:
    ssh.close()
