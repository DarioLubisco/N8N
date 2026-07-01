import paramiko
import sys

def run_remote_query(query):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('10.147.18.204', 22, 'root', 'Twinc3pt.2', timeout=10)
    stdin, stdout, stderr = ssh.exec_command(f'python3 /root/scripts/query_saint.py "{query}"')
    
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    
    if err:
        print('STDERR:', err)
    return out

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 query_via_ssh.py 'QUERY'")
        sys.exit(1)
    print(run_remote_query(sys.argv[1]))
