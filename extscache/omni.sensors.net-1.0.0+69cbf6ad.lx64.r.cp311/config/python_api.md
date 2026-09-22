# Public API for module omni.sensors.net:

## Classes

- class Endpoint
  - def __init__(self, egress_timestamp: int, type: EndpointType)
  - [property] def can(self) -> int
  - [can.setter] def can(self, arg0: int)
  - [property] def egress_timestamp(self) -> int
  - [egress_timestamp.setter] def egress_timestamp(self, arg0: int)
  - [property] def ip(self) -> IP4Endpoint
  - [ip.setter] def ip(self, arg0: IP4Endpoint)
  - [property] def type(self) -> EndpointType
  - [type.setter] def type(self, arg0: EndpointType)

- class EndpointType
  - def __init__(self, value: int)
  - [property] def name(self) -> str
  - [property] def value(self) -> int
  - E_CAN: omni.sensors.net._net.EndpointType
  - E_CUSTOM: omni.sensors.net._net.EndpointType
  - E_IP: omni.sensors.net._net.EndpointType
  - E_NONE: omni.sensors.net._net.EndpointType
  - E_REALM: omni.sensors.net._net.EndpointType

- class IChannel(_IChannel, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - def add_reception_consumer(self, arg0: typing.Callable[[bytes, Endpoint], None]) -> IReceptionConsumer
  - def remove_reception_consumer(self, consumer: IReceptionConsumer)
  - def send(self, arg0: bytes, arg1: Endpoint) -> bool
  - def send(self, arg0: bytes) -> bool
  - [property] def connected(self) -> bool

- class IConnectionConsumer(_IConnectionConsumer, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - def on_connect(self, arg0: IChannel, arg1: Endpoint)

- class INetworkBackend(_INetworkBackend, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - [property] def name(self) -> str

- class INetworkFactory(_INetworkFactory, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - def make_channel(self, arg0: dict) -> IChannel
  - def make_server(self, arg0: dict) -> IServer

- class IP4Endpoint
  - def __init__(self, port: int)
  - [property] def port(self) -> int
  - [port.setter] def port(self, arg0: int)

- class IReceptionConsumer(_IReceptionConsumer, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)

- class IServer(_IServer, omni.core._core.IObject)
  - def __init__(self, arg0: omni.core._core.IObject)
  - def __init__(self)
  - static def add_connection_consumer(*args, **kwargs) -> typing.Any
  - static def remove_connection_consumer(*args, **kwargs) -> typing.Any

## Other

- omni.core: public module
