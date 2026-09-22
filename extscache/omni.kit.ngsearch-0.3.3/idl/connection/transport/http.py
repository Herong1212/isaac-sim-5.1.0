import asyncio
import json
import os
import ssl
import logging
import urllib.parse
from asyncio.locks import Event
from functools import partial
from typing import Type, AsyncIterator, Optional, Iterable

from aiohttp import ClientSession
from aiohttp.web_request import Request as _Request
from aiohttp.web_response import Response, StreamResponse
from aiohttp.web_runner import AppRunner, Application, TCPSite

from idl.connection.marshallers import Marshaller
from idl.data.serializers import Serializer
from idl.data.serializers.json import JSONSerializer
from . import (
    Client, MethodName, RequestType, ResponseType, TransportError, Server, Dispatcher, InterfaceName, DispatcherError,
    TransportSettings, Meta, Request, init_debug_logger, make_log_id
)
from idl.types.initialization import initialize
from idl.telemetry.http import BaseHTTPServerTelemetry, BaseHTTPClientTelemetry
from idl.telemetry import DefaultHTTPClientTelemetry, DefaultHTTPServerTelemetry

PROTOCOL_NAME = "sohttp"  # Services over HTTP

logger = logging.getLogger('idl.connection.http')
init_debug_logger(logger)


class HttpClient(Client):
    @classmethod
    def create(cls, settings: TransportSettings, kwargs: dict = None) -> 'HttpClient':
        if kwargs is None:
            kwargs = {}

        if settings.name != cls.name():
            raise ValueError(
                "Provided settings are not supported by this transport. "
                f"You should pass them to a client type with {settings.name!r} name."
            )
        marshaller = Marshaller.create(settings.meta["marshaller"], settings.meta["serializer"])
        params = json.loads(settings.params)
        if "uri" in params:
            uri = params["uri"]
        elif "host" in params:
            uri = f"http://{params['host']}"
            if "port" in params:
                uri += f":{params['port']}"
        else:
            raise ValueError("Provided settings must contain 'uri' or 'host' with optional 'port'.")

        ssl_context = kwargs.get("ssl_context")
        return cls(uri=uri, marshaller=marshaller, ssl_context=ssl_context)

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
                yield {
                    "marshaller": marshaller_cls.name(),
                    "serializer": serializer_cls.name()
                }

    def __init__(self, uri: str, *, marshaller: Marshaller = None, ssl_context: ssl.SSLContext = None,
                 client_telemetry: BaseHTTPClientTelemetry = DefaultHTTPClientTelemetry()):
        """
        Instantiates an HTTP client to communicate with the specified URI using Services over HTTP protocol.
        :param uri: The URI to connect to the service. Must use http:// or https:// scheme.
        :param ssl_context: A SSLContext object from `ssl` module. If not specified and if https:// `uri` is used, then
            the default SSLContext is used. If `OMNI_TRUSTED_CERTIFICATE` environment variable is specified, then this
            argument is ignored and SSLContext is resolved based on the environment variable value:
            - If `OMNI_TRUSTED_CERTIFICATE`=`ALL`, then the client will accept any SSL certificate.
            - If path is specified in `OMNI_TRUSTED_CERTIFICATE`, then it's used to add a certificate to the system
              certificate chain.
        :param marshaller: A marshaller used to serialize data and binary content. If it's not specified, uses
            the default marshaller (sending bytes separately) with JSONSerializer.
        """
        if marshaller is None:
            try:
                marshaller = Marshaller(JSONSerializer())
            except (ImportError, ModuleNotFoundError):
                marshaller = None

        self.uri = uri.rstrip("/")
        if uri.startswith("https://"):
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

        self.marshaller = marshaller
        self.ssl_context = ssl_context
        self.prepared = False
        self._session: Optional[ClientSession] = None
        self._closed: Event = Event()
        self.client_telemetry = client_telemetry

    @property
    def session(self):
        if not self._session:
            self._session = ClientSession()
        return self._session

    @property
    def closed(self) -> Event:
        return self._closed

    def params(self) -> dict:
        uri = urllib.parse.urlparse(self.uri)
        return {
            "uri": self.uri,
            "host": uri.hostname,
            "port": uri.port,
        }

    async def prepare(self):
        if self.prepared:
            return
        self._closed.clear()
        self.prepared = True

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None
        self._closed.set()
        self.prepared = False

    async def call(self, interface: InterfaceName, method: MethodName, request, request_type: Type[RequestType], return_type: Type[ResponseType]) -> ResponseType:
        request = initialize(request, request_type)
        url = self.get_url(interface, method)
        headers = self.client_telemetry.inject_headers(headers={})
        response = await self.session.post(url, data=self._send(request), headers=headers, ssl_context=self.ssl_context)
        if 400 < response.status <= 599:
            resp_text = await response.text()
            logger.debug(f'< {make_log_id(request)}: code={response.status} msg={resp_text}')
            raise TransportError(resp_text, code=response.status)

        content = HttpContent(response.content, self.marshaller, make_log_id(request))
        result = await content.read_object(return_type)
        return initialize(result, return_type)

    async def call_many(self, interface: InterfaceName, method: MethodName, request, request_type: Type[RequestType], return_type: Type[ResponseType]) -> AsyncIterator[ResponseType]:
        request = initialize(request, request_type)
        url = self.get_url(interface, method)
        headers = self.client_telemetry.inject_headers(headers={})
        response = await self.session.post(url, data=self._send(request), headers=headers, ssl_context=self.ssl_context)
        if 400 <= response.status <= 599:
            resp_text = await response.text()
            logger.debug(f'< {make_log_id(request)}: code={response.status} msg={resp_text}')
            raise TransportError(await response.text(), code=response.status)

        content = HttpContent(response.content, self.marshaller, make_log_id(request))
        while True:
            obj = await content.read_object(return_type)
            if obj:
                yield initialize(obj, return_type)
            else:
                break

    def get_url(self, interface: str, method: str) -> str:
        return f"{self.uri}/{interface}/{method}/"

    async def _send(self, request):
        content, byte_fields = await self.marshaller.marshal(request)
        logger.debug(f'> {make_log_id(request)}: {str(content, "utf-8")}')
        yield content
        for byte_field in byte_fields:
            sent_separator = False
            chunks = byte_field.get()
            if chunks is not None:
                async for chunk in chunks:
                    if not sent_separator:
                        yield SEPARATOR
                        sent_separator = True
                    yield chunk


