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
    
    print("--- Subiendo Archivos ---")
    sftp = ssh.open_sftp()
    local_dir = r"C:\source\N8N\Importar Inventario Dronena"
    remote_dir = "/opt/scripts/Dronena"
    
    files = ["Imp_Inv_Dronena.py", "Imp_Inv_Dronena.env"]
    for f in files:
        print(f"Uploading {f}...")
        sftp.put(f"{local_dir}\\{f}", f"{remote_dir}/{f}")
    sftp.close()
    
    print("--- Verificando ---")
    execute(ssh, "ls -l /opt/scripts/Dronena")
    
except Exception as e:
    print("Exception:", e)
finally:
    ssh.close()
