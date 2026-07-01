# Solución para Error "This model does not support custom API keys"

## Problema
El modelo nativo (Composer 2.5) no debería requerir API keys, pero Cursor está mostrando este error.

## Pasos para Resolver

### 1. Verificar Configuración del Modelo en Cursor Desktop

En Cursor Desktop:
- Ve a **Settings** (⌘/Ctrl + ,)
- Busca **Models** o **Model Provider**
- Asegúrate de que **Composer 2.5** esté seleccionado como modelo por defecto
- Verifica que no haya ningún proveedor externo configurado (OpenAI, Anthropic, etc.)

### 2. Limpiar Configuración de Vision

Cursor puede estar intentando procesar contenido visual. Desactiva:

**En Settings → Models:**
- Desactiva cualquier feature de "Vision" o "Image Analysis"
- Configura **Text-only mode** si está disponible

### 3. Verificar Configuración de MCP

Los MCPs pueden estar intentando usar vision capabilities. Revisa `~/.cursor/mcp.json`:

```bash
cat ~/.cursor/mcp.json
```

Asegúrate de que los MCPs no tengan configuraciones relacionadas con visión.

### 4. Crear Workspace Verdaderamente Limpio

Para crear un workspace sin contaminación:

```bash
# Crea un directorio nuevo
mkdir -p ~/clean-workspace-$(date +%s)
cd ~/clean-workspace-$(date +%s)

# Inicializa git para evitar contaminación
git init
echo "# Clean workspace" > README.md
git add README.md
git commit -m "Initial commit"
```

Luego abre este nuevo workspace en Cursor Desktop.

### 5. Verificar Variables de Entorno

Elimina cualquier variable de entorno relacionada con modelos o APIs:

```bash
# Verificar
env | grep -i "api\|model\|openai\|anthropic\|gemini\|zhipu"

# Si hay alguna, elimínala temporalmente
```

### 6. Configuración Manual de Composer 2.5

Si el problema persiste, fuerza la configuración del modelo nativo:

Crea un archivo `.cursor/config.json` en tu workspace:

```json
{
  "model": {
    "default": "composer-2.5",
    "provider": "cursor-native"
  },
  "features": {
    "vision": false,
    "imageProcessing": false
  }
}
```

### 7. Verificar Plugins y Extensions

Algunos plugins pueden estar forzando el uso de API keys:

```bash
# Listar extensions
ls ~/.cursor/extensions/
```

Si hay extensiones sospechosas, temporalmente muévelas:

```bash
mkdir -p ~/extensions-backup
mv ~/.cursor/extensions/* ~/extensions-backup/
```

### 8. Reinstalar Cursor Desktop (último recurso)

Si nada funciona:
- Cierra completamente Cursor
- Limpia caché: `rm -rf ~/.cursor/cache/`
- Reinicia Cursor Desktop

## Diagnóstico Adicional

Para identificar qué está causando el error:

1. Abre **Developer Tools** en Cursor Desktop (Help → Toggle Developer Tools)
2. Busca errores en la consola relacionados con "API key" o "model"
3. Busca cualquier mención de vision o image processing

## Patrones Conocidos

El problema ocurre cuando:
- Cursor detecta screenshots o contenido visual
- MCPs están configurados para procesar imágenes
- Hay configuraciones residuales de otros modelos
- El workspace contiene archivos con imágenes incrustadas

## Solución Rápida

```bash
# Crear workspace completamente nuevo
cd ~
mkdir cursor-test-$(date +%s)
cd cursor-test-$(date +%s)

# Crear archivo README solo texto
cat > README.md << 'EOF'
# Test Workspace

This is a clean workspace for testing Composer 2.5 without vision capabilities.
EOF

# Abrir en Cursor Desktop
code-gateway .  # O abre desde el menú de Cursor Desktop
```

Luego verifica que puedes usar Composer 2.5 sin errores.