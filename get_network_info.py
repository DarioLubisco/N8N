import paramiko

def execute(ssh, command):
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(f"Output:\n{out}")
    if err:
        print(f"Error:\n{err}")
    return out

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('10.147.18.204', username='root', password='Twinc3pt.2')
    
    print("--- Tailscale ---")
    execute(ssh, "tailscale status")
    execute(ssh, "tailscale ip -4")
    
    print("\n--- ZeroTier ---")
    execute(ssh, "zerotier-cli status")
    execute(ssh, "zerotier-cli listnetworks")
    
except Exception as e:
    print("Exception:", e)
finally:
    ssh.close()
