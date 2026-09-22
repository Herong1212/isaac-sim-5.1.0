import argparse
import asyncio
import importlib
import os
from typing import List

from idl.connection.marshallers import Marshaller
from idl.connection.transport import Dispatcher, Server
from idl.connection.transport.ws import WebSocketServer
from idl.data.serializers import Serializer
from idl.data.serializers.json import JSONSerializer
from idl.service import Service


async def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("interfaces", metavar="INTERFACES", type=str, nargs="+",
                        help="List of interface names and paths each as <name>:<module_path>. "
                             "Multiple interfaces should be separated by whitespace.")
    parser.add_argument("-s", "--serializer", type=str, choices=["json"], default="json", dest="serializer_name",
                        help="Serializer for the service marshaller. Available options: json.")
    parser.add_argument("-t", "--transport", type=str, choices=["ws"], default="ws", dest="transport_name",
                        help="Transport to use for the service. Available options: ws.")
    args = parser.parse_args()

    service = Service()
    service.dispatcher = Dispatcher()
    service.transport = create_transport(args.transport_name, create_serializer(args.serializer_name))
    print("Transport:", service.transport.name())
    print("  ", service.transport.params())

    interfaces = create_interfaces(args.interfaces)
    print("Interfaces:")
    for interface in interfaces:
        print("  ", interface.__interface_name__)

        methods = ", ".join((method_name for method_name, *args in interface.__interface_methods__))
        print("     ", methods)

    print("Running the service...")
    await service.run(interfaces)


def create_serializer(name: str) -> Serializer:
    name = name.lower()
    if name == "json":
        return JSONSerializer()
    raise ValueError(f"Unknown serializer {name}.")


def create_transport(name: str, serializer: Serializer) -> Server:
    name = name.lower()
    if name == "ws":
        host = os.environ.get("WS_HOST", "0.0.0.0")
        port = int(os.environ.get("WS_PORT", 8095))
        return WebSocketServer(host=host, port=port, marshaller=Marshaller(serializer))
    raise ValueError(f"Unknown transport {name}.")


def create_interfaces(interface_args: List[str]) -> list:
    interfaces = []

    for arg in interface_args:
        try:
            name, module = arg.split(":")
        except ValueError:
            raise ValueError(f"Interface arg should be in format <name>:<module_path>. Got {arg} instead.")

        interface_module = importlib.import_module(module)
        interface = getattr(interface_module, name)
        interfaces.append(interface())
    return interfaces


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
