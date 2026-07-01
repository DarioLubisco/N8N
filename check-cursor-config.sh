#!/bin/bash

# Script para verificar la configuración actual de Cursor y modelos

echo "=== Verificación de Configuración de Cursor ==="
echo ""

# Verificar si Cursor está corriendo
echo "1. Procesos de Cursor:"
ps aux | grep -i cursor | grep -v grep || echo "   No se detectaron procesos de Cursor"
echo ""

# Verificar configuración del CLI
echo "2. Configuración CLI (~/.cursor/cli-config.json):"
if [[ -f ~/.cursor/cli-config.json ]]; then
    cat ~/.cursor/cli-config.json
else
    echo "   No existe archivo de configuración CLI"
fi
echo ""

# Verificar configuración MCP
echo "3. Configuración MCP (~/.cursor/mcp.json):"
if [[ -f ~/.cursor/mcp.json ]]; then
    echo "   Servidores MCP configurados:"
    cat ~/.cursor/mcp.json | jq -r '.mcpServers | keys[]' 2>/dev/null || echo "   (no se pudo parsear JSON)"
    echo ""
    echo "   Detalles de configuración:"
    cat ~/.cursor/mcp.json
else
    echo "   No existe configuración MCP"
fi
echo ""

# Verificar plugins
echo "4. Plugins instalados:"
if [[ -d ~/.cursor/plugins ]]; then
    find ~/.cursor/plugins -name "metadata.json" -o -name "package.json" 2>/dev/null | while read plugin; do
        echo "   $plugin"
        cat "$plugin" | grep -E '"name"|"description"' | head -2 2>/dev/null || true
    done | head -20
else
    echo "   No se encontraron plugins"
fi
echo ""

# Verificar skills personalizados
echo "5. Skills personales:"
if [[ -d ~/.cursor/skills ]]; then
    find ~/.cursor/skills -name "SKILL.md" 2>/dev/null | wc -l | xargs -I {} echo "   {} skills encontrados"
else
    echo "   No se encontraron skills personales"
fi
echo ""

# Verificar directorios de proyecto activos
echo "6. Proyectos activos recientes:"
if [[ -d ~/.cursor/projects ]]; then
    ls -1t ~/.cursor/projects/ | head -10 | while read project; do
        echo "   - $project"
    done
else
    echo "   No se encontraron proyectos"
fi
echo ""

# Verificar configuración de red
echo "7. Configuración de red:"
if [[ -f ~/.cursor/cli-config.json ]]; then
    cat ~/.cursor/cli-config.json | grep -A 5 "network" || echo "   No hay configuración de red específica"
fi
echo ""

# Verificar archivos temporales
echo "8. Archivos temporales/caché:"
if [[ -d ~/.cursor/cache ]]; then
    du -sh ~/.cursor/cache 2>/dev/null || echo "   Directorio cache existe (sin datos de tamaño)"
else
    echo "   No se encontró directorio cache"
fi
echo ""

# Buscar referencias a modelos externos
echo "9. Referencias a modelos externos en configuración:"
find ~/.cursor -name "*.json" -type f 2>/dev/null | xargs grep -lE "openai|anthropic|gemini|zhipu|claude|gpt" 2>/dev/null | grep -v "projects/" | head -10 || echo "   No se encontraron referencias a modelos externos"
echo ""

# Verificar permisos
echo "10. Permisos de configuración:"
if [[ -f ~/.cursor/cli-config.json ]]; then
    ls -l ~/.cursor/cli-config.json
fi
if [[ -f ~/.cursor/mcp.json ]]; then
    ls -l ~/.cursor/mcp.json
fi
echo ""

# Diagnóstico de vision capabilities
echo "11. Configuración relacionada con visión:"
grep -ri "vision\|image\|picture\|visual" ~/.cursor/*.json 2>/dev/null | grep -v "projects/" || echo "   No se encontraron configuraciones de visión"
echo ""

# Sugerencias
echo "=== Sugerencias de depuración ==="
echo ""
echo "Si el problema persiste:"
echo ""
echo "1. Forzar reinicio de Cursor Desktop:"
echo "   - Cierra completamente Cursor"
echo "   - Matar procesos: pkill -9 cursor"
echo "   - Limpia caché: rm -rf ~/.cursor/cache/"
echo "   - Reinicia Cursor"
echo ""
echo "2. Verificar en Cursor Desktop Settings:"
echo "   - Settings → Models"
echo "   - Confirmar que 'Composer 2.5' está seleccionado"
echo "   - Desactivar cualquier opción de 'Vision' o 'Image Analysis'"
echo "   - Configurar 'Text-only mode' si está disponible"
echo ""
echo "3. Verificar Developer Tools:"
echo "   - Help → Toggle Developer Tools"
echo "   - Buscar errores en Console tab"
echo "   - Buscar errores en Network tab relacionados con 'model' o 'api'"
echo ""
echo "4. Verificar Workspace:"
echo "   - El workspace no debe contener imágenes"
echo "   - No debe haber archivos con visión habilitada"
echo "   - Considera usar el workspace de prueba creado por fix-cursor-api-key.sh"