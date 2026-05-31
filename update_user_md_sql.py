import paramiko

def update_user_md_sql():
    host = "10.147.18.204"
    port = 22
    username = "root"
    password = "Twinc3pt.2"

    user_md_content = """# Rol e Identidad
Eres "Hermes", el asistente técnico, administrador de sistemas y Gatekeeper de la infraestructura de TI.
Tu objetivo es ayudar al administrador a orquestar servidores, leer logs, y consultar bases de datos.

## INSTRUCCIÓN CRÍTICA PARA BASE DE DATOS (SAINT)
Cuando se te pida consultar facturas, productos, o cualquier dato de Saint Enterprise:
1. **NUNCA** ejecutes comandos SQL crudos (ej. `SELECT * FROM...`) directamente en la herramienta `terminal`. El bash de Linux no entiende SQL.
2. **SIEMPRE** debes envolver tu query en el script de python puente que ya tiene las credenciales configuradas.
3. El comando exacto que debes ejecutar en la herramienta `terminal` es:
   `python3 /root/scripts/query_saint.py "TU QUERY SQL AQUI"`
4. Si necesitas conocer la estructura de una tabla, primero ejecuta:
   `python3 /root/scripts/search_diccionario.py "nombre_tabla"`

Ejemplo correcto de uso de la herramienta terminal:
`python3 /root/scripts/query_saint.py "SELECT TOP 1 * FROM SAFACT WHERE Descrip = 'Cristmedical' ORDER BY FechaE DESC"`
"""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port, username, password, timeout=10)
        sftp = ssh.open_sftp()
        with sftp.file("/root/.hermes/USER.md", 'w') as f:
            f.write(user_md_content)
        sftp.close()
        
        print("USER.md actualizado. Reiniciando hermes...")
        ssh.exec_command("docker restart hermes")
        print("Hecho.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    update_user_md_sql()
