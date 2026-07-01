#!/bin/bash
set -e

SYNC_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Importando configuración Cursor + Antigravity ==="

mkdir -p ~/.cursor ~/.gemini/config/skills

cp "$SYNC_DIR/mcp-config/mcp.json" ~/.cursor/mcp.json
echo "✅ MCPs copiados (incluye GitKraken)"

if [[ -f "$SYNC_DIR/mcp-config/mcp-blocklist.json" ]]; then
  cp "$SYNC_DIR/mcp-config/mcp-blocklist.json" ~/.cursor/mcp-blocklist.json
fi

if [[ -f "$SYNC_DIR/config/cli-config.json" ]]; then
  cp "$SYNC_DIR/config/cli-config.json" ~/.cursor/cli-config.json
fi

cp -r "$SYNC_DIR/antigravity-skills/"* ~/.gemini/config/skills/
echo "✅ Skills de Antigravity copiados"

echo ""
echo "Listo. Reinicia Cursor y Antigravity."
