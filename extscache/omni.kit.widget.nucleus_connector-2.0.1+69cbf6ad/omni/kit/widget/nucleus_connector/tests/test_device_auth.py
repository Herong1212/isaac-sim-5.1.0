## Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import asyncio
from unittest.mock import patch, Mock

import omni.kit.test
import omni.client
import omni.kit.ui_test as ui_test

from ..extension import get_instance, connect, connect_with_dialog, reconnect
from ..test_helper import NucleusConnectorTestHelper
from ..device_auth import DeviceAuthConnector
from ..ui import DeviceAuthFlowDialog


class TestAddServerWithValidationDeviceAuth(omni.kit.test.AsyncTestCase):
    """Testing FilePickerView.add_server_with_validation"""

    # omni.client.AuthDeviceFlowParams can't be initiated directly in python since it didn't define constructors; so
    # for testing had to fake an object with those attrs.
    class _MockParams():
        def __init__(self, server, url, expiration, code) -> None:
            self.server = server
            self.url = url
            self.expiration = expiration
            self.code = code

    async def setUp(self):
        self._test_name = "ov-test"
        self._test_url = "omniverse://ov-test"
        self._expected_stat_results = [omni.client.Result.OK, omni.client.Result.OK]
        self._stat_latency = 1
        self._iter = 0

        # patch qrcode generation so we don't acutally install qrcode module and generates the image
        patch_qrcode_gen = patch.object(DeviceAuthFlowDialog, "_generate_qrcode")
        patch_qrcode_gen.start()
        self.addCleanup(patch_qrcode_gen.stop)

    async def tearDown(self):
        pass

    async def _mock_stat_async_impl(self, url: str):
        # During a stat, omni.client triggers the device auth callback.
        # The callback was previously set via the subscription method: omni.client.register_device_flow_auth_callback.
        ext = get_instance()
        if self._iter == 0:
            if ext:
                mock_param = TestAddServerWithValidationDeviceAuth._MockParams(url, "https://dummy/auth", 10, "FOOBAR42")
                ext._on_device_auth(1, mock_param)
        result = self._expected_stat_results[self._iter]
        self._iter += 1
        # Simulates the latency due to user signing in through device auth
        await asyncio.sleep(self._stat_latency)
        ext._on_device_auth(1, None)
        return result, {}

    def _mock_auth_cancel_impl(self, auth_handle: int):
        # A cancellation event also executes the device auth callback, but with the params set to None.
        ext = get_instance()
        if ext:
            ext._on_device_auth(auth_handle, None)

    async def test_connect_with_dialog_succeeds(self):
        """Testing that connecting to server through dialog succeeds"""
        under_test = get_instance()
        under_test._connector = DeviceAuthConnector()
        async with NucleusConnectorTestHelper() as connector_helper:
            with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl):
                mock_success_fn, mock_failed_fn = Mock(), Mock()
                connect_with_dialog(on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                # Connector dialog will show up first prompting for user input
                await connector_helper.wait_for_popup()
                await connector_helper.click_apply_async(name=self._test_name, url=self._test_url)
                await connector_helper.wait_for_close()
                # The device auth flow dialog will show up displaying the qrcode etc.
                await connector_helper.wait_for_popup(url=self._test_url)
                await connector_helper.wait_for_close(timeout=1000, url=self._test_url)
                # Confirm on_success callback called
                await ui_test.human_delay(10)
                mock_success_fn.assert_called_once_with(self._test_name, self._test_url)
                mock_failed_fn.assert_not_called()

    async def test_connect_with_given_url_succeeds(self):
        under_test = get_instance()
        under_test._connector = DeviceAuthConnector()
        async with NucleusConnectorTestHelper() as connector_helper:
            with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl):
                mock_success_fn, mock_failed_fn = Mock(), Mock()
                connect(self._test_name, self._test_url, on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                await ui_test.human_delay(10)
                # Only the device auth dialog will show up
                await connector_helper.wait_for_popup(url=self._test_url)
                await connector_helper.wait_for_close(timeout=1000, url=self._test_url)
                # Confirm on_success callback called
                await ui_test.human_delay(10)
                mock_success_fn.assert_called_once_with(self._test_name, self._test_url)
                mock_failed_fn.assert_not_called()

    async def test_connect_then_reconnect_succeeds(self):
        """Testing that when connect fails the first time, retries with a reconnect"""
        under_test = get_instance()
        under_test._connector = DeviceAuthConnector()
        # In this case, the first stat will result in an error, but will succeed after a reconnect
        self._expected_stat_results = [omni.client.Result.ERROR_CONNECTION, omni.client.Result.OK]
        async with NucleusConnectorTestHelper() as connector_helper:
            with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl),\
                patch("omni.client.reconnect") as mock_reconnect:

                mock_success_fn, mock_failed_fn = Mock(), Mock()
                connect(self._test_name, self._test_url, on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                await ui_test.human_delay(10)
                await connector_helper.wait_for_popup(url=self._test_url)
                #await connector_helper.click_apply_async(name=self._test_name, url=self._test_url)
                await connector_helper.wait_for_close(timeout=1000, url=self._test_url)

                # auth dialog is closed during second stat_async, need wait more time for connect completed
                await asyncio.sleep(self._stat_latency)
                # Confirm reconnect attempted and connection succeeded
                mock_reconnect.assert_called_once_with(self._test_url)
                mock_success_fn.assert_called_once_with(self._test_name, self._test_url)
                mock_failed_fn.assert_not_called()

    async def test_connect_with_url_cancelled(self):
        """Testing that user is able to cancel out of connection flow"""
        under_test = get_instance()
        under_test._connector = DeviceAuthConnector()
        async with NucleusConnectorTestHelper() as connector_helper:
            with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl),\
                patch("omni.client.authentication_cancel", side_effect=self._mock_auth_cancel_impl):
                mock_success_fn, mock_failed_fn = Mock(), Mock()
                connect(self._test_name, self._test_url, on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                await ui_test.human_delay(10)
                # Only the device auth dialog will show up
                await connector_helper.wait_for_popup(url=self._test_url)
                # Click cancel after some time
                await asyncio.sleep(.5*self._stat_latency)
                await connector_helper.click_cancel_async(url=self._test_url)
                await connector_helper.wait_for_close(timeout=1000, url=self._test_url)
                # Confirm neither callbacks invoked
                mock_success_fn.assert_not_called()
                mock_failed_fn.assert_not_called()

                # make sure we finish the mock stat return
                await asyncio.sleep(0.5* self._stat_latency)

    async def test_reconnect_with_given_url_succeeds(self):
        under_test = get_instance()
        under_test._connector = DeviceAuthConnector()
        self._expected_stat_results = [omni.client.Result.OK]
        async with NucleusConnectorTestHelper() as connector_helper:
             with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl),\
                patch("omni.client.reconnect") as mock_reconnect:

                mock_success_fn, mock_failed_fn = Mock(), Mock()
                reconnect(self._test_url, on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                for _ in range(1000):
                    await omni.kit.app.get_app().next_update_async()
                # Confirm on_success callback called
                mock_success_fn.assert_called_once_with(self._test_name, self._test_url)
                mock_failed_fn.assert_not_called()
                mock_reconnect.assert_called_once_with(self._test_url)
