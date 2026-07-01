import requests
import json
import re

BASE_URL = "http://127.0.0.1:5678/api/v1" # Use API since n8n is running locally?
# Actually, the fix_n8n_workflows.py used "https://n8n.farmaciaamericana.es/rest" and email/password login.
# I will use that same method since it's tested.

BASE_URL = "https://n8n.farmaciaamericana.es/rest"
EMAIL = "dario.lubisco@gmail.com"
PASSWORD = "Twinc3pt."

def login():
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    resp.raise_for_status()
    print("Logged in successfully.")
    return session

def get_workflows(session):
    resp = session.get(f"{BASE_URL}/workflows")
    resp.raise_for_status()
    return resp.json()["data"]

def get_workflow(session, wf_id):
    resp = session.get(f"{BASE_URL}/workflows/{wf_id}")
    resp.raise_for_status()
    return resp.json()["data"]

def update_workflow(session, wf_id, wf_data):
    resp = session.patch(f"{BASE_URL}/workflows/{wf_id}", json=wf_data)
    resp.raise_for_status()
    print(f"Updated workflow {wf_id}")

def process_ssh_command(cmd):
    # Fix paths and args
    if "/opt/scripts/Dronena/Imp_Inv_Dronena.py" in cmd:
        cmd = cmd.replace("/opt/scripts/Dronena/Imp_Inv_Dronena.py", "/opt/scripts/droguerias/nena.py")
    
    if "cat" in cmd and "python3" in cmd and "|" not in cmd:
        cmd = cmd.replace("python3", "| python3")
    
    if "insuaminca.py" in cmd and "--sucursal" not in cmd:
        # Assuming M by default or detect from context
        cmd = cmd.replace("insuaminca.py", "insuaminca.py --sucursal M")

    # Only apply 3x3 if it's not already applied
    if "for cycle in 1 2 3" in cmd:
        return cmd

    # Generate 3x3 wrapper
    wrapper = f'''cmd="{cmd}"
for cycle in 1 2 3; do
    for attempt in 1 2 3; do
        if eval "$cmd"; then
            exit 0
        fi
        if [ $attempt -lt 3 ]; then
            sleep 10
        fi
    done
    if [ $cycle -lt 3 ]; then
        sleep 300
    fi
done
exit 1'''
    return wrapper

def patch_workflow(wf):
    changed = False
    
    def patch_nodes(nodes):
        nonlocal changed
        for node in nodes:
            # Update Schedule Trigger to 20 mins
            if node["type"] == "n8n-nodes-base.scheduleTrigger":
                if "rule" in node["parameters"] and "interval" in node["parameters"]["rule"]:
                    intervals = node["parameters"]["rule"]["interval"]
                    for interval in intervals:
                        if interval["field"] == "minutes" and interval.get("minutesInterval") != 20:
                            interval["minutesInterval"] = 20
                            changed = True
                        elif interval["field"] == "hours":
                            # Change from hours to minutes
                            interval["field"] = "minutes"
                            interval["minutesInterval"] = 20
                            if "hoursInterval" in interval:
                                del interval["hoursInterval"]
                            changed = True

            # Update SSH nodes
            if node["type"] == "n8n-nodes-base.ssh":
                if "command" in node["parameters"]:
                    old_cmd = node["parameters"]["command"]
                    new_cmd = process_ssh_command(old_cmd)
                    if old_cmd != new_cmd:
                        node["parameters"]["command"] = new_cmd
                        changed = True

    patch_nodes(wf.get("nodes", []))
    if "activeVersion" in wf and "nodes" in wf["activeVersion"]:
         patch_nodes(wf["activeVersion"]["nodes"])
         
    return changed

def main():
    session = login()
    workflows = get_workflows(session)
    
    for wf_meta in workflows:
        name = wf_meta["name"].lower()
        if "inventario" in name or "ingesta" in name or "proveedor" in name:
            try:
                wf = get_workflow(session, wf_meta["id"])
                if patch_workflow(wf):
                    print(f"Updating workflow: {wf_meta['name']}")
                    update_workflow(session, wf_meta["id"], wf)
            except Exception as e:
                print(f"Error processing {wf_meta['name']}: {e}")

if __name__ == "__main__":
    main()
