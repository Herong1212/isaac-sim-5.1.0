# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from functools import wraps
import omni.ext
import asyncio
import omni.client
from omni.kit.async_engine import run_coroutine

def singleton(class_):
    """A singleton decorator"""
    instances = {}

    @wraps(class_)
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class ServiceDiscovery():
    def __init__(self):
        self._nucleus_services = {}
        self._connection_status_sub = omni.client.register_connection_status_callback(self._server_status_changed)

    def destory(self):
        self._connection_status_sub = None
        self._nucleus_services.clear()

    def _server_status_changed(self, url: str, status: omni.client.ConnectionStatus) -> None:
        """Collect signed in server's service information based upon server status changed."""
        if status == omni.client.ConnectionStatus.CONNECTED:
            # must run on main thread as this one does not have async loop...
            run_coroutine(self.get_nucleus_services_async(url))

    def _extract_server_from_url(self, url):
        client_url = omni.client.break_url(url)
        server_url = omni.client.make_url(scheme=client_url.scheme, host=client_url.host, port=client_url.port)
        return server_url

    def is_service_supported_for_nucleus(self, nucleus_url: str, service_name: str):
        if not nucleus_url:
            return False

        nucleus_url = self._extract_server_from_url(nucleus_url)
        if nucleus_url not in self._nucleus_services:
            self.get_nucleus_services(nucleus_url)
        if nucleus_url in self._nucleus_services:
            server_services =self._nucleus_services[nucleus_url]
            for service in server_services:
                if service.service_interface.name.startswith(service_name):
                    return True
        else:
            scheme=omni.client.break_url(nucleus_url).scheme
            # This is to ensure forward compatibility, otherwise some extension out of kit repo tests will fail
            # such as omni.kit.widget.extended_searchfield
            if scheme and scheme.startswith("omniverse"):
                return True
        return False

    def get_nucleus_services(self, nucleus_url: str):
        if not nucleus_url:
            return None
        nucleus_url = self._extract_server_from_url(nucleus_url)
        if nucleus_url in self._nucleus_services:
            return self._nucleus_services[nucleus_url]
        asyncio.ensure_future(self.get_nucleus_services_async(nucleus_url))
        return None

    async def get_nucleus_services_async(self, nucleus_url: str):
        try:
            from idl.connection.transport.ws import WebSocketClient
            from omni.discovery.client import DiscoverySearch

            if not nucleus_url:
                return None
            nucleus_url = self._extract_server_from_url(nucleus_url)
            if nucleus_url in self._nucleus_services:
                return self._nucleus_services[nucleus_url]
            nucleus_services = []
            client_url = omni.client.break_url(nucleus_url)
            transport = WebSocketClient(uri=f"ws://{client_url.host}:3333")
            discovery = DiscoverySearch(transport)
            async with discovery:
                async for service in discovery.find_all():
                    nucleus_services.append(service)
            self._nucleus_services[nucleus_url] = nucleus_services
            return self._nucleus_services[nucleus_url]
        except:
            return None
