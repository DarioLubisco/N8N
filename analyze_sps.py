import pymssql
import json
import re

try:
    print("Connecting to DB...")
    conn = pymssql.connect(server="10.147.18.192", port="49751", user="sa", password="Twinc3pt.", database="EnterpriseAdmin_AMC", login_timeout=15, timeout=60)
    cursor = conn.cursor()
    
    print("Fetching columns list...")
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'por_aprobacion_equivalencias' AND TABLE_SCHEMA = 'Procurement'")
    all_columns = [row[0] for row in cursor.fetchall()]
    
    print("Fetching SPs...")
    cursor.execute("""
    SELECT OBJECT_NAME(m.object_id), m.definition 
    FROM sys.sql_modules m
    JOIN sys.objects o ON m.object_id = o.object_id
    WHERE o.type = 'P' AND m.definition LIKE '%por_aprobacion_equivalencias%'
    """)
    sps = cursor.fetchall()
    print(f"Found {len(sps)} SPs.")
    
    sp_columns = {col: False for col in all_columns}
    
    for sp_name, definition in sps:
        # Regex to find which columns from the table are mentioned in the SP definition
        for col in all_columns:
            if re.search(rf'\b{col}\b', definition, re.IGNORECASE):
                sp_columns[col] = True
                
    result = {
        "sp_names": [sp[0] for sp in sps],
        "columns_in_sps": sp_columns
    }
    
    with open('/home/synapse/source/N8N/sp_analysis.json', 'w') as f:
        json.dump(result, f, indent=2)
        
    print("Saved SP analysis to sp_analysis.json")
    conn.close()
except Exception as e:
    print("Error:", e)
