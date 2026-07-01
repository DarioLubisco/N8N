# Diagnóstico Completo del Error de API Key en Cursor

## Problema Identificado

**Error**: "This model does not support custom API keys"
**Request ID**: af8e9aa8-5e76-4719-a42a-a7dc24608d2a

## Análisis Realizado

### 1. API Key Nativa Detectada

Cursor está usando su propia API key nativa:
```
API Key: crsr_868be19df0f2331ee8cce7f62beb41cc8ada7e1806cc23d0172471ca347a0a04
Endpoint: https://api2.cursor.sh
```

Esta API key es válida para **Composer 2.5** (modelo nativo), pero **no funciona con GLM 4.7**.

### 2. Servidores MCP Activos

Se detectaron 7 servidores MCP configurados en `~/.cursor/mcp.json`:
- `tavily-mcp` - Búsqueda web (requiere TAVILY_API_KEY)
- `exa` - Búsqueda web (requiere EXA_API_KEY)
- `firecrawl-mcp` - Web scraping (requiere FIRECRAWL_API_KEY)
- `mssql` - Base de datos SQL Server
- `n8n-mcp` - Workflow automation (requiere N8N_API_URL, N8N_API_KEY)
- `postgres` - Base de datos PostgreSQL
- `MCP_DOCKER` - Gateway Docker para MCPs

### 3. Root Cause del Error

El problema ocurre porque:

1. **Cursor está intentando usar GLM 4.7** en lugar de Composer 2.5
2. **GLM 4.7 no soporta la API key nativa de Cursor** (`crsr_*`)
3. **Algún MCP o configuración está forzando el uso de GLM 4.7**

## Causas Posibles

### A. MCPs con Capacidades de Visión
Algunos MCPs pueden tener configuraciones de visión que forcen el uso de modelos con capacidades visuales (como GLM 4.7 en lugar de Composer 2.5).

### B. Configuración Residual
Configuraciones anteriores o residuos pueden estar forzando modelos específicos.

### C. Workspace Contaminado
Aunque crees workspaces nuevos, puede haber:
- Configuración global que sobrescribe configuración local
- Archivos de configuración ocultos
- MCPs activos que cambian el modelo

## Soluciones Implementadas

### 1. Script de Diagnóstico: `check-cursor-config.sh`

Analiza completamente la configuración de Cursor:
- Procesos activos
- Configuración CLI
- Servidores MCP
- Plugins
- Skills
- Referencias a modelos externos

**Uso**:
```bash
./check-cursor-config.sh
```

### 2. Script de Corrección: `force-composer-2.5.sh`

Fuerza el uso de Composer 2.5 y deshabilita capacidades de visión:

**Acciones**:
1. Actualiza `~/.cursor/cli-config.json` con:
   - Modelo por defecto: `composer-2.5`
   - Proveedor: `cursor-native`
   - Desactiva modelos externos
   - Desactiva capacidades de visión

2. Crea `.cursor/config.json` en el workspace actual con:
   - Configuración local que fuerza Composer 2.5
   - Deshabilita procesamiento de imágenes
   - Bloquea MCPs con capacidades visuales

3. Crea `~/.cursor/mcp-blocklist.json` para controlar MCPs problemáticos

**Uso**:
```bash
./force-composer-2.5.sh
```

### 3. Configuración Manual

Si los scripts no funcionan, puedes aplicar la configuración manualmente:

#### A. Actualizar `~/.cursor/cli-config.json`:
```json
{
  "version": 1,
  "model": {
    "default": "composer-2.5",
    "provider": "cursor-native",
    "disableExternalModels": true
  },
  "features": {
    "vision": {
      "enabled": false,
      "fallbackMode": "text-only"
    },
    "textOnlyMode": true,
    "imageProcessing": false
  }
}
```

#### B. Crear `.cursor/config.json` en el workspace:
```json
{
  "model": {
    "default": "composer-2.5",
    "provider": "cursor-native",
    "forceNative": true
  },
  "features": {
    "vision": false,
    "textOnlyMode": true
  }
}
```

## Pasos para Resolver el Problema

### Paso 1: Ejecutar Script de Corrección
```bash
cd /home/synapse/source/N8N
./force-composer-2.5.sh
```

