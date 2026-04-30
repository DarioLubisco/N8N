#!/usr/bin/env python3
import sys, pyodbc
from datetime import datetime

CONN_STR = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.147.18.192;DATABASE=EnterpriseAdmin_AMC;UID=sa;PWD=Twinc3pt.;"
TABLE = "[Proveedores].[DROCERCA_Inventario]"

def main():
    raw = sys.stdin.read()
    if not raw.strip(): return
    # ProteoERP suele usar CSV estándar
    import csv
    from io import StringIO
    f = StringIO(raw)
    reader = csv.reader(f, delimiter=',')
    rows = []
    for p in reader:
        if len(p) < 5: continue
        # Adaptar según columnas de Proteo
        rows.append((p[0], p[1], p[2], p[3], datetime.now()))
    
    conn = pyodbc.connect(CONN_STR)
    # ... ejecutar merge ...
    conn.commit()
    print(f"OK ROWS:{len(rows)}")

if __name__ == "__main__": main()
