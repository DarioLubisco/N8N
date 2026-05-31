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
    
    stdin, stdout, stderr = ssh.exec_command(f"cat {config_path}")
    config = stdout.read().decode('utf-8')
    
    if not config:
        print("Error: No se pudo leer el archivo de configuración.")
        exit(1)
        
    # Reemplazar google/gemini-2.0-flash-lite-001 por google/gemma-3-27b-it en todo el archivo
    new_config = config.replace("google/gemini-2.0-flash-lite-001", "google/gemma-3-27b-it")
    # Y por si acaso habían puesto la versión vieja de gemma como fallback
    new_config = new_config.replace("google/gemma-4-31b-it", "google/gemma-3-27b-it")
    
    sftp = ssh.open_sftp()
    with sftp.file(config_path, 'w') as f:
        f.write(new_config)
    sftp.close()
    
    print("\n¡Modelo actualizado a google/gemma-3-27b-it!")
    print("Reiniciando el contenedor hermes para aplicar cambios...")
    ssh.exec_command("docker restart hermes")
    
except Exception as e:
    print(f"Error de red o conexión: {e}")
finally:
    ssh.close()
