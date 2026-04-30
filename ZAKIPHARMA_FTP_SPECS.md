# 📁 Zakipharma — Especificaciones de Archivos FTP

**Fuente:** Documentación Oficial Zakipharma C.A.

---

## 🔌 Parámetros de Conexión

| Campo | Valor |
|-------|-------|
| **Servidor** | `zakipharma.com` (o IP `45.137.159.247`) |
| **Usuario** | `u840108517.clientes30` |
| **Clave** | `4Tj-daAt` |
| **Protocolo** | FTP |

---

## 📥 1. Inventario / Existencias (BAJADA — Droguería → Nosotros)

Actualización cada **30 minutos**.

| Parámetro | Valor |
|-----------|-------|
| **Carpeta FTP** | `inventario/` |
| **Nombre del archivo** | `inventario.txt` (Nota: el doc también menciona `inventariocaracas.txt`) |
| **Encabezados** | ❌ No |
| **Separador de campos** | `;` |
| **Separador decimal** | `.` |
| **Decimales** | 2 |

### Estructura de campos (8 columnas):

| # | Campo | Tipo | Notas |
|---|-------|------|-------|
| 1 | `codigo_producto` | Texto | — |
| 2 | `codigo_barras` | Texto | — |
| 3 | `descripcion_producto` | Texto | — |
| 4 | `fecha_lote` | Texto | Formato `DD/MM/YYYY` |
| 5 | `precio_unitario` | Decimal | Precio base |
| 6 | `porcentaje_oferta_vigente` | Decimal | — |
| 7 | `precio_unitario_final` | Decimal | — |
| 8 | `stock_disponible` | Entero | — |

---

## 📤 2. Pedidos (SUBIDA — Nosotros → Droguería)

| Parámetro | Valor |
|-----------|-------|
| **Carpeta FTP** | `Pedidos/` |
| **Nombre del archivo** | `<CodCliente 4 chars>P<Correlativo 6 chars>.txt` |
| **Encabezados** | ❌ No |
| **Separador** | `;` |

### Estructura (4 columnas):
1. `codigo_producto` (Texto, max 6)
2. `descripcion_producto` (Texto)
3. `Cantidad` (Entero)
4. `precio_unitario` (Decimal)

---

## 📥 3. Facturas (BAJADA — Droguería → Nosotros)

| Parámetro | Valor |
|-----------|-------|
| **Carpeta FTP** | `Facturas/<CodCliente>/` |
| **Nombre del archivo** | `F<NumeroFactura>.txt` |
| **Discriminador** | Campo `tipo`: `R` = Renglón, `E` = Encabezado |

### 3A. Detalle Renglón (`tipo = R`)
1. `tipo` (R)
2. `fact_num`
3. `numcon`
4. `Codigo_producto` (Dromega)
5. `codigo_barras`
6. `descripcion_producto`
7. `Cantidad_Articulo`
8. `Neto_Renglon`
9. `Precio_unitario`
10. `Porcentaje_Descuentos` (D1+D2+D3)
11. `precio_unitario_final`
12. `Numero_Lote`
13. `fecha_lote` (DD/MM/YYYY)
14. `porcentaje_IVA`

### 3B. Encabezado (`tipo = E`)
1. `tipo` (E)
2. `fact_num`
3. `numcon`
4. `fecha_emision` (DD/MM/YYYY)
5. `Uso_Interno` (Nulo)
6. `Uso_Interno` (Nulo)
7. `Total_Numero_Renglones`
8. `Total_Numero_Unidades`
9. `Total_Neto`
10. `Tasa`
11. `Monto_descuento_Global`
12. `Porcentaje_descuento_global`
13. `Guia_Sicm`
14. `Monto_iva`
