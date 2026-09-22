# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.app
import omni.kit.test
import omni.timeline
from ..zoom_handler import Range, ZoomHandler, ZoomState


class TestZoomHandler(omni.kit.test.AsyncTestCase):
    async def test_zoom(self):
        timeline_name = "New timeline"
        timeline_fps = 24
        timeline = omni.timeline.get_timeline_interface(timeline_name=timeline_name)
        timeline.set_time_codes_per_second(timeline_fps)
        timeline.set_end_time(10)
        timeline.set_start_time(0)
        await omni.kit.app.get_app().next_update_async()
        timeline_start_time_code = timeline.time_to_time_code(timeline.get_start_time())
        timeline_end_time_code = timeline.time_to_time_code(timeline.get_end_time())

        ## Range object
        start = 10
        end = 42
        range = Range(start=start, end=end)
        self.assertEqual(start, range.start)
        self.assertEqual(end, end)

        ## ZoomState object
        self._zoom_state: ZoomState = ZoomHandler().get_zoom(timeline_name=timeline_name)
        self.assertEqual(self._zoom_state.timeline_name, timeline_name)
        self._assert_zoom_state(False, 0, 0, 0, 0)
        self._assert_timeline(timeline, timeline_start_time_code, timeline_end_time_code)

        ## Normal range
        self._zoom_state.normal_range = Range(timeline_start_time_code, timeline_end_time_code)
        self._assert_zoom_state(False, timeline_start_time_code, timeline_end_time_code, 0, 0)
        self._assert_timeline(timeline, timeline_start_time_code, timeline_end_time_code)

        ## Zoom
        zoom_start_time_code = timeline.time_to_time_code(3)
        zoom_end_time_code = timeline.time_to_time_code(6)
        self._zoom_state.zoom(Range(zoom_start_time_code, zoom_end_time_code))
        await omni.kit.app.get_app().next_update_async()
        self._assert_zoom_state(True, timeline_start_time_code, timeline_end_time_code,
            zoom_start_time_code, zoom_end_time_code)
        self._assert_timeline(timeline, zoom_start_time_code, zoom_end_time_code)

        ## Undo
        self._zoom_state.reset_zoom()
        await omni.kit.app.get_app().next_update_async()
        self.assertFalse(self._zoom_state.zoomed)
        self._assert_timeline(timeline, timeline_start_time_code, timeline_end_time_code)

        ## Cull at borders
        zoom_start_time_code = -1000
        zoom_end_time_code = 1000000
        self._zoom_state.zoom(Range(zoom_start_time_code, zoom_end_time_code))
        await omni.kit.app.get_app().next_update_async()
        self._assert_zoom_state(True, timeline_start_time_code, timeline_end_time_code,
            timeline_start_time_code, timeline_end_time_code)
        self._assert_timeline(timeline, timeline_start_time_code, timeline_end_time_code)

        ## Second timeline
        other_timeline_name = ''  # Main timeline to test the default parameter in get_zoom below
        other_timeline_fps = 60
        other_timeline = omni.timeline.get_timeline_interface(timeline_name=other_timeline_name)
        other_timeline.set_time_codes_per_second(other_timeline_fps)
        other_timeline.set_end_time(8)
        other_timeline.set_start_time(1)
        await omni.kit.app.get_app().next_update_async()
        other_timeline_start_time_code = other_timeline.time_to_time_code(other_timeline.get_start_time())
        other_timeline_end_time_code = other_timeline.time_to_time_code(other_timeline.get_end_time())

        other_zoom_state: ZoomState = ZoomHandler().get_zoom()  # Default parameter
        self.assertEqual(other_zoom_state.timeline_name, other_timeline_name)
        other_zoom_start_time_code = timeline.time_to_time_code(4)
        other_zoom_end_time_code = timeline.time_to_time_code(7)
        other_zoom_state.normal_range = Range(other_timeline_start_time_code, other_timeline_end_time_code)
        other_zoom_state.zoom(Range(other_zoom_start_time_code, other_zoom_end_time_code))
        await omni.kit.app.get_app().next_update_async()
        # Assert the first timeline and zoom state
        self._assert_zoom_state(True, timeline_start_time_code, timeline_end_time_code,
            timeline_start_time_code, timeline_end_time_code)
        self._assert_timeline(timeline, timeline_start_time_code, timeline_end_time_code)
        # Assert the seconds (other) timeline and zoom state
        self._zoom_state = other_zoom_state
        self._assert_zoom_state(True, other_timeline_start_time_code, other_timeline_end_time_code,
            other_zoom_start_time_code, other_zoom_end_time_code)
        self._assert_timeline(other_timeline, other_zoom_start_time_code, other_zoom_end_time_code)

        ## Destroy
        ZoomHandler().destroy()
        self._zoom_state: ZoomState = ZoomHandler().get_zoom(timeline_name=timeline_name)
        self._assert_zoom_state(False, 0, 0, 0, 0)

        omni.timeline.destroy_timeline(timeline_name=timeline_name)

    def _assert_zoom_state(self, is_zoomed, normal_start, normal_end, zoomed_start, zoomed_end):
        self.assertEqual(self._zoom_state.zoomed, is_zoomed)
        self.assertEqual(self._zoom_state.normal_range.start, normal_start)
        self.assertEqual(self._zoom_state.normal_range.end, normal_end)
        self.assertEqual(self._zoom_state.zoom_range.start, zoomed_start)
        self.assertEqual(self._zoom_state.zoom_range.end, zoomed_end)

    def _assert_timeline(self, timeline, start_time_code, end_time_code):
        start_time = timeline.time_code_to_time(start_time_code)
        end_time = timeline.time_code_to_time(end_time_code)
        self.assertAlmostEqual(start_time, timeline.get_start_time())
        self.assertAlmostEqual(end_time, timeline.get_end_time())
