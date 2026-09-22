# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb.settings
import omni.kit.app
import omni.kit.test
import omni.usd

from pathlib import Path
from pxr import UsdGeom

PERSISTENT_SETTINGS_PREFIX = "/persistent"
STAGE_TIME_CODES_PER_SECOND_SETTING_PATH = PERSISTENT_SETTINGS_PREFIX + "/app/stage/timeCodesPerSecond"
STAGE_TIME_RANGE_SETTING_PATH = PERSISTENT_SETTINGS_PREFIX + "/app/stage/timeCodeRange"

class TestUsdTimeline(omni.kit.test.AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._settings = carb.settings.get_settings()
        self._test_scene = str(Path(__file__).parent.joinpath("data").joinpath("test_usd_timeline.usda"))

    async def setUp(self):
        self._usd_context = omni.usd.get_context()
        self._app = omni.kit.app.get_app()

    async def test_usd_timeline(self):
        timeline = self._usd_context.get_timeline()

        # Set current time to 0.0 to make sure it's smaller than the stage's start time.
        timeline.set_current_time(0.0)
        timeline.commit()
        await self._app.next_update_async()

        await self._usd_context.open_stage_async(self._test_scene)
        stage = self._usd_context.get_stage()

        start_time_code = stage.GetStartTimeCode()
        end_time_code = stage.GetEndTimeCode()
        time_codes_per_second = stage.GetTimeCodesPerSecond()

        await self._app.next_update_async()

        # Make sure the start time and end time are set correctly to the stage's start and end time codes
        self.assertEqual(timeline.time_to_time_code(timeline.get_start_time()), start_time_code)
        self.assertEqual(timeline.time_to_time_code(timeline.get_end_time()), end_time_code)
        self.assertEqual(timeline.get_time_codes_per_second(), time_codes_per_second)

        # Since the stage's startTime is not 0, the current time should be set to the stage's start time code.
        # Make sure the current time is set correctly to the stage's start time code
        current_time_code = timeline.time_to_time_code(timeline.get_current_time())
        self.assertEqual(current_time_code, start_time_code)

        cube = stage.GetPrimAtPath("/AnimatedCube")
        cube_api = UsdGeom.XformCommonAPI(cube)

        # Make sure the cube is at the correct position at current time code
        translate = cube_api.GetXformVectors(current_time_code)[0]
        self.assertEqual(translate, (100, 0, 0))

        # Make sure the cube is at the correct position at end time code
        timeline.set_current_time(timeline.time_code_to_time(end_time_code))
        await self._app.next_update_async()

        current_time_code = timeline.time_to_time_code(timeline.get_current_time())
        translate = cube_api.GetXformVectors(current_time_code)[0]
        self.assertEqual(translate, (200, 0, 0))

        # Open a new stage and make sure timeline is reset to default values
        await self._usd_context.new_stage_async()
        await self._app.next_update_async()

        default_time_codes_per_second = self._settings.get(STAGE_TIME_CODES_PER_SECOND_SETTING_PATH)
        default_time_range = self._settings.get(STAGE_TIME_RANGE_SETTING_PATH)

        self.assertEqual(timeline.get_time_codes_per_second(), default_time_codes_per_second)
        self.assertEqual(timeline.get_start_time(), default_time_range[0] / default_time_codes_per_second)
        self.assertEqual(timeline.get_end_time(), default_time_range[1] / default_time_codes_per_second)

    async def test_usd_timeline_sync(self):
        """Test bidirectional synchronization between USD Stage and omni.timeline"""
        # Create new stage
        await self._usd_context.new_stage_async()
        stage = self._usd_context.get_stage()
        timeline = self._usd_context.get_timeline()
        await self._app.next_update_async()

        # Test USD to Timeline sync
        stage.SetStartTimeCode(10.0)
        stage.SetEndTimeCode(50.0)
        stage.SetTimeCodesPerSecond(30.0)
        await self._app.next_update_async()

        # Verify timeline received USD changes
        self.assertEqual(timeline.time_to_time_code(timeline.get_start_time()), 10.0)
        self.assertEqual(timeline.time_to_time_code(timeline.get_end_time()), 50.0)
        self.assertEqual(timeline.get_time_codes_per_second(), 30.0)

        # Test Timeline to USD sync
        timeline.set_time_codes_per_second(24.0)
        await self._app.next_update_async()

        # Verify USD received timeline changes
        self.assertEqual(stage.GetTimeCodesPerSecond(), 24.0)

        # Test timeline range updates
        new_start = timeline.time_code_to_time(5.0)
        new_end = timeline.time_code_to_time(100.0)
        timeline.set_start_time(new_start)
        timeline.set_end_time(new_end)
        await self._app.next_update_async()

        # Verify USD received new range
        self.assertEqual(stage.GetStartTimeCode(), 5.0)
        self.assertEqual(stage.GetEndTimeCode(), 100.0)