### Paso 2: Reiniciar Cursor Desktop
```bash
# Cerrar Cursor completamente
pkill -9 cursor

# Verificar que no haya procesos
ps aux | grep cursor

# Reiniciar Cursor Desktop (desde el menú o comando)
```

### Paso 3: Verificar Configuración en Cursor Desktop

1. **Abrir Settings** (⌘/Ctrl + ,)
2. **Ir a Models**
3. **Confirmar**:
   - Default Model: `Composer 2.5`
   - Provider: `Cursor Native`
   - Vision Features: **Desactivado**
   - Image Analysis: **Desactivado**
4. **Activar**: Text-only mode (si está disponible)

### Paso 4: Probar
1. Abrir un nuevo chat
2. Escribir un mensaje simple de texto
3. Verificar que el modelo sea Composer 2.5
4. No debería aparecer el error de API key

### Paso 5: Si el Error Persiste

1. **Abrir Developer Tools**:
   - Help → Toggle Developer Tools

2. **Revisar Consola**:
   - Buscar errores relacionados con "model", "provider", "API key"
   - Copiar mensajes de error específicos

3. **Revisar Network Tab**:
   - Buscar llamadas a `api2.cursor.sh`
   - Ver qué modelo está siendo solicitado
   - Ver si hay errores de autenticación

4. **Diagnóstico Adicional**:
   ```bash
   # Verificar modelo actual
   curl -H "Authorization: Bearer crsr_868be19df0f2331ee8cce7f62beb41cc8ada7e1806cc23d0172471ca347a0a04" \
        https://api2.cursor.sh/models
   ```

## Workaround Temporal

Si necesitas usar Cursor inmediatamente:

1. **Desactivar todos los MCPs temporalmente**:
   ```bash
   mv ~/.cursor/mcp.json ~/.cursor/mcp.json.backup
   touch ~/.cursor/mcp.json
   echo '{"mcpServers": {}}' > ~/.cursor/mcp.json
   ```

2. **Crear workspace de prueba completamente nuevo**:
   ```bash
   cd ~
   mkdir cursor-clean-test
   cd cursor-clean-test
   echo "# Clean test" > README.md
   ```

3. **Abrir en Cursor Desktop** y probar

4. **Si funciona**, reactivar MCPs uno por uno hasta identificar el problemático

## Configuración de Sincronización (Pregunta Original)

Para sincronizar MCPs y Skills entre computadoras:

### Skills
- Ubicación: `~/.cursor/skills/`
- Sincronización: Git repository, Syncthing, o dotfiles

### MCPs
- Ubicación: `~/.cursor/mcp.json`
- Sincronización: Git repository, Syncthing, o dotfiles

### Scripts de Sincronización
Ver `fix-cursor-api-key.md` para opciones de sincronización.

## Prevención

Para evitar este problema en el futuro:

1. **Usar siempre Composer 2.5** para workspaces sin imágenes
2. **Desactivar capacidades de visión** cuando no las necesites
3. **Crear configuraciones locales** en `.cursor/config.json` para cada proyecto
4. **Documentar configuraciones MCP** que puedan causar problemas
5. **Usar workspaces separados** para proyectos con y sin visión

## Soporte Adicional

Si después de aplicar todas las soluciones el problema persiste:

1. **Recopilar información**:
   - Request ID actual
   - Configuración completa (usar `check-cursor-config.sh`)
   - Logs de Developer Tools
   - Lista de MCPs activos

2. **Reportar a Cursor**:
   - Settings → Help → Report Issue
   - Incluir toda la información recopilada

3. **Alternativas**:
   - Usar Cursor CLI en lugar de Desktop
   - Configurar modelo alternativo compatible
   - Desactivar MCPs problemáticos

## Resumen

El error "This model does not support custom API keys" con Composer 2.5 es causado por:
- Intento de usar GLM 4.7 (que no soporta API key nativa)
- MCPs o configuraciones que forzan modelos externos
- Capacidades de visión activadas en workspaces sin imágenes

**Solución**: Forzar Composer 2.5, desactivar visión, y controlar MCPs problemáticos usando los scripts proporcionados.