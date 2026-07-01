#!/bin/bash

# Script de sincronización para Skills y MCPs entre computadoras
# Este script crea repositorios Git para sincronizar configuraciones de Cursor

echo "=== Configurando Sincronización de Cursor ==="
echo ""

# Crear directorio principal de sincronización
SYNC_DIR="$HOME/cursor-sync"
mkdir -p "$SYNC_DIR"
cd "$SYNC_DIR"
echo "✅ Directorio de sincronización creado: $SYNC_DIR"

# Crear repositorio para Skills
echo ""
echo "1. Configurando sincronización de Skills..."
SKILLS_DIR="$SYNC_DIR/skills"
mkdir -p "$SKILLS_DIR"

# Copiar skills personales si existen
if [[ -d ~/.cursor/skills ]]; then
    cp -r ~/.cursor/skills/* "$SKILLS_DIR/" 2>/dev/null || true
    echo "   ✅ Skills personales copiados"
else
    echo "   ℹ️  No se encontraron skills personales"
fi

# Crear README para Skills
cat > "$SKILLS_DIR/README.md" << 'EOF'
# Cursor Skills - Sincronización

Este directorio contiene todos los Skills personales de Cursor.

## Estructura
- Cada skill está en su propio directorio
- Cada directorio contiene un archivo SKILL.md obligatorio

## Uso
Este repositorio se sincroniza entre computadoras para mantener los mismos Skills.

## Agregar nuevo Skill
1. Crear directorio: `mkdir nombre-del-skill`
2. Crear archivo SKILL.md con instrucciones
3. Commit y push a este repositorio
EOF

cd "$SKILLS_DIR"
git init 2>/dev/null || true
git add . 2>/dev/null || true
git commit -m "Initial commit: Cursor skills synchronization" 2>/dev/null || true
cd "$SYNC_DIR"

echo "   ✅ Repositorio de Skills configurado"
echo "   📍 Ruta: $SKILLS_DIR"

# Crear repositorio para MCPs
echo ""
echo "2. Configurando sincronización de MCPs..."
MCP_DIR="$SYNC_DIR/mcp-config"
mkdir -p "$MCP_DIR"

# Copiar configuración de MCPs
if [[ -f ~/.cursor/mcp.json ]]; then
    cp ~/.cursor/mcp.json "$MCP_DIR/"
    echo "   ✅ Configuración de MCPs copiada"
else
    echo "   ℹ️  No se encontró configuración de MCPs"
fi

# Copiar blocklist de MCPs si existe
if [[ -f ~/.cursor/mcp-blocklist.json ]]; then
    cp ~/.cursor/mcp-blocklist.json "$MCP_DIR/"
    echo "   ✅ Blocklist de MCPs copiado"
fi

# Crear README para MCPs
cat > "$MCP_DIR/README.md" << 'EOF'
# Cursor MCPs - Sincronización

Este directorio contiene la configuración de MCPs de Cursor.

## Archivos
- `mcp.json`: Configuración principal de MCPs
- `mcp-blocklist.json`: Lista de bloqueo de MCPs problemáticos

## Estructura de mcp.json
```json
{
  "mcpServers": {
    "nombre-del-servidor": {
      "command": "comando",
      "args": ["argumentos"],
      "env": {
        "VARIABLE": "${env:NOMBRE_DE_VARIABLE}"
      }
    }
  }
}
```

## Variables de Entorno
Los MCPs pueden requerir variables de entorno. Debes configurarlas en cada computadora:
- TAVILY_API_KEY
- EXA_API_KEY
- FIRECRAWL_API_KEY
- N8N_API_URL
- N8N_API_KEY
- MSSQL_SERVER
- MSSQL_DATABASE
- MSSQL_USER
- MSSQL_PASSWORD
- POSTGRES_CONNECTION_STRING

## Aplicar Configuración
Para aplicar esta configuración:
```bash
cp mcp.json ~/.cursor/mcp.json
cp mcp-blocklist.json ~/.cursor/mcp-blocklist.json
```

## Sincronización
Este repositorio se sincroniza entre computadoras para mantener los mismos MCPs.
EOF

cd "$MCP_DIR"
git init 2>/dev/null || true
git add . 2>/dev/null || true
git commit -m "Initial commit: Cursor MCPs synchronization" 2>/dev/null || true
cd "$SYNC_DIR"

echo "   ✅ Repositorio de MCPs configurado"
echo "   📍 Ruta: $MCP_DIR"

# Crear repositorio para configuración general
echo ""
echo "3. Configurando sincronización de configuración general..."
CONFIG_DIR="$SYNC_DIR/config"
mkdir -p "$CONFIG_DIR"

# Copiar configuración CLI
if [[ -f ~/.cursor/cli-config.json ]]; then
    cp ~/.cursor/cli-config.json "$CONFIG_DIR/"
    echo "   ✅ Configuración CLI copiada"
fi

# Crear README para configuración
cat > "$CONFIG_DIR/README.md" << 'EOF'
# Cursor Configuration - Sincronización

Este directorio contiene la configuración general de Cursor.

## Archivos
- `cli-config.json`: Configuración CLI de Cursor

## Aplicar Configuración
Para aplicar esta configuración:
```bash
cp cli-config.json ~/.cursor/cli-config.json
```

## Importante
Después de actualizar la configuración, debes reiniciar Cursor Desktop para que los cambios tengan efecto.

## Sincronización
Este repositorio se sincroniza entre computadoras para mantener la misma configuración.
EOF

cd "$CONFIG_DIR"
git init 2>/dev/null || true
git add . 2>/dev/null || true
git commit -m "Initial commit: Cursor configuration synchronization" 2>/dev/null || true
cd "$SYNC_DIR"

echo "   ✅ Repositorio de configuración configurado"
echo "   📍 Ruta: $CONFIG_DIR"

# Crear script de aplicación
echo ""
echo "4. Creando scripts de sincronización..."

# Script para aplicar configuración desde sincronización
cat > "$SYNC_DIR/apply-sync.sh" << 'EOF'
#!/bin/bash

# Script para aplicar configuración desde el directorio de sincronización

SYNC_DIR="$(dirname "$0")"

echo "=== Aplicando Configuración de Cursor desde Sincronización ==="
echo ""

# Aplicar configuración CLI
if [[ -f "$SYNC_DIR/config/cli-config.json" ]]; then
    cp "$SYNC_DIR/config/cli-config.json" ~/.cursor/cli-config.json
    echo "✅ Configuración CLI aplicada"
else
    echo "⚠️  No se encontró configuración CLI"
fi

# Aplicar MCPs
if [[ -f "$SYNC_DIR/mcp-config/mcp.json" ]]; then
    cp "$SYNC_DIR/mcp-config/mcp.json" ~/.cursor/mcp.json
    echo "✅ Configuración de MCPs aplicada"
else
    echo "⚠️  No se encontró configuración de MCPs"
fi

# Aplicar blocklist de MCPs
if [[ -f "$SYNC_DIR/mcp-config/mcp-blocklist.json" ]]; then
    cp "$SYNC_DIR/mcp-config/mcp-blocklist.json" ~/.cursor/mcp-blocklist.json
    echo "✅ Blocklist de MCPs aplicado"
fi

# Aplicar Skills
if [[ -d "$SYNC_DIR/skills" ]]; then
    mkdir -p ~/.cursor/skills
    cp -r "$SYNC_DIR/skills/"* ~/.cursor/skills/ 2>/dev/null || true
    echo "✅ Skills aplicados"
else
    echo "⚠️  No se encontraron skills"
fi

echo ""
echo "=== Configuración aplicada ==="
echo ""
echo "⚠️  IMPORTANTE: Debes reiniciar Cursor Desktop para que los cambios tengan efecto."
echo ""
echo "Para reiniciar Cursor Desktop:"
echo "1. Cierra Cursor Desktop (Cmd/Ctrl + Q)"
echo "2. Verifica que no haya procesos: ps aux | grep cursor"
echo "3. Si hay procesos, elimínalos: pkill -9 cursor"
echo "4. Reinicia Cursor Desktop"
EOF

chmod +x "$SYNC_DIR/apply-sync.sh"
echo "   ✅ Script de aplicación creado"

# Script para actualizar sincronización desde configuración actual
cat > "$SYNC_DIR/update-sync.sh" << 'EOF'
#!/bin/bash

# Script para actualizar el directorio de sincronización desde la configuración actual

SYNC_DIR="$(dirname "$0")"

echo "=== Actualizando Directorio de Sincronización ==="
echo ""

# Actualizar configuración CLI
if [[ -f ~/.cursor/cli-config.json ]]; then
    mkdir -p "$SYNC_DIR/config"
    cp ~/.cursor/cli-config.json "$SYNC_DIR/config/cli-config.json"
    cd "$SYNC_DIR/config"
    git add cli-config.json 2>/dev/null || true
    git commit -m "Update: CLI configuration" 2>/dev/null || true
    cd "$SYNC_DIR"
    echo "✅ Configuración CLI actualizada en sincronización"
else
    echo "⚠️  No se encontró configuración CLI"
fi

# Actualizar MCPs
if [[ -f ~/.cursor/mcp.json ]]; then
    mkdir -p "$SYNC_DIR/mcp-config"
    cp ~/.cursor/mcp.json "$SYNC_DIR/mcp-config/"
    cd "$SYNC_DIR/mcp-config"
    git add mcp.json 2>/dev/null || true
    git commit -m "Update: MCP configuration" 2>/dev/null || true
    cd "$SYNC_DIR"
    echo "✅ Configuración de MCPs actualizada en sincronización"
else
    echo "⚠️  No se encontró configuración de MCPs"
fi

# Actualizar blocklist de MCPs
if [[ -f ~/.cursor/mcp-blocklist.json ]]; then
    mkdir -p "$SYNC_DIR/mcp-config"
    cp ~/.cursor/mcp-blocklist.json "$SYNC_DIR/mcp-config/"
    cd "$SYNC_DIR/mcp-config"
    git add mcp-blocklist.json 2>/dev/null || true
    git commit -m "Update: MCP blocklist" 2>/dev/null || true
    cd "$SYNC_DIR"
    echo "✅ Blocklist de MCPs actualizado en sincronización"
fi

# Actualizar Skills
if [[ -d ~/.cursor/skills ]]; then
    mkdir -p "$SYNC_DIR/skills"
    cp -r ~/.cursor/skills/* "$SYNC_DIR/skills/" 2>/dev/null || true
    cd "$SYNC_DIR/skills"
    git add . 2>/dev/null || true
    git commit -m "Update: Skills" 2>/dev/null || true
    cd "$SYNC_DIR"
    echo "✅ Skills actualizados en sincronización"
else
    echo "⚠️  No se encontraron skills"
fi

echo ""
echo "=== Sincronización actualizada ==="
echo ""
echo "Los cambios están listos para ser subidos a tu repositorio remoto."
echo ""
echo "Para subir a GitHub/GitLab:"
echo "cd $SYNC_DIR/config && git push origin main"
echo "cd $SYNC_DIR/mcp-config && git push origin main"
echo "cd $SYNC_DIR/skills && git push origin main"
EOF

chmod +x "$SYNC_DIR/update-sync.sh"
echo "   ✅ Script de actualización creado"

# Crear README principal
cat > "$SYNC_DIR/README.md" << 'EOF'
# Cursor Sync - Sincronización entre Computadoras

Este directorio contiene toda la configuración de Cursor que se sincroniza entre múltiples computadoras.

## Estructura

```
cursor-sync/
├── skills/           # Skills personales de Cursor
├── mcp-config/       # Configuración de MCPs
├── config/           # Configuración general
├── apply-sync.sh     # Aplicar configuración desde sincronización
├── update-sync.sh    # Actualizar sincronización desde configuración actual
└── README.md         # Este archivo
```

## Uso Inicial

### 1. En la primera computadora:

```bash
# Ir al directorio de sincronización
cd ~/cursor-sync

# Crear repositorios remotos (GitHub/GitLab)
cd skills
git remote add origin https://github.com/tu-usuario/cursor-skills.git
git branch -M main
git push -u origin main

cd ../mcp-config
git remote add origin https://github.com/tu-usuario/cursor-mcps.git
git branch -M main
git push -u origin main

cd ../config
git remote add origin https://github.com/tu-usuario/cursor-config.git
git branch -M main
git push -u origin main
```

### 2. En otras computadoras:

```bash
# Clonar repositorios
mkdir -p ~/cursor-sync
cd ~/cursor-sync

git clone https://github.com/tu-usuario/cursor-skills.git skills
git clone https://github.com/tu-usuario/cursor-mcps.git mcp-config
git clone https://github.com/tu-usuario/cursor-config.git config

# Aplicar configuración
./apply-sync.sh
```

## Uso Diario

### Aplicar cambios desde sincronización:

```bash
cd ~/cursor-sync
git pull --all
./apply-sync.sh
# Reiniciar Cursor Desktop
```

### Actualizar sincronización con cambios locales:

```bash
cd ~/cursor-sync
./update-sync.sh
git push --all
```

## Scripts

### `apply-sync.sh`
Aplica la configuración desde el directorio de sincronización a la configuración de Cursor local.

**Uso:**
```bash
cd ~/cursor-sync
./apply-sync.sh
```

**⚠️ Importante:** Debes reiniciar Cursor Desktop después de aplicar cambios.

### `update-sync.sh`
Actualiza el directorio de sincronización con la configuración actual de Cursor.

**Uso:**
```bash
cd ~/cursor-sync
./update-sync.sh
```

## Variables de Entorno

Algunos MCPs requieren variables de entorno. Debes configurarlas en cada computadora:

```bash
# Editar ~/.bashrc o ~/.zshrc
export TAVILY_API_KEY="tu-api-key"
export EXA_API_KEY="tu-api-key"
export FIRECRAWL_API_KEY="tu-api-key"
export N8N_API_URL="https://tu-n8n-instance.com"
export N8N_API_KEY="tu-api-key"
export MSSQL_SERVER="tu-servidor"
export MSSQL_DATABASE="tu-database"
export MSSQL_USER="tu-usuario"
export MSSQL_PASSWORD="tu-password"
export POSTGRES_CONNECTION_STRING="postgresql://usuario:password@localhost:5432/database"
```

## Solución de Problemas

### Cursor no reconoce los cambios después de aplicar sincronización

**Solución:** Reinicia Cursor Desktop completamente:
```bash
pkill -9 cursor
# Luego abre Cursor Desktop nuevamente
```

### MCPs no funcionan después de sincronizar

**Solución:** Verifica que las variables de entorno estén configuradas:
```bash
env | grep -i API
```

### Skills no aparecen después de sincronizar

**Solución:** Verifica la estructura de cada skill:
```bash
ls -la ~/.cursor/skills/*
# Cada directorio debe tener un archivo SKILL.md
```

## Automatización Opcional

Puedes crear un cron job para sincronizar automáticamente:

```bash
# Abrir crontab
crontab -e

# Agregar línea para sincronizar cada hora
0 * * * * cd ~/cursor-sync && git pull --all && ./apply-sync.sh
```

## Notas

- Este sistema usa Git para sincronización, por lo que necesitas repositorios remotos (GitHub, GitLab, etc.)
- Los cambios se sincronizan manualmente para evitar conflictos
- Asegúrate de configurar las variables de entorno en cada computadora
- Siempre prueba la configuración en una computadora antes de sincronizar
EOF

echo "   ✅ README principal creado"

# Resumen
echo ""
echo "=== Sincronización Configurada Exitosamente ==="
echo ""
echo "📍 Directorio de sincronización: $SYNC_DIR"
echo ""
echo "📁 Estructura creada:"
echo "   ├── skills/          - Skills personales"
echo "   ├── mcp-config/      - Configuración de MCPs"
echo "   ├── config/          - Configuración general"
echo "   ├── apply-sync.sh    - Aplicar sincronización"
echo "   ├── update-sync.sh   - Actualizar sincronización"
echo "   └── README.md        - Documentación completa"
echo ""
echo "📖 Documentación completa: $SYNC_DIR/README.md"
echo ""
echo "=== Próximos Pasos ==="
echo ""
echo "1. Revisa la documentación: cat $SYNC_DIR/README.md"
echo ""
echo "2. Para aplicar configuración desde sincronización:"
echo "   cd $SYNC_DIR && ./apply-sync.sh"
echo ""
echo "3. Para actualizar sincronización con cambios locales:"
echo "   cd $SYNC_DIR && ./update-sync.sh"
echo ""
echo "4. Importante: Reinicia Cursor Desktop después de aplicar cambios"
echo ""
echo "✅ Sincronización de Cursor configurada exitosamente"