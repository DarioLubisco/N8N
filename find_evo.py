import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.147.18.204', 22, 'root', 'Twinc3pt.2', timeout=10)
s, out, err = ssh.exec_command('docker ps --filter "name=evolution" --format "{{.Names}}"')
print('CONTAINERS:', out.read().decode())
s, out, err = ssh.exec_command('find / -name docker-compose.yml 2>/dev/null | grep evolution')
print('PATHS:', out.read().decode())
