# Copyright (c) 2020-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

"""Tests for encoders of the Kit microservices framework."""

import json
import gzip
import typing
from unittest.mock import patch

import fastapi

import carb

from omni.services.core import main, routers, exceptions

from . import base


class EncodingTest(base.BaseServiceTest):

    def tearDown(self):
        # Remove temporary routes added for the purposes of this test case after each test:
        self._remove_route_patterns(["*/gzip-test*"])

        super().tearDown()

    async def _post_request_async(self, url: str, data: typing.Any, content_encoding: str = "gzip") -> list:
        result = []
        scope = {
            "type": "http",  # Change this so it can be amqp etc. as well, will require Router change.
            "method": "POST",
            "path": url,
            "query_string": b"",
            "headers": [(b"content-type", b"application/json"), (b"content-encoding", str.encode(content_encoding))],
            "body": gzip.compress(json.dumps(data).encode("ascii")),
        }

        async def _receive():
            body = bytes(scope["body"], "ascii") if not isinstance(scope["body"], bytes) else scope["body"]
            return {"type": "http.request", "body": body}

        async def _send(result_data):
            result.append(result_data)

        await main.get_app()(scope, _receive, _send)

        return_value = None
        return_code = 200
        for entry in result:
            if entry["type"] == "http.response.body":
                return_value = json.loads(entry["body"].decode("utf-8"))
            elif entry["type"] == "http.response.start":
                return_code = entry["status"]

        return return_value, return_code

    async def test_post_gzip_data_norouter(self):
        async def foo(data=fastapi.Body(...)):
            return data

        main.register_endpoint("post", "/gzip-test", foo)

        data = {"foo": "bar"}
        result, status = await self._post_request_async("/gzip-test", data)
        self.assertEqual(result, data)
        self.assertEqual(status, 200)

    async def test_post_gzip_data_router(self):
        router = routers.ServiceAPIRouter()

        @router.post("/gzip-test-router")
        async def foo(data=fastapi.Body(...)):
            return data

        main.register_router(router)

        data = {"foo": "bar"}
        result, status = await self._post_request_async("/gzip-test-router", data)
        self.assertEqual(result, data)
        self.assertEqual(status, 200)

    async def test_post_gzip_data_router_without_matching_encoding_logs_an_error(self) -> None:
        """Validate that a compressed route without supported encoder prints an error to the log."""
        router = routers.ServiceAPIRouter()

        TEST_ENDPOINT_URL = "/gzip-test-compressed-route"
        TEST_CONTENT_ENCODING = "unsupported"

        @router.post(path=TEST_ENDPOINT_URL)
        async def lorem_ipsum(data = fastapi.Body(...)):
            return {"success": True} # pragma: no cover

        main.register_router(router=router)

        with patch.object(target=carb, attribute="log_error") as mock_carb_log_error:
            _, _ = await self._post_request_async(url=TEST_ENDPOINT_URL, data={}, content_encoding=TEST_CONTENT_ENCODING)

        mock_carb_log_error.assert_called_once_with(f"{TEST_CONTENT_ENCODING} is not a registered decoder")

    async def test_deregistering_websocket_router_succeeds(self):
        websocket_router = routers.ServiceAPIRouter()

        @websocket_router.websocket("/test-websocket-router")
        async def lorem_ipsum() -> None:
            return {} # pragma: no cover

        main.register_router(router=websocket_router)

        # Deregister the WebSocket router to ensure no exception is raised when attempting to list `methods` of a
        # router, which are not present on an `APIWebSocketRoute`:
        main.deregister_router(router=websocket_router)

    async def test_register_facility_registration(self):
        class FacilityStub():
            pass # pragma: no cover

        facility_stub = FacilityStub()

        router = routers.ServiceAPIRouter()
        router.register_facility("stub", facility_stub)

        # We do what fastapi does and call the dependency.
        router.get_facility("stub").dependency()

        # We should fail for a facility that doesn't exist.
        with self.assertRaises(exceptions.ServiceUnavailableError):
            router.get_facility("foo").dependency()
