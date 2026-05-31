import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.147.18.204', 22, 'root', 'Twinc3pt.2', timeout=10)

commands = [
    "docker rm -f evolution-api surfshark_proxy",
    "docker run -d --name surfshark_proxy --cap-add=NET_ADMIN -e VPN_SERVICE_PROVIDER=surfshark -e OPENVPN_USER=UTjwQvtFQwTfgqyAVyzt7m9x -e OPENVPN_PASSWORD=XGguKmkyNggSRT7MU3N3uLAw -e SERVER_COUNTRIES=Italy -p 8888:8888 -p 8088:8080 qmcgaw/gluetun",
    "sleep 10",
    "docker run --name=evolution-api -v evolution_store:/evolution/store --env=DATABASE_SAVE_DATA_INSTANCE=true --env=AUTHENTICATION_API_KEY=a8efc554faaf4b52ca1e3b7d05523903 --env=AUTHENTICATION_INSTANCE_CHATWOOT_TOKEN=Anvb7ggYMcyzoHjksUwBdurM --env=AUTHENTICATION_INSTANCE_CHATWOOT_URL=https://chatwoot.farmaciaamericana.es --env=AUTHENTICATION_SAVE_DATA_INSTANCE=true --network=container:surfshark_proxy --workdir=/evolution --restart=always --detach=true atendai/evolution-api:v1.6.1 node ./dist/src/main.js"
]

for cmd in commands:
    print(f"Executing: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    print("STDOUT:", stdout.read().decode('utf-8', errors='ignore').strip())
    print("STDERR:", stderr.read().decode('utf-8', errors='ignore').strip())
    print(f"Status: {exit_status}\n")
