import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("10.147.18.204", 22, "root", "Twinc3pt.2", timeout=10)
stdin, stdout, stderr = ssh.exec_command("docker logs --tail 50 surfshark_proxy")
print("STDOUT:", stdout.read().decode('utf-8', errors='ignore'))
print("STDERR:", stderr.read().decode('utf-8', errors='ignore'))