SEPARATOR = b"\0\0\0<!--OMNIHTTP-->"


class HttpServer(Server):
    @classmethod
    def name(cls) -> str:
        return PROTOCOL_NAME

    @classmethod
    def get_settings(cls, params: dict, meta: dict) -> TransportSettings:
        return get_settings(params, meta)

    def __init__(self, host: str, port: int, *, marshaller: Marshaller = None, ssl_context: ssl.SSLContext = None, server_telemetry: BaseHTTPServerTelemetry = DefaultHTTPServerTelemetry()):
        if marshaller is None:
            try:
                marshaller = Marshaller(JSONSerializer())
            except (ImportError, ModuleNotFoundError):
                marshaller = None

        self.marshaller = marshaller

        scheme = "https" if ssl_context else "http"
        self.uri = f"{scheme}://{host}:{port}"
        self.ssl_context = ssl_context
        self.site: Optional[TCPSite] = None
        self.server_telemetry = server_telemetry

    @property
    def cors_headers(self):
        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }

    def params(self) -> dict:
        uri = urllib.parse.urlparse(self.uri)
        return {
            "uri": self.uri,
            "host": uri.hostname,
            "port": uri.port,
        }

    def meta(self) -> dict:
        return {
            "marshaller": self.marshaller.name(),
            "serializer": self.marshaller.serializer.name(),
        }

    async def start(self, dispatcher: Dispatcher):
        app = Application()
        app.router.add_options("/{path:.*}", self._preflight)
        app.router.add_post("/{path:.*}", partial(self._handler, dispatcher=dispatcher))
        runner = AppRunner(app)
        await runner.setup()

        uri = urllib.parse.urlparse(self.uri)

        ssl_context = self.ssl_context
        if ssl_context is None:
            ssl_context = ssl.create_default_context() if uri.scheme == "https" else None

        self.site = TCPSite(runner, uri.hostname, uri.port, ssl_context=ssl_context)
        await self.site.start()

    async def stop(self):
        await self.site.stop()

    async def _preflight(self, request: _Request):
        return Response(headers=self.cors_headers)

    async def _handler(self, request: _Request, dispatcher: Dispatcher):
        with self.server_telemetry.get_context(request.headers):
            try:
                interface, method, *_ = request.match_info["path"].split("/")
            except ValueError:
                return Response(status=400, text="Invalid path for service method. "
                                                 "Path should contain interface name and method.")
            try:
                log_id = make_log_id(request)
                content = HttpContent(request.content, self.marshaller, log_id)
                params = await content.read_meta()
                call = dispatcher.get_call(interface, method, params)
                call_in = await content.read_bytes(params, call.args_type)
                call_in = initialize(call_in, call.args_type, force_validation=True)

                Request.set(HttpRequest(interface, method, call_in, http=request))

                call_out = call(call_in)
                response = StreamResponse(headers=self.cors_headers)

                if call.returns_many:
                    async for item in call_out:
                        item = initialize(item, call.return_type)
                        if not response.prepared:
                            await response.prepare(request)
                        await self._write(item, response, log_id)
                else:
                    result = await call_out
                    result = initialize(result, call.return_type)
                    await response.prepare(request)
                    await self._write(result, response, log_id, end=True)

                if not response.prepared:
                    await response.prepare(request)
                await response.write_eof()
                return response
            except DispatcherError as err:
                logger.debug(f'> {log_id}: status: {400} {str(err)}')
                return Response(status=400, text=str(err))

    async def _write(self, data, response, log_id, *, end=False):
        result, byte_fields = await self.marshaller.marshal(data)
        logger.debug(f'> {log_id}: {str(result, "utf-8")}')
        await response.write(result)
        if not end or byte_fields:
            await response.write(SEPARATOR)

        for byte_field in byte_fields:
            chunks = byte_field.get()
            if chunks is not None:
                async for chunk in chunks:
                    await response.write(chunk)
                await response.write(SEPARATOR)


