import pymssql
import json
try:
    conn = pymssql.connect(server="10.147.18.192", port="49751", user="sa", password="Twinc3pt.", database="EnterpriseAdmin_AMC")
    cursor = conn.cursor(as_dict=True)
    cursor.execute("""
    SELECT OBJECT_NAME(m.object_id) AS sp_name, m.definition
    FROM sys.sql_modules m
    INNER JOIN sys.objects o ON m.object_id = o.object_id
    WHERE o.type = 'P' AND m.definition LIKE '%por_aprobacion_equivalencias%'
    """)
    rows = cursor.fetchall()
    
    with open('/home/synapse/source/N8N/sp_definitions.json', 'w') as f:
        json.dump(rows, f, indent=2)
    print("Success! Found", len(rows), "SPs.")
    conn.close()
except Exception as e:
    print("Error:", e)
