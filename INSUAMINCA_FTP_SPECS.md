# 📁 Insuaminca — Especificaciones de Archivos FTP

**Empresa:** INSUAMINCA
**Destinatario:** FARMACIA AMERICANA, C.A. — RIF: J008376238

---

## 🔌 Parámetros de Conexión (Compartido por todas las sucursales)

| Campo | Valor |
|-------|-------|
| **Servidor** | `insuaminca.proteoerp.org` |
| **IP** | `186.167.69.10` |
| **Puerto** | **`50021`** ⚠️ Puerto no estándar |
| **Usuario** | `C01297` |
| **Contraseña** | `vua3FL1b` |
| **Protocolo** | FTP |

> [!WARNING]
> Puerto **50021** — no usar el 21 por defecto. Configurar explícitamente en n8n.

---

## 🏢 Sucursales y Nomenclatura

| Código Archivo | Sucursal | Tabla SQL |
|----------------|----------|-----------|
| `0` (ej: `F00337701.txt`) | Maturín | `InsuamincaM_Inventario` |
| `B` (ej: `FB0037305.txt`) | Caracas/Guarenas | `InsuamincaB_Inventario` |
| `C` (ej: `FC0001234.txt`) | Barquisimeto | `InsuamincaG_Inventario` |
| `D` prefix = Devolución | (todas) | — |

> [!NOTE]
> El documento oficial indica B=Caracas pero el ejemplo usa FB como Guarenas. Confirmar con proveedor.

---

## 📥 1. Inventario / Existencias

| Parámetro | Valor |
|-----------|-------|
| **Ruta** | `/Inventario.txt` |
| **Actualización** | Cada hora |
| **Encabezado** | ❌ No |
| **Separador** | `;` |
| **Nota** | Precio ya incluye descuento del cliente |

### Estructura (10 columnas):

| # | Campo | Tipo | Notas |
|---|-------|------|-------|
| 1 | `codigo_producto` | Texto | — |
| 2 | `codigo_barras` | Texto | — |
| 3 | `descripcion_producto` | Texto | — |
| 4 | `fecha_lote` | Texto `DD/MM/YYYY` | — |
| 5 | `precio_unitario` | Decimal | Sin descuento |
| 6 | `porcentaje_oferta_vigente` | Decimal | — |
| 7 | `precio_unitario_final` | Decimal | Con descuentos |
| 8 | `stock_disponible` | Entero | — |
| 9 | `marca_proveedor` | Texto | ⚠️ Extra vs estándar de 8 cols |
| 10 | `indexado_o_monto_factura` | Texto | ⚠️ Extra vs estándar de 8 cols |

---

## 📤 2. Pedidos (SUBIDA)

| Parámetro | Valor |
|-----------|-------|
| **Carpeta** | `/Pedidos/` |
| **Nombre** | `<CodCliente>P<Correlativo>` |

### Estructura (4 columnas):
1. `codigo_producto` (cadena 6 chars)
2. `descripcion_producto`
3. `cantidad`
4. `precio_unitario_neto`

---

## 📥 3. Facturas (BAJADA)

| Parámetro | Valor |
|-----------|-------|
| **Carpeta** | `/Facturas/` |
| **Nomenclatura** | `<F/D><sucursal><numero>.txt` |

### 3A. Renglón (`tipo = R`) — 14 campos:
1. `tipo` (R), 2. `fact_num`, 3. `numcon`, 4. `codigo_producto`, 5. `codigo_barras`
6. `descripcion_producto`, 7. `cantidad_articulo`, 8. `neto_renglon`
9. `precio_unitario`, 10. `porcentaje_descuentos` (D1+D2+D3+D4)
11. `precio_unitario_final`, 12. `numero_lote`, 13. `fecha_lote`, 14. `porcentaje_IVA`

### 3B. Encabezado (`tipo = E`) — campos adicionales:
`fecha_emision`, `tasa_dolar`, `total_numero_unidades`, `total_neto`,
`total_neto_sin_descuento`, `monto_descuento_global`, `guia_sicm`, `monto_iva`

---

## 📌 Integración n8n

- Script: `generic_inventario.py --proveedor INSUAMINCA_M --tabla InsuamincaM_Inventario` (misma estructura 10 cols que Intercontinental)
- Misma lógica para B y G cambiando `--proveedor` y `--tabla`
