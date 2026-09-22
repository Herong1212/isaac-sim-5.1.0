import asyncio
import json
from asyncio.locks import Event
from collections import defaultdict
from typing import Type, AsyncIterator, Dict, Iterable

from idl.connection.transport import (
    Client, InterfaceName, MethodName, Server, Dispatcher, TransportSettings, Meta,
    RequestType, ResponseType, Request
)
from idl.types import initialize


PROTOCOL_NAME = "memory"


class MemoryClient(Client):
    @classmethod
    def name(cls) -> str:
        return PROTOCOL_NAME

    @classmethod
    def get_settings(cls, params: dict, meta: dict) -> TransportSettings:
        return get_settings(params, meta)

    @classmethod
    def get_meta_choices(cls) -> Iterable[Meta]:
        pass

    @classmethod
    def create(cls, settings: TransportSettings, kwargs: dict = None) -> 'MemoryClient':
        if settings.name != cls.name():
            raise ValueError(
                "Provided settings is not supported by this transport. "
                f"You should pass them to a client type with {settings.name!r} name."
            )

        params = json.loads(settings.params)
        return cls(channel=params["channel"])

    def __init__(self, channel: str = "__all__"):
        self._channel = channel
        self._closed = Event()

    @property
    def closed(self) -> Event:
        return self._closed

    def params(self) -> dict:
        return {
            "channel": self._channel
        }

    async def close(self):
        self._closed.set()

    async def call(self, interface: InterfaceName, method: MethodName, request: dict, request_type: Type[RequestType], return_type: Type[ResponseType]) -> ResponseType:
        request = initialize(request, request_type)
        requests = channels[self._channel]
        req = MemoryRequest(interface, method, request)
        await requests.put(req)
        result = await req.result
        return initialize(result, return_type)

    async def call_many(self, interface: InterfaceName, method: MethodName, request: dict, request_type: Type[RequestType], return_type: Type[ResponseType]) -> AsyncIterator[ResponseType]:
        request = initialize(request, request_type)
        requests = channels[self._channel]
        req = MemoryRequest(interface, method, request)
        await requests.put(req)
        aiter_result = await req.result
        async for item in aiter_result:
            yield initialize(item, return_type)


class MemoryServer(Server):
    @classmethod
    def name(cls) -> str:
        return PROTOCOL_NAME

    @classmethod
    def get_settings(cls, params: dict, meta: dict) -> TransportSettings:
        return get_settings(params, meta)

    def __init__(self, channel: str = "__all__"):
        self._channel = channel
        self._tasks = []

    def params(self) -> dict:
        return {
            "channel": self._channel
        }

    def meta(self) -> dict:
        return {}

    async def start(self, dispatcher: Dispatcher):
        loop = asyncio.get_event_loop()
        self._tasks.append(loop.create_task(self._listen(dispatcher)))

    async def stop(self):
        for task in self._tasks:
            task.cancel()
        channels.clear()

    async def _listen(self, dispatcher: Dispatcher):
        running = True
        try:
            requests = channels[self._channel]
            while running:
                request: MemoryRequest = await requests.get()
                try:
                    call = dispatcher.get_call(request.interface, request.method, request.params)
                    params = initialize(request.params, call.args_type, force_validation=True)

                    Request.set(request)
                    if call.returns_many:
                        async def aiter_result():
                            async for item in call(params):
                                yield item
                        request.result.set_result(aiter_result())
                    else:
                        response = await call(params)
                        request.result.set_result(response)
                except Exception as e:
                    request.result.set_exception(e)
        except asyncio.CancelledError:
            pass


class MemoryRequest(Request):
    result: asyncio.Future

    def __init__(self, interface: InterfaceName, method: MethodName, params: dict):
        super().__init__(interface, method, params)
        self.result = asyncio.Future()


channels: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)


def get_settings(params: dict, meta: dict) -> TransportSettings:
    return TransportSettings(
        name=PROTOCOL_NAME,
        params=json.dumps({"channel": params["channel"]}),
        meta={}
    )
