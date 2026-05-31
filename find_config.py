import paramiko

host = "10.147.18.204"
username = "root"
password = "Twinc3pt.2"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(host, port=22, username=username, password=password, timeout=10)
    # Search for config.yaml in /opt/data
    stdin, stdout, stderr = ssh.exec_command("find /opt/data -name 'config.yaml'")
    output = stdout.read().decode('utf-8')
    print("Found files:")
    print(output)
finally:
    ssh.close()
