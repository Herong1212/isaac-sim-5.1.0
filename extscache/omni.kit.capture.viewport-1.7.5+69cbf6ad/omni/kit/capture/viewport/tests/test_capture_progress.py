import omni.kit.test
from omni.kit.capture.viewport import CaptureProgress, CaptureStatus


class TestCaptureProgress(omni.kit.test.AsyncTestCase):

    async def test_progress_basic_api(self):
        capture_progress = CaptureProgress()
        self.assertEqual(capture_progress.capture_status, CaptureStatus.NONE)
        capture_progress.start_capturing(total_frames=10, preroll_frames=0, capture_nth_frame=1)
        self.assertEqual(capture_progress.capture_status, CaptureStatus.CAPTURING)
        self.assertEqual(capture_progress.total_frames, 10)
        self.assertEqual(capture_progress.prerolled_frames, 0)
        self.assertEqual(capture_progress.total_preroll_frames, 0)
        self.assertFalse(capture_progress.is_prerolling())
        self.assertEqual(capture_progress.capture_every_nth_frame, 1)
        self.assertFalse(capture_progress.is_capturing_every_nth_frame())
        self.assertEqual(capture_progress.elapsed_time, "0.00s")
        self.assertEqual(capture_progress.estimated_time_remaining, "0.00s")
        self.assertEqual(capture_progress.current_frame_time, "0.00s")
        self.assertEqual(capture_progress.average_frame_time, "0.00s")
        self.assertEqual(capture_progress.encoding_time, "0.00s")
        self.assertEqual(capture_progress.current_subframe, 0)
        self.assertEqual(capture_progress.total_subframes, 1)
        self.assertEqual(capture_progress.subframe_time, "0.00s")
        self.assertEqual(capture_progress.average_time_per_subframe, "0.00s")
        capture_progress.finish_capturing()
        self.assertEqual(capture_progress.capture_status, CaptureStatus.DONE)
        capture_progress = None

        capture_progress = CaptureProgress()
        capture_progress.start_capturing(total_frames=10, preroll_frames=1, capture_nth_frame=2)
        self.assertEqual(capture_progress.capture_status, CaptureStatus.CAPTURING)
        self.assertEqual(capture_progress.total_frames, 10)
        self.assertEqual(capture_progress.prerolled_frames, 0)
        self.assertEqual(capture_progress.total_preroll_frames, 1)
        self.assertTrue(capture_progress.is_prerolling())
        self.assertEqual(capture_progress.capture_every_nth_frame, 2)
        self.assertTrue(capture_progress.is_capturing_every_nth_frame())
        capture_progress.finish_capturing()
        self.assertEqual(capture_progress.capture_status, CaptureStatus.DONE)
        capture_progress = None

    async def test_progress_time_format_string(self):
        capture_progress = CaptureProgress()
        time_string = capture_progress._get_time_string(1)
        self.assertEqual(time_string, "1.00s")

        time_string = capture_progress._get_time_string(10.25)
        self.assertEqual(time_string, "10.25s")

        time_string = capture_progress._get_time_string(60)
        self.assertEqual(time_string, "1m 0.00s")

        time_string = capture_progress._get_time_string(60.25)
        self.assertEqual(time_string, "1m 0.25s")

        time_string = capture_progress._get_time_string(3600)
        self.assertEqual(time_string, "1h 0m 0.00s")

        time_string = capture_progress._get_time_string(3600.25)
        self.assertEqual(time_string, "1h 0m 0.25s")

        time_string = capture_progress._get_time_string(3660.25)
        self.assertEqual(time_string, "1h 1m 0.25s")

    async def test_progress_single_frame_pt(self):
        capture_progress = CaptureProgress()
        capture_progress.start_capturing(total_frames=1, preroll_frames=0, capture_nth_frame=1)
        # add progress for the first subframe
        capture_progress.add_single_frame_capture_time_for_pt(subframe=0, total_subframes=8, delta_time=0.16)
        self.assertEqual(capture_progress.elapsed_time, "0.16s")
        self.assertEqual(capture_progress.estimated_time_remaining, "0.00s")
        self.assertEqual(capture_progress.current_subframe, 0)
        self.assertEqual(capture_progress.subframe_time, "0.16s")
        self.assertEqual(capture_progress.progress, 0.0)
        # add another progress for the first subframe
        capture_progress.add_single_frame_capture_time_for_pt(subframe=0, total_subframes=8, delta_time=0.18)
        self.assertEqual(capture_progress.elapsed_time, "0.34s")
        self.assertEqual(capture_progress.estimated_time_remaining, "0.00s")
        self.assertEqual(capture_progress.current_subframe, 0)
        self.assertEqual(capture_progress.subframe_time, "0.34s")
        self.assertEqual(capture_progress.progress, 0.0)
        # add progress for the second subframe, progress should change
        capture_progress.add_single_frame_capture_time_for_pt(subframe=1, total_subframes=8, delta_time=0.18)
        self.assertEqual(capture_progress.elapsed_time, "0.52s")
        self.assertEqual(capture_progress.estimated_time_remaining, "3.64s") # 0.52x7=3.64
        self.assertEqual(capture_progress.current_subframe, 1)
        self.assertEqual(capture_progress.subframe_time, "0.18s")
        self.assertEqual(capture_progress.progress, 1/8)

        capture_progress = None

    async def test_progress_single_frame_iray(self):
        capture_progress = CaptureProgress()
        capture_progress.start_capturing(total_frames=1, preroll_frames=0, capture_nth_frame=1)
        # add progress for the first subframe
        capture_progress.add_single_frame_capture_time_for_iray(subframe=0, total_subframes=8, iterations_done=16, iterations_per_subframe=32, delta_time=0.16)
        self.assertEqual(capture_progress.elapsed_time, "0.16s")
        self.assertEqual(capture_progress.estimated_time_remaining, "0.00s")
        self.assertEqual(capture_progress.current_subframe, 0)
        self.assertEqual(capture_progress.path_trace_iteration_num, 16)
        self.assertEqual(capture_progress.progress, 0.0)
        # add another progress for the first subframe
        capture_progress.add_single_frame_capture_time_for_iray(subframe=0, total_subframes=8, iterations_done=32, iterations_per_subframe=32, delta_time=0.18)
        self.assertEqual(capture_progress.elapsed_time, "0.34s")
        self.assertEqual(capture_progress.estimated_time_remaining, "0.00s")
        self.assertEqual(capture_progress.current_subframe, 0)
        self.assertEqual(capture_progress.path_trace_iteration_num, 32)
        self.assertEqual(capture_progress.progress, 0.0)
        # add progress for the second subframe, progress should change
        capture_progress.add_single_frame_capture_time_for_iray(subframe=1, total_subframes=8, iterations_done=16, iterations_per_subframe=32, delta_time=0.18)
        self.assertEqual(capture_progress.elapsed_time, "0.52s")
        self.assertEqual(capture_progress.estimated_time_remaining, "3.64s") # 0.52x7=3.64
        self.assertEqual(capture_progress.current_subframe, 1)
        self.assertEqual(capture_progress.path_trace_iteration_num, 16)
        self.assertEqual(capture_progress.progress, 1/8)

        capture_progress = None


