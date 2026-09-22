from typing import AsyncIterator, Dict, List, Optional

from idl.connection.transport import Client
from idl.types import Literal, Record

from .data import *


class DiscoverySearch:
    def __init__(self, transport: Client):
        self.transport = transport

    async def __aenter__(self) -> 'DiscoverySearch':
        await self.transport.prepare()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.transport.close()
    
    async def find(self, query: DiscoverInterfaceQuery) -> SearchResult:
        """
        Finds an entry for specified origin and interface.
        A query can specify the required capabilities, connection settings and
        other metadata.
        """
        _request = {}
        _request["query"] = query
        _request["version"] = DiscoverySearchFindClientVersion
        _response = await self.transport.call("DiscoverySearch", "find", _request, request_type=DiscoverySearchFindArgs, return_type=SearchResult)
        return _response
    
    async def find_all(self, ) -> AsyncIterator[SearchResult]:
        """
        Retrieves all registered interfaces for this discovery service.
        """
        _request = {}
        _request["version"] = DiscoverySearchFindAllClientVersion
        agen = self.transport.call_many("DiscoverySearch", "find_all", _request, request_type=DiscoverySearchFindAllArgs, return_type=SearchResult)
        try:
            async for _response in agen:
                yield _response
        finally:
            await agen.aclose()
    
    __interface_name__ = "DiscoverySearch"
    __interface_origin__ = "Discovery.idl.ts"
    __interface_capabilities__ = DiscoverySearchClientLocalCapabilities
    

class DiscoveryRegistration:
    def __init__(self, transport: Client):
        self.transport = transport

    async def __aenter__(self) -> 'DiscoveryRegistration':
        await self.transport.prepare()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.transport.close()
    
    async def register(self, manifest: Manifest) -> AsyncIterator[HealthCheck]:
        """
        Registers a new service with specified connection settings and
        interfaces.
        The discovery keeps a subscription to ensure that registered service is
        still available.
        The service is removed from discovery as soon as it stops receiving
        health checks from the subscription.

        You can use `register_unsafe` to register a service without a
        subscription and health checks.
        """
        _request = {}
        _request["manifest"] = manifest
        _request["version"] = DiscoveryRegistrationRegisterClientVersion
        agen = self.transport.call_many("DiscoveryRegistration", "register", _request, request_type=DiscoveryRegistrationRegisterArgs, return_type=HealthCheck)
        try:
            async for _response in agen:
                yield _response
        finally:
            await agen.aclose()
    
    async def register_unsafe(self, manifest: Manifest) -> HealthCheck:
        """
        Registers a new service without a health checking.
        It's a service responsibility to call `unregister_unsafe` when the
        provided functions become not available.
        """
        _request = {}
        _request["manifest"] = manifest
        _request["version"] = DiscoveryRegistrationRegisterUnsafeClientVersion
        _response = await self.transport.call("DiscoveryRegistration", "register_unsafe", _request, request_type=DiscoveryRegistrationRegisterUnsafeArgs, return_type=HealthCheck)
        return _response
    
    async def unregister_unsafe(self, manifest: Manifest) -> HealthCheck:
        """
        Removes the service registered with `register_unsafe` from the
        discovery.
        """
        _request = {}
        _request["manifest"] = manifest
        _request["version"] = DiscoveryRegistrationUnregisterUnsafeClientVersion
        _response = await self.transport.call("DiscoveryRegistration", "unregister_unsafe", _request, request_type=DiscoveryRegistrationUnregisterUnsafeArgs, return_type=HealthCheck)
        return _response
    
    __interface_name__ = "DiscoveryRegistration"
    __interface_origin__ = "Discovery.idl.ts"
    __interface_capabilities__ = DiscoveryRegistrationClientLocalCapabilities


class DiscoverySearchFindArgs(Record):
    query: DiscoverInterfaceQuery
    version: Optional[Literal(DiscoverySearchFindClientVersion)] = DiscoverySearchFindClientVersion


class DiscoverySearchFindAllArgs(Record):
    version: Optional[Literal(DiscoverySearchFindAllClientVersion)] = DiscoverySearchFindAllClientVersion


class DiscoveryRegistrationRegisterArgs(Record):
    manifest: Manifest
    version: Optional[Literal(DiscoveryRegistrationRegisterClientVersion)] = DiscoveryRegistrationRegisterClientVersion


class DiscoveryRegistrationRegisterUnsafeArgs(Record):
    manifest: Manifest
    version: Optional[Literal(DiscoveryRegistrationRegisterUnsafeClientVersion)] = DiscoveryRegistrationRegisterUnsafeClientVersion


class DiscoveryRegistrationUnregisterUnsafeArgs(Record):
    manifest: Manifest
    version: Optional[Literal(DiscoveryRegistrationUnregisterUnsafeClientVersion)] = DiscoveryRegistrationUnregisterUnsafeClientVersion

