import paramiko

host = "10.147.18.204"
port = 22
username = "root"
password = "Twinc3pt.2"

# Tools contents
ping_tool = r"""#!/bin/bash
# Tool for checking network connectivity
ping -c 4 $1
"""

docker_tool = r"""#!/bin/bash
# Tool for checking docker container logs
container_name=$1
tail_lines=${2:-50}
echo "Container Status:"
docker ps --filter "name=$container_name" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo -e "\nLast $tail_lines logs:"
docker logs --tail $tail_lines $container_name
"""

sql_tool = r"""#!/bin/bash
# Tool for running SQL queries (requires sqlcmd to be installed on Debian, or via docker)
query=$1
# Connect to SRV-DC-AMC (10.147.18.192) using sa / Twinc3pt.
# Example using mssql-tools if installed:
# sqlcmd -S 10.147.18.192 -U sa -P "Twinc3pt." -d EnterpriseAdmin_AMC -Q "$query"
echo "[DEBUG] Ejecutando query en 10.147.18.192 (Saint)..."
echo "Query: $query"
# Real implementation depends on Debian environment having mssql-tools.
"""

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port, username, password, timeout=10)
    
    base_dir = "/opt/data/skills"
    
    # Create tools directories
    dirs = [
        f"{base_dir}/subagent_it_devops/tools",
        f"{base_dir}/subagent_sql_saint/tools",
        f"{base_dir}/subagent_marketing/tools"
    ]
    
    for d in dirs:
        ssh.exec_command(f"mkdir -p {d}")
        
    sftp = ssh.open_sftp()
    
    # Deploy IT Tools
    with sftp.file(f"{base_dir}/subagent_it_devops/tools/ping_network.sh", 'w') as f:
        f.write(ping_tool)
    with sftp.file(f"{base_dir}/subagent_it_devops/tools/check_docker.sh", 'w') as f:
        f.write(docker_tool)
        
    # Deploy SQL Tools
    with sftp.file(f"{base_dir}/subagent_sql_saint/tools/run_query.sh", 'w') as f:
        f.write(sql_tool)
        
    sftp.close()
    
    # Make scripts executable
    ssh.exec_command(f"chmod +x {base_dir}/subagent_it_devops/tools/*.sh")
    ssh.exec_command(f"chmod +x {base_dir}/subagent_sql_saint/tools/*.sh")
    
    print("Tools deployed successfully.")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
