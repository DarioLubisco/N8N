-- ============================================================
-- Vital Clinic — Tabla de Inventario
-- Schema: Proveedores
-- ============================================================
-- Ejecutar en: EnterpriseAdmin_AMC
-- ============================================================

USE [EnterpriseAdmin_AMC];
GO

IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = 'Proveedores')
BEGIN
    EXEC('CREATE SCHEMA [Proveedores]');
    PRINT 'Schema [Proveedores] creado.';
END
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.tables t
    INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE s.name = 'Proveedores' AND t.name = 'VitalClinic_Inventario'
)
BEGIN
    CREATE TABLE [Proveedores].[VitalClinic_Inventario] (
        -- PK compuesta: producto + proveedor (para escalar a multi-sucursal)
        [id]                        INT             IDENTITY(1,1) NOT NULL,
        [proveedor]                 VARCHAR(30)     NOT NULL DEFAULT 'VITAL_CLINIC',
        [codigo_producto]           VARCHAR(20)     NOT NULL,

        -- Identificación del artículo
        [codigo_barras]             VARCHAR(30)     NULL,
        [descripcion_producto]      VARCHAR(255)    NOT NULL,

        -- Precios
        [precio_unitario]           DECIMAL(18, 2)  NULL,
        [pct_oferta_vigente_dp]     VARCHAR(10)     NULL,   -- Descuento de Precio (DP)
        [precio_unitario_final]     DECIMAL(18, 2)  NULL,   -- Precio tras DP + DA
        [descuento_adicional_da]    VARCHAR(10)     NULL,   -- Descuento Adicional (DA)

        -- Stock y lote
        [stock_disponible]          INT             NULL,
        [fecha_lote]                DATE            NULL,
        [articulo_indexado]         BIT             NOT NULL DEFAULT 0,

        -- Auditoría
        [fecha_carga]               DATETIME        NOT NULL DEFAULT GETDATE(),

        CONSTRAINT [PK_VitalClinic_Inventario] PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [UQ_VitalClinic_Prod] UNIQUE ([codigo_producto], [proveedor])
    );

    -- Índices para búsqueda rápida
    CREATE INDEX [IX_VitalClinic_CodigoBarras]
        ON [Proveedores].[VitalClinic_Inventario] ([codigo_barras]);

    CREATE INDEX [IX_VitalClinic_Stock]
        ON [Proveedores].[VitalClinic_Inventario] ([stock_disponible])
        WHERE [stock_disponible] > 0;

    PRINT 'Tabla [Proveedores].[VitalClinic_Inventario] creada correctamente.';
END
ELSE
BEGIN
    PRINT 'La tabla ya existe. No se realizaron cambios.';
END
GO
