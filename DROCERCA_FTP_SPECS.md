# 📁 DROCERCA — Especificaciones de Archivos FTP

**Empresa:** Droguería Drocerca

---

## 🔌 Parámetros de Conexión

| Campo | Valor |
|-------|-------|
| **Servidor** | `drocerca.proteoerp.org` |
| **Puerto** | `21` |
| **Usuario FTP** | `C0005r` |
| **Contraseña FTP** | `j008376238` |
| **Usuario Web** | `W0005R` |
| **Contraseña Web** | `J008376238` |
| **Protocolo** | FTP |

> [!WARNING]
> **Error de Autenticación Temporal (530):** En la última validación de conexión el servidor reportó un error de login con las credenciales indicadas. Se recomienda verificar si el sistema es sensible a mayúsculas (`J008376238` en lugar de `j008376238`).

---

## 📥 1. Inventario / Existencias

| Parámetro | Valor |
|-----------|-------|
| **Formato** | Generado por **ProteoERP** |
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

- **Script Debian a usar:** `python3 /opt/scripts/droguerias/drocerca.py` (o el genérico configurado para su tabla).
