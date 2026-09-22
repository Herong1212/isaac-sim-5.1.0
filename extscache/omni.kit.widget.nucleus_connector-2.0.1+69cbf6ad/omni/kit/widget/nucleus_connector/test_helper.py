## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import asyncio
from typing import Optional, Union

import omni.kit.app
from omni.kit import ui_test
from .ui import ConnectorDialog, DeviceAuthFlowDialog
from .extension import get_instance as get_nucleus_connector
from .connector import NucleusConnector
from .device_auth import DeviceAuthConnector


class NucleusConnectorTestHelper:
    # NOTE Since the file dialog is a singleton, use an async lock to ensure mutex access in unit tests.
    # During run-time, this is not a issue because the dialog is effectively modal.
    __async_lock = asyncio.Lock()

    async def __aenter__(self):
        await self.__async_lock.acquire()
        return self

    async def __aexit__(self, *args):
        self.__async_lock.release()

    def get_connector_dialog(self, url: str = None) -> Optional[Union[ConnectorDialog, DeviceAuthFlowDialog]]:
        ext = get_nucleus_connector()
        if ext and ext._connector:
            if isinstance(ext._connector, NucleusConnector) or url is None:
                return ext._connector._dialog
            if isinstance(ext._connector, DeviceAuthConnector) and url:
                return ext._connector._pending_results.get(url, (None, None))[1]
        return None  # pragma: no cover

    async def wait_for_popup(self, timeout: int = 100, url: str = None):
        dialog = self.get_connector_dialog(url=url)
        if dialog:
            for _ in range(timeout):
                if dialog.visible:
                    return
                await omni.kit.app.get_app().next_update_async()
        raise Exception("Error: The connector dialog never opened.")

    async def wait_for_close(self, timeout: int = 100, url: str = None):
        dialog = self.get_connector_dialog(url=url)
        # OM-76995: Since we are creating the dialog on demand, it is considered ok if the dialog doesn't exist
        if dialog:
            for _ in range(timeout):
                if not dialog.visible:
                    return
                await omni.kit.app.get_app().next_update_async()
            raise Exception("Error: The connector dialog never closed.")  # pragma: no cover

    async def click_apply_async(self, name: str = None, url: str = None):
        """Helper function to click the apply button"""
        dialog = self.get_connector_dialog()
        if dialog:
            dialog.set_value('name', name)
            dialog.set_value('url', url)
            ok_button = ui_test.find(f"{dialog._window.title}//Frame/**/Button[0]")
            await ok_button.click()
            await ui_test.human_delay()

    async def click_cancel_async(self, url: str = None):
        """Helper function to click the cancel button"""
        dialog = self.get_connector_dialog(url=url)
        if dialog:
            cancel_button = ui_test.find(f"{dialog._window.title}//Frame/**/Button[1]")
            await cancel_button.click()
            await ui_test.human_delay()
