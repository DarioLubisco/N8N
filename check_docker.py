import paramiko
import sys

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('10.147.18.204', username='root', password='Twinc3pt.2', timeout=10)
    
    print("Checking containers...")
    stdin, stdout, stderr = ssh.exec_command("docker exec -i postgres-n8n env")
    output = stdout.read().decode()
    print(output)
            
    ssh.close()
except Exception as e:
    print(f"Failed to execute via SSH: {e}")
    sys.exit(1)
