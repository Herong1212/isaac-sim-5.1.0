import math

import carb
import carb.settings
from omni.anim.widget.timeline import SMPTE_Timecode
from omni.kit.test.async_unittest import AsyncTestCase


class TestSmpte(AsyncTestCase):
    async def test_from_frames(self):
        smpte_1_30 = SMPTE_Timecode.from_frames(1, 30)
        self.assertEqual(str(smpte_1_30), "00:00:00.01")
        self.assertEqual(smpte_1_30.frames, 1)
        smpte_15_30 = SMPTE_Timecode.from_frames(15, 30)
        self.assertEqual(str(smpte_15_30), "00:00:00.15")
        self.assertEqual(smpte_15_30.frames, 15)
        smpte_29_30 = SMPTE_Timecode.from_frames(29, 30)
        self.assertEqual(str(smpte_29_30), "00:00:00.29")
        self.assertEqual(smpte_29_30.frames, 29)
        smpte_30_30 = SMPTE_Timecode.from_frames(30, 30)
        self.assertEqual(str(smpte_30_30), "00:00:01.00")
        self.assertEqual(smpte_30_30.frames, 0)
        self.assertEqual(smpte_30_30.seconds, 1)
        smpte_60_30 = SMPTE_Timecode.from_frames(60, 30)
        self.assertEqual(str(smpte_60_30), "00:00:02.00")
        self.assertEqual(smpte_60_30.frames, 0)
        self.assertEqual(smpte_60_30.seconds, 2)
        smpte_1800_30 = SMPTE_Timecode.from_frames(1800, 30)
        self.assertEqual(str(smpte_1800_30), "00:01:00.00")
        self.assertEqual(smpte_1800_30.frames, 0)
        self.assertEqual(smpte_1800_30.minutes, 1)
        smpte_108000_30 = SMPTE_Timecode.from_frames(108000, 30)
        self.assertEqual(str(smpte_108000_30), "01:00:00.00")
        self.assertEqual(smpte_108000_30.frames, 0)
        self.assertEqual(smpte_108000_30.hours, 1)

    async def test_frames_fractional_to_smpte(self):
        smpte_1_30 = SMPTE_Timecode.from_frames(1.5, 30)
        self.assertEqual(str(smpte_1_30), "00:00:00.01*")
        self.assertEqual(smpte_1_30.frames, 1)
        self.assertEqual(smpte_1_30.frames_fractional, 0.5)

    async def test_handle_zero_framerate(self):
        smpte_1_0 = SMPTE_Timecode.from_frames(1, 0)
        self.assertTrue(math.isnan(smpte_1_0))
