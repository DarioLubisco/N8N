import paramiko

def switch_fallback():
    host = "10.147.18.204"
    port = 22
    username = "root"
    password = "Twinc3pt.2"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port, username, password, timeout=10)
        sftp = ssh.open_sftp()
        with sftp.open('/root/.hermes/config.yaml', 'r') as f:
            config = f.read().decode('utf-8')
        
        # Replace the fallback model
        config = config.replace('fallback_model: "google/gemini-2.0-flash-001"', 'fallback_model: "deepseek/deepseek-r1-distill-llama-70b"')

        with sftp.open('/root/.hermes/config.yaml', 'w') as f:
            f.write(config)

        sftp.close()
        
        print("Configuracion actualizada. fallback_model ahora es deepseek/deepseek-r1-distill-llama-70b. Reiniciando hermes...")
        ssh.exec_command("docker restart hermes")
        print("Hecho.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    switch_fallback()
