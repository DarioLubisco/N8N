#!/bin/bash

# Script para forzar el uso de Composer 2.5 y evitar el error de API key

echo "=== Forzando configuración de Composer 2.5 ==="
echo ""

# 1. Actualizar cli-config.json para forzar modelo nativo
echo "1. Configurando modelo nativo en cli-config.json..."
cat > ~/.cursor/cli-config.json << 'EOF'
{
  "version": 1,
  "editor": {
    "vimMode": false
  },
  "display": {
    "showLineNumbers": false,
    "showThinkingBlocks": false,
    "showStatusIndicators": false,
    "showStatusLineRunningTime": false
  },
  "notifications": true,
  "hints": true,
  "rewind": true,
  "suggestNextPrompt": false,
  "hasChangedDefaultModel": false,
  "permissions": {
    "allow": [
      "Shell(ls)"
    ],
    "deny": []
  },
  "approvalMode": "allowlist",
  "sandbox": {
    "mode": "disabled",
    "networkAccess": "user_config_with_defaults"
  },
  "runEverythingSettingsPromptStreak": 0,
  "network": {
    "useHttp1ForAgent": false
  },
  "attribution": {
    "attributeCommitsToAgent": true,
    "attributePRsToAgent": true
  },
  "model": {
    "default": "composer-2.5",
    "provider": "cursor-native",
    "disableExternalModels": true,
    "disableCustomAPIKeys": false
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
EOF
echo "   ✅ Configuración actualizada"
echo ""

# 2. Crear configuración específica del workspace
echo "2. Creando configuración local del workspace..."
WORKSPACE_CONFIG_DIR="$(pwd)/.cursor"
mkdir -p "$WORKSPACE_CONFIG_DIR"

cat > "$WORKSPACE_CONFIG_DIR/config.json" << 'EOF'
{
  "model": {
    "default": "composer-2.5",
    "provider": "cursor-native",
    "forceNative": true,
    "availableModels": [
      "composer-2.5",
      "composer-2.5-fast"
    ]
  },
  "features": {
    "vision": false,
    "textOnlyMode": true,
    "imageProcessing": false,
    "disableVisionFallback": true
  },
  "mcp": {
    "disableVisionServers": true,
    "disableImageCapabilities": true
  },
  "workarounds": {
    "disableCustomApiKeyCheck": true,
    "forceNativeModel": true,
    "disableExternalModelRouting": true
  }
}
EOF
echo "   ✅ Configuración local creada en: $WORKSPACE_CONFIG_DIR/config.json"
echo ""

# 3. Verificar MCPs que podrían estar causando problemas
echo "3. Verificando MCPs con capacidades de visión..."
grep -r "vision\|image\|picture" ~/.cursor/mcp.json 2>/dev/null | head -5 || echo "   No se encontraron MCPs con capacidades de visión"
echo ""

# 4. Verificar si hay MCPs que puedan estar forzando modelos externos
echo "4. MCPs activos:"
cat ~/.cursor/mcp.json | jq -r '.mcpServers | keys[]' 2>/dev/null || echo "   No se pudo listar MCPs"
echo ""

# 5. Crear lista de bloqueo de MCPs problemáticos
echo "5. Creando configuración para deshabilitar MCPs problemáticos..."
cat > ~/.cursor/mcp-blocklist.json << 'EOF'
{
  "blockedServers": [],
  "reason": "Prevent MCPs from forcing external models or vision capabilities",
  "allowList": [
    "cursor-app-control",
    "cursor-ide-browser"
  ]
}
EOF
echo "   ✅ Bloqueo de MCPs configurado"
echo ""

# 6. Verificar configuración de entorno
echo "6. Variables de entorno que pueden interferir:"
env | grep -iE "cursor_model|cursor_provider|cursor_api" || echo "   No se encontraron variables de configuración de Cursor"
echo ""

# 7. Instrucciones de reinicio
echo "=== Instrucciones para aplicar cambios ==="
echo ""
echo "1. **Reiniciar Cursor Desktop** (obligatorio):"
echo "   - Cierra completamente Cursor (Cmd/Ctrl + Q)"
echo "   - Verifica que no haya procesos: ps aux | grep cursor"
echo "   - Si hay procesos, elimínalos: pkill -9 cursor"
echo "   - Reinicia Cursor Desktop"
echo ""
echo "2. **Abrir este workspace** en Cursor Desktop"
echo "   - Abre el proyecto desde File → Open Folder"
echo "   - Verifica en Settings → Models que 'Composer 2.5' esté seleccionado"
echo ""
echo "3. **Verificar en Settings**:"
echo "   - Settings → Models"
echo "   - Confirma: Default Model = Composer 2.5"
echo "   - Desactiva: 'Enable Vision Features'"
echo "   - Desactiva: 'Image Analysis'"
echo "   - Activa: 'Text Only Mode' (si está disponible)"
echo ""
echo "4. **Prueba**:"
echo "   - Abre un nuevo chat"
echo "   - Escribe un mensaje simple"
echo "   - El modelo debería ser Composer 2.5 (sin error de API key)"
echo ""
echo "5. **Si el error persiste**:"
echo "   - Abre Developer Tools (Help → Toggle Developer Tools)"
echo "   - Revisa la consola para errores específicos"
echo "   - Busca en Network tab las llamadas a api2.cursor.sh"
echo "   - Mira qué modelo está siendo solicitado"
echo ""
echo "Configuración completada. Reinicia Cursor para aplicar cambios."