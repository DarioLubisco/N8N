import paramiko

def deploy_sql_skill():
    host = "10.147.18.204"
    port = 22
    username = "root"
    password = "Twinc3pt.2"

    skill_content = """# Skill: Base de Datos Saint Enterprise
Eres capaz de consultar la base de datos SQL Server (Saint Enterprise).

## Herramientas Disponibles
- **terminal**: Usa esta herramienta para ejecutar el script que conecta a la BD.

## Procedimiento de Consulta
1. **NO PIDAS CREDENCIALES.** Las credenciales y la conexion ya estan configuradas en el servidor.
2. NO intentes ejecutar comandos SQL crudos en la terminal de bash.
3. Para ejecutar cualquier consulta, utiliza el script proporcionado.
4. Comando a ejecutar en tu herramienta `terminal`:
   `python3 /root/scripts/query_saint.py "TU_QUERY_SQL_AQUI"`

### Notas
- Si necesitas saber la estructura de las tablas (ej. `SAFACT`, `SAITEMFAC`, `SAPROD`), usa primero tu skill de **Diccionario Saint** llamando a `python3 /root/scripts/search_diccionario.py "nombre_tabla"`.
- Ejemplo de ejecucion: `python3 /root/scripts/query_saint.py "SELECT TOP 5 * FROM SAFACT"`
"""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port, username, password, timeout=10)
        sftp = ssh.open_sftp()
        with sftp.file("/root/.hermes/skills/SQL_Saint.md", 'w') as f:
            f.write(skill_content)
        sftp.close()
        
        print("Skill SQL desplegada. Reiniciando hermes...")
        ssh.exec_command("docker restart hermes")
        print("Hecho.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_sql_skill()
