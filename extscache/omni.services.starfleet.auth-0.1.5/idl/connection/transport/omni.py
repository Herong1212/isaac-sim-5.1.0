import asyncio
import json
import logging
import os
import ssl
import traceback
from asyncio import Event
from typing import AsyncIterator, Dict, Iterable, List, Optional, Tuple, Type

import websockets
import websockets.legacy.http
from idl.data.serializers.json import JSONSerializer
from idl.types import initialize

from ..marshallers import Marshaller
from . import (
    Client,
    InterfaceName,
    Meta,
    MethodName,
    RequestType,
    ResponseType,
    TransportError,
    TransportSettings,
    init_debug_logger,
    make_log_id,
)

MAX_SIZE = 2 ** 25

logger = logging.getLogger("idl.connection.omni")
init_debug_logger(logger)

# https://nvidia-omniverse.atlassian.net/browse/OM-43643
MAX_HTTP_LINE = os.getenv("WS_MAX_HTTP_LINE")
if MAX_HTTP_LINE:
    try:
        websockets.legacy.http.MAX_LINE = int(MAX_HTTP_LINE)
    except ValueError:
        raise EnvironmentError("WS_MAX_HTTP_LINE must be an integer number.")


class OmniClientTransport(Client):
    @classmethod
    def name(cls) -> str:
        return "connlib"

    @classmethod
    def get_settings(cls, params: dict, meta: dict):
        return TransportSettings(
            name=cls.name(),
            params=json.dumps({
                "url": params["url"]
            }),
            meta={}
        )

    @classmethod
    def get_meta_choices(cls) -> Iterable[Meta]:
        yield {}

    @classmethod
    def create(cls, settings: TransportSettings, kwargs: dict = None) -> 'OmniClientTransport':
        if kwargs is None:
            kwargs = {}

        if settings.name != cls.name():
            raise ValueError(
                "Provided settings is not supported by this transport. "
                f"You should pass them to a client type with {settings.name!r} name."
            )
        params = json.loads(settings.params)

        ssl_context = kwargs.get("ssl_context")
        return cls(url=params["url"], ssl_context=ssl_context)

    def __init__(self, url: str, *, max_size: int = MAX_SIZE,
                 ssl_context: ssl.SSLContext = None, **kwargs):
        """
        Instantiates a WebSocket client to communicate with the specified URL using Omniverse API protocol.
        :param url: The URL to connect to the service. Must use ws:// or wss:// scheme.
        :param ssl_context: A SSLContext object from `ssl` module. If not specified and if wss:// `url` is used, then
            the default SSLContext is used. If `OMNI_TRUSTED_CERTIFICATE` environment variable is specified, then this
            argument is ignored and SSLContext is resolved passed on the environment variable value:
            - If `OMNI_TRUSTED_CERTIFICATE`=`ALL`, then the client will accept any SSL certificate.
            - If path is specified in `OMNI_TRUSTED_CERTIFICATE`, then it's used to add a certificate to the system
              certificate chain.
        :param max_size: Maximum size of a single WebSocket message. Passed to `websockets.connect`.
        """
        self.url = url
        if url.startswith("wss://"):
            trusted_cert = os.getenv("OMNI_TRUSTED_CERTIFICATE")
            if trusted_cert == "ALL":
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            elif trusted_cert:
                ssl_context = ssl.create_default_context()
                ssl_context.load_verify_locations(trusted_cert)
            elif ssl_context is None:
                ssl_context = ssl.create_default_context()

        self.ssl_context = ssl_context
        self.marshaller = Marshaller(JSONSerializer())
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.max_size = max_size
        self.requests: Dict[int, asyncio.Queue] = {}
        self.request_count = 0
        self.listening = None
        self.prepared = False

        self._closed = Event()

        # Websockets documentation says: "Once the connection is open, a Ping frame is sent every ping_interval
        # seconds. If the corresponding Pong frame isn’t received within ping_timeout seconds, the connection is
        # considered unusable and is closed. ping_interval is 20 seconds by default."
        # We should make this parameter configurable
        self.ping_interval = kwargs.get('ping_interval', 20)

    @property
    def closed(self) -> Event:
        return self._closed

    def params(self) -> dict:
        return {
            "url": self.url,
        }

    async def prepare(self):
        if self.prepared:
            return

        self._closed.clear()
        try:
            self.ws = await websockets.connect(self.url, max_size=self.max_size, compression=None, ssl=self.ssl_context, ping_interval=self.ping_interval)
        except (ssl.SSLError, ssl.CertificateError):
            raise
        except (ConnectionRefusedError, ConnectionError, websockets.WebSocketException, OSError) as err:
            raise TransportError(str(err))
        self.listening = asyncio.get_event_loop().create_task(self._listen())
        self.prepared = True

    async def close(self):
        self._closed.set()
        self.prepared = False
        if self.ws is not None:
            await self.ws.close()
        if self.listening:
            self.listening.cancel()
        await self._cleanup()

    async def call(self, interface: InterfaceName, method: MethodName, request: dict, request_type: Type[RequestType], return_type: Type[ResponseType]) -> ResponseType:
        if self._closed.is_set():
           raise TransportError("Connection is already closed")
        request = initialize(request, request_type)
        command_id, data = await self._serialize(method, request)
        self.requests[command_id] = handle = asyncio.Queue()
        try:
            await self.ws.send(data)
            result = await handle.get()
            if result is self.END:
                raise TransportError("Unexpected END of response.")
            if isinstance(result, TransportError):
                raise result
            meta, content = result
            result = await self._deserialize(meta, content, return_type)
            return initialize(result, return_type)
        except (ConnectionRefusedError, ConnectionError, websockets.WebSocketException) as err:
            raise TransportError(str(err))
        finally:
            del self.requests[command_id]

    async def call_many(self, interface: InterfaceName, method: MethodName, request: dict, request_type: Type[RequestType], return_type: Type[ResponseType]) -> AsyncIterator[ResponseType]:
        if self._closed.is_set():
           raise TransportError("Connection is already closed")
        request = initialize(request, request_type)
        command_id, data = await self._serialize(method, request)
        self.requests[command_id] = handle = asyncio.Queue()
        try:
            await self.ws.send(data)
            while True:
                result = await handle.get()
                if result is self.END:
                    return
                if isinstance(result, TransportError):
                    raise result
                meta, content = result
                result = await self._deserialize(meta, content, return_type)
                yield initialize(result, return_type)
        except (ConnectionRefusedError, ConnectionError, websockets.WebSocketException) as err:
            raise TransportError(str(err))
        finally:
            del self.requests[command_id]
            await asyncio.shield(self._stop_subscription(command_id))

    async def _listen(self):
        try:
            async for data in self.ws:
                if not data:
                    break

                separator = data.find(b"\0")
                if separator == -1:
                    meta, content = data, None
                else:
                    meta, content = data[0:separator], data[separator + 1:]

                try:
                    response = await self.marshaller.unmarshal(meta)
                except ValueError:
                    # Skip responses that can't be parsed by the serializer.
                    continue

                command_id = response.pop("id")
                try:
                    command_id = int(command_id)
                except ValueError:
                    continue

                queue = self.requests.get(command_id, None)
                if not queue:
                    continue

                await queue.put((response, content))
        except (ConnectionRefusedError, ConnectionError, websockets.WebSocketException) as err:
            command_ids = self.requests.keys()
            for command_id in command_ids:
                queue = self.requests.get(command_id)
                if queue:
                    await queue.put(TransportError(str(err)))
            await self._cleanup()
            self._closed.set()
        except asyncio.CancelledError:
            pass

    async def _serialize(self, method: str, request) -> Tuple[int, bytes]:
        data = {}
        data["id"] = self.request_count = command_id = self.request_count + 1
        data["command"] = method
        data.update({field: value for field, value in request.items() if value is not None})

        logger.debug(f"> {make_log_id(self)}: {data}")

        data, byte_fields = await self.marshaller.marshal(data, from_type=type(request))
        if len(byte_fields) > 1:
            raise ValueError("Multiple binary fields are not supported.")

        if len(byte_fields) == 1:
            byte_field = byte_fields[0]

            chunks = byte_field.get()
            if chunks is not None:
                binary = bytearray()

                async for chunk in chunks:
                    binary.extend(chunk)

                if binary:
                    data += b"\0" + binary
        return command_id, data

    async def _deserialize(self, meta: dict, content: bytes, return_type: Type[ResponseType]) -> ResponseType:
        async def reader(data):
            yield data

        if content is None:
            content = b""

        logger.debug(f"< {make_log_id(self)}: {meta}")

        byte_fields = self.marshaller.introspect(meta, return_type)
        if len(byte_fields) > 1:
            raise ValueError("Multiple binary fields are not supported.")

        if len(byte_fields) == 1:
            byte_field = byte_fields[0]
            chunks = byte_field.get()
            if chunks is None:
                byte_field.set(reader(content))
        return meta

    async def _stop_subscription(self, command_id: int):
        _, data = await self._serialize("stop", {"subscription_id": command_id})
        try:
            await self.ws.send(data)
        except websockets.ConnectionClosed:
            pass

    async def _cleanup(self):
        for requests in self.requests.values():
            requests.put_nowait(self.END)
        self.listening = None

    END = object()
