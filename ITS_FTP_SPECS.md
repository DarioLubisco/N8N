# 📁 ITS — Especificaciones de Archivos FTP

**Empresa:** Droguería ITS

---

## 🔌 Parámetros de Conexión

| Campo | Valor |
|-------|-------|
| **Servidor** | `ftp.knc.dsp.mybluehost.me` |
| **Puerto** | `21` |
| **Usuario (Inventario)** | `clienteits0722@drogueriaits2015.com.ve` |
| **Contraseña** | `droguer159..` |
| **Protocolo** | FTP |

---

## 📥 1. Inventario / Existencias

| Parámetro | Valor |
|-----------|-------|
| **Ruta Confirmada** | `/0722_inventario.txt` (En la raíz del FTP) |
| **Separador** | `;` |
| **Encabezado** | ❌ No |

### Estructura (8 columnas estándar):

| # | Campo |
|---|-------|
| 1 | `codigo_producto` |
| 2 | `codigo_barras` |
| 3 | `descripcion_producto` |
| 4 | `fecha_lote` |
| 5 | `precio_unitario` |
| 6 | `porcentaje_oferta_vigente` |
| 7 | `precio_unitario_final` |
| 8 | `stock_disponible` |

---

## 📌 Integración n8n

- **Script Debian a usar:** `python3 /opt/scripts/droguerias/its.py` o `generic_inventario.py` (con `--proveedor ITS --tabla ITS_Inventario`).
- **Estado de conexión:** ✅ Verificada correctamente mediante script de muestreo local.
