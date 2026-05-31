import paramiko

def check_hermes():
    host = "10.147.18.204"
    port = 22
    username = "root"
    password = "Twinc3pt.2"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port, username, password, timeout=10)
        
        # Check docker status
        stdin, stdout, stderr = ssh.exec_command('docker ps --filter "name=hermes"')
        print("--- DOCKER PS ---")
        print(stdout.read().decode())
        
        # Check logs tail 100
        stdin, stdout, stderr = ssh.exec_command('docker logs --tail 100 hermes')
        print("--- DOCKER LOGS ---")
        print(stdout.read().decode('utf-8', 'ignore'))
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_hermes()
