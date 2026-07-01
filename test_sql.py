import pymssql
import json
try:
    conn = pymssql.connect(server="10.147.18.192", port="49751", user="sa", password="Twinc3pt.", database="EnterpriseAdmin_AMC")
    cursor = conn.cursor(as_dict=True)
    cursor.execute("SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'por_aprobacion_equivalencias' AND TABLE_SCHEMA = 'Procurement'")
    rows = cursor.fetchall()
    with open('/home/synapse/source/N8N/columns.json', 'w') as f:
        json.dump(rows, f, indent=2)
    print("Success! Dumped", len(rows), "columns.")
    conn.close()
except Exception as e:
    print("Error:", e)
