import asyncio
import logging
import os
import ssl
import urllib.parse
from typing import Callable, Optional, Awaitable, List, Dict

from idl.connection.marshallers import Marshaller
from idl.connection.transport import Client, TransportSettings, TransportError
from idl.connection.transport.http import HttpClient
from idl.connection.transport.http_file import HttpFileClient
from idl.connection.transport.omni import OmniClientTransport
from idl.connection.transport.ws import WebSocketClient
from idl.data.serializers import Serializer
from idl.data.serializers.json import JSONSerializer
from idl.types import Record
from .client import (
    DiscoveryRegistration as DiscoveryRegistrationClient,
    DiscoverySearch as DiscoverySearchClient
)
from .data import (
    Manifest, HealthStatus, Meta, HealthCheck, DiscoverInterfaceQuery, ServiceInterface, SupportedTransport,
)

logger = logging.getLogger("omni.discovery")
sentinel = object()

Stop = bool

DISCOVERY_ENDPOINT = "/omni/discovery"


class DiscoveryManifest(Record):
    token: str
    interfaces: list
    transport: TransportSettings
    meta: Optional[Meta]


class DiscoveryRegistration:
    def __init__(self, uri: str, ssl_context: ssl.SSLContext = None, *, conn_timeout: float = 5.0):
        self.uri = uri
        self.ssl_context = ssl_context
        self.conn_timeout = conn_timeout

    async def register(self, manifest: DiscoveryManifest,
                       on_check: Callable[[HealthCheck], Awaitable[Optional[Stop]]] = None,
                       retry_timeout: float = 5.0):
        registered_manifest = Manifest(
            token=manifest.token,
            transport=manifest.transport,
            meta=manifest.meta,
            interfaces={
                interface.__interface_name__: ServiceInterface(
                    origin=interface.__interface_origin__,
                    name=interface.__interface_name__,
                    capabilities=getattr(interface, "__interface_capabilities__", None)
                )
                for interface in manifest.interfaces
            }
        )

        info = "\n".join([
            f" Discovery URI: {self.uri}",
            f" Transport settings: {registered_manifest.transport}",
            f" Meta: {registered_manifest.meta}"
        ])
        logger.info(f"Registering the service in the discovery with these parameters:\n{info}")

        running = True
        while running:
            try:
                registering = True

                ws = await connect(self.uri, self.ssl_context, timeout=self.conn_timeout)
                if ws is None:
                    raise ConnectionError(f"Failed to connect to the discovery service {self.uri}")

                async with DiscoveryRegistrationClient(ws) as discovery:
                    async for health_check in discovery.register(registered_manifest):
                        if on_check:
                            stop = await on_check(health_check)
                            if stop:
                                break

                        if health_check.status == HealthStatus.OK:
                            if registering:
                                if manifest.meta:
                                    logger.info(f"Registered in {self.uri} with {manifest.meta} meta.")
                                else:
                                    logger.info(f"Registered in {self.uri}.")
                                registering = False
                        else:
                            logger.error(
                                f"Can't register the service: {health_check.message or health_check.status}.\n"
                                f"Info:\n{info}"
                            )
                            if registering:
                                running = False
                            break
            except asyncio.CancelledError:
                return
            except Exception as exc:
                logger.exception(
                    f"An error has occurred while registering the service in the discovery.\n"
                    f"Info:\n{info}",
                    exc_info=exc
                )
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    break
                else:
                    if loop.is_closed():
                        break
                await asyncio.sleep(retry_timeout)


class DiscoverySearch:
    def __init__(self, uri: str, ssl_context: ssl.SSLContext = None):
        self._uri = uri
        self._ssl_context = ssl_context
        self._ws: Optional[WebSocketClient] = None
        self._closing: Optional[asyncio.Task] = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def find(
            self,
            interface,
            meta: Meta = None,
            supported_transport: Optional[List[SupportedTransport]] = sentinel,
            capabilities: Dict[str, int] = None,
            *,
            timeout: float = 5.0
    ):
        if supported_transport is sentinel:
            supported_transport = list(Client.get_supported())

        ws = await self._connect(timeout)
        discovery = DiscoverySearchClient(ws)
        origin = interface.__interface_origin__
        interface_name = interface.__interface_name__

        if capabilities is None:
            capabilities = getattr(interface, "__interface_capabilities__", None)

        try:
            response = await discovery.find(DiscoverInterfaceQuery(
                service_interface=ServiceInterface(
                    origin=origin,
                    name=interface_name,
                    capabilities=capabilities
                ),
                supported_transport=supported_transport,
                meta=meta
            ))
        except TransportError as exc:
            raise ConnectionError(f"Failed to communicate with the discovery service {self._uri}.") from exc

        if not response.found:
            raise ConnectionError(
                f"Interface {interface_name!r} from {origin!r} has not been found."
            )

        transport = Client.create(response.transport, kwargs={
            "ssl_context": self._ssl_context
        })
        try:
            await transport.prepare()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            msg = "\n".join([
                f"An error has occurred when tried to establish a connection to {interface.__name__}.",
                f"Info: ",
                f"  Discovery URI: {self._uri}",
                f"  Interface: {interface_name}",
                f"  Meta: {meta}",
                f"  Response: {response}",
            ])
            raise ConnectionError(msg) from exc
        instance = interface(transport)
        if response.service_interface and response.service_interface.capabilities:
            instance.__interface_capabilities__ = response.service_interface.capabilities
        return instance

    async def close(self):
        if self._closing:
            self._closing.cancel()
        if self._ws:
            await self._ws.close()

    async def _connect(self, timeout: float = 5.0):
        if self._ws is not None:
            return self._ws

        ws = await connect(self._uri, self._ssl_context, timeout=timeout)
        if ws is None:
            raise ConnectionError(f"Failed to connect to the discovery service {self._uri}.")

        loop = asyncio.get_event_loop()
        if self._closing:
            self._closing.cancel()
        self._ws = ws
        self._closing = loop.create_task(self._wait_closed())
        return self._ws

    async def _wait_closed(self):
        if self._ws is not None:
            await self._ws.closed.wait()
            self._ws = None


