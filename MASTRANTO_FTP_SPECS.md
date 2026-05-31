# Especificaciones de Integración FTP - MASTRANTO

*Este documento detalla la estructura y los formatos requeridos para la integración automatizada de Inventarios y Pedidos con la droguería Mastranto.*

## 1. Conexión FTP

*   **Host:** `drogueriaelmastrantomm.com`
*   **Puerto:** `21`
*   **Usuario:** `clientes`
*   **Contraseña:** `M4str4nt0*`

### Estructura de Directorios
Dentro del FTP principal existen dos carpetas:
*   `/Listados/` (Para descarga de inventarios diarios)
*   `/pedidos/` (Para carga de pedidos hacia la droguería)

---

## 2. Ingesta de Inventario (Descarga)

Mastranto dispone los listados en 3 formatos idénticos en columnas, ubicados en las siguientes rutas:
*   `/Listados/txt/` (Recomendado, usa `|` como separador)
*   `/Listados/csv/` (Comilla doble `"` para texto, `.` para decimales, `,` para separación)
*   `/Listados/excel/` (`.xlsx`)

**Estructura de Columnas (20 Columnas):**

1.  **CODIGO INTERNO** (Máx 15 caracteres alfanuméricos)
2.  **CODIGO DE BARRAS** (EAN13)
3.  **ETIQUETA** (Características / Nuevas entradas)
4.  **CATEGORIA** (medicamento, material medico, miscelaneo, otros)
5.  **PRODUCTO** (Nombre y descripción)
6.  **STOCK CENTRO** (Cantidad disponible en Carrizal)
7.  **STOCK BARINAS** (Cantidad disponible en Barinas)
8.  **COMPONENTE ACTIVO**
9.  **LABORATORIO**
10. **UNIDAD MANEJO** (Por defecto unidad)
11. **IVA / EXENTO** ("EXENTO" o "16%")
12. **ACCION TERAPEUTICA** (Función principal)
13. **$PRECIO ANTES** (Precio base divisa, usa decimales)
14. **DESCUENTO** (Primer descuento ventas)
15. **DESCUENTO 2** (Segundo descuento comercial)
16. **$PRECIO NETO** (Precio final tras descuentos)
17. **$ PRECIO CON IVA** (Precio neto + IVA si aplica)
18. **ORIGEN** (País de origen)
19. **VENCIMIENTO CENTRO** (Fecha vto. Carrizal)
20. **VENCIMIENTO BARINAS** (Fecha vto. Barinas)

---

## 3. Emisión de Pedidos (Subida)

Los pedidos deben subirse en una subcarpeta identificada por el **RIF de la Farmacia** (que actúa como código de cliente). Nosotros debemos crear la carpeta si no existe.

*   **Ruta de Subida:** `/pedidos/<RIF_FARMACIA>/`
*   **Nombre de Archivo Sugerido:** `<NroPedido>_<YYYYMMDDHHMMSS>.txt` (Ej: `PED001_20260506.txt`)
*   **Formato Recomendado:** TXT (Separador `|` Barra vertical)

### Estructura del Archivo de Pedido (Mínimo requerido)
Cada línea del archivo debe contener, como mínimo, la siguiente información separada por `|`:
1.  **Código Interno de Producto**
2.  **Cantidad Solicitada**
3.  **Precio** (Separador decimal con punto `.`)

> ⚠️ **Consideración Especial para Mastranto:** Las facturas digitales no se emiten por esta vía FTP, sino a través de una plataforma alterna (en desarrollo por parte de Mastranto). Por lo tanto, no aplica el sub-flujo de lectura de facturas.
