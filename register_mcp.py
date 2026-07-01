import json

config_path = '/home/synapse/.gemini/config/mcp_config.json'

with open(config_path, 'r') as f:
    config = json.load(f)

# Add the new python mssql-server configuration
config["mcpServers"]["mssql-server"] = {
    "command": "python3",
    "args": [
        "-W",
        "ignore",
        "-m",
        "mssql_mcp_server.server"
    ],
    "env": {
        "MSSQL_DRIVER": "ODBC Driver 18 for SQL Server",
        "MSSQL_HOST": "10.147.18.192,49751",
        "MSSQL_USER": "sa",
        "MSSQL_PASSWORD": "Twinc3pt.",
        "MSSQL_DATABASE": "EnterpriseAdmin_AMC",
        "TrustServerCertificate": "yes",
        "Trusted_Connection": "no"
      }
}

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("Successfully added mssql-server to config.json!")
