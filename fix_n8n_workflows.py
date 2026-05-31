import requests
import json
import os

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

def get_workflow(session, wf_id):
    resp = session.get(f"{BASE_URL}/workflows/{wf_id}")
    resp.raise_for_status()
    return resp.json()["data"]

def update_workflow(session, wf_id, wf_data):
    resp = session.patch(f"{BASE_URL}/workflows/{wf_id}", json=wf_data)
    resp.raise_for_status()
    print(f"Updated workflow {wf_id}")

def backup_workflow(wf_id, data, prefix="before"):
    os.makedirs("backup_workflows", exist_ok=True)
    with open(f"backup_workflows/{prefix}_{wf_id}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    session = login()

    # 1. Telegram Mute Handler (eYF98tmC3XJAUtbf)
    print("Fixing Telegram Mute Handler...")
    wf_mute = get_workflow(session, "eYF98tmC3XJAUtbf")
    backup_workflow("eYF98tmC3XJAUtbf", wf_mute, "before")
    def patch_parse_mute_info(node):
        if "fields" in node["parameters"]:
            fields = node["parameters"]["fields"]["values"]
        elif "assignments" in node["parameters"]:
            fields = node["parameters"]["assignments"]["assignments"]
        else:
            return

        for field in fields:
            if field["name"] == "hours":
                field["value"] = """={{ (() => { 
  const d = $json.callback_query?.data || $('Telegram Callback').first()?.json?.callback_query?.data; 
  if(!d) return 1; 
  const match = d.match(/^mute_(\\d+)_/);
  if (match) return parseInt(match[1], 10);
  if(d==="mute_1h") return 1; 
  if(d==="mute_4h") return 4; 
  if(d==="mute_12h") return 12; 
  return 1; 
})() }}"""
            elif field["name"] == "ServiceName":
                field["value"] = """={{ (() => { 
  const d = $json.callback_query?.data || $('Telegram Callback').first()?.json?.callback_query?.data; 
  if(!d) return "WindowsMonitor"; 
  const match = d.match(/^mute_\\d+_(.*)/);
  if (match) return match[1];
  return "WindowsMonitor"; 
})() }}"""
            elif field["name"] == "MuteUntil":
                field["value"] = """={{ (() => { 
  const h = (() => { 
    const d = $json.callback_query?.data || $('Telegram Callback').first()?.json?.callback_query?.data; 
    if(!d) return 1; 
    const match = d.match(/^mute_(\\d+)_/);
    if (match) return parseInt(match[1], 10);
    if(d==="mute_1h") return 1; 
    if(d==="mute_4h") return 4; 
    if(d==="mute_12h") return 12; 
    return 1; 
  })(); 
  if(h === 0) return $now.minus({ hours: 1 }).toISO(); 
  return $now.plus({ hours: h }).toISO(); 
})() }}"""

    for node in wf_mute["nodes"]:
        if node["name"] == "Parse Mute Info":
            patch_parse_mute_info(node)
    
    if "activeVersion" in wf_mute and "nodes" in wf_mute["activeVersion"]:
        for node in wf_mute["activeVersion"]["nodes"]:
            if node["name"] == "Parse Mute Info":
                patch_parse_mute_info(node)
    backup_workflow("eYF98tmC3XJAUtbf", wf_mute, "after")
    update_workflow(session, "eYF98tmC3XJAUtbf", wf_mute)

    # 2. Monitor de Infraestructura Global (4hS1QB91qEeHWYBB)
    print("Fixing Monitor de Infraestructura Global...")
    wf_monitor = get_workflow(session, "4hS1QB91qEeHWYBB")
    backup_workflow("4hS1QB91qEeHWYBB", wf_monitor, "before")
    def patch_monitor_nodes(node):
        if node["name"] == "Stop and Error": # Internal APIs
            node["parameters"]["errorMessage"] = """=={{ `⚠️ ADVERTENCIA (2do Grado): API Interna Caída
🖥️ Entidad Origen: Servidor Debian Webservices (IP ZeroTier: 10.147.18.204)
🎯 Entidad Destino: PC de Dario (IP Dinámica)
🔌 Servicio Afectado: ${$json.name}

📝 Diagnóstico: No se pudo conectar a la API local de la estación de trabajo.
🔍 Causas Probables: El servidor de desarrollo (FastAPI/Uvicorn) está detenido o la PC fue apagada.
🛠️ Log Nativo (n8n): ${$json.error.message}` }}"""
        elif node["name"] == "Stop and Error1": # Check SQL Connection
            node["parameters"]["errorMessage"] = """=={{ `🚨 CRÍTICO (1er Grado): Fallo en la Base de Datos
🖥️ Entidad Origen: Servidor Debian Webservices (IP ZeroTier: 10.147.18.204)
🎯 Entidad Destino: Servidor Windows SRV-DC-AMC (IP LAN: 10.200.8.5)
🔌 Servicio Afectado: MSSQL Server (Instancia: Saint)

📝 Diagnóstico: El nodo falló al validar la conexión SQL.
🔍 Causas Probables: El servicio MSSQL está detenido, la base de datos no acepta conexiones, o el túnel ZeroTier está caído.
🛠️ Log Nativo (n8n): ${$json.error.message}` }}"""
        elif node["name"] == "Stop and Error2": # Check Internet
            node["parameters"]["errorMessage"] = """=={{ `🚨 CRÍTICO (1er Grado): Servicios Web (Internet) Caídos
🖥️ Entidad Origen: Servidor Debian Webservices (IP ZeroTier: 10.147.18.204)
🎯 Entidad Destino: Internet (Google DNS 8.8.8.8)
🔌 Servicio Afectado: Conectividad Externa

📝 Diagnóstico: El nodo no pudo hacer ping HTTP a Google.
🔍 Causas Probables: El servidor Debian perdió conectividad a internet.
🛠️ Log Nativo (n8n): ${$json.error.message}` }}"""

    for node in wf_monitor["nodes"]:
        patch_monitor_nodes(node)
    
    if "activeVersion" in wf_monitor and "nodes" in wf_monitor["activeVersion"]:
        for node in wf_monitor["activeVersion"]["nodes"]:
            patch_monitor_nodes(node)
    backup_workflow("4hS1QB91qEeHWYBB", wf_monitor, "after")
    update_workflow(session, "4hS1QB91qEeHWYBB", wf_monitor)

    # 3. Error Notification System (zLtMDgsc7OSXyXrp)
    print("Fixing Error Notification System...")
    wf_error = get_workflow(session, "zLtMDgsc7OSXyXrp")
    backup_workflow("zLtMDgsc7OSXyXrp", wf_error, "before")
    def patch_error_nodes(node):
        if node["name"] == "Format Alert Data":
            if "fields" in node["parameters"]:
                fields = node["parameters"]["fields"]["values"]
            elif "assignments" in node["parameters"]:
                fields = node["parameters"]["assignments"]["assignments"]
            else:
                return
            for assign in fields:
                if assign["name"] == "alert_title":
                    assign["value"] = "" # Unused now
                elif assign["name"] == "alert_body":
                    assign["value"] = """={{ $json.execution?.error?.message || "⚠️ ERROR DESCONOCIDO\\n\\nNo se capturó un mensaje de error específico." }}"""
        elif node["name"] == "Send Telegram Alert":
            node["parameters"]["text"] = """={{ $("Format Alert Data").item.json.alert_body }}

<a href="{{ $("Format Alert Data").item.json.execution_url }}">🔍 Ver detalles de ejecución en n8n</a>"""

    for node in wf_error["nodes"]:
        patch_error_nodes(node)

    if "activeVersion" in wf_error and "nodes" in wf_error["activeVersion"]:
        for node in wf_error["activeVersion"]["nodes"]:
            patch_error_nodes(node)
    backup_workflow("zLtMDgsc7OSXyXrp", wf_error, "after")
    update_workflow(session, "zLtMDgsc7OSXyXrp", wf_error)

if __name__ == "__main__":
    main()
