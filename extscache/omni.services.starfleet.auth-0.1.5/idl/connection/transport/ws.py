import asyncio
import http
import json
import logging
import os
import ssl
import struct
import traceback
import urllib.parse
from typing import Type, AsyncIterator, Optional, Dict, Tuple, Iterable, Callable, Awaitable

import websockets
import websockets.exceptions
import websockets.legacy.http
from websockets.datastructures import HeadersLike, Headers

from idl.data.serializers import Serializer
from idl.data.serializers.json import JSONSerializer
from idl.types.initialization import initialize, ValidationError
from . import (
    Client, InterfaceName, MethodName, RequestType, ResponseType, Server, Dispatcher, TransportError, DispatcherError,
    TransportSettings, Meta, Request, init_debug_logger, make_log_id
)
from ..marshallers import Marshaller

ws_logger = logging.getLogger("idl.connection.ws")
init_debug_logger(ws_logger)

MAX_SIZE = 2 ** 25
PROTOCOL_NAME = "sows"  # Services over WebSocket

# https://nvidia-omniverse.atlassian.net/browse/OM-43643
MAX_HTTP_LINE = os.getenv("WS_MAX_HTTP_LINE")
if MAX_HTTP_LINE:
    try:
        websockets.legacy.http.MAX_LINE = int(MAX_HTTP_LINE)
    except ValueError:
        raise EnvironmentError("WS_MAX_HTTP_LINE must be an integer number.")


class _ErrorCode:
    UnexpectedMessage = 0x01
    UnknownInterface = 0x02
    UnknownMethod = 0x03
    InvalidParams = 0x04
    InternalServerError = 0xFF
    ServiceError = 0x100


_Errors = {
    _ErrorCode.UnexpectedMessage: "The message type '%s' is unexpected.",
    _ErrorCode.UnknownInterface: "Cannot find interface '%s'.",
    _ErrorCode.UnknownMethod: "The service method for '%s.%s' has not been found.",
    _ErrorCode.InvalidParams: "The sent parameters can't be parsed or invalid for this call.",
    _ErrorCode.InternalServerError: "An internal server error has occurred.",
}


class _Packet:
    type: int

    def __init__(self, request_id: int):
        self.request_id = request_id

    @property
    def framing(self):
        return True

    @property
    def data(self):
        return self.header()

    async def send(self, ws):
        if self.framing:
            await ws.send(self)
        else:
            await ws.send(self.data)

    async def __aiter__(self):
        yield self.header()

    def header(self):
        return struct.pack("<BI", self.type, self.request_id)

    @classmethod
    def parse_header(cls, data: bytes) -> Tuple[int, int, bytes]:
        packet_type, request_id = struct.unpack_from("<BI", data)
        return packet_type, request_id, data[5:]


class _Stop(_Packet):
    """
    Aborts the server request.
    Can be sent if the client used _StartRequest and wants to abort the request handling
    instead of sending _ContinueRequest or _FinishRequest.

    Also can be sent to stop receiving responses from the service.
    """
    type = 0

    @property
    def framing(self):
        return False


class _SendRequest(_Packet):
    """
    Sends the request to the server in one message.
    """

    type = 1

    def __init__(self, request_id: int, interface: str, method: str, params: bytes, blob: bytes = None):
        super().__init__(request_id)
        self.interface = interface
        self.method = method
        self.params = params
        self.blob = blob

    @property
    def framing(self):
        return bool(self.blob)

    @property
    def data(self):
        return self.content()

    async def __aiter__(self):
        yield self.content()
        if self.blob:
            yield self.blob

    def content(self):
        content = b""
        content += self.header()
        content += f"{self.interface}.{self.method}\0".encode()
        content += struct.pack("<I", len(self.params)) + self.params
        return content

    @classmethod
    def parse(cls, request_id: int, data: bytes) -> "_SendRequest":
        sep = data.find(b"\0")
        if sep == -1:
            raise ValueError("Malformed data for _SendRequest.")

        data_mv = memoryview(data)
        call, payload = data_mv[0:sep], data_mv[sep + 1:]
        interface, method = call.tobytes().decode().split(".", maxsplit=1)

        params_size, = struct.unpack_from("<I", payload)
        params, blob = payload[4:params_size + 4].tobytes(), payload[params_size + 4:].tobytes()
        return cls(request_id, interface, method, params, blob)


class _StartRequest(_SendRequest):
    type = 2


