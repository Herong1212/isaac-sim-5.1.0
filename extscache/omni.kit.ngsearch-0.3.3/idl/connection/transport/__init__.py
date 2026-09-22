import sys
import logging
import os
from abc import ABC, abstractmethod
from asyncio import Event
from typing import AsyncIterator, Generic, Type, TypeVar, Callable, Dict, Optional, Iterable, Iterator

from idl.types import Record


RequestType = TypeVar("Request")
ResponseType = TypeVar("Response", bound=dict)
InterfaceName = str
MethodName = str
Meta = Dict[str, str]


class TransportError(Exception):
    """Raised when something went wrong with the transport."""
    def __init__(self, text: str, code: int = -1):
        self.text = text
        self.code = code


class TransportSettings(Record):
    name: str
    params: str
    meta: Optional[Dict[str, str]]


class Client:
    @classmethod
    @abstractmethod
    def name(cls) -> str: ...

    @abstractmethod
    def params(self) -> dict:
        ...

    @classmethod
    @abstractmethod
    def get_settings(cls, params: dict, meta: dict) -> TransportSettings: ...

    @classmethod
    def create(cls, settings: TransportSettings, kwargs: dict = None) -> 'Client':
        if kwargs is None:
            kwargs = {}

        for client_type, meta, registered_kwargs in registry:
            if not registered_kwargs:
                registered_kwargs = {}

            registered_kwargs = registered_kwargs.copy()
            registered_kwargs.update(kwargs)

            if client_type.name() == settings.name and meta == settings.meta:
                return client_type.create(settings, registered_kwargs)
        raise ValueError(f"Client transport {settings.name!r} is not registered.")

    @classmethod
    @abstractmethod
    def get_meta_choices(cls) -> Iterable[Meta]:
        ...

    @staticmethod
    def get_all() -> Iterator[Type['Client']]:
        return (client_type for client_type, meta, kwargs in registry)

    @staticmethod
    def get_supported() -> Iterator['SupportedTransport']:
        for client_type, meta, kwargs in registry:
            yield SupportedTransport(
                name=client_type.name(),
                meta=meta
            )

    @staticmethod
    def get_by_name(name: str):
        for client_type in registered_classes:
            if client_type.name() == name:
                return client_type
        raise ValueError(f"Client transport {name!r} is not registered.")

    @staticmethod
    def register(cls: Type['Client'], **kwargs):
        name = cls.name()
        if name and cls not in registered_classes:
            for meta in cls.get_meta_choices():
                registry.append((cls, meta, kwargs))
            registered_classes.add(cls)

    @staticmethod
    def unregister(cls: Type['Client']):
        if cls not in registered_classes:
            return

        registered_classes.remove(cls)

        global registry
        new_registry = []
        for client_type, meta, kwargs in registry:
            if client_type is not cls:
                new_registry.append((client_type, meta, kwargs))
        registry = new_registry

    async def __aenter__(self) -> 'Client':
        await self.prepare()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def prepare(self): pass

    async def close(self): pass

    @property
    @abstractmethod
    def closed(self) -> Event: ...

    @abstractmethod
    async def call(self, interface: InterfaceName, method: MethodName, request: dict, request_type: Type[RequestType], return_type: Type[ResponseType]) -> ResponseType: ...
    
    @abstractmethod
    async def call_many(self, interface: InterfaceName, method: MethodName, request: dict, request_type: Type[RequestType], return_type: Type[ResponseType]) -> AsyncIterator[ResponseType]: ...


class Request:
    """
    Represents info for a single server request.
    Can be used via `get` static method in service handlers.
    Implemented using contextvars package (only supported in Python 3.7+):
    https://docs.python.org/3/library/contextvars.html

    A transport can override this class and add low-level information like an opened socket or process name.
    It's highly recommended to avoid using this API and implement your service independently from the current transport.
    You should use this only if there is no other way around and you need to read the transport details in your
    request handler.
    """
    interface: InterfaceName
    method: MethodName
    params: dict

    @staticmethod
    def get() -> Optional["Request"]:
        """
        Gets the request object for the current asyncio task.
        """
        if sys.version_info[:2] < (3, 7):
            raise NotImplementedError()
        return _request.get()

    @staticmethod
    def set(request: "Request"):
        """
        Sets the request object for the current asyncio task.
        Will be accessible in any child coroutine awaited in this task tree.

        This is no-op in Python below 3.7.
        """
        if sys.version_info[:2] >= (3, 7):
            _request.set(request)

    def __init__(self, interface: str, method: str, params: dict):
        self.interface = interface
        self.method = method
        self.params = params


if sys.version_info[:2] >= (3, 7):
    from contextvars import ContextVar
    _request = ContextVar("request")


In = TypeVar("In", bound=dict)
Out = TypeVar("Out", bound=dict)


class ServerCall(Generic[In, Out]):
    def __init__(self,
                 args_type: Type[In],
                 return_type: Type[Out],
                 handler: Callable[..., Out],
                 *,
                 state: dict = None,
                 returns_many: bool = False):
        self.args_type = args_type
        self.return_type = return_type
        self.handler = handler
        self.state = state or {}
        self.returns_many = returns_many

    def __call__(self, arg: In) -> Out:
        return self.handler(**{key: value for key, value in arg.items() if key not in self.state})


class DispatcherError(Exception):
    pass


class Dispatcher:
    def __init__(self):
        self.calls = {}

    def register_call(self, interface: InterfaceName, method: MethodName, call: ServerCall):
        self.calls[(interface, method)] = call

    def get_call(self, interface: InterfaceName, method: MethodName, params: dict) -> ServerCall:
        if (interface, method) in self.calls:
            return self.calls[(interface, method)]
        raise DispatcherError(f"Call for {interface}.{method} was not found.")

    def clear(self):
        self.calls = {}


class Server(ABC):
    @classmethod
    @abstractmethod
    def name(cls) -> str: ...

    @abstractmethod
    def params(self) -> dict: ...

    @abstractmethod
    def meta(self) -> dict: ...

    @classmethod
    @abstractmethod
    def get_settings(cls, params: dict, meta: dict) -> TransportSettings: ...

    @abstractmethod
    async def start(self, dispatcher: Dispatcher): ...

    @abstractmethod
    async def stop(self): ...


class SupportedTransport(Record):
    name: str
    meta: Optional[Dict[str, str]]


def init_debug_logger(logger):
    if hasattr(logger, 'idl_debug_logging_initialized'):
        return
    omni_conn_log_env = os.getenv("OMNI_CONN_LOG")
    if omni_conn_log_env:
        logger.idl_debug_logging_initialized = True
        if omni_conn_log_env == 'stdout':
            handler = logging.StreamHandler(sys.stdout)
        elif omni_conn_log_env == 'stderr':
            handler = logging.StreamHandler(sys.stderr)
        else:
            handler = logging.FileHandler(omni_conn_log_env)
        logger.addHandler(handler)
        logger.propagate = False
        logger.setLevel(logging.DEBUG)


def make_log_id(obj):
    return hex(id(obj))


registry = []
registered_classes = set()
