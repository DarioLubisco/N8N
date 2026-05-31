import paramiko
import os

def deploy_dictionary():
    host = "10.147.18.204"
    port = 22
    username = "root"
    password = "Twinc3pt.2"

    local_json_path = r"C:\source\Synapse\diccionario_referencia.json"
    remote_dir = "/root/data"
    remote_json_path = "/root/data/diccionario_referencia.json"
    remote_script_path = "/root/scripts/search_diccionario.py"
    remote_skill_path = "/root/.hermes/skills/Diccionario_Saint.md"

    search_script_content = """import json
import sys

def search_dict(term):
    try:
        with open('/root/data/diccionario_referencia.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        term = term.lower()
        results = []
        
        # El JSON es probablemente una lista de diccionarios o tiene una estructura tabular
        # Buscaremos en todos los valores de las estructuras
        def search_obj(obj):
            if isinstance(obj, dict):
                # Check if this dict represents a row in a table or field list
                row_str = " | ".join(str(v) for k,v in obj.items() if v is not None and str(v) != 'NaN')
                if term in row_str.lower():
                    results.append(row_str)
            elif isinstance(obj, list):
                for item in obj:
                    search_obj(item)
                    
        search_obj(data)
        
        if results:
            print(f"Resultados para '{term}':")
            for r in results[:20]: # Limit to 20 results
                print("-", r)
            if len(results) > 20:
                print(f"... y {len(results)-20} resultados mas.")
        else:
            print(f"No se encontraron resultados para '{term}'.")
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 search_diccionario.py 'termino_busqueda'")
        sys.exit(1)
    search_dict(sys.argv[1])
"""

    skill_content = """# Skill: Diccionario de Datos Saint Enterprise
Este documento explica como consultar el diccionario de datos de Saint Administrativo.

## Herramientas Disponibles
- **terminal**: Ejecuta un script de Python que busca en el JSON del Diccionario.

## Procedimiento de Consulta
Cuando necesites saber en qué tabla se guarda un dato o qué significa un campo en Saint:
1. Usa la herramienta terminal para ejecutar el script de busqueda.
2. Comando: `python3 /root/scripts/search_diccionario.py "termino_a_buscar"`
3. Puedes buscar por nombre de tabla (ej. `SAPROD`) o por descripción (ej. `clientes`, `impuesto`).

El script devolverá las líneas del diccionario que coincidan con tu búsqueda.
"""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print("Conectando al servidor...")
        ssh.connect(host, port, username, password, timeout=10)
        
        ssh.exec_command(f"mkdir -p {remote_dir} /root/scripts /root/.hermes/skills")
        
        sftp = ssh.open_sftp()
        
        print("Subiendo diccionario_referencia.json...")
        sftp.put(local_json_path, remote_json_path)
        
        print("Subiendo script de busqueda...")
        with sftp.file(remote_script_path, 'w') as f:
            f.write(search_script_content)
            
        print("Subiendo Skill...")
        with sftp.file(remote_skill_path, 'w') as f:
            f.write(skill_content)
            
        sftp.close()
        print("Despliegue exitoso.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_dictionary()
