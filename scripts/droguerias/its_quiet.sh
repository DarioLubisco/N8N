#!/usr/bin/env bash
# Ejecuta its.py sin ruido en corridas idempotentes (SALTADO).
# - SALTADO / sin novedad: exit 0, sin salida
# - Éxito con datos: imprime solo líneas OK ROWS: / OK
# - Error: stderr con detalle, exit != 0

set -u
export LANG=C.UTF-8

run_its() {
  local log
  log=$(mktemp)
  if python3 /opt/scripts/droguerias/its.py >"$log" 2>&1; then
    if grep -q 'SALTADO' "$log"; then
      rm -f "$log"
      return 0
    fi
    grep -E 'OK ROWS:|^OK ' "$log" || true
    rm -f "$log"
    return 0
  fi
  cat "$log" >&2
  rm -f "$log"
  return 1
}

for cycle in 1 2 3; do
  for attempt in 1 2 3; do
    if run_its; then
      exit 0
    fi
    if [ "$attempt" -lt 3 ]; then
      sleep 10
    fi
  done
  if [ "$cycle" -lt 3 ]; then
    sleep 300
  fi
done
exit 1
