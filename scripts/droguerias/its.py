#!/usr/bin/env python3
import sys, pyodbc
from datetime import datetime

CONN_STR = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.147.18.192;DATABASE=EnterpriseAdmin_AMC;UID=sa;PWD=Twinc3pt.;"
TABLE = "[Proveedores].[ITS_Inventario]"

def main():
    raw = sys.stdin.read()
    if not raw.strip(): return
    lines = [l.split(";") for l in raw.splitlines() if ";" in l]
    rows = []
    for p in lines:
        if len(p) < 4: continue
        rows.append((p[0].strip(), p[1].strip(), float(p[2].replace(",","") or 0), int(p[3] or 0), datetime.now()))
    
    # Lógica de MERGE simplificada para el ejemplo
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    # ... ejecutar merge ...
    conn.commit()
    print(f"OK ROWS:{len(rows)}")

if __name__ == "__main__": main()
