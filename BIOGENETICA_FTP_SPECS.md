# 📁 Biogenética — Especificaciones de Archivos FTP

**Fuente:** Documentación Oficial Droguería Biogenética C.A.
**Código de Cliente FTP:** `0169` — FARMACIA AMERICANA, C.A.

---

## 🔌 Parámetros de Conexión

| Campo | Valor |
|-------|-------|
| **Servidor** | `46.202.182.119` |
| **Usuario** | `u381534864.clientesdrogueriabiogenetica` |
| **Clave** | `D=Qb13vi.Wmh` |
| **Puerto** | `21` |
| **Protocolo** | FTP |

---

## 📥 1. Inventario / Existencias (BAJADA — Droguería → Nosotros)

Actualización cada **30 minutos**. Formato idéntico al estándar → usa `generic_inventario.py`.

| Parámetro | Valor |
|-----------|-------|
| **Carpeta FTP** | `Existencia/` |
| **Nombre** | `inventario.txt` |
| **Encabezados** | ❌ No |
| **Separador** | `;` |

### Estructura (8 columnas):

| # | Campo | Tipo |
|---|-------|------|
| 1 | `codigo_producto` | Texto |
| 2 | `codigo_barras` | Texto |
| 3 | `descripcion_producto` | Texto |
| 4 | `fecha_lote` | Texto `DD/MM/YYYY` |
| 5 | `precio_unitario` | Decimal |
| 6 | `porcentaje_oferta_vigente` | Decimal |
| 7 | `precio_unitario_final` | Decimal |
| 8 | `stock_disponible` | Entero |

---

## 📤 2. Pedidos (SUBIDA — Nosotros → Droguería)

> [!WARNING]
> ⚠️ **DIFERENTE al estándar.** Biogenética pide un **Excel (.xls) CON encabezado**, no TXT sin encabezado.

| Parámetro | Valor |
|-----------|-------|
| **Carpeta FTP** | `Pedidos/` |
| **Nombre** | `<CodClienteFTP 4 chars>P<Correlativo 6 chars>` (sin .txt) |
| **Formato** | `.xls` con encabezado |
| **Separador** | N/A (Excel) |

### Estructura (2 columnas):

| Columna Header | Campo | Tipo |
|---------------|-------|------|
| `codigo` | `codigo_barras` | Texto (máx 20) |
| `cantidad` | `Cantidad` | Entero |

---

## 📥 3. Facturas (BAJADA — Droguería → Nosotros)

| Parámetro | Valor |
|-----------|-------|
| **Carpeta FTP** | `Facturas/<CodCliente>/` |
| **Nombre** | `F<NumeroFactura>.txt` |
| **Discriminador** | Campo `tipo`: `R` = Renglón, `E` = Encabezado |

### 3A. Detalle Renglón (`tipo = R`) — 14 campos:
1. `tipo` (R)
2. `fact_num` (Entero)
3. `numcon` (Texto)
4. `Codigo_producto` (Interno Biogenética)
5. `codigo_barras`
6. `descripcion_producto`
7. `Cantidad_Articulo` (Entero)
8. `Neto_Renglon` (Decimal)
9. `Precio_unitario` (Decimal)
10. `Porcentaje_Descuentos` (D1+D2+D3)
11. `precio_unitario_final` (Decimal)
12. `Numero_Lote` (Texto)
13. `fecha_lote` (DD/MM/YYYY)
14. `porcentaje_IVA` (Decimal)

### 3B. Encabezado (`tipo = E`) — 14 campos:
1. `tipo` (E)
2. `fact_num`
3. `numcon`
4. `fecha_emision` (DD/MM/YYYY)
5. `Uso_Interno` (Nulo)
6. `Uso_Interno` (Nulo)
7. `Total_Numero_Renglones` (Entero)
8. `Total_Numero_Unidades` (Decimal)
9. `Total_Neto` (Decimal)
10. `Uso_Interno` (Nulo)
11. `Monto_descuento_Global` (Decimal)
12. `Porcentaje_descuento_global` (Decimal)
13. `Guia_Sicm` (Texto)
14. `Monto_iva` (Decimal)

---

## 📌 Notas de Integración n8n

- **Inventario:** Usar `generic_inventario.py --proveedor BIOGENETICA --tabla Biogenetica_Inventario`
- **Pedidos (⚠️ Especial):** Requiere nodo **Code** en n8n para generar XLS (librería `openpyxl` o `xlwt` en Python). No es un simple TXT.
