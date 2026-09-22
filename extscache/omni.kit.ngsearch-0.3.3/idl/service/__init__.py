import asyncio
import logging
import typing
from typing import NamedTuple, List, Optional, Callable, Set, Dict

from idl.connection.transport import Dispatcher, Server, ServerCall

DefaultLogFormatter = logging.Formatter("%(asctime)-15s | %(message)s")
logger = logging.getLogger("idl.service")
logger.setLevel(logging.INFO)


class ServiceStub:
    prepared: bool = False
    __interface_name__: str
    __interface_methods__: List['ServiceStubMethodMeta']
    __interface_fields__: List['ServiceStubFieldMeta']
    __interface_origin__: str
    __interface_capabilities__: Optional[Dict[str, int]]
    __interface_disabled_methods__: List['ServiceStubMethodMeta']
    __interface_disabled_capabilities__: Dict[str, int]

    async def prepare(self):
        """
        This method is invoked once the stub is used in your service.
        You can override this method and put your initialization logic here.
        """
        self.prepared = True

    async def cleanup(self):
        """
        This method will be invoked on the service shutdown.
        You can override this method and put the cleanup logic here.
        """
        self.prepared = False

    def __instancecheck__(self, instance):
        return (
                hasattr(instance, "__interface_name__") and
                hasattr(instance, "__interface_fields__") and
                hasattr(instance, "__interface_methods__") and
                hasattr(instance, "__interface_origin__")
        )

    def __disablemethod__(self, method: str):
        """
        Removes the method with the specified name from declared methods available as the public API for transport and
        from the interface capabilities. The disabled method can be re-enabled by calling __enablemethod__ function.
        The disabled method is still available for explicit use in the service.
        """
        self.__init_disabled_attrs()

        for method_meta in self.__interface_methods__:
            func_name, *_ = method_meta
            if func_name == method:
                self.__interface_methods__.remove(method_meta)
                self.__interface_disabled_methods__.append(method_meta)
                break

        capabilities: Dict[str, int] = getattr(self, "__interface_capabilities__", None)
        if capabilities:
            version = capabilities.pop(method, None)
            if version:
                self.__interface_disabled_capabilities__[method] = version

    def __enablemethod__(self, method: str):
        """
        Re-enables the specified method excluded previously with __disablemethod__ call.
        This function adds the method with the specified name back to the public API available for transport
        and back to the interface capabilities.
        """
        self.__init_disabled_attrs()

        for method_meta in self.__interface_disabled_methods__:
            func_name, *_ = method_meta
            if func_name == method:
                self.__interface_disabled_methods__.remove(method_meta)
                self.__interface_methods__.append(method_meta)
                break

        if hasattr(self, "__interface_capabilities__"):
            version = self.__interface_disabled_capabilities__.pop(method, None)
            if version:
                self.__interface_capabilities__[method] = version

    def __init_disabled_attrs(self):
        if self.__interface_methods__ is self.__class__.__interface_methods__:
            # Copy is required otherwise this would disable the specified method for all interface instances
            self.__interface_methods__ = self.__interface_methods__.copy()

        supports_capabilities = hasattr(self, "__interface_capabilities__")
        if supports_capabilities and self.__interface_capabilities__ is self.__class__.__interface_capabilities__:
            # Copy is required otherwise this would remove the specified method from all interface instances
            self.__interface_capabilities__ = self.__interface_capabilities__.copy()

        if not hasattr(self, "__interface_disabled_methods__"):
            self.__interface_disabled_methods__ = []

        if not hasattr(self, "__interface_disabled_capabilities__"):
            self.__interface_disabled_capabilities__ = {}


class ServiceStubMethodMeta(NamedTuple):
    func_name: str
    handler: Callable
    args_type: type
    return_type: type
    returns_many: bool


class ServiceStubFieldMeta(NamedTuple):
    name: str
    type: type


class Service:
    dispatcher: Dispatcher
    transport: Server

    _running: Optional[asyncio.Future]

    def __init__(self):
        self.dispatcher = Dispatcher()
        self._running = None
        self._services = set()

    async def run(self, interfaces: List[ServiceStub], *, wait: bool = True):
        if self._running is not None:
            raise RuntimeError("The service is already running.")

        self._running = asyncio.Future()
        self._services = await self._init_services(interfaces)

        logger.info(f"Listen.")
        await self.transport.start(self.dispatcher)
        if wait:
            await self.wait()

    async def wait(self):
        try:
            await self._running
        finally:
            await self._finalize()

    async def stop(self):
        logger.info(f"Stop.")
        if self._running is not None:
            self._running.set_result(None)
        await self._finalize()

    def get_interface(self, name: str):
        for instance in self._services:
            if instance.__interface_name__ == name:
                return instance
        raise KeyError(f"Interface {name!r} is not registered.")

    async def _init_services(self, interfaces: List[ServiceStub]) -> Set[ServiceStub]:
        services = set()
        for instance in interfaces:
            if instance.__class__.__name__ == instance.__interface_name__:
                logger.info(f"Registering interface {instance.__interface_name__!r}:")
            else:
                logger.info(f"Registering class {instance.__class__.__name__!r} that implements "
                            f"interface {instance.__interface_name__!r}:")

            # State represents fields of literal type declared in the interface.
            # The other fields are passed directly to the service method.
            state = {
                field_name: field_type
                for field_name, field_type in instance.__interface_fields__
                if not isinstance(field_type, (type, typing.Callable))
            }
            if state:
                logger.info(f"  State: {state}")

            if not instance.prepared:
                await instance.prepare()

            for func_name, handler, args_type, return_type, returns_many in instance.__interface_methods__:
                logger.info(f"  Method: {handler.__name__!r}")
                self.dispatcher.register_call(
                    interface=instance.__interface_name__,
                    method=func_name,
                    call=ServerCall(
                        args_type=args_type,
                        return_type=return_type,
                        returns_many=returns_many,
                        handler=getattr(instance, handler.__name__),
                        state=state,
                    )
                )
            services.add(instance)
        return services

    async def _finalize(self):
        if self._running is None:
            return

        self._running = None
        await self.transport.stop()
        self.dispatcher.clear()

        for service in self._services:
            if service.prepared:
                await service.cleanup()
