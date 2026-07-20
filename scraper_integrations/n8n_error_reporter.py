"""Cliente de reporte de errores alineado con el protocolo n8n de Synapse.

Uso desde el scraper MDM (Clasificacion Medicamentos):

    from n8n_error_reporter import report_valueserp_no_urls

    report_valueserp_no_urls(
        trigger_id=1,
        ean="1254896321544",
        http_status=200,
        organic_count=0,
        api_message="success",
    )
"""

from __future__ import annotations

import json
import logging
import os
import socket
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_WEBHOOK_URL = "https://n8n.farmaciaamericana.es/webhook/scraper-error-report"
DEFAULT_ORIGIN_IP = os.getenv("DEBIAN_HOST_IP", "10.147.18.4")
DEFAULT_WORKFLOW_ID = "AAnxxGYtgg5sD0o8"
DEFAULT_WORKFLOW_NAME = "[PROD] Orquestador Clasificador (Ventanas)"


def _post_alert(payload: dict[str, Any]) -> bool:
    webhook_url = os.getenv("N8N_SCRAPER_ERROR_WEBHOOK_URL", DEFAULT_WEBHOOK_URL)
    token = os.getenv("N8N_SCRAPER_ERROR_TOKEN", "")

    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Synapse-Webhook-Token"] = token

    request = urllib.request.Request(webhook_url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode("utf-8")
            if response.status >= 400:
                logger.error("n8n webhook respondió %s: %s", response.status, body)
                return False
            logger.info("Alerta enviada a n8n: %s", body)
            return True
    except urllib.error.HTTPError as exc:
        logger.error("n8n webhook HTTP %s: %s", exc.code, exc.read().decode("utf-8", errors="replace"))
        return False
    except (urllib.error.URLError, socket.timeout) as exc:
        logger.error("No se pudo contactar el webhook n8n: %s", exc)
        return False


def report_external_error(
    *,
    severity: str = "warning",
    service_name: str,
    diagnosis: str,
    probable_causes: str,
    native_log: str,
    destination_entity: str,
    title: str | None = None,
    origin_entity: str = "Servidor Debian Webservices",
    origin_ip: str | None = None,
    trigger_id: int | None = None,
    workflow_id: str = DEFAULT_WORKFLOW_ID,
    workflow_name: str = DEFAULT_WORKFLOW_NAME,
    context: dict[str, Any] | None = None,
) -> bool:
    """Envía una alerta estructurada al flujo [PROD] External Error Reporter (Scraper)."""
    if trigger_id is not None and "[T" not in service_name:
        service_name = f"{service_name} [T{trigger_id}]"

    payload = {
        "severity": severity,
        "title": title,
        "service_name": service_name,
        "origin_entity": origin_entity,
        "origin_ip": origin_ip or DEFAULT_ORIGIN_IP,
        "destination_entity": destination_entity,
        "diagnosis": diagnosis,
        "probable_causes": probable_causes,
        "native_log": native_log,
        "workflow_id": workflow_id,
        "workflow_name": workflow_name,
        "context": context or {},
    }
    return _post_alert(payload)


def report_valueserp_no_urls(
    *,
    trigger_id: int,
    ean: str,
    http_status: int | None = None,
    organic_count: int | None = None,
    api_message: str | None = None,
    query: str | None = None,
) -> bool:
    """Reemplazo protocolizado del antiguo mensaje directo a Telegram."""
    status_part = f"http_status={http_status}" if http_status is not None else "http_status=desconocido"
    organic_part = f"organic_results={organic_count}" if organic_count is not None else "organic_results=desconocido"
    api_part = f"api_message={api_message}" if api_message else "api_message=sin_mensaje"
    query_part = f"query={query or ean}"

    if http_status in (402,):
        causes = "Créditos de ValueSERP agotados o problema de facturación (HTTP 402)."
    elif http_status in (429,):
        causes = "Rate limit de ValueSERP alcanzado (HTTP 429). Reintentar con backoff."
    elif http_status in (401, 403):
        causes = "API key inválida o no autorizada en ValueSERP."
    elif http_status and http_status >= 500:
        causes = "ValueSERP respondió con error de servidor. Posible incidente del proveedor."
    elif organic_count == 0:
        causes = (
            "La API respondió pero sin URLs orgánicas para ese EAN; puede ser un producto sin "
            "presencia web indexada o una consulta demasiado restrictiva."
        )
    else:
        causes = (
            "Respuesta incompleta de ValueSERP, timeout de red, o fallo al parsear resultados."
        )

    return report_external_error(
        severity="warning",
        service_name="MDM_Farmaceutico_Scraper",
        trigger_id=trigger_id,
        title="ValueSERP sin URLs para producto",
        destination_entity="ValueSERP API (api.valueserp.com)",
        diagnosis=f"ValueSERP no devolvió URLs utilizables para el producto {ean}.",
        probable_causes=causes,
        native_log=", ".join([status_part, organic_part, api_part, query_part]),
        context={
            "ean": ean,
            "trigger_id": trigger_id,
            "http_status": http_status,
            "organic_count": organic_count,
            "api_message": api_message,
            "query": query or ean,
        },
    )


def report_scraper_critical(
    *,
    trigger_id: int,
    diagnosis: str,
    probable_causes: str,
    native_log: str,
    destination_entity: str = "MSSQL Server (EnterpriseAdmin_AMC)",
    context: dict[str, Any] | None = None,
) -> bool:
    return report_external_error(
        severity="critical",
        service_name="MDM_Farmaceutico_Scraper",
        trigger_id=trigger_id,
        destination_entity=destination_entity,
        diagnosis=diagnosis,
        probable_causes=probable_causes,
        native_log=native_log,
        context=context,
    )
