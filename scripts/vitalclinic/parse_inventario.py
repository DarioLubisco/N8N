#!/usr/bin/env python3
"""
parse_inventario.py — Vital Clinic ETL
======================================
Lee inventario.txt desde stdin (enviado por n8n vía SSH),
parsea cada línea con el formato definido en la documentación FTP
y hace UPSERT en SQL Server (EnterpriseAdmin_AMC).

Formato de línea (separador: ';'):
  [0]  codigo_producto
  [1]  codigo_barras
  [2]  descripcion_producto
  [3]  fecha_lote           (DD/MM/YYYY)
  [4]  precio_unitario      (Decimal)
  [5]  porcentaje_oferta_vigente (DP)
  [6]  precio_unitario_final
  [7]  stock_disponible     (Entero)
  [8]  articulo_indexado    ('0' = indexado, '' = no indexado)
  [9]  descuento_adicional  (DA)

Salida (stdout):  "OK ROWS:<n>" → leída por n8n para validar éxito.
                  "ERROR: <mensaje>" → dispara rama de error en n8n.
"""

import sys
import pyodbc
from datetime import datetime

# ──────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────
CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=10.147.18.192;"          # ZeroTier → SRV-DC-AMC
    "DATABASE=EnterpriseAdmin_AMC;"
    "UID=sa;"
    "PWD=Twinc3pt.;"
    "TrustServerCertificate=yes;"
)

TARGET_SCHEMA  = "Proveedores"
TARGET_TABLE   = "VitalClinic_Inventario"
PROVEEDOR_CODE = "VITAL_CLINIC"
SEP            = ";"
ENCODING       = "utf-8"

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def safe_decimal(val: str) -> float | None:
    try:
        return float(val.strip()) if val.strip() else None
    except ValueError:
        return None

def safe_int(val: str) -> int | None:
    try:
        return int(val.strip()) if val.strip() else None
    except ValueError:
        return None

def parse_fecha(val: str) -> str | None:
    """Convierte DD/MM/YYYY → YYYY-MM-DD para SQL Server."""
    val = val.strip()
    if not val:
        return None
    try:
        return datetime.strptime(val, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    raw = sys.stdin.read()
    if not raw.strip():
        print("ERROR: stdin vacío — no se recibió contenido del archivo.")
        sys.exit(1)

    lines = [l for l in raw.splitlines() if l.strip()]
    rows = []

    for i, line in enumerate(lines, 1):
        parts = line.split(SEP)
        if len(parts) < 8:
            # Línea malformada — ignorar silenciosamente
            continue
        
        # Extender a 10 campos si faltan columnas opcionales
        while len(parts) < 10:
            parts.append("")

        rows.append({
            "codigo_producto":           parts[0].strip(),
            "codigo_barras":             parts[1].strip(),
            "descripcion_producto":      parts[2].strip(),
            "fecha_lote":                parse_fecha(parts[3]),
            "precio_unitario":           safe_decimal(parts[4]),
            "pct_oferta_vigente_dp":     parts[5].strip() or None,
            "precio_unitario_final":     safe_decimal(parts[6]),
            "stock_disponible":          safe_int(parts[7]),
            "articulo_indexado":         (parts[8].strip() == "0"),
            "descuento_adicional_da":    parts[9].strip() or None,
            "proveedor":                 PROVEEDOR_CODE,
            "fecha_carga":               datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    if not rows:
        print("ERROR: No se parsearon registros válidos del archivo.")
        sys.exit(1)

    # ── UPSERT en SQL Server ──────────────────
    merge_sql = f"""
    MERGE [{TARGET_SCHEMA}].[{TARGET_TABLE}] AS target
    USING (SELECT ? AS codigo_producto, ? AS proveedor) AS source
        ON target.codigo_producto = source.codigo_producto
        AND target.proveedor = source.proveedor
    WHEN MATCHED THEN
        UPDATE SET
            codigo_barras           = ?,
            descripcion_producto    = ?,
            fecha_lote              = ?,
            precio_unitario         = ?,
            pct_oferta_vigente_dp   = ?,
            precio_unitario_final   = ?,
            stock_disponible        = ?,
            articulo_indexado       = ?,
            descuento_adicional_da  = ?,
            fecha_carga             = ?
    WHEN NOT MATCHED THEN
        INSERT (codigo_producto, proveedor, codigo_barras, descripcion_producto,
                fecha_lote, precio_unitario, pct_oferta_vigente_dp,
                precio_unitario_final, stock_disponible, articulo_indexado,
                descuento_adicional_da, fecha_carga)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    try:
        conn = pyodbc.connect(CONN_STR, timeout=10)
        cursor = conn.cursor()
        cursor.fast_executemany = True

        params = []
        for r in rows:
            params.append((
                # USING clause
                r["codigo_producto"], r["proveedor"],
                # UPDATE SET
                r["codigo_barras"], r["descripcion_producto"], r["fecha_lote"],
                r["precio_unitario"], r["pct_oferta_vigente_dp"],
                r["precio_unitario_final"], r["stock_disponible"],
                r["articulo_indexado"], r["descuento_adicional_da"], r["fecha_carga"],
                # INSERT VALUES
                r["codigo_producto"], r["proveedor"],
                r["codigo_barras"], r["descripcion_producto"], r["fecha_lote"],
                r["precio_unitario"], r["pct_oferta_vigente_dp"],
                r["precio_unitario_final"], r["stock_disponible"],
                r["articulo_indexado"], r["descuento_adicional_da"], r["fecha_carga"],
            ))

        cursor.executemany(merge_sql, params)
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(f"OK ROWS:{len(rows)}")


if __name__ == "__main__":
    main()
