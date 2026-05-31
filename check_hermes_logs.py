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
        
        stdin, stdout, stderr = ssh.exec_command('docker logs --tail 200 hermes')
        output = stdout.read()
        
        with open("c:/source/N8N/hermes_last_logs_utf8.txt", "wb") as f:
            f.write(output)
            
        print("Logs saved to hermes_last_logs_utf8.txt")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_hermes()