async def connect(uri: str, ssl_context: ssl.SSLContext, *, timeout: float = 5.0) -> Optional[WebSocketClient]:
    loop = asyncio.get_event_loop()

    url = parse_url(uri)
    hostname = url.hostname

    # Path-based routing is not used on Workstation setup:
    # https://nvidia-omniverse.atlassian.net/browse/OM-32965
    force_pbr = int(os.getenv("OMNI_DISCOVERY_FORCE_PBR", "0"))
    if hostname in ("localhost", "127.0.0.1", "::1") and not force_pbr:
        ws_port_based_client_task = loop.create_task(create_port_based_client(uri, ssl_context=ssl_context))
        done, pending = await asyncio.wait({ws_port_based_client_task}, timeout=timeout)
        if ws_port_based_client_task in done:
            return ws_port_based_client_task.result()
        else:
            ws_port_based_client_task.cancel()
    else:
        wss_path_based_client_task = loop.create_task(
            create_path_based_client(uri, scheme="wss", ssl_context=ssl_context)
        )
        ws_path_based_client_task = loop.create_task(
            create_path_based_client(uri, scheme="ws", ssl_context=ssl_context)
        )
        ws_port_based_client_task = loop.create_task(
            create_port_based_client(uri, ssl_context=ssl_context)
        )
        tasks = [
            wss_path_based_client_task,
            ws_path_based_client_task,
            ws_port_based_client_task,
        ]
        done = []
        try:
            ws_timeout = loop.create_task(asyncio.sleep(timeout))
            done, pending = await asyncio.wait(
                {wss_path_based_client_task, ws_timeout},
                return_when=asyncio.FIRST_COMPLETED,
            )
            if wss_path_based_client_task in done:
                ws = wss_path_based_client_task.result()
                if ws:
                    return ws

            done, pending = await asyncio.wait(
                {ws_path_based_client_task, ws_timeout},
                return_when=asyncio.FIRST_COMPLETED
            )
            if ws_path_based_client_task in done:
                ws = ws_path_based_client_task.result()
                if ws:
                    return ws

            done, pending = await asyncio.wait(
                {ws_port_based_client_task, ws_timeout},
                return_when=asyncio.FIRST_COMPLETED
            )
            if ws_port_based_client_task in done:
                ws = ws_port_based_client_task.result()
                if ws:
                    return ws
        finally:
            for task in tasks:
                if task not in done:
                    if task.done():
                        ws: WebSocketClient = task.result()
                        if ws:
                            try:
                                await ws.close()
                            except:
                                pass
                    else:
                        task.cancel()


async def create_path_based_client(uri: str, scheme: str = "wss", ssl_context: ssl.SSLContext = None) -> Optional[WebSocketClient]:
    url = parse_url(uri, default_scheme=scheme)
    path = url.path.rstrip("/") + DISCOVERY_ENDPOINT
    hostname = url.hostname
    port = url.port
    scheme = url.scheme

    if port:
        uri = f"{scheme}://{hostname}:{port}{path}"
    else:
        uri = f"{scheme}://{hostname}{path}"

    try:
        ws = WebSocketClient(uri=uri, ssl_context=ssl_context)
        await ws.prepare()
        return ws
    except Exception as exc:
        msg = f"Failed to connect to the discovery service using path-based routing ({uri})."
        logger.debug(msg, exc_info=exc)
    return None


async def create_port_based_client(uri: str, ssl_context: ssl.SSLContext = None) -> Optional[WebSocketClient]:
    url = parse_url(uri, default_scheme="ws")
    hostname = url.hostname
    port = url.port
    scheme = url.scheme
    if not port:
        port = "3333"

    uri = f"{scheme}://{hostname}:{port}"
    try:
        ws = WebSocketClient(uri=uri, ssl_context=ssl_context)
        await ws.prepare()
        return ws
    except Exception as exc:
        msg = f"Failed to connect to the discovery service using port-based routing ({uri})."
        logger.debug(msg, exc_info=exc)
        return None


def parse_url(value: str, default_scheme: str = "ws") -> urllib.parse.ParseResult:
    url = urllib.parse.urlparse(value)
    if not url.scheme:
        url = urllib.parse.urlparse(f"{default_scheme}://{value}")
    return url


Serializer.register(JSONSerializer)
Marshaller.register(Marshaller)
Client.register(HttpClient)
Client.register(HttpFileClient)
Client.register(WebSocketClient)
Client.register(OmniClientTransport)
