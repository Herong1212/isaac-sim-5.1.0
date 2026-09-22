## Copyright (c) 2018-2019, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import asyncio
from unittest.mock import patch, Mock

import carb.settings
import omni.kit.test
import omni.ui as ui
import omni.kit.ui_test as ui_test

from ..ui import ConnectorDialog, DeviceAuthFlowDialog


class TestConnectorDialog(omni.kit.test.AsyncTestCase):
    """Tests for dialog base class"""
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def _mock_task_with_results(self):
        return 1, 2, 3

    async def _mock_cancellable_task(self):
        """After a short delay, hide the dialog.  This should result in cancelling this long-lasting task."""
        while True:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                return

    async def test_dialog_resturns_task_results(self):
        """Test that the dialog returns the results from it child task"""
        dialog = ConnectorDialog()
        dialog.show()
        with dialog.frame:
            ui.Label("Test label", height=20)
            results = await dialog.run_cancellable_task(self._mock_task_with_results())

        # Confirm returned result
        self.assertEqual(results, (1, 2, 3))
        dialog.destroy()

    async def test_dialog_cancels_task(self):
        """Test that hiding the dialog window cancels child task"""
        dialog = ConnectorDialog()

        # Hide the dialog a short time later.
        loop = asyncio.get_event_loop()
        loop.call_later(2, dialog.cancel_task)

        dialog.show()
        with dialog.frame:
            ui.Label("Test label")
            await dialog.run_cancellable_task(self._mock_cancellable_task())

        # Confirm that child task was cancelled
        self.assertEqual(dialog._task, None)
        dialog.destroy()


class TestDeviceAuthFlowDialog(omni.kit.test.AsyncTestCase):
    """Tests for DeviceAuthFlowDialog."""

    # omni.client.AuthDeviceFlowParams can't be initiated directly in python since it didn't define constructors; so
    # for testing had to fake an object with those attrs.
    class _MockParams():
        def __init__(self, server, url, expiration, code) -> None:
            self.server = server
            self.url = url
            self.expiration = expiration
            self.code = code

    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    @staticmethod
    def _mock_params(server, url, expiration, code):
        return TestDeviceAuthFlowDialog._MockParams(server, url, expiration, code)

    async def test_display_and_count_down(self):
        """Test that the dialog displays correctly and counts down correctly."""
        # mock qrcode generation so we don't actually generate that
        with patch.object(DeviceAuthFlowDialog, "_generate_qrcode") as mock_gen_qrcode:
            dialog = DeviceAuthFlowDialog(self._mock_params("dummy", "https://dummy/auth/url", 100, "FOOBAR42"))
            self.assertEqual(100, dialog._time_remaining)
            # test count down
            await asyncio.sleep(1.5)
            self.assertGreaterEqual(99, dialog._time_remaining)

            # test that qrcode generation is triggered
            mock_gen_qrcode.assert_called_once_with("https://dummy/auth/url")
        dialog.hide()
        dialog.destroy()

    async def test_cancel(self):
        """Test that the dialog cancel cancels the authentication and closes."""
        # mock qrcode generation so we don't actually generate that
        with patch.object(DeviceAuthFlowDialog, "_generate_qrcode"):
            dialog = DeviceAuthFlowDialog(self._mock_params("dummy", "https://dummy/auth/url", 100, "FOOBAR42"))
            self.assertTrue(dialog.window.visible)
            self.assertIsNotNone(dialog._count_down_task)

            await ui_test.human_delay(5)
            button = ui_test.find_all("Device Authentication//Frame/**/Button[*]")[-1]
            self.assertIsNotNone(button)
            self.assertEqual(button.widget.text, "Cancel")
            await button.click()
            await ui_test.human_delay(5)
            # check that count down is cancelled and window is hidden
            self.assertTrue(dialog._count_down_task.cancelled())
            self.assertFalse(dialog.window.visible)

    async def test_dialog_expiration_and_retry(self):
        """Test that the dialog correctly counts down and expires, and retry works."""
        # mock qrcode generation so we don't actually generate that
        with patch.object(DeviceAuthFlowDialog, "_generate_qrcode"), patch("omni.client.reconnect") as mock_reconnect:
            dialog = DeviceAuthFlowDialog(self._mock_params("dummy", "https://dummy/auth/url", 1, "FOOBAR42"))
            await ui_test.human_delay(5)
            buttons = ui_test.find_all("Device Authentication//Frame/**/Button[*]")
            retry, cancel = buttons[0], buttons[1]
            self.assertFalse(retry.widget.visible)
            self.assertTrue(cancel.widget.visible)

            # make sure we meet expiration
            await asyncio.sleep(1.5)

            # retry button should be enabled now
            self.assertTrue(retry.widget.visible)
            self.assertTrue(cancel.widget.visible)

            # click retry should cancel and hide the window, and issue a new reconnect
            await retry.click()
            await ui_test.human_delay(10)

            mock_reconnect.assert_called_once_with("omniverse://dummy")
            self.assertFalse(dialog.window.visible)
