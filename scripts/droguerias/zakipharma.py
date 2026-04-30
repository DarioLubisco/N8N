#!/usr/bin/env python3
import sys, pyodbc
from datetime import datetime

CONN_STR = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=10.147.18.192;DATABASE=EnterpriseAdmin_AMC;UID=sa;PWD=Twinc3pt.;"
TABLE = "[Proveedores].[Zakipharma_Inventario]"

def main():
    raw = sys.stdin.read()
    if not raw.strip(): return
    
    # Formato: 8 columnas separadas por ';'
    lines = [l.split(";") for l in raw.splitlines() if ";" in l]
    rows = []
    
    for p in lines:
        if len(p) < 8: continue
        try:
            # 1:codigo_producto, 2:codigo_barras, 3:descripcion, 4:fecha_lote (DD/MM/YYYY)
            # 5:precio_unitario, 6:porcentaje_oferta, 7:precio_final, 8:stock
            fecha_lote = datetime.strptime(p[3].strip(), "%d/%m/%Y").strftime("%Y-%m-%d") if p[3].strip() else None
            pu = float(p[4].strip() or 0)
            po = float(p[5].strip() or 0)
            pf = float(p[6].strip() or 0)
            st = int(p[7].strip() or 0)
            
            rows.append((
                p[0].strip(), p[1].strip(), p[2].strip(), fecha_lote,
                pu, po, pf, st, datetime.now()
            ))
        except Exception as e:
            continue
    
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    
    merge_sql = f"""
    MERGE {TABLE} AS T
    USING (SELECT ? AS cp, 'ZAKIPHARMA' AS prov) AS S ON T.codigo_producto = S.cp AND T.proveedor = S.prov
    WHEN MATCHED THEN UPDATE SET codigo_barras=?, descripcion_producto=?, fecha_lote=?, precio_unitario=?, porcentaje_oferta_vigente=?, precio_unitario_final=?, stock_disponible=?, fecha_carga=?
    WHEN NOT MATCHED THEN INSERT (codigo_producto, codigo_barras, descripcion_producto, fecha_lote, precio_unitario, porcentaje_oferta_vigente, precio_unitario_final, stock_disponible, fecha_carga)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    
    for r in rows:
        cursor.execute(merge_sql, (
            r[0], # Using CP
            r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], # Update
            r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]  # Insert
        ))
    
    conn.commit()
    print(f"OK ROWS:{len(rows)}")

if __name__ == "__main__": main()