class _ContinueRequest(_Packet):
    type = 3

    def __init__(self, request_id: int, blob: bytes = None):
        super().__init__(request_id)
        self.blob = blob

    @property
    def framing(self):
        return bool(self.blob)

    @property
    def data(self):
        return self.header()

    async def __aiter__(self):
        yield self.header()
        if self.blob:
            yield self.blob

    @classmethod
    def parse(cls, request_id: int, data: bytes) -> "_ContinueRequest":
        return cls(request_id, data)


class _EndRequest(_ContinueRequest):
    type = 4


class WebSocketClient(Client):
    @classmethod
    def name(cls) -> str:
        return PROTOCOL_NAME

    @classmethod
    def get_settings(cls, params: dict, meta: dict) -> TransportSettings:
        return get_settings(params, meta)

    @classmethod
    def get_meta_choices(cls) -> Iterable[Meta]:
        for serializer_cls in Serializer.get_all():
            for marshaller_cls in Marshaller.get_all():
                for using_ssl in ["true", "false"]:
                    yield {
                        "marshaller": marshaller_cls.name(),
                        "serializer": serializer_cls.name(),
                        "ssl": using_ssl
                    }
                    yield {
                        "marshaller": marshaller_cls.name(),
                        "serializer": serializer_cls.name(),
                        "ssl": using_ssl,
                        "supports_path": "true"
                    }

    @classmethod
    def create(cls, settings: TransportSettings, kwargs: dict = None) -> 'WebSocketClient':
        if kwargs is None:
            kwargs = {}

        if settings.name != cls.name():
            raise ValueError(
                "Provided settings are not supported by this transport. "
                f"You should pass them to a client type with {settings.name!r} name."
            )

        marshaller = Marshaller.create(settings.meta["marshaller"], settings.meta["serializer"])
        secure = settings.meta.get("ssl", "false")
        scheme = "wss" if secure == "true" else "ws"

        params = json.loads(settings.params)
        uri = f"{scheme}://{params['host']}"
        if "port" in params:
            uri += f":{params['port']}"
        if "path" in params:
            uri += params['path']

        ssl_context = kwargs.get("ssl_context")
        return cls(uri=uri, marshaller=marshaller, ssl_context=ssl_context)

    def __init__(self, uri: str, *, marshaller: Marshaller = None, max_size: int = MAX_SIZE,
                 ssl_context: ssl.SSLContext = None):
        """
        Instantiates a WebSocket client to communicate with the specified URI using Services over WebSocket protocol.
        :param uri: The URI to connect to the service. Must use ws:// or wss:// scheme.
        :param ssl_context: A SSLContext object from `ssl` module. If not specified and if wss:// `uri` is used, then
            the default SSLContext is used. If `OMNI_TRUSTED_CERTIFICATE` environment variable is specified, then this
            argument is ignored and SSLContext is resolved passed on the environment variable value:
            - If `OMNI_TRUSTED_CERTIFICATE`=`ALL`, then the client will accept any SSL certificate.
            - If path is specified in `OMNI_TRUSTED_CERTIFICATE`, then it's used to add a certificate to the system
              certificate chain.
        :param marshaller: A marshaller used to serialize data and binary content. If it's not specified, uses
            the default marshaller (sending bytes separately) with JSONSerializer.
        :param max_size: Maximum size of a single WebSocket message. Passed to `websockets.connect`.
        """
        if marshaller is None:
            try:
                from idl.data.serializers.json import JSONSerializer
                from idl.connection.marshallers import Marshaller
                marshaller = Marshaller(JSONSerializer())
            except (ImportError, ModuleNotFoundError):
                marshaller = None

        self.uri = uri
        if uri.startswith("wss://"):
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
        self.marshaller = marshaller
        self.max_size = max_size
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.listening: Optional[asyncio.Task] = None
        self.request_id = 0
        self.messages: Dict[int, asyncio.Queue] = {}
        self.results: Dict[int, asyncio.Queue] = {}
        self.locks: Dict[int, asyncio.Lock] = {}
        self.loop = asyncio.get_event_loop()
        self.prepared = False

        self._closed = asyncio.Event()

    @property
    def closed(self) -> asyncio.Event:
        return self._closed

    def params(self) -> dict:
        uri = urllib.parse.urlparse(self.uri)
        params = {
            "host": uri.hostname,
            "port": uri.port,
        }

        if uri.path and uri.path != "/":
            params["path"] = uri.path
        return params

    async def prepare(self):
        if self.prepared:
            return

        self._closed.clear()
        try:
            self.ws = await websockets.connect(
                self.uri,
                max_size=self.max_size,
                compression=None,
                ssl=self.ssl_context,
            )
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
        self._cleanup()

    async def _listen(self):
        try:
            while True:
                data = await self.ws.recv()
                packet_type, request_id, data = _Packet.parse_header(data)
                messages = self.messages.get(request_id)
                if messages:
                    await messages.put((packet_type, data))
        except (websockets.ConnectionClosedOK, asyncio.CancelledError) as err:
            pass
        except (ConnectionRefusedError, ConnectionError, websockets.WebSocketException) as err:
            ws_logger.exception("Connection error", exc_info=err)
            raise
        except:
            ws_logger.error(traceback.format_exc())
            raise
        finally:
            self._cleanup()

    async def call(self, interface: InterfaceName, method: MethodName, request: dict, request_type: Type[RequestType], return_type: Type[ResponseType]) -> ResponseType:
        if self._closed.is_set():
            raise TransportError("Connection is already closed")
        request = initialize(request, request_type)
        results, _ = await self._send(interface, method, request, return_type)
        result = await results.get()
        if isinstance(result, Exception):
            raise result
        if result is self.END:
            raise TransportError("The remote host has closed the connection.")
        return initialize(result, return_type)

    async def call_many(self, interface: InterfaceName, method: MethodName, request: dict, request_type: Type[RequestType], return_type: Type[ResponseType]) -> AsyncIterator[ResponseType]:
        if self._closed.is_set():
            raise TransportError("Connection is already closed")
        request = initialize(request, request_type)
        results, request_id = await self._send(interface, method, request, return_type)
        try:
            while True:
                result = await results.get()
                if isinstance(result, Exception):
                    raise result
                if result is self.END:
                    break
                yield initialize(result, return_type)

                # Move to the next response.
                # Release the content lock and skip all messages related to the current response.
                lock = self.locks.get(request_id, None)
                if lock is not None and lock.locked():
                    lock.release()
        finally:
            if self.listening:
                try:
                    await _Stop(request_id).send(self.ws)
                except websockets.ConnectionClosedOK:
                    pass

    END = object()

    async def _send(self, interface: str, method: str, request, return_type: Type):
        self.request_id = request_id = self.request_id + 1
        self.messages[request_id] = asyncio.Queue(maxsize=50)
        self.results[request_id] = results = asyncio.Queue()
        self.loop.create_task(self._receive(request_id, return_type))

        try:
            content, byte_fields = await self.marshaller.marshal(request)
            ws_logger.debug(f'> {make_log_id(self)}: id={request_id}, {str(content, "utf-8")}')
            streaming = False
            for byte_field in byte_fields:
                chunks = byte_field.get()
                if chunks is not None:
                    async for chunk in chunks:
                        if not streaming:
                            await _StartRequest(request_id, interface, method, content).send(self.ws)
                            streaming = True
                        await _ContinueRequest(request_id, chunk).send(self.ws)

            if streaming:
                await _EndRequest(request_id).send(self.ws)
            else:
                await _SendRequest(request_id, interface, method, content).send(self.ws)
            return results, request_id
        except (ConnectionRefusedError, ConnectionError, websockets.WebSocketException) as err:
            del self.messages[request_id]
            del self.results[request_id]
            raise TransportError(str(err))

    async def _receive(self, request_id: int, return_type: Type):
        messages = self.messages.get(request_id)
        if not messages:
            return

        results = self.results.get(request_id)
        if not results:
            return

        byte_queue = None

        lock = self.locks[request_id] = asyncio.Lock()

        async def receive_bytes(queue):
            release_lock = asyncio.ensure_future(lock.acquire())
            while lock.locked():
                receive_message = asyncio.ensure_future(queue.get())
                done, pending = await asyncio.wait([release_lock, receive_message], return_when=asyncio.FIRST_COMPLETED)
                if release_lock in done:
                    # User moved to the next response -- abort data receiving for the current.
                    # Technically it means that the user haven't processed the response BLOB.
                    # We are caching only the current response in a limited size queue to prevent memory overflow.
                    # It means that we enforce users to handle multiple responses with BLOBs one-by-one.
                    # If the user needs to process BLOBs after receiving all messages,
                    # he needs to read and cache BLOBs by his own.
                    lock.release()
                    break

                chunk = receive_message.result()
                if chunk is self.END:
                    if lock.locked():
                        release_lock.cancel()
                        lock.release()
                    break
                yield chunk

        try:
            while True:
                message = await messages.get()
                if message is self.END:
                    break

                response_type, data = message
                if response_type == _Error.type:
                    error = _Error.parse(request_id, data)
                    await results.put(TransportError(error.message, error.code))
                    break
                elif response_type in (_SendResponse.type, _StartResponse.type):
                    if response_type == _SendResponse.type:
                        response = _SendResponse.parse(request_id, data)
                    else:
                        response = _StartResponse.parse(request_id, data)

                    ws_logger.debug(f'< {make_log_id(self)}: id={request_id}, {str(response.params, "utf-8")}')
                    result = await self.marshaller.unmarshal(response.params)

                    # Wait until the user will read the content of previous response.
                    await lock.acquire()

                    byte_queue = asyncio.Queue(maxsize=50)
                    byte_fields = self.marshaller.introspect(result, return_type)
                    for byte_field in byte_fields:
                        byte_field.set(receive_bytes(byte_queue))
                        if response.blob:
                            byte_queue.put_nowait(response.blob)
                            response.blob = None

                    if response_type == _SendResponse.type:
                        byte_queue.put_nowait(self.END)

                    await results.put(return_type(result))
                    if response.last:
                        await results.put(self.END)

                elif response_type == _ContinueResponse.type:
                    if byte_queue is None:
                        await results.put(TransportError("Unexpected _ContinueResponse.", code=_ErrorCode.UnexpectedMessage))
                        break

                    response = _ContinueResponse.parse(request_id, data)
                    await byte_queue.put(response.blob)
                elif response_type == _EndResponse.type:
                    # Signals about the end of this response

                    if byte_queue is None:
                        await results.put(TransportError("Unexpected _EndResponse.", code=_ErrorCode.UnexpectedMessage))
                        break

                    response = _EndResponse.parse(request_id, data)
                    await byte_queue.put(response.blob)
                    await byte_queue.put(self.END)
                elif response_type == _Done.type:
                    await results.put(self.END)
                    break
        except (ConnectionRefusedError, ConnectionError, websockets.WebSocketException) as exc:
            self.results[request_id].put_nowait(TransportError(str(exc)))
        except Exception as exc:
            self.results[request_id].put_nowait(exc)
        finally:
            self.messages.pop(request_id, None)
            self.results.pop(request_id, None)
            self.locks.pop(request_id, None)

    def _cleanup(self):
        for messages in self.messages.values():
            messages.put_nowait(self.END)
        for results in self.results.values():
            results.put_nowait(self.END)


