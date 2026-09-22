import logging
from typing import ContextManager

from idl.telemetry.http import BaseHTTPClientTelemetry, BaseHTTPServerTelemetry

logger = logging.getLogger('idl.telemetry.opentelemetry')


class OpenTelemetryHTTPClientTelemetry(BaseHTTPClientTelemetry):
    def __init__(self):
        assert check_opentelemetry_package(), (
            "opentelemetry package must be installed to use OpenTelemetryHTTPClientTelemetry class."
        )

    def inject_headers(self, headers: dict) -> dict:
        from opentelemetry import propagate
        propagate.get_global_textmap().inject(headers)
        return headers


class OpenTelemetryHTTPServerTelemetry(BaseHTTPServerTelemetry):
    def __init__(self):
        assert check_opentelemetry_package(), (
            "opentelemetry package must be installed to use OpenTelemetryHTTPServerTelemetry class."
        )

        from opentelemetry import trace
        self.tracer = trace.get_tracer(__name__)

    def get_context(self, headers: dict) -> ContextManager:
        from opentelemetry import propagate
        opentelemetry_context = propagate.get_global_textmap().extract(headers)
        opentelemetry_span = self.tracer.start_as_current_span("http_request", context=opentelemetry_context)
        return opentelemetry_span


def check_opentelemetry_package() -> bool:
    try:
        from opentelemetry import trace
        return True
    except ImportError:
        return False
