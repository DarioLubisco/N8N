import paramiko

def execute(ssh, command):
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(f"Output:\n{out.encode('cp1252', errors='replace').decode('cp1252')}")
    if err:
        print(f"Error:\n{err.encode('cp1252', errors='replace').decode('cp1252')}")
    print(f"Exit status: {exit_status}\n")
    return out

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('10.147.18.204', username='root', password='Twinc3pt.2')
    
    print("--- Tailscale Status ---")
    execute(ssh, "tailscale status")
    
    print("\n--- ZeroTier Status ---")
    execute(ssh, "zerotier-cli status")
    execute(ssh, "zerotier-cli listnetworks")
    execute(ssh, "zerotier-cli peers")
    execute(ssh, "ip addr show")
    
except Exception as e:
    print("Exception:", e)
finally:
    ssh.close()
