import json
import ssl
import sys
import urllib.parse
import logging
from asyncio.locks import Event
from functools import partial
from typing import Optional, Type, AsyncIterator, Iterable

from aiohttp import ClientSession
from aiohttp.web_app import Application
from aiohttp.web_request import Request as _Request
from aiohttp.web_response import Response as _Response, StreamResponse
from aiohttp.web_runner import AppRunner, TCPSite

from idl.connection.marshallers import Marshaller
from idl.connection.transport import Server, Dispatcher, TransportSettings, DispatcherError, Client, InterfaceName, \
    MethodName, RequestType, ResponseType, Meta, TransportError, init_debug_logger, make_log_id
from idl.types import initialize, Record
from idl.types.initialization import ValidationError

PROTOCOL_NAME = "http_file"
FILENAME_FIELD = "filename"

logger = logging.getLogger('idl.connection.http_file')
init_debug_logger(logger)


class HttpFileClient(Client):
    @classmethod
    def create(cls, settings: TransportSettings, kwargs: dict = None) -> 'HttpFileClient':
        if settings.name != cls.name():
            raise ValueError(
                "Provided settings is not supported by this transport. "
                f"You should pass them to a client type with {settings.name!r} name."
            )
        params = json.loads(settings.params)
        return cls(uri=params["uri"])

    @classmethod
    def name(cls) -> str:
        return PROTOCOL_NAME

    def params(self) -> dict:
        return {
            "uri": self.uri
        }

    @classmethod
    def get_settings(cls, params: dict, meta: dict) -> TransportSettings:
        return get_settings(params, meta)

    @classmethod
    def get_meta_choices(cls) -> Iterable[Meta]:
        return []

    def __init__(self, uri: str):
        self.uri = uri.rstrip("/")
        self._session: Optional[ClientSession] = None
        self._closed: Event = Event()

    @property
    def session(self):
        if not self._session:
            self._session = ClientSession()
        return self._session

    @property
    def closed(self) -> Event:
        return self._closed

    async def call(self, interface: InterfaceName, method: MethodName, request: dict,
                   request_type: Type[RequestType], return_type: Type[ResponseType]) -> ResponseType:
        request = initialize(request, request_type)
        marshaller = Marshaller(serializer=None)
        files = marshaller.introspect(request, type(request))
        if len(files) > 1:
            raise NotImplementedError("Multiple files are not supported.")
        elif len(files) == 1:
            data = files[0].get()
        else:
            data = None

        query = urllib.parse.urlencode(request, doseq=True)
        url = f"{self.uri}/{interface}/{method}/?{query}"
        logger.debug(f'> {make_log_id(request)}: url={url}')
        response = await self.session.post(url, data=data)
        if response.status >= 400:
            logger.debug(f'< {make_log_id(request)}: Error={response.status}')
            raise TransportError(f"Error {response.status}.")

        result = {}
        for header, value in response.headers.items():
            if header.startswith("Http-File-"):
                key = header[len("Http-File-"):]
                result[key.lower()] = json.loads(value)

        logger.debug(f'< {make_log_id(request)}: {result}')

        files = marshaller.introspect(result, return_type)
        if len(files) > 1:
            raise NotImplementedError("Multiple files are not supported.")
        elif len(files) == 1:
            file = files[0]
            result[file.name] = response.content.iter_chunked(1024)

        result = initialize(result, return_type)
        return result

    async def call_many(self, interface: InterfaceName, method: MethodName, request: dict,
                        request_type: Type[RequestType], return_type: Type[ResponseType]) -> AsyncIterator[ResponseType]:
        raise NotImplementedError("Multiple responses are not supported.")

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None
        self._closed.set()


