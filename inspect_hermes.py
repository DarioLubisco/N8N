import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("10.147.18.204", 22, "root", "Twinc3pt.2", timeout=10)
stdin, stdout, stderr = ssh.exec_command("docker inspect hermes | grep -A 20 'Mounts'")
print(stdout.read().decode())
