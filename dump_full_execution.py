import pg8000.dbapi
import json

conn = pg8000.dbapi.connect(
    host="172.20.0.2",
    port=5432,
    user="n8n",
    password="Twinc3pt.2",
    database="n8n"
)
cursor = conn.cursor()

cursor.execute("""
    SELECT data 
    FROM execution_data 
    WHERE "executionId" IN (
        SELECT id FROM execution_entity WHERE "workflowId" = 'fDCuAMGVUsXPdmXp'
    )
    ORDER BY "executionId" DESC 
    LIMIT 1 OFFSET 2;
""")
row = cursor.fetchone()
if not row:
    print("No se encontraron ejecuciones.")
    exit(0)
    
data_str = row[0]
data = json.loads(data_str)

def resolve(val, data_list):
    if isinstance(val, str) and val.isdigit():
        idx = int(val)
        if idx < len(data_list):
            return resolve(data_list[idx], data_list)
    elif isinstance(val, list):
        return [resolve(item, data_list) for item in val]
    elif isinstance(val, dict):
        return {k: resolve(v, data_list) for k, v in val.items()}
    return val

resolved_data = resolve(data[0], data)

with open("/home/synapse/source/N8N/resolved_execution.json", "w") as f:
    json.dump(resolved_data, f, indent=2)

print("Resolved JSON written to /home/synapse/source/N8N/resolved_execution.json")
