# 📁 Vital Clinic — Especificaciones de Archivos FTP

**Fuente:** Documentación Conexión FTP — Departamento de Sistemas Vital Clinic
**Realizado por:** Joel M. Boada | **Verificado por:** Carlos de la Guardia
**Publicación:** Diciembre 2025

---

## 🔌 Parámetros de Conexión

| Campo | Valor |
|-------|-------|
| **Servidor** | `ftp2.vitalclinicdrogueria.com` |
| **Usuario** | `ftp2@vitalcliniconline.com` |
| **Clave** | `V1t9844.!hHrj` |
| **Protocolo** | FTP |

---

## 📤 1. Pedidos (SUBIDA — Nosotros → Droguería)

Archivo con los artículos solicitados a la droguería. **Nosotros lo generamos y subimos.**

| Parámetro | Valor |
|-----------|-------|
| **Carpeta FTP** | `Pedidos/` |
| **Nombre del archivo** | `<CodCliente 4 chars>P<Correlativo 6 chars>.txt` |
| **Ejemplo** | `0001P000001.txt` |
| **Encabezados** | ❌ No |
| **Separador de campos** | `;` |
| **Separador decimal** | `.` |
| **Decimales** | 2 |

### Estructura de campos:

| # | Campo | Tipo | Notas |
|---|-------|------|-------|
| 1 | `codigo_producto` | Texto | Máx. 6 caracteres |
| 2 | `descripcion_producto` | Texto | — |
| 3 | `cantidad` | Entero | — |
| 4 | `precio_unitario` | Decimal | Ej: `1250.00` |

**Ejemplo de línea:**
```
001234;AMOXICILINA 500MG CAPS;10;125.50
```

---

## 📥 2. Inventario / Existencias (BAJADA — Droguería → Nosotros)

Archivo con el stock disponible. **La droguería lo publica, nosotros lo descargamos.**
La droguería actualiza este archivo cada **20 minutos**.

| Parámetro | Valor |
|-----------|-------|
| **Carpeta FTP** | `Existencia/` |
| **Nombre del archivo** | `inventario.txt` |
| **Encabezados** | ❌ No |
| **Separador de campos** | `;` |
| **Separador decimal** | `.` |
| **Decimales** | 2 |

### Estructura de campos:

| # | Campo | Tipo | Notas |
|---|-------|------|-------|
| 1 | `codigo_producto` | Texto | Código interno Vital Clinic |
| 2 | `codigo_barras` | Texto | — |
| 3 | `descripcion_producto` | Texto | — |
| 4 | `fecha_lote` | Texto | Formato `DD/MM/YYYY` |
| 5 | `precio_unitario` | Decimal | Precio antes de descuentos |
| 6 | `porcentaje_oferta_vigente` (DP) | Carácter | Descuento de Precio |
| 7 | `precio_unitario_final` | Decimal | Precio tras aplicar DP + DA |
| 8 | `stock_disponible` | Entero | — |
| 9 | `articulo_indexado` | Carácter | `0` = indexado; vacío = no indexado |
| 10 | `descuento_adicional` (DA) | Carácter | Descuento Adicional |

---

## 📥 3. Facturas (BAJADA — Droguería → Nosotros)

Archivo de factura emitida por la droguería. Contiene **dos tipos de renglones** en el mismo archivo: encabezado (`E`) y detalle (`R`).

| Parámetro | Valor |
|-----------|-------|
| **Carpeta FTP** | `Facturas/<CodCliente 4 chars>/` |
| **Nombre del archivo** | `<NroFactura>.txt` — Ej: `50137345.txt` |
| **Encabezados** | ❌ No |
| **Separador de campos** | `;` |
| **Separador decimal** | `.` |
| **Decimales** | 2 |
| **Discriminador de tipo** | Campo `tipo`: `R` = Renglón de detalle, `E` = Encabezado |

---

### 3A. Renglón de Detalle (`tipo = R`)

| # | Campo | Tipo | Notas |
|---|-------|------|-------|
| 1 | `tipo` | Carácter | `R` |
| 2 | `fact_num` | Entero | Número de factura |
| 3 | `numcon` | Texto | Número de control |
| 4 | `codigo_producto` | Texto | Código interno Vital Clinic |
| 5 | `codigo_barras` | Texto | — |
| 6 | `descripcion_producto` | Texto | — |
| 7 | `cantidad_articulo` | Entero | Total de artículo comprado por lote |
| 8 | `neto_renglon` | Decimal | Monto neto del renglón (incluye descuento) |
| 9 | `precio_unitario` | Decimal | Precio antes de descuentos |
| 10 | `porcentaje_descuentos` | Carácter | Cuatro descuentos: `D1+D2+D3+D4` |
| 11 | `precio_unitario_final` | Decimal | Precio neto tras aplicar descuentos |
| 12 | `numero_lote` | Texto | Número de lote del producto |
| 13 | `fecha_lote` | Texto | Formato `DD/MM/YYYY` |
| 14 | `porcentaje_iva` | Decimal | — |
| 15 | `uso_interno` | Nulo | Ignorar |
| 16 | `articulo_indexado` | Texto | `0` = indexado; vacío = no indexado |

---

### 3B. Renglón de Encabezado (`tipo = E`)

| # | Campo | Tipo | Notas |
|---|-------|------|-------|
| 1 | `tipo` | Carácter | `E` |
| 2 | `fact_num` | Entero | Número de factura |
| 3 | `numcon` | Texto | Número de control |
| 4 | `fecha_emision` | Texto | Formato `DD/MM/YYYY` |
| 5 | `uso_interno` | Nulo | Ignorar |
| 6 | `uso_interno` | Nulo | Ignorar |
| 7 | `total_numero_renglones` | Entero | — |
| 8 | `total_numero_unidades` | Decimal | — |
| 9 | `total_neto` | Decimal | Neto total de la factura |
| 10 | `uso_interno` | Nulo | Ignorar |
| 11 | `monto_descuento_global` | Decimal | — |
| 12 | `porcentaje_descuento_global` | Decimal | — |
| 13 | `guia_sicm` | Texto | Número de Guía SICM |
| 14 | `monto_iva` | Decimal | Monto del impuesto en factura |
| 15 | `tasa_factura` | Decimal | Tasa Bs BCV |
| 16 | `factura_indexada` | Texto | `0` = indexada; vacío = no indexada |

---

## 📌 Notas de Integración n8n

- **Inventario:** Descargar `Existencia/inventario.txt` con nodo FTP. Frecuencia sugerida: cada 30 min (actualización droguería: cada 20 min).
- **Pedidos:** Generar archivo `.txt` en formato correcto y subirlo a `Pedidos/` con nodo FTP.
- **Facturas:** Monitorear la carpeta `Facturas/<CodCliente>/` para detectar nuevos `.txt` y procesarlos.
- El campo `tipo` en el archivo de facturas permite un solo `Split` para separar encabezados de renglones.
- Los campos `uso_interno` deben ignorarse en el parseo.
