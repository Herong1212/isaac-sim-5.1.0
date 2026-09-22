from typing import List, Optional, Dict, AsyncIterator
from idl.types import Enum, Record, Literal


Capabilities = Dict[str, int]
DiscoverySearchServerRemoteCapabilities = Capabilities
DiscoverySearchServerLocalCapabilities = {'find': 2, 'find_all': 2}
DiscoverySearchServerCapabilities = DiscoverySearchServerRemoteCapabilities
DiscoverySearchClientRemoteCapabilities = Capabilities
DiscoverySearchClientLocalCapabilities = {'find': 2, 'find_all': 2}
DiscoverySearchClientCapabilities = DiscoverySearchClientLocalCapabilities
DiscoverySearchFindAllServerRemoteVersion = int
DiscoverySearchFindAllServerLocalVersion = 2
DiscoverySearchFindAllServerVersion = DiscoverySearchFindAllServerRemoteVersion
DiscoverySearchFindAllClientRemoteVersion = int
DiscoverySearchFindAllClientLocalVersion = 2
DiscoverySearchFindServerRemoteVersion = int
DiscoverySearchFindServerLocalVersion = 2
DiscoverySearchFindServerVersion = DiscoverySearchFindServerRemoteVersion
DiscoverySearchFindClientRemoteVersion = int
DiscoverySearchFindClientLocalVersion = 2
DiscoveryRegistrationServerRemoteCapabilities = Capabilities
DiscoveryRegistrationServerLocalCapabilities = {'register': 2, 'register_unsafe': 2, 'unregister_unsafe': 2}
DiscoveryRegistrationServerCapabilities = DiscoveryRegistrationServerRemoteCapabilities
DiscoveryRegistrationClientRemoteCapabilities = Capabilities
DiscoveryRegistrationClientLocalCapabilities = {'register': 2, 'register_unsafe': 2, 'unregister_unsafe': 2}
DiscoveryRegistrationClientCapabilities = DiscoveryRegistrationClientLocalCapabilities
DiscoveryRegistrationUnregisterUnsafeServerRemoteVersion = int
DiscoveryRegistrationUnregisterUnsafeServerLocalVersion = 2
DiscoveryRegistrationUnregisterUnsafeServerVersion = DiscoveryRegistrationUnregisterUnsafeServerRemoteVersion
DiscoveryRegistrationUnregisterUnsafeClientRemoteVersion = int
DiscoveryRegistrationUnregisterUnsafeClientLocalVersion = 2
DiscoveryRegistrationRegisterUnsafeServerRemoteVersion = int
DiscoveryRegistrationRegisterUnsafeServerLocalVersion = 2
DiscoveryRegistrationRegisterUnsafeServerVersion = DiscoveryRegistrationRegisterUnsafeServerRemoteVersion
DiscoveryRegistrationRegisterUnsafeClientRemoteVersion = int
DiscoveryRegistrationRegisterUnsafeClientLocalVersion = 2
DiscoveryRegistrationRegisterServerRemoteVersion = int
DiscoveryRegistrationRegisterServerLocalVersion = 2
DiscoveryRegistrationRegisterServerVersion = DiscoveryRegistrationRegisterServerRemoteVersion
DiscoveryRegistrationRegisterClientRemoteVersion = int
DiscoveryRegistrationRegisterClientLocalVersion = 2


Meta = Dict[str, str]


class HealthStatus(metaclass=Enum):
    OK = "OK"
    Closed = "CLOSED"
    Denied = "DENIED"
    AlreadyExists = "ALREADY_EXISTS"
    InvalidSettings = "INVALID_SETTINGS"
    InvalidCapabilities = "INVALID_CAPABILITIES"


class ServiceInterface(Record):
    origin: str
    name: str
    capabilities: Optional[Capabilities]


class TransportSettings(Record):
    name: str
    params: str
    meta: Meta


ServiceInterfaceMap = Dict[str, ServiceInterface]


class SupportedTransport(Record):
    name: str
    meta: Optional[Meta]


class SearchResult(Record):
    found: bool
    version: Optional[int]
    service_interface: Optional[ServiceInterface]
    transport: Optional[TransportSettings]
    meta: Optional[Meta]


DiscoverySearchFindAllClientVersion = DiscoverySearchFindAllClientLocalVersion
DiscoverySearchFindClientVersion = DiscoverySearchFindClientLocalVersion


class DiscoverInterfaceQuery(Record):
    service_interface: ServiceInterface
    supported_transport: Optional[List[SupportedTransport]]
    meta: Optional[Meta]




class HealthCheck(Record):
    status: HealthStatus
    time: str
    version: Optional[int]
    message: Optional[str]
    meta: Optional[Meta]


DiscoveryRegistrationUnregisterUnsafeClientVersion = DiscoveryRegistrationUnregisterUnsafeClientLocalVersion


class Manifest(Record):
    interfaces: ServiceInterfaceMap
    transport: TransportSettings
    token: str
    meta: Optional[Meta]


DiscoveryRegistrationRegisterUnsafeClientVersion = DiscoveryRegistrationRegisterUnsafeClientLocalVersion
DiscoveryRegistrationRegisterClientVersion = DiscoveryRegistrationRegisterClientLocalVersion