class HttpFileServer(Server):
    @classmethod
    def name(cls) -> str:
        return PROTOCOL_NAME

    @classmethod
    def get_settings(cls, params: dict, meta: dict) -> TransportSettings:
        return get_settings(params, meta)

    def __init__(self, host: str, port: int, *, ssl_context: ssl.SSLContext = None):
        scheme = "https" if ssl_context else "http"
        self.uri = f"{scheme}://{host}:{port}"

        self.ssl_context = ssl_context
        self.site: Optional[TCPSite] = None

    @property
    def cors_headers(self):
        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }

    def params(self) -> dict:
        return {
            "uri": self.uri,
        }

    def meta(self) -> dict:
        return {}

    async def start(self, dispatcher: Dispatcher):
        app = Application()
        app.router.add_options("/{path:.*}", self._preflight)
        app.router.add_post("/{path:.*}", partial(self._handler, dispatcher=dispatcher))
        app.router.add_get("/{path:.*}", partial(self._handler, dispatcher=dispatcher))
        runner = AppRunner(app)
        await runner.setup()

        uri = urllib.parse.urlparse(self.uri)

        ssl_context = self.ssl_context
        if ssl_context is None:
            ssl_context = ssl.create_default_context() if uri.scheme == "https" else None

        self.site = TCPSite(runner, uri.hostname, uri.port, ssl_context=ssl_context)
        await self.site.start()

    async def stop(self):
        if self.site:
            await self.site.stop()

    async def _preflight(self, request: _Request) -> _Response:
        return _Response(headers=self.cors_headers)

    async def _handler(self, request: _Request, dispatcher: Dispatcher) -> _Response:
        try:
            interface, method, *_ = request.match_info["path"].split("/")
        except ValueError:
            return _Response(status=400, text="Invalid path for service method. "
                                              "Path should contain interface name and method.")

        try:
            call = dispatcher.get_call(interface, method, {})
        except DispatcherError as err:
            return _Response(status=400, text=str(err))

        if call.returns_many:
            raise NotImplementedError("Multiple responses are not supported.")

        params = parse_qs(request.query_string, call.args_type)
        logger.debug(f'< {make_log_id(request)}: {params}')
        marshaller = Marshaller(serializer=None)
        files = marshaller.introspect(params, call.args_type)
        if len(files) > 1:
            raise NotImplementedError("Multiple files are not supported.")
        elif len(files) == 1:
            file = files[0]
            params[file.name] = request.content.iter_chunked(1024)

        try:
            params = initialize(params, call.args_type, force_validation=True)
        except ValidationError as err:
            return _Response(status=400, text=str(err))

        result = await call(params)
        result = initialize(result, call.return_type)

        headers = self.cors_headers
        files = marshaller.introspect(result, call.return_type)
        if len(files) > 1:
            raise NotImplementedError("Multiple files are not supported.")
        elif len(files) == 1:
            file = files[0]
        else:
            file = None

        logger.debug(f'> {make_log_id(request)}: {result}')
        for key, value in result.items():
            if file is None or file.name != key:
                headers[f"Http-File-{key.title()}"] = json.dumps(value)

        if FILENAME_FIELD in result:
            headers["Content-Disposition"] = f'attachment; filename="{result.filename}"'

        response = StreamResponse(headers=headers)
        await response.prepare(request=request)

        if file:
            chunks = file.get()
            if chunks is not None:
                async for chunk in chunks:
                    await response.write(chunk)

        await response.write_eof()
        return response


def get_settings(params: dict, meta: dict) -> TransportSettings:
    return TransportSettings(
        name=PROTOCOL_NAME,
        params=json.dumps({"uri": params["uri"]}),
        meta={}
    )


def parse_qs(qs: str, args_type: Type[Record]) -> dict:
    data = urllib.parse.parse_qs(qs)
    params = {}
    for key, value in data.items():
        field = args_type.__fields__.get(key)
        if not field:
            continue

        try:
            if sys.version_info[:2] >= (3, 7):
                origin = field.__origin__
            else:
                origin = field.__extra__
        except AttributeError:
            origin = None

        try:
            if issubclass(origin, list):
                params[key] = value
            else:
                params[key] = value.pop()
        except TypeError:
            params[key] = value.pop()
    return params
