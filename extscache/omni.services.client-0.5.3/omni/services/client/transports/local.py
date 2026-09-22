# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from enum import Enum
import json
from urllib.parse import ParseResult, urlencode
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from starlette.types import Message

from omni.services.transport.client.base.consumer import BaseConsumer, BaseStandin
from omni.services.transport.client.base.exceptions import ServiceNotFoundError


class Match(Enum):
    NONE = 0
    PARTIAL = 1
    FULL = 2


class Transport(BaseConsumer):
    """Transport for the `local://` scheme."""

    def __init__(
        self,
        parsed_uri: ParseResult,
        app: Optional[FastAPI],
        version: Optional[Any],
        persist_connections: bool = False,
        raise_for_status: bool = True,
    ):
        """
        Constructor.

        Args:
            parsed_uri (ParseResult): Parsed URI of the server.
            app (Optional[FastAPI]): Reference to the application running on the server.
            version (Optional[Any]): Version of the application running on the server.
            persist_connections (bool): Flag indicating whether to persist connections to the server.
            raise_for_status (bool): Flag indicating whether to raise exceptions for errors.

        Returns:
            None

        """
        if app is None:
            try:
                from omni.services.core import main
                app = main.get_app()
            except ImportError:
                raise Exception(
                    "The local transport needs a FastAPI app to function. Either pass it through in the constructor or make sure the omni.services.core extension is enabled"
                )

        self._base_uri = parsed_uri.path
        super().__init__(parsed_uri, app, version, persist_connections=persist_connections, raise_for_status=raise_for_status)

    def __getattr__(self, name: str):
        return BaseStandin(name, self)

    def _create_full_uri(self, uri: str) -> str:
        """
        Create the full URI of the call based on the nomenclature used by the Client.

        Args:
            uri (str): URI of the server endpoint to call.

        Returns:
            str: The full URI of the call to the server.

        """
        full_uri = "/".join((self._base_uri, uri))
        return full_uri.replace("_", "-")

    async def __call__(
        self,
        uri: str,
        *args,
        __method__: Optional[str] = None,
        __headers__: Optional[Dict[str, str]] = None,
        __raw__: bool = False,
        **kwargs
    ):
        """
        Perform a call to the server endpoint identified by the Client's attribute nomenclature.

        Args:
            uri (str): URI of the server to connect to.
            __method__ (Optional[str]): Method to use to perform the call.
            __headers__ (Optional[Dict[str, str]]): Headers to send along with the request.
            __raw__ (bool): Flag indicating whether the request should be sent in raw mode.

        Returns:
            Any: The response emitted by the server after processing the given request.

        """
        candidates = self._app.routes
        uri = self._create_full_uri(uri)

        if args:
            path_args = "/".join([str(arg) for arg in args])
            uri = "/".join((uri, path_args))

        async def _receive():
            return {"type": "http.request", "body": bytes(json.dumps(kwargs), "ascii")}

        headers = __headers__ or {}
        encoded_headers = []
        for header, value in headers.items():
            encoded_headers.append((header.lower().encode("ascii"), value.encode("ascii")))

        scope = {"type": "http", "path": uri, "query_string": "", "headers": encoded_headers}

        for route in candidates:
            if not hasattr(route, "methods"):
                # No methods available so not a path we'd want to call
                continue

            scope["method"] = __method__.upper() if __method__ else self._get_route_method(route.methods)
            match, child_scope = route.matches(scope)
            if match.value != Match.FULL.value:
                continue

            if scope["method"] == "GET":
                scope["query_string"] = urlencode(kwargs, doseq=True)

            scope.update(child_scope)

            await route.handle(scope, _receive, self._send)
            return self._result
        else:
            raise ServiceNotFoundError(
                f"{uri} cannot be found. Make sure the URL is correct and the correct arguments are provided."
            )

    def _get_route_method(self, route_methods: List[str]) -> Optional[str]:
        """
        Return the method to use to perform a request, from the given candidate route methods.

        Args:
            route_method (List[str]): List of methods supported by the candidate route.

        Returns:
            Optional[str]: The method to use to perform a request to the route supporting the given methods.

        """
        methods = ["POST", "GET", "UPDATE", "DELETE", "PATCH"]
        for method in methods:
            if method in route_methods:
                return method

    async def _send(self, data: Message) -> None:
        if data["type"] == "http.response.body":
            try:
                self._result = json.loads(data["body"])
            except Exception:
                self._result = data["body"]
