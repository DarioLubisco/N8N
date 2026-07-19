# Parche recomendado para `its.py` (Debian)

## Problema

Si `its.py` escribe logs JSON estructurados en **stdout**, cualquier integración que lea la salida del script (n8n SSH, cron, etc.) puede interpretarlos como eventos a notificar.

Mensajes como `SALTADO: El archivo ... ya fue procesado exitosamente` son **informativos** (idempotencia), no errores.

## Convención estándar (igual que `generic_inventario.py` y `blv_email_fetch.py`)

| Canal | Contenido |
|-------|-----------|
| **stdout** | Solo resultado machine-readable: `OK ROWS:123`, `OK SKIP`, o `ERROR: ...` |
| **stderr** | Logs detallados (JSON o texto) para auditoría |

## Cambio mínimo en Python

```python
import json
import logging
import sys

class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "ts": self.formatTime(record),
            "level": record.levelname,
            "module": "its",
            "msg": record.getMessage(),
        })

logger = logging.getLogger("its")
logger.handlers.clear()
handler = logging.StreamHandler(sys.stderr)  # ← stderr, NO stdout
handler.setFormatter(JsonLogFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Al finalizar sin error (incluyendo SALTADO/idempotencia):
print("OK SKIP")   # o print(f"OK ROWS:{count}")
sys.exit(0)

# En fallo real:
print(f"ERROR: {exc}")
sys.exit(1)
```

## Despliegue en Debian

```bash
scp scripts/droguerias/its.py root@10.147.18.204:/opt/scripts/droguerias/its.py
ssh root@10.147.18.204 "chmod +x /opt/scripts/droguerias/its.py"
```
