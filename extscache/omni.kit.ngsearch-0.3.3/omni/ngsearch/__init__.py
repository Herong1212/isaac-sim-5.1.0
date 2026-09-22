# Copyright (c) 2020-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# standard modules
import asyncio
import base64
import io
import json
import pickle
import zlib
from contextlib import asynccontextmanager
from multiprocessing import Queue
from queue import Empty
from typing import Any, Dict, List

# local / proprietary modules
from idl.connection.marshallers import Marshaller
from idl.connection.transport.ws import WebSocketClient
from idl.data.serializers.json import JSONSerializer

try:
    from omni.discovery import DiscoverySearch
except ImportError:
    DiscoverySearch = None

from .client import NGSearchService, Search


def decompress_embedding(input: str) -> list:
    # return json.loads(zlib.decompress(input.encode('latin1')).decode())
    return json.loads(input)


class NGSearchClient:
    @staticmethod
    async def get_service(host: str = "localhost", port: int = 3503) -> NGSearchService:
        """Client that connects to the DeepTag service.

        Args:
            str host: IP where the service is running
            int port: port, here the service is available
        """
        marshaller = Marshaller(JSONSerializer())
        transport = WebSocketClient(f"ws://{host}:{port}", marshaller=marshaller)
        await transport.prepare()

        return NGSearchService(transport)

    @staticmethod
    @asynccontextmanager
    async def get_service_context(host: str = "localhost", port: int = 3503) -> NGSearchService:
        """A context manager yielding client that connects to the DeepTag service.

        Args:
            str host: IP where the service is running
            int port: port, here the service is available
        """
        marshaller = Marshaller(JSONSerializer())
        transport = WebSocketClient(f"ws://{host}:{port}", marshaller=marshaller)
        async with transport as prepared_transport:
            yield NGSearchService(prepared_transport)

    @staticmethod
    async def discover_service(server: str, **kwargs) -> NGSearchService:
        if DiscoverySearch is None:
            raise RuntimeError("omni.discovery package not found; service discovery not possible")
        async with DiscoverySearch(server) as discovery:
            service: NGSearchService = await discovery.find(NGSearchService, **kwargs)
        return service

    @staticmethod
    async def connect(server: str = None, host: str = None, port: int = None, **kwargs) -> NGSearchService:
        """Connect to server using either server name or host and port.

        Args:
            server (str, optional): omniverse service where service can be discovered. Defaults to None.
            host (str, optional): host of the service. Defaults to None.
            port (int, optional): port of ther service. Defaults to None.

        Returns:
            NGSearchService: deepsearch client
        """
        if server is None:
            assert host is not None
            assert port is not None

            return await NGSearchClient.get_service(host, port)
        else:
            return await NGSearchClient.discover_service(server, **kwargs)


class SearchClient:
    @staticmethod
    async def get_service(host: str = "localhost", port: int = 3503) -> Search:
        """Client that connects to the DeepTag service.

        Args:
            str host: IP where the service is running
            int port: port, here the service is available
        """
        marshaller = Marshaller(JSONSerializer())
        transport = WebSocketClient(f"ws://{host}:{port}", marshaller=marshaller)
        await transport.prepare()

        return Search(transport)

    @staticmethod
    async def discover_service(server: str, **kwargs) -> Search:
        if DiscoverySearch is None:
            raise RuntimeError("omni.discovery package not found; service discovery not possible")
        async with DiscoverySearch(server) as discovery:
            service: Search = await discovery.find(Search, **kwargs)
        return service

    @staticmethod
    async def connect(server: str = None, host: str = None, port: int = None) -> Search:
        """Connect to server using either server name or host and port.

        Args:
            server (str, optional): omniverse service where service can be discovered. Defaults to None.
            host (str, optional): host of the service. Defaults to None.
            port (int, optional): port of ther service. Defaults to None.

        Returns:
            NGSearchService: deepsearch client
        """
        if server is None:
            assert host is not None
            assert port is not None

            return await SearchClient.get_service(host, port)
        else:
            return await SearchClient.discover_service(server)


async def queue_listener(in_q: Queue, out_q: Queue, server: str = None, host: str = None, port: int = None):
    """Listener that starts an infinite loop and sends commands from the queue to the DeepSearchClient

    Args:
        in_q (Queue): queue for input commands
        out_q (Queue): queue for output commands
        server (str, optional): omniverse server where service can be discovered. Defaults to ``None``.
        host (str, optional): alternatively you can provide direct link to service host. Defaults to ``None``.
        port (int, optional): and service port. Defaults to ``None``.

    Raises:
        NotImplementedError: raises when unknown command is passed
    """
    while True:
        try:
            client = await NGSearchClient.connect(server=server, host=host, port=port)
            while True:
                try:
                    data = in_q.get_nowait()
                    if data["command"] == "search":
                        response = await client.search(**data["payload"])
                    elif data["command"] == "datasource_info":
                        response = await client.datasource_info()
                    elif data["command"] == "recreate":
                        print("recreate client")
                        break
                    else:
                        raise NotImplementedError("only search functionality is supported for now")
                    out_q.put(response)
                except Empty:
                    await asyncio.sleep(0.1)

        except Exception as e:
            print(str(e))
            await asyncio.sleep(0.1)


def queue_runner(in_q: Queue, out_q: Queue, server: str = None, host: str = None, port: int = None):
    """Runner function that set-up the queue listener.

    Args:
        in_q (Queue): queue for input commands
        out_q (Queue): queue for output commands
        server (str, optional): omniverse server where service can be discovered. Defaults to ``None``.
        host (str, optional): alternatively you can provide direct link to service host. Defaults to ``None``.
        port (int, optional): and service port. Defaults to ``None``.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(queue_listener(in_q, out_q, server, host, port))


def any_to_string(input: Any) -> str:
    """Encode any data to string

    Args:
        input (Any): any data

    Returns:
        str: encoded string
    """
    return pickle.dumps(input).decode("latin1")


def any_from_string(input: str) -> Any:
    """Deserialize data from string using pickle.

    Args:
        input (str): input string

    Returns:
        Any: data decoded from string
    """
    return pickle.loads(input.encode("latin1"))


def image_to_base64(input, format: str = "JPEG") -> str:
    """Covert image to base64 format

    Args:
        input: PIL image type

    Returns:
        str: base64 encoding of an image
    """
    with io.BytesIO() as output:
        input.convert("RGB").save(output, format=format)
        content = base64.b64encode(output.getvalue()).decode("ascii")
    return content
