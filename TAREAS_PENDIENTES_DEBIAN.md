# ⏳ Tareas Pendientes — Servidor Debian (`10.147.18.204`)

> Debian está caído. Ejecutar estos comandos en orden cuando vuelva a levantarse.

---

## 1. SQL Server — Crear Tablas Faltantes

Conectar a `EnterpriseAdmin_AMC` y ejecutar:

```sql
USE [EnterpriseAdmin_AMC];

-- INSUAMINCA Maturín (10 cols: + marca + indexado)
IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id WHERE s.name='Proveedores' AND t.name='InsuamincaM_Inventario')
CREATE TABLE [Proveedores].[InsuamincaM_Inventario] (
    [id] INT IDENTITY(1,1) PRIMARY KEY, [proveedor] VARCHAR(30) DEFAULT 'INSUAMINCA_M',
    [sucursal] VARCHAR(20) DEFAULT 'Maturin', [codigo_producto] VARCHAR(20) NOT NULL,
    [codigo_barras] VARCHAR(30), [descripcion_producto] VARCHAR(255) NOT NULL,
    [fecha_lote] DATE, [precio_unitario] DECIMAL(18,2), [pct_oferta_vigente] VARCHAR(10),
    [precio_unitario_final] DECIMAL(18,2), [stock_disponible] INT,
    [marca_proveedor] VARCHAR(50), [indexado_monto] VARCHAR(15),
    [fecha_carga] DATETIME DEFAULT GETDATE(),
    CONSTRAINT [UQ_InsuamincaM_Prod] UNIQUE ([codigo_producto],[proveedor]));

-- INSUAMINCA Caracas/Guarenas (B)
IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id WHERE s.name='Proveedores' AND t.name='InsuamincaB_Inventario')
CREATE TABLE [Proveedores].[InsuamincaB_Inventario] (
    [id] INT IDENTITY(1,1) PRIMARY KEY, [proveedor] VARCHAR(30) DEFAULT 'INSUAMINCA_B',
    [sucursal] VARCHAR(20) DEFAULT 'Caracas', [codigo_producto] VARCHAR(20) NOT NULL,
    [codigo_barras] VARCHAR(30), [descripcion_producto] VARCHAR(255) NOT NULL,
    [fecha_lote] DATE, [precio_unitario] DECIMAL(18,2), [pct_oferta_vigente] VARCHAR(10),
    [precio_unitario_final] DECIMAL(18,2), [stock_disponible] INT,
    [marca_proveedor] VARCHAR(50), [indexado_monto] VARCHAR(15),
    [fecha_carga] DATETIME DEFAULT GETDATE(),
    CONSTRAINT [UQ_InsuamincaB_Prod] UNIQUE ([codigo_producto],[proveedor]));

-- INSUAMINCA Barquisimeto (G/C)
IF NOT EXISTS (SELECT 1 FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id WHERE s.name='Proveedores' AND t.name='InsuamincaG_Inventario')
CREATE TABLE [Proveedores].[InsuamincaG_Inventario] (
    [id] INT IDENTITY(1,1) PRIMARY KEY, [proveedor] VARCHAR(30) DEFAULT 'INSUAMINCA_G',
    [sucursal] VARCHAR(20) DEFAULT 'Barquisimeto', [codigo_producto] VARCHAR(20) NOT NULL,
    [codigo_barras] VARCHAR(30), [descripcion_producto] VARCHAR(255) NOT NULL,
    [fecha_lote] DATE, [precio_unitario] DECIMAL(18,2), [pct_oferta_vigente] VARCHAR(10),
    [precio_unitario_final] DECIMAL(18,2), [stock_disponible] INT,
    [marca_proveedor] VARCHAR(50), [indexado_monto] VARCHAR(15),
    [fecha_carga] DATETIME DEFAULT GETDATE(),
    CONSTRAINT [UQ_InsuamincaG_Prod] UNIQUE ([codigo_producto],[proveedor]));
```

---

## 2. Debian — Subir Scripts ETL

```bash
# Crear estructura de directorios
mkdir -p /opt/scripts/droguerias

# Subir scripts (desde Windows vía SCP):
scp c:\source\N8N\scripts\droguerias\generic_inventario.py   root@10.147.18.204:/opt/scripts/droguerias/
scp c:\source\N8N\scripts\droguerias\nena.py                 root@10.147.18.204:/opt/scripts/droguerias/
scp c:\source\N8N\scripts\droguerias\zakipharma.py           root@10.147.18.204:/opt/scripts/droguerias/
scp c:\source\N8N\scripts\droguerias\intercontinental.py     root@10.147.18.204:/opt/scripts/droguerias/
scp c:\source\N8N\scripts\droguerias\its.py                  root@10.147.18.204:/opt/scripts/droguerias/

# Dar permisos
ssh root@10.147.18.204 "chmod +x /opt/scripts/droguerias/*.py"

# Verificar dependencias en Debian
ssh root@10.147.18.204 "pip3 install pyodbc python-dotenv"
```

---

## 3. Debian — Verificar Conectividad a FTPs con Puerto No Estándar

```bash
# Intercontinental (puerto 58021)
curl -v --connect-timeout 10 ftp://C02753:YMLZ\>Lch@interca.proteoerp.org:58021/

# Insuaminca (puerto 50021)
curl -v --connect-timeout 10 ftp://C01297:vua3FL1b@insuaminca.proteoerp.org:50021/

# NENA (credenciales fallaron — verificar)
# Usuario C344 retornó "530 User cannot log in" — confirmar clave con proveedor

# DROCERCA (credenciales fallaron)
# C0005r / j008376238 retornó "530 Login incorrect" — confirmar clave con proveedor
```

---

## 4. n8n — Importar Workflows (cuando Debian levante)

Para cada droguería, importar el JSON correspondiente de `c:\source\N8N\workflows\`:
- `PROD_VitalClinic_Inventario_ETL.json` → Credencial: `[PROD] Vital Clinic - FTP`
- Replicar para ITS, NENA, DROCERCA, ZAKIPHARMA, BIOGENÉTICA, INTERCONTINENTAL, INSUAMINCA (x3)

**Configuración del nodo SSH en n8n:**
```
python3 /opt/scripts/droguerias/generic_inventario.py --proveedor BIOGENETICA --tabla Biogenetica_Inventario
```
*(Cambiar --proveedor y --tabla por droguería)*

---

## 5. Credenciales con Problemas de Acceso FTP (Verificar)

| Droguería | Error | Acción |
|-----------|-------|--------|
| **NENA** | `530 User cannot log in` | Confirmar clave con proveedor. Posible: usuario `C344` no activo |
| **DROCERCA** | `530 Login incorrect` | Verificar si clave es `j008376238` o `J008376238` (mayúsculas) |
| **ZAKIPHARMA** | Timeout puerto 21 | Verificar si usan otro puerto o IP `45.137.159.247` directamente |
| **GAMA** | Conecta pero listing timeout | Modo pasivo FTP. Probar con `ftp_pasv=True` en script |
| **ITS** | Archivo en `/0722_inventario.txt` (raíz) | No en `Existencia/` — actualizar ruta en workflow |
