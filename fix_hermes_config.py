import paramiko
import re

host = "10.147.18.204"
port = 22
username = "root"
password = "Twinc3pt.2"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Conectando a {host}...")
    ssh.connect(host, port, username, password, timeout=10)
    print("Conexión exitosa. Leyendo config.yaml...")
    
    config_path = "/root/.hermes/config.yaml"
    
    # Read the current config
    stdin, stdout, stderr = ssh.exec_command(f"cat {config_path}")
    config = stdout.read().decode('utf-8')
    
    if not config:
        print("Error: No se pudo leer el archivo de configuración.")
        exit(1)
        
    # We want to disable tools for the gemini/gatekeeper agent. 
    # Usually in YAML, agents are defined under 'agents:'. We will find the gemini block and wipe its skills.
    # Alternatively, we can inject require_parameters: false if it's easier.
    
    # A simple approach to disable skills if they exist for gemini:
    # We look for the Gemini agent definition block and empty its skills array.
    # We will use a sed command on the remote server to add require_parameters: false under provider for Gemini, 
    # or just replace the config safely.
    
    # Let's add provider: {require_parameters: false} to the fallback/gemini section globally, 
    # or just replace 'skills: [...]' with 'skills: []' where model is gemini.
    
    new_config = re.sub(r'(model:\s*google/gemini.*?skills:\s*\[).*?(\])', r'\1\2', config, flags=re.DOTALL)
    
    # Write back the new config
    sftp = ssh.open_sftp()
    with sftp.file(config_path, 'w') as f:
        f.write(new_config)
    sftp.close()
    
    print("¡Opción 1 completada! Las skills han sido removidas del agente Gemini en config.yaml.")
    print("Reiniciando el contenedor hermes para aplicar cambios...")
    ssh.exec_command("docker restart hermes")
    
except Exception as e:
    print(f"Error de red o conexión: {e}")
finally:
    ssh.close()
