# Copyright (c) 2020-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

"""Tests for the core interface of the Kit microservices framework."""

import os

from pathlib import Path
from typing import List

import fastapi
import starlette

from fastapi.staticfiles import StaticFiles

import omni.services.core.main as main
from omni.services.facilities.base import Facility

from . import base
from ..routers import ServiceAPIRouter


class TestServicesCore(base.BaseServiceTest):

    def tearDown(self):
        # Remove temporary routes added for the purposes of this test case after each test:
        self._remove_route_patterns(["*/foo*", "*/bar*"])

        super().tearDown()

    async def test_register_get_endpoint(self):
        async def foo():
            return "bar"

        main.register_endpoint("get", "/foo", foo)
        result, status = await self._get_request_async("/foo")
        self.assertEqual(status, 200)
        self.assertEqual(result, "bar")

    async def test_register_post_endpoint(self):
        async def foo():
            return "bar"

        main.register_endpoint("post", "/foo", foo)
        result, status = await self._post_request_async(url="/foo", data={})
        self.assertEqual(status, 200)
        self.assertEqual(result, "bar")

    async def test_register_router_no_prefix(self):
        router = fastapi.APIRouter()

        @router.get("/bar")
        async def bar():
            return "foo"

        main.register_router(router)
        result, status = await self._get_request_async("/bar")
        self.assertEqual(status, 200)
        self.assertEqual(result, "foo")

    async def test_register_router_prefix(self):
        router = fastapi.APIRouter()

        @router.get("/bar")
        async def bar():
            return "foo"

        main.register_router(router, prefix="/test")
        result, status = await self._get_request_async("/test/bar")
        self.assertEqual(status, 200)
        self.assertEqual(result, "foo")

    async def test_register_router_main_dotted_prefix(self):
        router = fastapi.APIRouter()

        @router.get("/bar")
        async def bar():
            return "foo"

        main.register_router(router, prefix="test.baz")
        result, status = await self._get_request_async("/test/baz/bar")
        self.assertEqual(status, 200)
        self.assertEqual(result, "foo")

    async def test_register_router_with_prefix(self):
        router = ServiceAPIRouter(prefix="/test")

        @router.get("/bar")
        async def bar():
            return "foo"

        main.register_router(router)
        result, status = await self._get_request_async("/test/bar")
        self.assertEqual(status, 200)
        self.assertEqual(result, "foo")

    async def test_deregister_router_with_prefix(self):
        """Validate that deregistering routers with a given prefix succeeds."""
        TEST_ROUTER_PREFIX = "/test"

        router = ServiceAPIRouter(prefix=TEST_ROUTER_PREFIX)

        @router.get("/bar")
        async def bar():
            return "foo"

        main.register_router(router=router)
        result, status = await self._get_request_async("/test/bar")
        self.assertEqual(first=status, second=200)
        self.assertEqual(first=result, second="foo")

        main.deregister_router(router=router, prefix=TEST_ROUTER_PREFIX.replace("/", ""))

    async def test_register_router_with_dotted_prefix(self):
        router = ServiceAPIRouter(prefix="test.baz")

        @router.get("/bar")
        async def bar():
            return "foo"

        main.register_router(router)
        result, status = await self._get_request_async("/test/baz/bar")
        self.assertEqual(status, 200)
        self.assertEqual(result, "foo")

    async def test_default_status_response(self) -> None:
        """Validate that the response from the `/status` endpoint matches the expected data."""
        result, status = await self._get_request_async("/status")

        expected_response = await main._status()
        self.assertEqual(first=status, second=200)
        self.assertEqual(first=result, second=expected_response)
        self.assertIsInstance(obj=result, cls=str)

    async def test_register_router_with_bypassed_path(self):
        """Validate that registering a router with bypassed paths does not make the endpoint available."""
        router = ServiceAPIRouter()
        router._bypassed_paths = ["/path-a", "/path-b"]

        @router.get("/bar")
        async def bar():
            return "foo"

        main.register_router(router=router, prefix="/test")
        result, status = await self._get_request_async("/test/bar")

        self.assertEqual(first=status, second=200)
        self.assertEqual(first=result, second="foo")

    async def test_router_with_list_param(self):
        router = ServiceAPIRouter(prefix="/test")

        @router.get("/bar")
        async def bar(test_param: List = fastapi.Query(default=None)):
            return test_param

        main.register_router(router)
        list_param = ['one', '2', "three"]
        result, status = await self._get_request_async("/test/bar", query_params={"test_param": list_param})
        self.assertEqual(status, 200)
        self.assertEqual(result, list_param)

    async def test_router_tags(self):
        router = ServiceAPIRouter(prefix="/foo", tags=["foo", "bar"])
        self.assertEqual(router.tags, ["foo", "bar"])

    async def test_register_facility(self) -> None:
        """Validate that registering a Facility increases the number of tracked Facility instances."""
        class TestFacility(Facility):
            pass

        test_facility = TestFacility()

        initial_facility_count = len(main._singleton._facilities)
        main.register_facility(facility=test_facility)
        final_facility_count = len(main._singleton._facilities)

        self.assertEqual(first=final_facility_count, second=initial_facility_count + 1)

    async def test_registering_a_middleware_after_application_start_raises_an_exception(self) -> None:
        """Validate that registering a Middleware after starting the application raises an Exception."""
        class TestMiddleware:
            pass # pragma: no cover

        with self.assertRaises(expected_exception=RuntimeError) as exc:
            main.register_middleware(cls=TestMiddleware)

        self.assertGreater(a=len(exc.exception.args), b=0)
        self.assertEqual(first=exc.exception.args[0], second="Cannot add middleware after an application has started")

    async def test_registering_a_websocket_endpoint_does_not_raise_an_exception(self) -> None:
        """Validate that registering a WebSocket endpoint does not raise an Exception."""
        async def lorem_ipsum():
            return {"success": True}

        main.register_websocket_endpoint(url="/test-websocket-endpoint", func=lorem_ipsum)

        response, status = await self._get_request_async(url="/test-websocket-endpoint")

        self.assertIn(member="detail", container=response)
        self.assertEqual(first="Not Found", second=response["detail"])
        self.assertEqual(first=status, second=404)

    async def test_register_mount(self):
        static_files_directory = os.path.join(Path(__file__).parent.absolute(), "static-files")

        main.register_mount("/foo", StaticFiles(directory=static_files_directory))
        result, status = await self._get_request_async("/foo/bar.json")
        self.assertEqual(status, 200)
        self.assertEqual(result, {"baz": "qux"})

    async def test_register_mount_with_args(self):
        static_files_directory = os.path.join(Path(__file__).parent.absolute(), "static-files")

        main.register_mount("/foo", StaticFiles(directory=static_files_directory), name="foo")

        routes_found = []
        for route in main.get_app().routes:
            if isinstance(route, starlette.routing.Mount) and route.path == "/foo":
                routes_found.append(route)

        self.assertEqual(len(routes_found), 1)
        self.assertEqual(routes_found[0].name, "foo")
        self.assertEqual(routes_found[0].path, "/foo")

    async def test_mounting_html_redirects_to_index_file(self):
        static_files_directory = os.path.join(Path(__file__).parent.absolute(), "static-files")

        main.register_mount("/foo", StaticFiles(directory=static_files_directory, html=True))

        # Validate that a request for "/foo" receives a response for a 307 redirect to "/foo/":
        result, status = await self._get_request_async("/foo")
        self.assertEqual(status, 307)
        self.assertEqual(result, "")

        # Validate that a request for "/foo/" receives a response from the "index.html" file in the mounted directory:
        result, status = await self._get_request_async("/foo/")
        self.assertEqual(status, 200)
        self.assertIn("<h1>foo</h1>", result)

    async def test_mount_returns_404_for_missing_files(self):
        static_files_directory = os.path.join(Path(__file__).parent.absolute(), "static-files")

        main.register_mount("/foo", StaticFiles(directory=static_files_directory, html=True))
        result, status = await self._get_request_async("/foo/non-existing-file.mp4")
        self.assertEqual(status, 404)

    async def test_deregister_endpoint(self):
        async def foo():
            return "bar"

        main.register_endpoint("get", "/foo", foo)
        result, status = await self._get_request_async("/foo")
        self.assertEqual(status, 200)
        self.assertEqual(result, "bar")

        main.deregister_endpoint("get", "/foo")
        result, status = await self._get_request_async("/foo")
        self.assertEqual(status, 404)
        self.assertEqual(result, {"detail": "Not Found"})

    async def test_deregister_endpoint_with_arg(self):
        async def foo(arg):
            return arg

        url = "/foo/{arg}"

        main.register_endpoint("get", url, foo)
        result, status = await self._get_request_async("/foo/bar")
        self.assertEqual(status, 200)
        self.assertEqual(result, "bar")

        main.deregister_endpoint("get", url)
        result, status = await self._get_request_async("/foo/bar")
        self.assertEqual(status, 404)

    async def test_deregister_router(self):
        router = fastapi.APIRouter()
        prefix = "/test"

        @router.get("/bar")
        async def bar():
            return "foo"

        main.register_router(router, prefix=prefix)
        result, status = await self._get_request_async("/test/bar")
        self.assertEqual(status, 200)
        self.assertEqual(result, "foo")

        main.deregister_router(router, prefix=prefix)
        result, status = await self._get_request_async("/foo/bar")
        self.assertEqual(status, 404)

    async def test_deregister_mount(self):
        static_files_directory = os.path.join(Path(__file__).parent.absolute(), "static-files")

        main.register_mount("/foo", StaticFiles(directory=static_files_directory))
        result, status = await self._get_request_async("/foo/bar.json")
        self.assertEqual(status, 200)
        self.assertEqual(result, {"baz": "qux"})

        main.deregister_mount("/foo")
        result, status = await self._get_request_async("/foo")
        self.assertEqual(status, 404)
        self.assertEqual(result, {"detail": "Not Found"})

    async def test_set_description(self):
        main.set_metadata(
            "foo", "bar", "123"
        )

        self.assertEqual(main.get_app().title, "foo")
        self.assertEqual(main.get_app().description, "bar")
        self.assertEqual(main.get_app().version, "123")

    async def test_set_application_root_path(self) -> None:
        """Validate that setting the application's root path configures the application as expected."""
        TEST_ROOT_PATH = "/test-root-path"

        original_root_path = main.get_app().root_path
        main.set_metadata(title="foo", description="bar", version="123", root_path=TEST_ROOT_PATH)
        final_root_path = main.get_app().root_path

        self.assertEqual(first=final_root_path, second=TEST_ROOT_PATH)

        main.set_metadata(title="foo", description="bar", version="123", root_path=original_root_path)

    async def test_set_tag_metadata(self):
        tags_metadata = [
            {"name": "tag", "description": "tag_description"}
        ]

        main.set_metadata(
            "foo", "bar", "123",
            tags_metadata=tags_metadata
        )
        self.assertEqual(main.get_app().openapi_tags, tags_metadata)