class HttpContent:
    def __init__(self, reader, marshaller: Marshaller, log_id):
        self.reader = reader
        self.log_id = log_id
        self.marshaller = marshaller
        self.tail = b""
        self.wait_read = None

    async def read_object(self, return_type: Type[Response]) -> Optional[Response]:
        meta = await self.read_meta()
        if meta:
            obj = await self.read_bytes(meta, return_type)
            return return_type(obj)
        return None

    async def read_meta(self) -> Optional[Response]:
        if self.wait_read:
            await self.wait_read
            self.wait_read = None

        meta = bytearray()
        async for chunk in self._read_chunks():
            meta.extend(chunk)
        if not meta:
            return None
        logger.debug(f'< {self.log_id}: {str(meta, "utf-8")}')
        return await self.marshaller.unmarshal(meta)

    async def read_bytes(self, meta: Response, return_type: Type[Response]) -> Response:
        self.wait_read = asyncio.Future()

        async def read_bytes():
            async for data in self._read_chunks():
                yield data
            self.wait_read.set_result(True)

        byte_fields = self.marshaller.introspect(meta, return_type)
        if len(byte_fields) > 1:
            raise ValueError("Data may contain only one AsyncIterator[bytes] field.")
        elif len(byte_fields) == 1:
            byte_field = byte_fields[0]
            byte_field.set(read_bytes())
        else:
            self.wait_read.set_result(True)
        return meta

    async def _read_chunks(self):
        while True:
            if self.tail:
                chunk = self.tail
                self.tail = b""
            else:
                chunk, chunk_end = await self.reader.readchunk()
            if not chunk and not chunk_end:
                return
            sep_index = chunk.find(SEPARATOR)
            if sep_index == -1:
                yield chunk
            else:
                yield chunk[:sep_index]
                self.tail = chunk[sep_index + len(SEPARATOR):]
                return


def get_settings(params: dict, meta: dict) -> TransportSettings:
    return TransportSettings(
        name=PROTOCOL_NAME,
        params=json.dumps(params),
        meta={
            "marshaller": meta.get("marshaller", Marshaller.name()),
            "serializer": meta.get("serializer", JSONSerializer.name()),
        }
    )


class HttpRequest(Request):
    def __init__(self, interface: str, method: str, params: dict, http: _Request):
        super().__init__(interface, method, params)
        self.http = http
