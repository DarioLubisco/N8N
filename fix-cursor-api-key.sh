#!/bin/bash

# Script para crear un workspace limpio y diagnosticar el problema de API key

echo "=== Diagnóstico del problema de API key en Cursor ==="
echo ""

# 1. Verificar variables de entorno
echo "1. Variables de entorno relacionadas con APIs:"
env | grep -iE "api|model|openai|anthropic|gemini|zhipu|cursor" || echo "   No se encontraron variables sospechosas"
echo ""

# 2. Verificar configuración de Cursor
echo "2. Configuración de Cursor:"
ls -la ~/.cursor/*.json 2>/dev/null | while read file; do
    echo "   Archivo: $file"
    if [[ -f "$file" ]]; then
        grep -iE "api|model|provider|vision" "$file" 2>/dev/null | head -5 || echo "   (sin coincidencias)"
    fi
done
echo ""

# 3. Verificar configuración de MCP
echo "3. Configuración de MCP:"
if [[ -f ~/.cursor/mcp.json ]]; then
    echo "   MCP servers configurados:"
    cat ~/.cursor/mcp.json | grep -o '"[^"]*"' | grep -vE "command|args|env|url|header" | sort -u
else
    echo "   No se encontró configuración MCP"
fi
echo ""

# 4. Crear workspace de prueba
echo "4. Creando workspace de prueba limpio..."
TIMESTAMP=$(date +%s)
WORKSPACE="$HOME/cursor-test-$TIMESTAMP"

mkdir -p "$WORKSPACE"
cd "$WORKSPACE"

# Crear archivo .gitignore
cat > .gitignore << 'EOF'
# Cursor
.cursor/
.vscode/

# Common
node_modules/
.env

# No images
*.png
*.jpg
*.jpeg
*.gif
*.svg
*.webp
EOF

# Crear README solo texto
cat > README.md << 'EOF'
# Cursor Test Workspace

This workspace is designed for testing Composer 2.5 without any vision capabilities.

## Purpose
- Test native Cursor model (Composer 2.5)
- Verify no API key requirements
- Ensure text-only operation

## Files
- All files are text-only
- No images or visual content
- Clean configuration
EOF

# Inicializar git
git init
git add .
git commit -m "Initial commit - clean workspace for Composer 2.5 testing"

# Crear configuración local de Cursor
mkdir -p .cursor
cat > .cursor/config.json << 'EOF'
{
  "model": {
    "default": "composer-2.5",
    "provider": "cursor-native"
  },
  "features": {
    "vision": false,
    "imageProcessing": false,
    "textOnlyMode": true
  }
}
EOF

echo "   Workspace creado en: $WORKSPACE"
echo ""

# 5. Verificar extensiones
echo "5. Extensiones instaladas:"
if [[ -d ~/.cursor/extensions ]]; then
    ls -1 ~/.cursor/extensions/ 2>/dev/null | wc -l | xargs -I {} echo "   {} extensiones encontradas"
    echo "   Lista:"
    ls -1 ~/.cursor/extensions/ 2>/dev/null | head -10
else
    echo "   No se encontraron extensiones"
fi
echo ""

# 6. Información de diagnóstico
echo "6. Información para reportar:"
echo "   Timestamp: $TIMESTAMP"
echo "   Workspace: $WORKSPACE"
echo "   Config file: $WORKSPACE/.cursor/config.json"
echo ""

# 7. Instrucciones
echo "=== Instrucciones para probar ==="
echo ""
echo "1. Abre Cursor Desktop"
echo "2. Abre el workspace: $WORKSPACE"
echo "3. Abre un nuevo chat"
echo "4. Intenta usar el modelo Composer 2.5"
echo "5. Si el error persiste, proporciona esta información:"
echo ""
echo "   - Error exacto:"
echo "     Request ID: af8e9aa8-5e76-4719-a42a-a7dc24608d2a"
echo "   - Timestamp de creación: $TIMESTAMP"
echo "   - Ruta del workspace: $WORKSPACE"
echo "   - ¿El error ocurre en el primer mensaje o después?"
echo "   - ¿Qué tipo de mensaje estás enviando (texto, código, etc.)?"
echo ""
echo "   También revisa:"
echo "   - Developer Tools (Help → Toggle Developer Tools)"
echo "   - Consola para errores relacionados con model provider"
echo ""
echo "Workspace limpio creado exitosamente."