## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from functools import partial
from unittest.mock import patch
from omni.kit.test.async_unittest import AsyncTestCase
from ..service_discovery import ServiceDiscovery
from ..ui import NucleusAboutDialog
from .. import is_service_available, get_nucleus_services, get_nucleus_services_async

class MockServiceInterface:
    def __init__(self, name):
        self.name = name


class MockService:
    def __init__(self, name):
        self.service_interface = MockServiceInterface(name)
        self.meta = {"version": "test_version"}

class MockInfo:
    def __init__(self):
        self.version = "test_nucleus_version"
        self.checkpoints_enabled = True
        self.omniojects_enabled = True


class TestDiscovery(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        self._mock_service_content= [MockService("NGSearch"),MockService("Object"),MockService("Search")]
        self._mock_service_localhost= [MockService("Object"),MockService("Otherservice")]

    # After running each test
    async def tearDown(self):
        pass

    async def _mock_get_nucleus_services_async(self, url: str):
        discovery = ServiceDiscovery()
        if url == "omniverse://content":
            discovery._nucleus_services["omniverse://content"] = self._mock_service_content
            return discovery._nucleus_services["omniverse://content"]
        if url == "omniverse://localhost":
            discovery._nucleus_services["omniverse://localhost"] = self._mock_service_localhost
            return discovery._nucleus_services["omniverse://localhost"]

    async def test_service_discovery(self):
        discovery = ServiceDiscovery()
        test_unknow = await discovery.get_nucleus_services_async("unknow://unknow")
        self.assertIsNone(test_unknow)
        with patch.object(discovery, "get_nucleus_services_async", side_effect=self._mock_get_nucleus_services_async):
            content_services = await discovery.get_nucleus_services_async("omniverse://content")
            await discovery.get_nucleus_services_async("omniverse://localhost")
            self.assertIsNone(discovery.get_nucleus_services("unknow://unknow"))
            self.assertTrue(discovery.is_service_supported_for_nucleus("omniverse://content", "NGSearch"))
            self.assertFalse(discovery.is_service_supported_for_nucleus("omniverse://localhost", "NGSearch"))
            self.assertFalse(discovery.is_service_supported_for_nucleus("l://other", "other"))
            self.assertTrue(discovery.is_service_supported_for_nucleus("omniverse://localhost", "Otherservice"))
            self.assertEqual(discovery.get_nucleus_services("omniverse://content"), self._mock_service_content)
            self.assertEqual(discovery.get_nucleus_services("omniverse://localhost"), self._mock_service_localhost)
            dialog = NucleusAboutDialog(MockInfo(), content_services)
            dialog.show()
            self.assertTrue(dialog._window.visible)
            dialog.hide()
            self.assertFalse(dialog._window.visible)
            dialog.destroy()
        discovery.destory()

    async def test_interface(self):
        test_unknow = await get_nucleus_services_async("unknow://unknow")
        self.assertIsNone(test_unknow)
        with  patch.object(ServiceDiscovery.__wrapped__, "get_nucleus_services_async", side_effect=self._mock_get_nucleus_services_async):
            discovery = ServiceDiscovery()
            await discovery.get_nucleus_services_async("omniverse://content")
            await discovery.get_nucleus_services_async("omniverse://localhost")
            self.assertTrue(is_service_available("NGSearch", "omniverse://content"))
            self.assertTrue(is_service_available("Otherservice", "omniverse://localhost"))
            discovery.destory()
            self.assertIsNone(get_nucleus_services("omniverse://content"))
            self.assertIsNone(get_nucleus_services("omniverse://localhost"))
