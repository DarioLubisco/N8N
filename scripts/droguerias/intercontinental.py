#!/usr/bin/env python3
"""
intercontinental.py — ETL Inventario Intercontinental
======================================================
10 columnas (diferente al genérico de 8/10 estándar):
  Codigo, CodBarras, Descripcion, Vence (DATE),
  Precio, Descuento, PrecioFinal, Existencia, Marca, montofactura

Puerto FTP: 58021 (no estándar — configurar en n8n)
"""
import sys, pyodbc
from datetime import datetime

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=10.147.18.192;DATABASE=EnterpriseAdmin_AMC;"
    "UID=sa;PWD=Twinc3pt.;TrustServerCertificate=yes;"
)
TABLE = "[Proveedores].[Intercontinental_Inventario]"

def safe_d(v):
    try: return float(v.strip()) if v.strip() else None
    except: return None

def safe_i(v):
    try: return int(float(v.strip())) if v.strip() else None
    except: return None

def parse_fecha(v):
    v = v.strip()
    if not v: return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try: return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
        except: continue
    return None

def main():
    raw = sys.stdin.read()
    if not raw.strip():
        print("ERROR: stdin vacío"); sys.exit(1)

    rows = []
    for line in raw.splitlines():
        if not line.strip(): continue
        p = line.split(";")
        while len(p) < 10: p.append("")
        try:
            rows.append({
                "cp":   p[0].strip(),
                "cb":   p[1].strip(),
                "dp":   p[2].strip(),
                "vence": parse_fecha(p[3]),
                "precio": safe_d(p[4]),
                "dcto":  safe_d(p[5]),
                "pf":    safe_d(p[6]),
                "exist": safe_i(p[7]),
                "marca": p[8].strip(),
                "mf":    p[9].strip(),
                "fc":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        except: continue

    if not rows:
        print("ERROR: No se parsearon filas"); sys.exit(1)

    merge_sql = f"""
    MERGE {TABLE} AS T
    USING (SELECT ? AS cp, 'INTERCONTINENTAL' AS prov) AS S
      ON T.codigo_producto = S.cp AND T.proveedor = S.prov
    WHEN MATCHED THEN UPDATE SET
        codigo_barras=?, descripcion_producto=?, fecha_lote=?,
        precio_unitario=?, pct_oferta_vigente=?, precio_unitario_final=?,
        stock_disponible=?, articulo_indexado=0, descuento_adicional=?, fecha_carga=?
    WHEN NOT MATCHED THEN INSERT
        (proveedor, codigo_producto, codigo_barras, descripcion_producto, fecha_lote,
         precio_unitario, pct_oferta_vigente, precio_unitario_final,
         stock_disponible, articulo_indexado, descuento_adicional, fecha_carga)
    VALUES ('INTERCONTINENTAL', ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?);
    """

    try:
        conn = pyodbc.connect(CONN_STR, timeout=10)
        cursor = conn.cursor()
        for r in rows:
            cursor.execute(merge_sql, (
                r["cp"],
                r["cb"], r["dp"], r["vence"], r["precio"],
                str(r["dcto"]) if r["dcto"] else None,
                r["pf"], r["exist"], r["mf"], r["fc"],
                r["cp"], r["cb"], r["dp"], r["vence"], r["precio"],
                str(r["dcto"]) if r["dcto"] else None,
                r["pf"], r["exist"], r["mf"], r["fc"],
            ))
        conn.commit()
        print(f"OK ROWS:{len(rows)}")
    except Exception as e:
        print(f"ERROR: {e}"); sys.exit(1)

if __name__ == "__main__": main()
