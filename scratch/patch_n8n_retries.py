import json
import urllib.request

with open("/home/synapse/.gemini/config/mcp_config.json") as f:
    config = json.load(f)

api_key = config["mcpServers"]["n8n-mcp"]["env"]["N8N_API_KEY"]
api_host = config["mcpServers"]["n8n-mcp"]["env"]["N8N_API_URL"]

workflow_id = "R0GNsexEiQLZr01K"
url = f"{api_host}/api/v1/workflows/{workflow_id}"

# 1. Fetch current workflow
req = urllib.request.Request(url, headers={"X-N8N-API-KEY": api_key, "Accept": "application/json"})
with urllib.request.urlopen(req) as response:
    workflow = json.loads(response.read())

# 2. Add retry settings to the database nodes
updated_nodes = 0
for node in workflow["nodes"]:
    if node["name"] in ["Get Recent Dates", "Update & Maintain DB"]:
        node["retryOnFail"] = True
        node["maxTries"] = 5
        node["waitBetweenTries"] = 15000  # 15 seconds
        updated_nodes += 1
        print(f"Added retry settings to node: {node['name']}")

if updated_nodes != 2:
    print(f"Warning: Only updated {updated_nodes} nodes.")

# 3. Clean up read-only fields for PUT
payload = {
    "name": workflow["name"],
    "nodes": workflow["nodes"],
    "connections": workflow["connections"],
    "settings": workflow.get("settings", {}),
    "staticData": workflow.get("staticData", {})
}

# 4. Push update to n8n
req_update = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"X-N8N-API-KEY": api_key, "Content-Type": "application/json", "Accept": "application/json"},
    method="PUT"
)

try:
    with urllib.request.urlopen(req_update) as response:
        print("Update Successful. Status:", response.status)
        # Write back to git
        with open("/home/synapse/source/N8N/workflows/R0GNsexEiQLZr01K.json", "w") as f:
            json.dump(workflow, f, indent=2)
        print("Workflow backed up to Git.")
except Exception as e:
    print("Error updating workflow:", e)
    if hasattr(e, "read"):
        print(e.read().decode('utf-8'))
