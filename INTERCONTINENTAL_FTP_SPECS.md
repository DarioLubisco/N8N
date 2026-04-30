# 📁 Intercontinental — Especificaciones de Archivos FTP

**Empresa:** Inversiones Gasanrod C.A.
**Fuente:** Datos de conexión oficiales recibidos.

---

## 🔌 Parámetros de Conexión

| Campo | Valor |
|-------|-------|
| **Servidor** | `interca.proteoerp.org` |
| **Puerto** | **`58021`** ⚠️ Puerto no estándar |
| **Usuario** | `C02753` |
| **Contraseña** | `YMLZ>Lch` |
| **Protocolo** | FTP |

> [!WARNING]
> Puerto **58021** — no usar el 21 por defecto. Configurar explícitamente en n8n.

---

## 📥 1. Inventario / Existencias

| Parámetro | Valor |
|-----------|-------|
| **Ruta** | `/Inventario.txt` (raíz del FTP) |
| **Separador** | `;` |
| **Nota** | El precio ya incluye el descuento del cliente aplicado |

### Estructura (10 columnas):

| # | Campo | Tipo BD | Notas |
|---|-------|---------|-------|
| 1 | `Codigo` | VARCHAR(15) | Código interno |
| 2 | `CodBarras` | VARCHAR(15) | — |
| 3 | `Descripcion` | VARCHAR(45) | — |
| 4 | `Vence` | DATE | Fecha vencimiento lote |
| 5 | `Precio` | DECIMAL(25,2) | Precio sin descuento |
| 6 | `Descuento` | DECIMAL(33,2) | % Descuento |
| 7 | `PrecioFinal` | DECIMAL(25,2) | **Precio con descuento aplicado** |
| 8 | `Existencia` | DECIMAL(12,0) | Stock |
| 9 | `Marca` | VARCHAR(30) | ⚠️ Extra vs estándar |
| 10 | `montofactura` | VARCHAR(10) | ⚠️ Extra vs estándar |

---

## 📤 2. Pedidos (SUBIDA)

| Parámetro | Valor |
|-----------|-------|
| **Carpeta FTP** | `/Pedidos/` |

### Estructura (4 columnas):
| # | Campo | Tipo |
|---|-------|------|
| 1 | `Codigo` | VARCHAR(15) |
| 2 | `Descripcion` | VARCHAR(45) |
| 3 | `Cantidad` | DECIMAL(12,3) |
| 4 | `Cod_cli` | VARCHAR(15) |

---

## 📥 3. Facturas (BAJADA)

| Parámetro | Valor |
|-----------|-------|
| **Carpeta FTP** | `/Facturas/` |
| **Discriminador** | Campo `Renglon`: `R` = Detalle, `E` = Encabezado |

### 3A. Detalle Renglón (`Renglon = R`) — 14 campos:
| # | Campo | Tipo | Notas |
|---|-------|------|-------|
| 1 | `Renglon` | VARCHAR(1) | `R` |
| 2 | `No_Factura` | VARCHAR(9) | — |
| 3 | `No_Fiscal` | VARCHAR(9) | Nro. de Control |
| 4 | `Codigo` | CHAR(15) | Código interno |
| 5 | `Barras` | VARCHAR(15) | Código de barras |
| 6 | `Descripcion` | VARCHAR(40) | — |
| 7 | `Cantidad` | DECIMAL(12,3) | — |
| 8 | `Neto` | DECIMAL(19,2) | Monto neto renglón |
| 9 | `PrecioSD` | DECIMAL(19,2) | Precio unitario **sin** descuento |
| 10 | `Descuentos` | DECIMAL(19,2) | % Descuento aplicado |
| 11 | `PrecionCD` | DECIMAL(19,2) | Precio unitario **con** descuento |
| 12 | `lote` | VARCHAR(12) | — |
| 13 | `fechalote` | DATE | — |
| 14 | `TasaIVA` | DECIMAL(6,2) | — |

### 3B. Encabezado (`Renglon = E`) — 12 campos:
| # | Campo | Tipo | Notas |
|---|-------|------|-------|
| 1 | `Renglon` | VARCHAR(1) | `E` |
| 2 | `No_Factura` | VARCHAR(9) | — |
| 3 | `No_Fiscal` | VARCHAR(9) | — |
| 4 | `FechaEmi` | DATE | Fecha emisión |
| 5 | `tasabcv` | DECIMAL(25,2) | Tasa BCV |
| 6 | `Totalunidades` | DECIMAL(25) | — |
| 7 | `Neto` | DECIMAL(19,2) | Neto total factura |
| 8 | `Des.Lineal` | DECIMAL(19,2) | Descuento lineal |
| 9 | `Mon.des` | DECIMAL(19,2) | Monto descuento |
| 10 | `Desc.eso` | DECIMAL(19,2) | Descuento especial |
| 11 | `SICM` | DECIMAL(19,2) | Guía SICM |
| 12 | `totalIVA` | DECIMAL(6,2) | — |

---

## 📌 Notas de Integración n8n

- ⚠️ Configurar puerto **58021** explícitamente en la credencial FTP de n8n.
- El inventario tiene **10 columnas** (2 extra vs estándar): usar script dedicado, no el genérico.
- `Existencia` es DECIMAL(12,0), tratarlo como entero en Python.
