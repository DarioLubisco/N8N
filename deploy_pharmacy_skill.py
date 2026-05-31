import paramiko

def deploy_skill():
    host = "10.147.18.204"
    port = 22
    username = "root"
    password = "Twinc3pt.2"

    skill_content = """# Skill: Consulta de Inventario Farmacia Americana
Este documento describe como el Agente debe consultar el stock y precios en el sistema Saint Enterprise.

## Herramientas Disponibles
- **terminal**: Usa esta herramienta para ejecutar consultas SQL mediante un script de Python en el servidor.

## Procedimiento de Consulta
Cuando un cliente pregunte por la disponibilidad o precio de un producto:
1. Extrae el nombre del medicamento o principio activo.
2. Genera una query SQL basada en la tabla `dbo.CUSTOM_LOTES` y `dbo.SAPROD`.
3. Ejecuta la query usando el comando: `python3 /root/scripts/query_saint.py "TU_QUERY_SQL"`

## Ejemplo de Query (Stock Directo)
```sql
SELECT sp.Descrip, cl.Cantidad, cl.Precio1 
FROM dbo.CUSTOM_LOTES cl 
INNER JOIN dbo.SAPROD sp ON cl.CodProd = sp.CodProd 
WHERE sp.Descrip LIKE '%termino%' AND cl.Cantidad > 0
```
"""

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port, username, password, timeout=10)
        ssh.exec_command("mkdir -p /root/.hermes/skills /root/scripts")
        
        sftp = ssh.open_sftp()
        with sftp.file("/root/.hermes/skills/Farmacia_Inventario.md", 'w') as f:
            f.write(skill_content)
        sftp.close()
        
        print("Skill desplegada.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_skill()
