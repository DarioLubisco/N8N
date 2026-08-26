"""Tests para distinguir fallo de acceso ValueSERP vs. EAN sin resultados."""

from __future__ import annotations

import unittest

from n8n_error_reporter import is_valueserp_access_failure, report_valueserp_access_failure


class TestValueSerpAccessFailure(unittest.TestCase):
    def test_sin_resultados_no_es_fallo(self) -> None:
        self.assertFalse(
            is_valueserp_access_failure(
                http_status=200,
                organic_count=0,
                request_success=True,
            )
        )

    def test_resultados_filtrados_no_es_fallo(self) -> None:
        self.assertFalse(
            is_valueserp_access_failure(
                http_status=200,
                organic_count=3,
                request_success=True,
            )
        )

    def test_error_http_es_fallo(self) -> None:
        self.assertTrue(is_valueserp_access_failure(http_status=503))

    def test_error_red_es_fallo(self) -> None:
        self.assertTrue(is_valueserp_access_failure(access_error="timeout"))

    def test_report_no_alert_on_empty_organic(self) -> None:
        self.assertFalse(
            report_valueserp_access_failure(
                trigger_id=1,
                ean="7591948156018",
                http_status=200,
                organic_count=1,
                request_success=True,
            )
        )


if __name__ == "__main__":
    unittest.main()
