import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.147.18.204', 22, 'root', 'Twinc3pt.2', timeout=10)
stdin, stdout, stderr = ssh.exec_command('python3 /root/scripts/query_saint.py "SELECT TOP 1 * FROM safact"')
print('STDOUT:', stdout.read().decode('utf-8'))
print('STDERR:', stderr.read().decode('utf-8'))
