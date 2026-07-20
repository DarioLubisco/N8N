#!/usr/bin/env python3
"""Parchea el repo Clasificacion Medicamentos para usar n8n_error_reporter.

Busca alertas directas a Telegram del scraper y las reemplaza por el cliente
alineado al protocolo n8n.

Uso:
  python3 patch_scraper_telegram.py "/ruta/a/Clasificacion Medicamentos"
  python3 patch_scraper_telegram.py "/ruta/a/Clasificacion Medicamentos" --dry-run
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
MODULE_SOURCE = REPO_ROOT / "n8n_error_reporter.py"
MODULE_DEST_NAME = "n8n_error_reporter.py"

IMPORT_LINE = (
    "from n8n_error_reporter import report_valueserp_access_failure, "
    "report_external_error, report_scraper_critical\n"
)

REPLACEMENT_CALL = (
    "report_valueserp_access_failure("
    "trigger_id=trigger_id, ean=ean, http_status=http_status, "
    "organic_count=organic_count, api_message=api_message, "
    "request_success=request_success, query=query, access_error=access_error)"
)

# Patrón típico del mensaje legacy observado en producción.
LEGACY_FSTRING = re.compile(
    r"""f?['\"]⚠️\s*SCRAPER\s*\[T\{?trigger_id\}?[^\n]*\n"
    r"?ValueSERP no devolvió URLs para \{?ean\}?[^'\"]*['\"]""",
    re.IGNORECASE | re.VERBOSE,
)

LEGACY_PLAIN = re.compile(
    r"['\"]⚠️ SCRAPER \[T\d+\][^\n]*\nValueSERP no devolvió URLs para [^'\"]+['\"]",
    re.IGNORECASE,
)

TELEGRAM_SEND_PATTERNS = [
    re.compile(r"requests\.post\([^\)]*api\.telegram\.org[^\)]*sendMessage[^\)]*\)", re.DOTALL),
    re.compile(r"send_telegram(?:_alert|_message)?\([^\)]*SCRAPER[^\)]*\)", re.DOTALL | re.IGNORECASE),
]


def copy_module(target_repo: Path) -> Path:
    dest = target_repo / MODULE_DEST_NAME
    shutil.copy2(MODULE_SOURCE, dest)
    return dest


def ensure_import(content: str) -> str:
    if "from n8n_error_reporter import" in content:
        return content
    lines = content.splitlines(keepends=True)
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1
    lines.insert(insert_at, IMPORT_LINE)
    return "".join(lines)


def patch_file(path: Path, dry_run: bool) -> list[str]:
    original = path.read_text(encoding="utf-8")
    updated = original
    changes: list[str] = []

    if "ValueSERP no devolvió URLs" in updated or "SCRAPER [T" in updated:
        if LEGACY_FSTRING.search(updated):
            updated = LEGACY_FSTRING.sub(
                REPLACEMENT_CALL,
                updated,
            )
            changes.append("reemplazó f-string legacy SCRAPER/ValueSERP")

        if LEGACY_PLAIN.search(updated):
            updated = LEGACY_PLAIN.sub(
                REPLACEMENT_CALL,
                updated,
            )
            changes.append("reemplazó string literal legacy SCRAPER/ValueSERP")

        for pattern in TELEGRAM_SEND_PATTERNS:
            if pattern.search(updated) and "SCRAPER" in updated:
                updated = pattern.sub(
                    REPLACEMENT_CALL,
                    updated,
                )
                changes.append("reemplazó envío directo a Telegram del scraper")

        updated = ensure_import(updated)

    if updated != original:
        if not dry_run:
            path.write_text(updated, encoding="utf-8")
        changes.insert(0, f"actualizado {path}")
    return changes


def scan_repo(repo: Path, dry_run: bool) -> int:
    if not repo.exists():
        raise FileNotFoundError(f"No existe el repo: {repo}")

    module_dest = copy_module(repo) if not dry_run else repo / MODULE_DEST_NAME
    print(f"{'[dry-run] ' if dry_run else ''}Módulo destino: {module_dest}")

    total_changes = 0
    for path in repo.rglob("*.py"):
        if path.name == MODULE_DEST_NAME:
            continue
        file_changes = patch_file(path, dry_run)
        if file_changes:
            total_changes += 1
            print(" -", "; ".join(file_changes))

    if total_changes == 0:
        print("No se encontraron patrones legacy. Revisar manualmente el archivo que emite:")
        print("  ⚠️ SCRAPER [T1] <ean> / ValueSERP no devolvió URLs ...")
        print("y reemplazar por report_valueserp_access_failure(...)")
    return total_changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path", nargs="?", default="/home/synapse/source/repos/Clasificacion Medicamentos")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        changed = scan_repo(Path(args.repo_path), args.dry_run)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(f"Archivos modificados: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
