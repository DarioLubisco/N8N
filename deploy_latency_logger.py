import paramiko

def deploy_latency_logger():
    host = "10.147.18.204"
    port = 22
    username = "root"
    password = "Twinc3pt.2"

    logger_script = """import os
import time
import urllib.request
import json
from datetime import datetime

API_KEY_PATH = '/root/.hermes/.env'
LOG_FILE = '/var/log/hermes_latency.log'
MODEL = 'deepseek/deepseek-v4-flash'
URL = 'https://openrouter.ai/api/v1/chat/completions'

def get_api_key():
    try:
        with open(API_KEY_PATH, 'r') as f:
            for line in f:
                if line.startswith('OPENROUTER_API_KEY='):
                    return line.strip().split('=', 1)[1]
    except Exception:
        return None
    return None

def log_latency():
    api_key = get_api_key()
    if not api_key:
        write_log("ERROR", 0, "No API key found in .env")
        return

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': MODEL,
        'messages': [{'role': 'user', 'content': 'ping'}],
        'max_tokens': 5
    }

    start_time = time.time()
    try:
        req = urllib.request.Request(URL, headers=headers, data=json.dumps(data).encode('utf-8'))
        with urllib.request.urlopen(req, timeout=30) as response:
            response.read()
            elapsed = time.time() - start_time
            write_log("SUCCESS", elapsed, "OK")
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start_time
        write_log("HTTP_ERROR", elapsed, f"Code: {e.code}")
    except Exception as e:
        elapsed = time.time() - start_time
        write_log("ERROR", elapsed, str(e))

def write_log(status, latency, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] STATUS: {status} | LATENCY: {latency:.2f}s | MSG: {message}\\n"
    with open(LOG_FILE, 'a') as f:
        f.write(log_line)

if __name__ == '__main__':
    write_log("START", 0, "Latency logger started")
    while True:
        log_latency()
        time.sleep(60)  # Check every 60 seconds
"""

    service_file = """[Unit]
Description=Hermes OpenRouter Latency Logger
After=network.target

[Service]
ExecStart=/usr/bin/python3 /root/scripts/latency_logger.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
"""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port, username, password, timeout=10)
        sftp = ssh.open_sftp()
        
        # Deploy Python Script
        with sftp.open('/root/scripts/latency_logger.py', 'w') as f:
            f.write(logger_script)
            
        # Deploy Service File
        with sftp.open('/etc/systemd/system/hermes-latency.service', 'w') as f:
            f.write(service_file)
            
        sftp.close()
        
        print("Archivos desplegados. Configurando servicio systemd...")
        ssh.exec_command("systemctl daemon-reload")
        ssh.exec_command("systemctl enable hermes-latency.service")
        ssh.exec_command("systemctl restart hermes-latency.service")
        print("Servicio hermes-latency iniciado correctamente.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_latency_logger()
