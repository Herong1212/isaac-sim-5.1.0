# Copyright (c) 2022-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import glob
import logging
import os
from pathlib import Path

import carb
import carb.settings
import omni.kit.ui_test as ui_test
import omni.timeline
import omni.usd
from omni.kit.test_suite.helpers import wait_stage_loading
from omni.ui.tests.test_base import OmniUiTest

EXT_DATA_PATH = Path(carb.tokens.get_tokens_interface().resolve("${omni.kit.stagerecorder.ui}/data"))

logger = logging.getLogger(__name__)


class BaseTest(OmniUiTest):
    async def setUp(self):
        """Runs before each test. Use omni.kit.window.inpsector for widget paths"""
        await super().setUp()
        self._context = omni.usd.get_context()
        self._selection = self._context.get_selection()
        self._golden_img_dir = EXT_DATA_PATH.absolute().resolve().joinpath("tests").joinpath("golden")
        self._test_output_dir = EXT_DATA_PATH.absolute().resolve().joinpath("tests").joinpath("_output")
        self._usd_scene_dir = EXT_DATA_PATH.absolute().resolve().joinpath("tests")
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()
        self._timeline.set_current_time(0.0)
        self._timeline.set_auto_update(False)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        self._settings = carb.settings.get_settings()

    async def tearDown(self):
        """Runs after each test."""
        self._golden_img_dir = None
        self._timeline.set_auto_update(True)
        self._timeline.stop()
        await super().tearDown()
        for p in glob.glob(os.path.join(self._test_output_dir, "*")):
            if os.path.isfile(p):
                try:
                    os.remove(p)
                except Exception as exc:
                    carb.log_warn(f"Unexpected error trying to remove file from {self._test_output_dir}: {exc}")

    async def snapshot_test(self, golden_img_name: str, stack_depth=2):
        """Takes a snapshot into the golden image folder (e.g. {repo}\_build\windows-x86_64\release\data\_testoutput\exttest_omni_kit_stagerecorder_ui)."""
        await ui_test.human_delay(100)
        await self.finalize_test(
            golden_img_dir=self._golden_img_dir,
            golden_img_name=f"{golden_img_name}.png",
        )

    async def load_stage(self, stage_name):
        stage_name = os.path.join(self._usd_scene_dir, stage_name)
        result = None
        (result, err) = await self._context.open_stage_async(stage_name, omni.usd.UsdContextInitialLoadSet.LOAD_ALL)
        await wait_stage_loading()
        self.assertTrue(result)
        return result

    def set_timeline_in_seconds(self, time_in_secs: float):
        self._timeline.play()
        self._timeline.set_auto_update(False)
        self._timeline.set_current_time(time_in_secs)

    # use these event handler methods to register and wait for events
    #
    # Example:
    #
    # future_event = asyncio.Future()
    # self._regster_event_handler(lambda e: self._handle_event(e, future_event, omni.usd.StageEventType.OPENED))
    # ... do something here
    # await future_event
    #
    def regster_event_handler(self, event_handler_fn):
        self._event_handler_fn = event_handler_fn

    async def handle_event(event, future_test, event_id):
        if event == event_id:
            # pause to let async funcs finish
            await ui_test.human_delay()
            # test complete
            future_test.set_result(True)
