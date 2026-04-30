#!/usr/bin/env python3
import sys, pyodbc, logging
from datetime import datetime

# Configuración
CONN_STR = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.147.18.192;DATABASE=EnterpriseAdmin_AMC;UID=sa;PWD=Twinc3pt.;"
TABLE = "[Proveedores].[NENA_Inventario]"

# Columnas de Ancho Fijo (Start, End)
COL_SPECS = [
    (0, 7), (7, 48), (48, 63), (63, 75), (75, 82), (82, 93), (93, 104),
    (104, 112), (112, 120), (120, 137), (137, 142), (142, 152), (152, 182),
    (182, 193), (193, 202), (202, 215), (215, 226), (226, 236), (236, 246),
    (246, 250), (250, 263), (263, 266)
]

def main():
    raw = sys.stdin.read()
    if not raw.strip():
        print("ERROR: No input data")
        sys.exit(1)

    lines = raw.splitlines()[1:] # Saltar encabezado si existe
    rows = []
    for line in lines:
        if len(line) < 137: continue
        try:
            codigo = line[0:7].strip()
            desc = line[7:48].strip()
            precio = float(line[48:63].strip() or 0)
            stock = int(line[63:75].strip() or 0)
            codbarras = line[120:137].strip()
            lote = line[152:182].strip()
            
            if codbarras:
                rows.append((codbarras, codigo, desc, precio, stock, lote, 'NENA', datetime.now()))
        except: continue

    if not rows:
        print("ERROR: No rows parsed")
        sys.exit(1)

    merge_sql = f"""
    MERGE {TABLE} AS T
    USING (SELECT ? AS cb) AS S ON T.codigo_barras = S.cb
    WHEN MATCHED THEN UPDATE SET codigo=?, descripcion_producto=?, precio_unitario=?, stock_disponible=?, fecha_lote=?, fecha_carga=?
    WHEN NOT MATCHED THEN INSERT (codigo_barras, codigo_producto, descripcion_producto, precio_unitario, stock_disponible, fecha_lote, fecha_carga)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """

    try:
        conn = pyodbc.connect(CONN_STR)
        cursor = conn.cursor()
        for r in rows:
            # (cb, cod, desc, precio, stock, lote, prov, date)
            cursor.execute(merge_sql, (r[0], r[1], r[2], r[3], r[4], r[5], r[7], r[0], r[1], r[2], r[3], r[4], r[5], r[7]))
        conn.commit()
        print(f"OK ROWS:{len(rows)}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__": main()
