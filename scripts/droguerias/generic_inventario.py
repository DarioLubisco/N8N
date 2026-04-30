#!/usr/bin/env python3
"""
generic_inventario.py — ETL Genérico de Inventario
=====================================================
Sirve para todas las droguerías con formato de inventario
estándar separado por ';'.

Argumentos:
  --proveedor     Nombre del proveedor (ej: CRISTMED)
  --tabla         Tabla destino (ej: Cristmed_Inventario)
  --cols          Número de columnas esperadas (default: 10)

Formato de entrada (stdin, separador ';'):
  [0] codigo_producto
  [1] codigo_barras
  [2] descripcion_producto
  [3] fecha_lote (DD/MM/YYYY)
  [4] precio_unitario
  [5] pct_oferta_vigente (DP)
  [6] precio_unitario_final
  [7] stock_disponible
  [8] articulo_indexado  (opcional: '0'=indexado)
  [9] descuento_adicional (opcional: DA)

Salida: "OK ROWS:<n>" o "ERROR: <mensaje>"
"""

import sys
import argparse
import pyodbc
from datetime import datetime

CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=10.147.18.192;"
    "DATABASE=EnterpriseAdmin_AMC;"
    "UID=sa;"
    "PWD=Twinc3pt.;"
    "TrustServerCertificate=yes;"
)

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--proveedor", required=True)
    p.add_argument("--tabla", required=True)
    p.add_argument("--cols", type=int, default=10)
    return p.parse_args()

def safe_decimal(v):
    try: return float(v.strip()) if v.strip() else None
    except: return None

def safe_int(v):
    try: return int(v.strip()) if v.strip() else None
    except: return None

def parse_fecha(v):
    v = v.strip()
    if not v: return None
    try: return datetime.strptime(v, "%d/%m/%Y").strftime("%Y-%m-%d")
    except: return None

def main():
    args = parse_args()
    raw = sys.stdin.read()
    if not raw.strip():
        print("ERROR: stdin vacío")
        sys.exit(1)

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
                "fl":   parse_fecha(p[3]),
                "pu":   safe_decimal(p[4]),
                "pov":  p[5].strip() or None,
                "pf":   safe_decimal(p[6]),
                "st":   safe_int(p[7]),
                "idx":  (p[8].strip() == "0"),
                "da":   p[9].strip() or None,
                "prov": args.proveedor,
                "fc":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        except: continue

    if not rows:
        print("ERROR: No se parsearon filas válidas")
        sys.exit(1)

    tabla = f"[Proveedores].[{args.tabla}]"
    merge_sql = f"""
    MERGE {tabla} AS T
    USING (SELECT ? AS cp, ? AS prov) AS S
      ON T.codigo_producto = S.cp AND T.proveedor = S.prov
    WHEN MATCHED THEN UPDATE SET
        codigo_barras=?, descripcion_producto=?, fecha_lote=?,
        precio_unitario=?, pct_oferta_vigente=?, precio_unitario_final=?,
        stock_disponible=?, articulo_indexado=?, descuento_adicional=?, fecha_carga=?
    WHEN NOT MATCHED THEN INSERT
        (proveedor, codigo_producto, codigo_barras, descripcion_producto, fecha_lote,
         precio_unitario, pct_oferta_vigente, precio_unitario_final,
         stock_disponible, articulo_indexado, descuento_adicional, fecha_carga)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    try:
        conn = pyodbc.connect(CONN_STR, timeout=10)
        cursor = conn.cursor()
        for r in rows:
            cursor.execute(merge_sql, (
                r["cp"], r["prov"],
                # UPDATE
                r["cb"], r["dp"], r["fl"], r["pu"], r["pov"],
                r["pf"], r["st"], r["idx"], r["da"], r["fc"],
                # INSERT
                r["prov"], r["cp"], r["cb"], r["dp"], r["fl"],
                r["pu"], r["pov"], r["pf"], r["st"], r["idx"], r["da"], r["fc"],
            ))
        conn.commit()
        print(f"OK ROWS:{len(rows)}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
