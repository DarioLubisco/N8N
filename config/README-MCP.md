# MCP — n8n

## n8n-mcp (recomendado)

Copiar a `~/.cursor/mcp.json` o fusionar con tu configuración existente:

```bash
cp config/mcp.json ~/.cursor/mcp.json
```

Definir la API key como **secreto de entorno** (no en el JSON):

```bash
export N8N_API_URL=https://n8n.farmaciaamericana.es
export N8N_API_KEY=<clave desde n8n > Settings > API>
```

En **Cursor Cloud Agents**, añadir `N8N_API_KEY` en los secrets del environment.

## Despliegue de workflows sin MCP

Si el MCP no está conectado en el agente, usar el script compatible con la misma API v1:

```bash
export N8N_API_URL=https://n8n.farmaciaamericana.es
export N8N_API_KEY=<tu-clave>
python3 fix_its_workflow.py
```
