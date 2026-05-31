import paramiko

def switch_to_deepseek_v4_flash():
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
        
        # Replace the model
        config = config.replace('nousresearch/hermes-2-pro-llama-3-8b', 'deepseek/deepseek-v4-flash')
        config = config.replace('nousresearch/hermes-4-70b', 'deepseek/deepseek-v4-flash')
        config = config.replace('nousresearch/hermes-4-405b', 'deepseek/deepseek-v4-flash')

        with sftp.open('/root/.hermes/config.yaml', 'w') as f:
            f.write(config)

        sftp.close()
        
        print("Configuracion actualizada a deepseek/deepseek-v4-flash. Reiniciando hermes...")
        ssh.exec_command("docker restart hermes")
        print("Hecho.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    switch_to_deepseek_v4_flash()
