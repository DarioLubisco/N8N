# ITS — Silencio en ejecuciones sin novedad

## Regla

Si no hay error ni trabajo nuevo, **no debe haber salida visible** (ni en n8n, ni en Telegram, ni en logs operativos).

| Resultado | stdout | stderr | exit |
|-----------|--------|--------|------|
| SALTADO (ya procesado) | *(vacío)* | *(vacío)* | 0 |
| OK con filas nuevas | `OK ROWS:N` | opcional | 0 |
| Error real | `ERROR: ...` | detalle | 1 |

## Implementado en n8n (inmediato)

El flujo `[PROD] [Inventario] - ETL Inventario ITS` captura la salida de `its.py` en un archivo temporal:

- Si contiene `SALTADO` → termina en silencio (exit 0, sin stdout).
- Si hay éxito con datos → solo imprime líneas `OK ROWS:` / `OK`.
- Si falla → stderr con el log completo → handler global de errores.

## Opcional en Debian (recomendado a medio plazo)

Desplegar el wrapper y apuntar el cron/n8n a él:

```bash
scp scripts/droguerias/its_quiet.sh root@10.147.18.204:/opt/scripts/droguerias/
ssh root@10.147.18.204 "chmod +x /opt/scripts/droguerias/its_quiet.sh"
```

O parchear `its.py` para que los logs JSON vayan a **stderr** y en SALTADO no imprima nada en stdout:

```python
# logger → sys.stderr
# al finalizar idempotente:
sys.exit(0)  # sin print
```
