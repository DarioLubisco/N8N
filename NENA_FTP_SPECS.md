# 📁 NENA — Especificaciones de Archivos FTP

**Empresa:** Droguería Nena (Oriente)
**Código de Cliente:** C344

---

## 🔌 Parámetros de Conexión

| Campo | Valor |
|-------|-------|
| **Servidor** | `ftp.dronena.com` |
| **Puerto** | `21` |
| **Usuario** | `c344-foraneo` (Anteriormente se usaba `C344`) |
| **Contraseña** | *Por confirmar* (Login falló con `dronena2024`) |
| **Protocolo** | FTP |

> [!WARNING]
> **Error de Autenticación (530):** El servidor rechaza la conexión con los usuarios documentados y la clave reportada. Se requiere validación de la contraseña correcta o autorización de IP con el departamento de soporte de Nena.

---

## 📥 1. Inventario / Existencias

| Parámetro | Valor |
|-----------|-------|
| **Rutas Posibles** | `/Maracay/C344/inventario.txt` <br> `/Maracay/C344/C344.txt` <br> `/inventario.txt` |
| **Separador** | Ancho fijo (Fixed-width) o delimitado |

> [!NOTE]
> La estructura de Dronena históricamente utiliza posiciones de ancho fijo en lugar de delimitadores como punto y coma (`;`). Existe un script dedicado (`/opt/scripts/droguerias/nena.py`) diseñado para parsear este formato particular, basándose en la versión anterior `Imp_Inv_Dronena.py`.

---

## 📌 Integración n8n

- **Script Debian a usar:** `python3 /opt/scripts/droguerias/nena.py`
- Requiere resolución previa de credenciales para iniciar el desarrollo del workflow.
