# Public API for module omni.kit.telemetry:

## Classes

- class ITelemetry(_ITelemetry, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - def send_custom_event(self, eventType: str, duration: float = 0.0, data1: str = None, data2: str = None, value1: float = 0.0, value2: float = 0.0)
  - def send_generic_event(self, event_type: str, duration: float, data1: str, data2: str, value1: float, value2: float)

- class ITelemetry2(_ITelemetry2, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - def send_custom_event(self, eventType: str, duration: float = 0.0, data1: str = None, data2: str = None, value1: float = 0.0, value2: float = 0.0)
  - [property] def cloud_session(self) -> bool
  - [property] def cloud_session_id(self) -> str
  - [property] def customer_id(self) -> str
  - [property] def run_environment(self) -> typing.Any

- class RunEnvironment
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - CLOUD: omni.kit.telemetry._telemetry.RunEnvironment
  - ENTERPRISE: omni.kit.telemetry._telemetry.RunEnvironment
  - INDIVIDUAL: omni.kit.telemetry._telemetry.RunEnvironment
  - UNDETERMINED: omni.kit.telemetry._telemetry.RunEnvironment

## Functions

- def should_enable_sentry(app, settings) -> bool
- def start_sentry(app, settings) -> bool
- def remove_sentry_pii_data(event, hint, app_root_path: str | None = None) -> dict
