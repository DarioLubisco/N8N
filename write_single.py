import paramiko

host = '10.147.18.204'
port = 22
username = 'root'
password = 'Twinc3pt.2'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, port, username, password, timeout=10)

script = '''import os
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

def write_log(status, latency, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] STATUS: {status} | LATENCY: {latency:.2f}s | MSG: {message}\\n"
    with open(LOG_FILE, 'a') as f:
        f.write(log_line)
    print(log_line.strip())

def log_latency():
    api_key = get_api_key()
    if not api_key:
        write_log('ERROR', 0, 'No API key found in .env')
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
            write_log('SUCCESS', elapsed, 'OK')
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start_time
        write_log('HTTP_ERROR', elapsed, f'Code: {e.code}')
    except Exception as e:
        elapsed = time.time() - start_time
        write_log('ERROR', elapsed, str(e))

if __name__ == '__main__':
    log_latency()
'''

sftp = ssh.open_sftp()
with sftp.open('/root/scripts/latency_logger_single.py', 'w') as f:
    f.write(script)
sftp.close()

# Disable the systemd service since n8n will run it
ssh.exec_command('systemctl stop hermes-latency.service')
ssh.exec_command('systemctl disable hermes-latency.service')
print("Single script deployed and service disabled.")