class _Error(_Packet):
    type = 0

    def __init__(self, request_id: int, code: int, *args, message: str = None):
        super().__init__(request_id)
        self.code = code
        self.args = args
        if message is None:
            message = _Errors[self.code] % self.args
        self.message = message

    @property
    def framing(self):
        return False

    @property
    def data(self):
        content = b""
        content += self.header()
        content += struct.pack("<H", self.code)
        content += self.message.encode()
        return content

    @classmethod
    def parse(cls, request_id: int, data: bytes) -> "_Error":
        code, *_ = struct.unpack_from("<H", data)
        message = data[2:].decode()
        return cls(request_id, code, message=message)


class _SendResponse(_Packet):
    type = 1

    def __init__(self, request_id: int, params: bytes, last: bool = False, blob: bytes = b""):
        super().__init__(request_id)
        self.params = params
        self.last = last
        self.blob = blob

    @property
    def framing(self):
        return bool(self.blob)

    @property
    def data(self):
        return self.content()

    async def __aiter__(self):
        yield self.content()
        if self.blob:
            yield self.blob

    def content(self):
        content = b""
        content += self.header()
        content += struct.pack("<B", self.last)
        content += struct.pack("<I", len(self.params)) + self.params
        return content

    @classmethod
    def parse(cls, request_id: int, data: bytes) -> "_SendResponse":
        last, params_size = struct.unpack_from("<BI", data)
        params, blob = data[5:params_size + 5], data[params_size + 5:]
        return cls(request_id, params=params, last=bool(last), blob=blob)


