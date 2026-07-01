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
    SELECT "executionId", data 
    FROM execution_data 
    WHERE "executionId" IN (
        SELECT id FROM execution_entity WHERE "workflowId" = 'fDCuAMGVUsXPdmXp'
    )
    ORDER BY "executionId" DESC 
    LIMIT 1;
""")
row = cursor.fetchone()
if not row:
    print("No se encontraron ejecuciones.")
    exit(0)
    
exec_id, data_str = row
print(f"Detalles de Ejecución ID: {exec_id}")

data = json.loads(data_str)

step_0 = data[0]
print("step_0 type:", type(step_0))
print("step_0 keys:", step_0.keys())
print("resultData type:", type(step_0.get("resultData")))
print("resultData value snippet:", str(step_0.get("resultData"))[:1000])
