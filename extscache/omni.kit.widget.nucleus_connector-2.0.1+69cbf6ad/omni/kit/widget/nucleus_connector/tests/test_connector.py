## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import asyncio
import omni.kit.test
import omni.client

from unittest.mock import patch, Mock
from ..extension import get_instance
from ..test_helper import NucleusConnectorTestHelper
from ..extension import connect_with_dialog, connect, reconnect, disconnect


class TestAddServerWithValidation(omni.kit.test.AsyncTestCase):
    """Testing FilePickerView.add_server_with_validation"""
    async def setUp(self):
        self._test_name = "ov-test"
        self._test_url = "omniverse://ov-test"
        self._expected_stat_results = [omni.client.Result.OK, omni.client.Result.OK]
        self._expected_stat_results_cancelled = [omni.client.Result.OK, omni.client.Result.ERROR_CONNECTION, omni.client.Result.OK]
        self._stat_latency = 1
        self._iter = 0

    async def tearDown(self):
        pass

    async def _mock_stat_async_impl(self, url: str):
        # During a stat, omni.client triggers the browser sign in flow by executing the _on_authenticate callback.
        # The callback was previously set via the subscription method: omni.client.set_authentication_message_box_callback.
        if self._iter == 0:
            ext = get_instance()
            if ext:
                ext._on_authenticate(True, url, 1)
        result = self._expected_stat_results[self._iter]
        self._iter += 1
        # Simulates the latency due to user signing in through brower
        await asyncio.sleep(self._stat_latency)
        return result, {}

    async def _mock_stat_async_impl_cancelled(self, url: str):
        # During a stat, omni.client triggers the browser sign in flow by executing the _on_authenticate callback.
        # The callback was previously set via the subscription method: omni.client.set_authentication_message_box_callback.
        ext = get_instance()
        if ext:
            ext._on_authenticate(True, url, 1)
        result = self._expected_stat_results_cancelled[self._iter]
        self._iter += 1
        # Simulates the latency due to user signing in through brower
        await asyncio.sleep(self._stat_latency)
        return result, {}

    def _mock_auth_cancel_impl(self, auth_handle: int):
        # A cancellation event also executes the _on_authenticate callback, but with the first input set to False.
        ext = get_instance()
        if ext:
            ext._on_authenticate(False, None, auth_handle)

    async def test_connect_with_dialog_succeeds(self):
        """Testing that connecting to server through dialog succeeds"""
        async with NucleusConnectorTestHelper() as connector_helper:
            with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl):

                mock_success_fn, mock_failed_fn = Mock(), Mock()
                connect_with_dialog(on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                await connector_helper.wait_for_popup()
                await connector_helper.click_apply_async(name=self._test_name, url=self._test_url)
                await connector_helper.wait_for_close(timeout=1000)
                # Confirm on_success callback called
                mock_success_fn.assert_called_once_with(self._test_name, self._test_url)
                mock_failed_fn.assert_not_called()

    async def test_connect_with_given_url_succeeds(self):
        async with NucleusConnectorTestHelper() as connector_helper:
            with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl):

                mock_success_fn, mock_failed_fn = Mock(), Mock()
                connect(self._test_name, self._test_url, on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                await connector_helper.wait_for_popup()
                # Note that it's not necessary to click the apply button; the dialog automatically proceeds to make the
                # connection, using the given server name and url.
                await connector_helper.wait_for_close(timeout=1000)
                # Confirm on_success callback called
                mock_success_fn.assert_called_once_with(self._test_name, self._test_url)
                mock_failed_fn.assert_not_called()

    async def test_connect_with_dialog_cancelled(self):
        """Testing that user is able to cancel out of connection flow"""
        async with NucleusConnectorTestHelper() as connector_helper:
            with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl),\
                patch("omni.client.authentication_cancel", side_effect=self._mock_auth_cancel_impl):

                mock_success_fn, mock_failed_fn = Mock(), Mock()
                connect_with_dialog(on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                await connector_helper.wait_for_popup()
                await connector_helper.click_apply_async(name=self._test_name, url=self._test_url)
                # Click cancel after some time
                await asyncio.sleep(.5*self._stat_latency)
                await connector_helper.click_cancel_async()
                await connector_helper.wait_for_close(timeout=1000)
                # Confirm neither callbacks invoked
                mock_success_fn.assert_not_called()
                mock_failed_fn.assert_not_called()

    async def test_connect_with_dialog_cancelled_url_again(self):
        """OMPE-29317: Testing that user is able to connect to cancelled url again"""
        async with NucleusConnectorTestHelper() as connector_helper:
            with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl_cancelled),\
                patch("omni.client.authentication_cancel", side_effect=self._mock_auth_cancel_impl),\
                patch("omni.client.reconnect") as mock_reconnect,\
                patch("omni.client.sign_out") as mock_sign_out:

                mock_success_fn, mock_failed_fn = Mock(), Mock()
                connect_with_dialog(on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                await connector_helper.wait_for_popup()
                await connector_helper.click_apply_async(name=self._test_name, url=self._test_url)
                # Click cancel after some time
                await asyncio.sleep(.5*self._stat_latency)
                await connector_helper.click_cancel_async()
                # Confirm neither callbacks invoked
                mock_success_fn.assert_not_called()
                mock_failed_fn.assert_not_called()
                # It's necessary to destroy the dialog before the next connect_with_dialog
                dialog = connector_helper.get_connector_dialog()
                dialog = None
                connect_with_dialog(on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                await connector_helper.wait_for_popup()
                await connector_helper.click_apply_async(name=self._test_name, url=self._test_url)
                await asyncio.sleep(5*self._stat_latency)
                mock_reconnect.assert_called_once_with(self._test_url)
                await connector_helper.wait_for_close(timeout=1000)


    async def test_connect_then_reconnect_succeeds(self):
        """Testing that when connect fails the first time, retries with a reconnect"""
        under_test = get_instance()
        # OM-122760: Only retry on signed out server to reduce connecting time to invalid server
        under_test._connector._connection_status[self._test_url] = omni.client.ConnectionStatus.SIGNED_OUT
        # In this case, the first stat will result in an error, but will succeed after a reconnect
        self._expected_stat_results = [omni.client.Result.ERROR_CONNECTION, omni.client.Result.OK]
        async with NucleusConnectorTestHelper() as connector_helper:
            with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl),\
                patch("omni.client.reconnect") as mock_reconnect:

                mock_success_fn, mock_failed_fn = Mock(), Mock()
                connect_with_dialog(on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                await connector_helper.wait_for_popup()
                await connector_helper.click_apply_async(name=self._test_name, url=self._test_url)
                await connector_helper.wait_for_close(timeout=1000)
                # Confirm reconnect attempted and connection succeeded
                mock_reconnect.assert_called_once_with(self._test_url)
                mock_success_fn.assert_called_once_with(self._test_name, self._test_url)
                mock_failed_fn.assert_not_called()

    async def test_connect_and_reconnect_fails(self):
        """Testing that both the connect and reconnect attempts fail"""
        under_test = get_instance()
        # OM-122760: Only retry on signed out server to reduce connecting time to invalid server
        under_test._connector._connection_status[self._test_url] = omni.client.ConnectionStatus.SIGNED_OUT
        # In this case, the first stat will result in an error, but will succeed after a reconnect
        self._expected_stat_results = [omni.client.Result.ERROR_CONNECTION, omni.client.Result.ERROR_CONNECTION]
        async with NucleusConnectorTestHelper() as connector_helper:
            with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl),\
                patch("omni.client.reconnect") as mock_reconnect:

                mock_success_fn, mock_failed_fn = Mock(), Mock()
                connect_with_dialog(on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                await connector_helper.wait_for_popup()
                await connector_helper.click_apply_async(name=self._test_name, url=self._test_url)
                # Cancel to close the dialog after some time
                await asyncio.sleep(2.5*self._stat_latency)
                await connector_helper.click_cancel_async()
                await connector_helper.wait_for_close(timeout=1000)
                # Confirm reconnect attempted and connection succeeded
                mock_reconnect.assert_called_once_with(self._test_url)
                mock_failed_fn.assert_called_once_with(self._test_name, self._test_url)
                mock_success_fn.assert_not_called()

    async def test_reconnect_with_given_url_succeeds(self):
        self._expected_stat_results = [omni.client.Result.OK]
        async with NucleusConnectorTestHelper() as connector_helper:
             with patch("omni.client.stat_async", side_effect=self._mock_stat_async_impl),\
                patch("omni.client.reconnect") as mock_reconnect:

                mock_success_fn, mock_failed_fn = Mock(), Mock()
                reconnect(self._test_url, on_success_fn=mock_success_fn, on_failed_fn=mock_failed_fn)
                for _ in range(100):
                    dialog = connector_helper.get_connector_dialog()
                    if dialog and dialog.visible:
                        break
                    await omni.kit.app.get_app().next_update_async()

                await connector_helper.wait_for_close(timeout=1000)
                # Confirm on_success callback called
                mock_success_fn.assert_called_once_with(self._test_name, self._test_url)
                mock_failed_fn.assert_not_called()
                mock_reconnect.assert_called_once_with(self._test_url)