class _StartResponse(_SendResponse):
    type = 2


class _ContinueResponse(_Packet):
    type = 3

    def __init__(self, request_id: int, blob: bytes = None):
        super().__init__(request_id)
        self.blob = blob

    @property
    def framing(self):
        return bool(self.blob)

    @property
    def data(self):
        return self.header()

    async def __aiter__(self):
        yield self.header()
        if self.blob:
            yield self.blob

    @classmethod
    def parse(cls, request_id: int, data: bytes) -> "_ContinueResponse":
        return cls(request_id, blob=data)


class _EndResponse(_ContinueResponse):
    type = 4


class _Done(_Packet):
    type = 5

    @property
    def framing(self):
        return False


HTTPResponse = Tuple[http.HTTPStatus, HeadersLike, bytes]


class WebSocketServer(Server):
    @classmethod
    def name(cls) -> str:
        return PROTOCOL_NAME

    @classmethod
    def get_settings(cls, params: dict, meta: dict) -> TransportSettings:
        return get_settings(params, meta)

    def __init__(
        self,
        host: str,
        port: int,
        *,
        marshaller: Marshaller = None,
        max_size: int = MAX_SIZE,
        ssl_context: ssl.SSLContext = None,
        extra_headers: dict = None,
        process_request: Optional[
            Callable[[str, Headers], Awaitable[Optional[HTTPResponse]]]
        ] = None
    ):
        if marshaller is None:
            try:
                from idl.data.serializers.json import JSONSerializer
                from idl.connection.marshallers import Marshaller
                marshaller = Marshaller(JSONSerializer())
            except (ImportError, ModuleNotFoundError):
                marshaller = None

        self.marshaller = marshaller

        self.scheme = "wss" if ssl_context else "ws"
        self.uri = f"{self.scheme}://{host}:{port}/"
        self.ssl_context = ssl_context
        self.max_size = max_size
        self.extra_headers = extra_headers
        self.process_request = process_request

        self.server: Optional[websockets.WebSocketServer] = None

    def params(self) -> dict:
        uri = urllib.parse.urlparse(self.uri)
        return {
            "host": uri.hostname,
            "port": uri.port,
        }

    def meta(self) -> dict:
        return {
            "marshaller": self.marshaller.name(),
            "serializer": self.marshaller.serializer.name(),
            "ssl": "true" if self.scheme == "wss" else "false",
        }

    async def start(self, dispatcher: Dispatcher):
        async def handle(ws: websockets.WebSocketServerProtocol, path: str):
            loop = asyncio.get_event_loop()
            tasks = set()
            messages_by_id = {}
            requests_by_id = {}
            try:
                while True:
                    data = await ws.recv()
                    packet_type, request_id, data = _Packet.parse_header(data)
                    if packet_type == _Stop.type:
                        # Cancels the request.
                        request = requests_by_id.pop(request_id, None)
                        if request:
                            request.cancel()
                    elif packet_type in (_SendRequest.type, _StartRequest.type):
                        # Starts the request.

                        if packet_type == _SendRequest.type:
                            request = _SendRequest.parse(request_id, data)
                        else:
                            request = _StartRequest.parse(request_id, data)

                        ws_logger.debug(f'< {make_log_id(ws)}: id={request_id}, {str(request.params, "utf-8")}')

                        messages_by_id[request_id] = messages = asyncio.Queue(maxsize=50)
                        if request.blob:
                            messages.put_nowait((request.type, request.blob))

                        requests_by_id[request_id] = task = loop.create_task(
                            self._call_service(request, ws, dispatcher, messages_by_id))

                        task.add_done_callback(tasks.remove)
                        tasks.add(task)
                    elif packet_type == _ContinueRequest.type and request_id in messages_by_id:
                        # The client continues sending BLOBs

                        request = _ContinueRequest.parse(request_id, data)
                        messages = messages_by_id[request_id]
                        await messages.put((request.type, request.blob))
                    elif packet_type == _EndRequest.type and request_id in messages_by_id:
                        # The client has finished sending BLOBs

                        request = _EndRequest.parse(request_id, data)
                        messages = messages_by_id[request_id]
                        await messages.put((request.type, request.blob))
                    else:
                        await _Error(request_id, _ErrorCode.UnexpectedMessage, packet_type).send(ws)
            except websockets.ConnectionClosed:
                pass
            finally:
                for task in tasks:
                    task.cancel()

        uri = urllib.parse.urlparse(self.uri)

        ssl_context = self.ssl_context
        if ssl_context is None:
            ssl_context = ssl.create_default_context() if uri.scheme == "wss" else None

        self.server = await websockets.serve(
            handle, uri.hostname, uri.port, ssl=ssl_context, compression=None, max_size=self.max_size,
            extra_headers=self.extra_headers, process_request=self.process_request
        )

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

    async def _call_service(self,
                            request: _SendRequest,
                            ws: websockets.WebSocketServerProtocol,
                            dispatcher: Dispatcher,
                            messages_by_id: Dict[int, asyncio.Queue]):
        try:
            try:
                params = await self.marshaller.unmarshal(request.params)
            except (ValueError, TypeError):
                await _Error(request.request_id, _ErrorCode.InvalidParams).send(ws)
                return

            try:
                call = dispatcher.get_call(request.interface, request.method, params)
            except DispatcherError:
                await _Error(request.request_id, _ErrorCode.UnknownMethod, request.interface, request.method).send(ws)
                return

            messages = messages_by_id.get(request.request_id)
            if messages is None:
                # Task has been cancelled
                return

            byte_fields = self.marshaller.introspect(params, call.args_type)
            for byte_field in byte_fields:
                byte_field.set(self._recv_packets(messages))

            try:
                params = initialize(params, call.args_type, force_validation=True)
            except ValidationError:
                await _Error(request.request_id, _ErrorCode.InvalidParams).send(ws)
                return

            try:
                Request.set(WebSocketRequest(
                    interface=request.interface,
                    method=request.method,
                    params=params,
                    ws=ws
                ))

                resp = call(params)
                if call.returns_many:
                    async for item in resp:
                        await self._send_response(request.request_id, item, call.return_type, ws)
                    await _Done(request.request_id).send(ws)
                else:
                    await self._send_response(request.request_id, await resp, call.return_type, ws, last=True)
            except asyncio.CancelledError:
                return
            except TransportError as error:
                await _Error(request.request_id, error.code).send(ws)
        except websockets.WebSocketException:
            ws_logger.debug(traceback.format_exc())
        except:
            ws_logger.error(traceback.format_exc())
            await _Error(request.request_id, _ErrorCode.InternalServerError).send(ws)
        finally:
            messages = messages_by_id.pop(request.request_id, None)
            if messages:
                # Puts a Stop message into the queue to abort receiving BLOBs
                messages.put_nowait(_Stop(request.request_id))

    async def _send_response(self, request_id: int, response: ResponseType, response_type: Type[ResponseType],
                             ws: websockets.WebSocketServerProtocol, last: bool = False):
        response = initialize(response, response_type)
        content, byte_fields = await self.marshaller.marshal(response)
        ws_logger.debug(f'> {make_log_id(ws)}: id={request_id}, {str(content, "utf-8")}')
        streaming = False
        for byte_field in byte_fields:
            chunks = byte_field.get()
            if chunks:
                async for chunk in chunks:
                    if not streaming:
                        await _StartResponse(request_id, content, last=last).send(ws)
                        streaming = True
                    await _ContinueResponse(request_id, chunk).send(ws)

        if streaming:
            await _EndResponse(request_id).send(ws)
        else:
            await _SendResponse(request_id, content, last=last).send(ws)

    async def _recv_packets(self, message_queue: asyncio.Queue):
        while True:
            packet_type, data = await message_queue.get()
            if packet_type == _Stop.type:
                raise asyncio.CancelledError()

            if packet_type in (_SendRequest.type, _EndRequest.type):
                if data:
                    yield data
                break

            if packet_type in (_StartRequest.type, _ContinueRequest.type):
                if data:
                    yield data
            else:
                raise TransportError(_Errors[_ErrorCode.UnexpectedMessage] % packet_type, _ErrorCode.UnexpectedMessage)


def get_settings(params: dict, meta: dict) -> TransportSettings:
    settings_meta = {
        "marshaller": meta.get("marshaller", Marshaller.name()),
        "serializer": meta.get("serializer", JSONSerializer.name()),
        "ssl": meta.get("ssl", "false"),
    }

    path = params.get("path", "")
    if path and path != "/":
        settings_meta["supports_path"] = "true"

    settings_params = json.dumps(params)
    return TransportSettings(
        name=PROTOCOL_NAME,
        params=settings_params,
        meta=settings_meta
    )


class WebSocketRequest(Request):
    def __init__(self, interface: str, method: str, params: dict, ws: websockets.WebSocketServerProtocol):
        super().__init__(interface, method, params)
        self.ws = ws
