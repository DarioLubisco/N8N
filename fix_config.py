import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect("100.123.98.5", 22, "root", "Twinc3pt.2", timeout=10)
    stdin, stdout, stderr = ssh.exec_command("cat /root/.hermes/config.yaml")
    config = stdout.read().decode('utf-8')
    import re
    # Remove skills from the gatekeeper/gemini agent, assuming it has a skills block
    print("CURRENT CONFIG:\n", config)
finally:
    ssh.close()
