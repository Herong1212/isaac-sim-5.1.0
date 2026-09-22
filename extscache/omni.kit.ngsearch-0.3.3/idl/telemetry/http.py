from abc import abstractmethod
from contextlib import nullcontext
from typing import ContextManager



class BaseHTTPServerTelemetry:
    @abstractmethod
    def get_context(self, headers: dict) -> ContextManager:
        ...


class BaseHTTPClientTelemetry:
    @abstractmethod
    def inject_headers(self, headers: dict) -> dict:
        ...


class NullHTTPServerTelemetry(BaseHTTPServerTelemetry):
    def get_context(self, headers: dict) -> ContextManager:
        return nullcontext()


class NullHTTPClientTelemetry(BaseHTTPClientTelemetry):
    def inject_headers(self, headers: dict) -> dict:
        return headers
