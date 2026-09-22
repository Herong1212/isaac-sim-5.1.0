from idl.telemetry.http import NullHTTPServerTelemetry, NullHTTPClientTelemetry
from idl.telemetry.opentelemetry import check_opentelemetry_package

if check_opentelemetry_package():
    from idl.telemetry.opentelemetry import OpenTelemetryHTTPClientTelemetry, OpenTelemetryHTTPServerTelemetry

    DefaultHTTPServerTelemetry = OpenTelemetryHTTPServerTelemetry
    DefaultHTTPClientTelemetry = OpenTelemetryHTTPClientTelemetry
else:
    DefaultHTTPServerTelemetry = NullHTTPServerTelemetry
    DefaultHTTPClientTelemetry = NullHTTPClientTelemetry
