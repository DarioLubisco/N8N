import requests

BASE_URL = "https://n8n.farmaciaamericana.es/rest"
EMAIL = "dario.lubisco@gmail.com"
PASSWORD = "Twinc3pt."

def login():
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/login", json={
        "emailOrLdapLoginId": EMAIL,
        "password": PASSWORD
    })
    resp.raise_for_status()
    print("Logged in successfully.")
    return session

def fix_workflows():
    session = login()
    resp = session.get(f"{BASE_URL}/workflows")
    resp.raise_for_status()
    workflows = resp.json()["data"]
    
    corrupted_workflows = []
    
    for wf in workflows:
        wf_id = wf["id"]
        wf_name = wf["name"]
        
        # Get full workflow to check nodes
        try:
            wf_detail_resp = session.get(f"{BASE_URL}/workflows/{wf_id}")
            wf_detail_resp.raise_for_status()
            full_wf = wf_detail_resp.json()["data"]
        except Exception as e:
            print(f"Failed to fetch {wf_id}: {e}")
            continue
            
        nodes = full_wf.get("nodes", [])
        active_version = full_wf.get("activeVersion") or {}
        active_nodes = active_version.get("nodes", [])
        
        # If visual nodes are empty but active version has nodes, it's corrupted
        if len(nodes) == 0 and len(active_nodes) > 0:
            print(f"Found corrupted workflow: {wf_name} ({wf_id})")
            corrupted_workflows.append(full_wf)
            
            # Fix it
            full_wf["nodes"] = active_version.get("nodes", [])
            full_wf["connections"] = active_version.get("connections", {})
            
            try:
                update_resp = session.patch(f"{BASE_URL}/workflows/{wf_id}", json=full_wf)
                update_resp.raise_for_status()
                print(f"  -> Successfully restored visual nodes for: {wf_name}")
            except Exception as e:
                print(f"  -> Failed to update {wf_name}: {e}")

if __name__ == "__main__":
    fix_workflows()
