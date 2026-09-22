## Copyright (c) 2018-2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
from pathlib import Path
import omni.kit.test
from omni.ui.tests.test_base import OmniUiTest
from omni.kit.app import queue_event
import carb
import carb.events
import asyncio

CURRENT_PATH = Path(__file__).parent
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data").joinpath("test")
PROGRESS_GLOBAL_EVT = "omni.kit.window.status_bar@progress"
ACTIVITY_GLOBAL_EVT = "omni.kit.window.status_bar@activity"

class TestStatusBar(OmniUiTest):
    # Before running each test
    async def setUp(self):
        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden_img").absolute()
        queue_event(ACTIVITY_GLOBAL_EVT, {"text": ""})
        queue_event(PROGRESS_GLOBAL_EVT, {"progress": "-1"})

    # After running each test
    async def tearDown(self):
        pass

    async def test_general(self):
        await self.create_test_area(256, 64)

        async def log():
            # Delayed log because self.finalize_test logs things
            carb.log_warn("StatusBar test")

        asyncio.ensure_future(log())

        await self.finalize_test("test_general.png")

    async def test_activity(self):
        await self.create_test_area(512, 64)

        async def log():
            # Delayed log because self.finalize_test logs things
            carb.log_warn("StatusBar test")

        # Test activity name with spaces URL-encoded
        queue_event(ACTIVITY_GLOBAL_EVT, payload={"text": "MFC%20For%20NvidiaAnimated.usd"})
        queue_event(PROGRESS_GLOBAL_EVT, payload={"progress": "0.2"})
        asyncio.ensure_future(log())

        await self.finalize_test("test_activity.png")

    async def test_invalid_value(self):
        # Test invalid payload value
        queue_event(ACTIVITY_GLOBAL_EVT, payload={"text": 0})
        queue_event(PROGRESS_GLOBAL_EVT, payload={"progress": "adsfagdadf"})

        queue_event(ACTIVITY_GLOBAL_EVT, payload={"text": True})
        queue_event(PROGRESS_GLOBAL_EVT, payload={"progress": False})

        queue_event(ACTIVITY_GLOBAL_EVT, payload={"text": {"derp": True}})
        queue_event(PROGRESS_GLOBAL_EVT, payload={"progress": {"herp": False}})

        queue_event(ACTIVITY_GLOBAL_EVT, payload={"text": {}})
        queue_event(PROGRESS_GLOBAL_EVT, payload={"progress": {}})


        # OMPE-14601: This test still has error log from carb.dictionary.plugin because of invalid value
        # we just make sure it will not crash
        await self.finalize_test_no_image()

    async def finalize_test(self, golden_img_name: str):
        await super().finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name=golden_img_name)