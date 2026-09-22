from __future__ import annotations
import omni.sensors.net._net
import typing
import omni.core._core

__all__ = [
    "Endpoint",
    "EndpointType",
    "IChannel",
    "IConnectionConsumer",
    "INetworkBackend",
    "INetworkFactory",
    "IP4Endpoint",
    "IReceptionConsumer",
    "IServer"
]


class Endpoint():
    def __init__(self, egress_timestamp: int, type: EndpointType) -> None: ...
    @property
    def can(self) -> int:
        """
        :type: int
        """
    @can.setter
    def can(self, arg0: int) -> None:
        pass
    @property
    def egress_timestamp(self) -> int:
        """
        :type: int
        """
    @egress_timestamp.setter
    def egress_timestamp(self, arg0: int) -> None:
        pass
    @property
    def ip(self) -> IP4Endpoint:
        """
        :type: IP4Endpoint
        """
    @ip.setter
    def ip(self, arg0: IP4Endpoint) -> None:
        pass
    @property
    def type(self) -> EndpointType:
        """
        :type: EndpointType
        """
    @type.setter
    def type(self, arg0: EndpointType) -> None:
        pass
    pass
class EndpointType():
    """
    Members:

      E_NONE

      E_CUSTOM : A custom endpoint, each protocol defines what this means.

      E_CAN : A CAN endpoint.

      E_IP : An IPv4 address

      E_REALM : A realm endpoint
    """
    def __eq__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: object) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def value(self) -> int:
        """
        :type: int
        """
    E_CAN: omni.sensors.net._net.EndpointType # value = <EndpointType.E_CAN: 2>
    E_CUSTOM: omni.sensors.net._net.EndpointType # value = <EndpointType.E_CUSTOM: 1>
    E_IP: omni.sensors.net._net.EndpointType # value = <EndpointType.E_IP: 3>
    E_NONE: omni.sensors.net._net.EndpointType # value = <EndpointType.E_NONE: 0>
    E_REALM: omni.sensors.net._net.EndpointType # value = <EndpointType.E_REALM: 4>
    __members__: dict # value = {'E_NONE': <EndpointType.E_NONE: 0>, 'E_CUSTOM': <EndpointType.E_CUSTOM: 1>, 'E_CAN': <EndpointType.E_CAN: 2>, 'E_IP': <EndpointType.E_IP: 3>, 'E_REALM': <EndpointType.E_REALM: 4>}
    pass
class IChannel(_IChannel, omni.core._core.IObject):
    """
    Channel interface for sending/receiving data over different kinds of networks

    @note Create a channel according to a description using the network factory. See @ref INetworkFactory
    """
    def __enter__(self) -> IChannel: ...
    def __exit__(self, arg0: object, arg1: object, arg2: object) -> None: ...
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def add_reception_consumer(self, arg0: typing.Callable[[bytes, Endpoint], None]) -> IReceptionConsumer: ...
    def remove_reception_consumer(self, consumer: IReceptionConsumer) -> None: 
        """
        Unregister a previously registered consumer
        @param consumer The previously registered consumer on this channel
        """
    @typing.overload
    def send(self, arg0: bytes, arg1: Endpoint) -> bool: ...
    @typing.overload
    def send(self, arg0: bytes) -> bool: ...
    @property
    def connected(self) -> bool:
        """
        :type: bool
        """
    pass
class IConnectionConsumer(_IConnectionConsumer, omni.core._core.IObject):
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def on_connect(self, arg0: IChannel, arg1: Endpoint) -> None: ...
    pass
class INetworkBackend(_INetworkBackend, omni.core._core.IObject):
    """
    An interface to a network backend that provides channel-based networking

    @note used by the INetworkFactory to create channels supported by that backend
    """
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    pass
class INetworkFactory(_INetworkFactory, omni.core._core.IObject):
    def __enter__(self) -> INetworkFactory: ...
    def __exit__(self, arg0: object, arg1: object, arg2: object) -> None: ...
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def make_channel(self, arg0: dict) -> IChannel: ...
    def make_server(self, arg0: dict) -> IServer: ...
    pass
class IP4Endpoint():
    def __init__(self, port: int) -> None: ...
    @property
    def port(self) -> int:
        """
        :type: int
        """
    @port.setter
    def port(self, arg0: int) -> None:
        pass
    pass
class IReceptionConsumer(_IReceptionConsumer, omni.core._core.IObject):
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    pass
class IServer(_IServer, omni.core._core.IObject):
    """
    Server interface for connection-based channels (eg. TCP and WebSocket servers)

    @note Create a server according to a description using the network factory. See @ref INetworkFactory
    """
    def __enter__(self) -> IServer: ...
    def __exit__(self, arg0: object, arg1: object, arg2: object) -> None: ...
    @typing.overload
    def __init__(self, arg0: omni.core._core.IObject) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    @staticmethod
    def add_connection_consumer(*args, **kwargs) -> typing.Any: 
        """
        Register a consumer that will be called when a new client connects to the server
        @param consumer The consumer class to be used when making a callback. See @ref IChannel::IReceptionConsumer
        """
    @staticmethod
    def remove_connection_consumer(*args, **kwargs) -> typing.Any: 
        """
        Unregisters a previously registered handler
        @param id handler id of a handler previously registered on this server
        """
    pass
class _IChannel(omni.core._core.IObject):
    pass
class _IConnectionConsumer(omni.core._core.IObject):
    pass
class _INetworkBackend(omni.core._core.IObject):
    pass
class _INetworkFactory(omni.core._core.IObject):
    pass
class _IReceptionConsumer(omni.core._core.IObject):
    pass
class _IServer(omni.core._core.IObject):
    pass
