import os
import unittest
import threading
import carb
import asyncio
import omni.kit.test
import omni.ui as ui
import omni.appwindow
import omni.client.utils as clientutils
from pathlib import Path
from omni.kit import ui_test
from omni.kit.test_suite.helpers import StageEventHandler


class TestExternalDragDropUtils(omni.kit.test.AsyncTestCase):
    async def test_external_drag_drop(self):
        # new stage
        await omni.usd.get_context().new_stage_async()
        await ui_test.human_delay(50)

        self._stage_event_handler = StageEventHandler("omni.kit.window.drop_support")
        await self._stage_event_handler.reset_stage_event(omni.usd.StageEventType.OPENED)

        # get file path
        extension_path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        file_path = str(Path(extension_path).joinpath("data/tests/4Lights.usda")).replace("\\", "/")

        # position mouse
        await ui_test.find("Viewport").click()
        await ui_test.human_delay()

        # simulate drag/drop
        omni.appwindow.get_default_app_window().get_window_drop_event_stream().push(0, 0, {'paths': [file_path]})
        await ui_test.human_delay(50)

        # wait for stage event OPENED
        await self._stage_event_handler.wait_for_stage_event()
        await ui_test.human_delay(50)

        # verify
        root_layer = omni.usd.get_context().get_stage().GetRootLayer()
        self.assertTrue(clientutils.equal_urls(root_layer.identifier, file_path))
