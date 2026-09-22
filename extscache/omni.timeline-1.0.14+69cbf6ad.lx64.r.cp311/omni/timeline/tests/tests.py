# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb.events

import omni.kit.app
import omni.kit.test
import omni.timeline
import carb.settings
import carb.eventdispatcher

import queue
import asyncio

from time import sleep


USE_FIXED_TIMESTEP_PATH = "/app/player/useFixedTimeStepping"
RUNLOOP_RATE_LIMIT_PATH = "/app/runLoops/main/rateLimitFrequency"
COMPENSATE_PLAY_DELAY_PATH = "/app/player/CompensatePlayDelayInSecs"


class TestTimeline(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._app = omni.kit.app.get_app()
        self._ed = carb.eventdispatcher.get_eventdispatcher()
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event
        )
        self._buffered_evts = queue.Queue()

        self._settings = carb.settings.acquire_settings_interface()

    async def tearDown(self):
        self._timeline = None
        self._timeline_sub = None

    async def test_timeline_api(self):
        ## Check initial states
        self.assertFalse(self._timeline.is_playing())
        self.assertTrue(self._timeline.is_stopped())
        self.assertEqual(0.0, self._timeline.get_start_time())
        self.assertEqual(0.0, self._timeline.get_end_time())
        self.assertEqual(0.0, self._timeline.get_current_time())
        self.assertEqual(0.0, self._timeline.get_time_codes_per_seconds())
        self.assertTrue(self._timeline.is_looping())
        self.assertTrue(self._timeline.is_auto_updating())
        self.assertFalse(self._timeline.is_prerolling())
        self.assertFalse(self._timeline.is_zoomed())

        ## Change start time
        start_time = -1.0
        self._timeline.set_start_time(start_time)
        self._assert_no_change_then_commit(self._timeline.get_start_time(), 0)
        self._verify_evt(omni.timeline.TimelineEventType.START_TIME_CHANGED, "startTime", start_time)
        self.assertTrue(self._buffered_evts.empty())
        self.assertEqual(start_time, self._timeline.get_start_time())
        self.assertEqual(0.0, self._timeline.get_current_time())

        ## Change end time
        end_time = 2.0
        self._timeline.set_end_time(end_time)
        self._assert_no_change_then_commit(self._timeline.get_end_time(), 0)
        self._verify_evt(omni.timeline.TimelineEventType.END_TIME_CHANGED, "endTime", end_time)
        self.assertTrue(self._buffered_evts.empty())
        self.assertEqual(end_time, self._timeline.get_end_time())
        self.assertEqual(0.0, self._timeline.get_current_time())

        ## Change timecode per second
        time_code_per_sec = 24.0
        self._timeline.set_time_codes_per_second(time_code_per_sec)
        self._assert_no_change_then_commit(self._timeline.get_time_codes_per_seconds(), 0)
        self._verify_evt(
            omni.timeline.TimelineEventType.TIME_CODE_PER_SECOND_CHANGED, "timeCodesPerSecond", time_code_per_sec
        )
        self.assertEqual(time_code_per_sec, self._timeline.get_time_codes_per_seconds())

        ## Do not allow endtime <= starttime
        ## Reset current time to start time
        frame_time = 1.0 / time_code_per_sec
        new_start_time = end_time
        self._timeline.set_start_time(new_start_time)
        self._assert_no_change_then_commit(self._timeline.get_start_time(), start_time)
        self._verify_evt(omni.timeline.TimelineEventType.START_TIME_CHANGED, "startTime", new_start_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "currentTime", new_start_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "currentTime", new_start_time)
        self._verify_evt(
            omni.timeline.TimelineEventType.END_TIME_CHANGED,
            "endTime",
            new_start_time + frame_time,
            exact=False
        )
        self.assertTrue(self._buffered_evts.empty())
        new_start_time = new_start_time + 10.0 * frame_time
        self._timeline.set_start_time(new_start_time)
        self._timeline.commit()
        self._verify_evt(omni.timeline.TimelineEventType.START_TIME_CHANGED, "startTime", new_start_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "currentTime", new_start_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "currentTime", new_start_time)
        self._verify_evt(
            omni.timeline.TimelineEventType.END_TIME_CHANGED,
            "endTime",
            new_start_time + frame_time,
            exact=False
        )
        self.assertTrue(self._buffered_evts.empty())

        new_end_time = self._timeline.get_start_time()
        self._timeline.set_end_time(new_end_time)
        self._timeline.commit()
        self._verify_evt(omni.timeline.TimelineEventType.END_TIME_CHANGED, "endTime", new_end_time)
        self._verify_evt(
            omni.timeline.TimelineEventType.START_TIME_CHANGED,
            "startTime",
            new_end_time - frame_time,
            exact=False
        )
        self.assertTrue(self._buffered_evts.empty())
        new_end_time = new_end_time - 10.0 * frame_time
        self._timeline.set_end_time(new_end_time)
        self._timeline.commit()
        self._verify_evt(omni.timeline.TimelineEventType.END_TIME_CHANGED, "endTime", new_end_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "currentTime", new_end_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "currentTime", new_end_time)
        self._verify_evt(
            omni.timeline.TimelineEventType.START_TIME_CHANGED,
            "startTime",
            new_end_time - frame_time,
            exact=False
        )
        self.assertTrue(self._buffered_evts.empty())
        # Revert
        start_time = 1.0
        self._timeline.set_start_time(start_time)
        self._timeline.set_end_time(end_time)
        self._timeline.set_current_time(start_time)
        self._timeline.commit()
        self._clear_evt_queue()  # Don't care

        ## Time conversion
        self.assertAlmostEqual(self._timeline.time_to_time_code(-1), -24, places=5)
        self.assertAlmostEqual(self._timeline.time_to_time_code(0), 0, places=5)
        self.assertAlmostEqual(self._timeline.time_to_time_code(0.5), 12, places=5)
        self.assertAlmostEqual(self._timeline.time_to_time_code(2), 48, places=5)

        self.assertAlmostEqual(self._timeline.time_code_to_time(-24), -1, places=5)
        self.assertAlmostEqual(self._timeline.time_code_to_time(0), 0, places=5)
        self.assertAlmostEqual(self._timeline.time_code_to_time(12), 0.5, places=5)
        self.assertAlmostEqual(self._timeline.time_code_to_time(48), 2, places=5)
        self.assertTrue(self._buffered_evts.empty())

        ## Set current time
        old_current_time = self._timeline.get_current_time()
        new_current_time = start_time
        self._timeline.set_current_time(new_current_time)
        self._assert_no_change_then_commit(self._timeline.get_current_time(), old_current_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "currentTime", new_current_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "currentTime", new_current_time)
        self.assertEqual(new_current_time, self._timeline.get_current_time())

        # dt is smaller than 1 frame
        old_current_time = self._timeline.get_current_time()
        expected_dt = 0.5 * frame_time
        new_current_time = start_time + expected_dt
        self._timeline.set_current_time(new_current_time)
        self._assert_no_change_then_commit(self._timeline.get_current_time(), old_current_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "dt", expected_dt, False)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "dt", expected_dt, False)
        self.assertEqual(new_current_time, self._timeline.get_current_time())

        # Edge case: dt is exactly one frame
        old_current_time = self._timeline.get_current_time()
        expected_dt = 1.0 * frame_time
        new_current_time = new_current_time + expected_dt
        self._timeline.set_current_time(new_current_time)
        self._assert_no_change_then_commit(self._timeline.get_current_time(), old_current_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "dt", expected_dt, False)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "dt", expected_dt, False)
        self.assertEqual(new_current_time, self._timeline.get_current_time())

        # If dt would be too large to simulate, it is set to zero
        old_current_time = self._timeline.get_current_time()
        expected_dt = 0
        new_current_time = new_current_time + 1.5 * frame_time
        self._timeline.set_current_time(new_current_time)
        self._assert_no_change_then_commit(self._timeline.get_current_time(), old_current_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "dt", expected_dt, False)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "dt", expected_dt, False)
        self.assertEqual(new_current_time, self._timeline.get_current_time())

        # If dt would be negative, it is set to zero
        old_current_time = self._timeline.get_current_time()
        expected_dt = 0
        new_current_time = start_time
        self._timeline.set_current_time(new_current_time)
        self._assert_no_change_then_commit(self._timeline.get_current_time(), old_current_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "dt", expected_dt, False)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "dt", expected_dt, False)
        self.assertEqual(new_current_time, self._timeline.get_current_time())

        ## Forward one frame
        old_current_time = self._timeline.get_current_time()
        self._timeline.forward_one_frame()
        self._assert_no_change_then_commit(self._timeline.get_current_time(), old_current_time)
        # Forward one frame triggers a play and pause if the timeline was not playing
        self._verify_evt(omni.timeline.TimelineEventType.PLAY)
        self._verify_evt(
            omni.timeline.TimelineEventType.CURRENT_TIME_TICKED,
            "currentTime", start_time + 1.0 / time_code_per_sec
        )
        self._verify_evt(
            omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT,
            "currentTime", start_time + 1.0 / time_code_per_sec
        )
        self._verify_evt(omni.timeline.TimelineEventType.PAUSE)
        self.assertAlmostEqual(start_time + 1.0 / time_code_per_sec, self._timeline.get_current_time(), places=5)

        ## Rewind one frame
        old_current_time = self._timeline.get_current_time()
        self._timeline.rewind_one_frame()
        self._assert_no_change_then_commit(self._timeline.get_current_time(), old_current_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "currentTime", start_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "currentTime", start_time)
        self.assertAlmostEqual(start_time, self._timeline.get_current_time(), places=5)
        new_current_time = self._timeline.get_current_time()

        ## Set target framerate.
        DEFAULT_TARGET_FRAMERATE = 60
        self.assertEqual(self._timeline.get_target_framerate(), DEFAULT_TARGET_FRAMERATE)
        target_vs_set_fps = [
            [2 * time_code_per_sec - 1, 2 * time_code_per_sec],
            [3 * time_code_per_sec + 15, 4 * time_code_per_sec],
            [5 * time_code_per_sec - 7, 5 * time_code_per_sec],
            [time_code_per_sec, time_code_per_sec]  # this comes last to avoid frame skipping in Play tests
        ]
        self._timeline.play()
        self._timeline.commit()
        self._clear_evt_queue()  # don't care
        for fps in target_vs_set_fps:
            target_fps = fps[0]
            desired_runloop_fps = fps[1]
            old_fps = self._timeline.get_target_framerate()
            self._timeline.set_target_framerate(target_fps)
            self._assert_no_change_then_commit(self._timeline.get_target_framerate(), old_fps)
            self._verify_evt(
                omni.timeline.TimelineEventType.TARGET_FRAMERATE_CHANGED, "targetFrameRate", target_fps
            )
            self.assertEqual(target_fps, self._timeline.get_target_framerate())
            self.assertEqual(self._settings.get(RUNLOOP_RATE_LIMIT_PATH), desired_runloop_fps)
        self._timeline.stop()
        self._timeline.commit()
        self._clear_evt_queue()  # don't care

        ## Play
        self._timeline.play()
        self._assert_no_change_then_commit(self._timeline.is_playing(), False)
        self._verify_evt(omni.timeline.TimelineEventType.PLAY)
        self.assertTrue(self._settings.get(USE_FIXED_TIMESTEP_PATH))
        self.assertTrue(self._timeline.is_playing())
        self.assertFalse(self._timeline.is_stopped())

        await self._app.next_update_async()
        dt = 1.0 / time_code_per_sec  # timeline uses fixed dt by default
        self.assertAlmostEqual(new_current_time + dt, self._timeline.get_current_time(), places=5)
        self._verify_evt(
            omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "currentTime", new_current_time + dt, exact=False
        )
        self._verify_evt(
            omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "dt", dt, exact=False
        )

        # varying dt
        self._timeline.stop()
        self._settings.set(USE_FIXED_TIMESTEP_PATH, False)
        self._timeline.play()
        self._timeline.commit()
        self._clear_evt_queue()
        new_current_time = self._timeline.get_current_time()
        dt = await self._app.next_update_async()
        self.assertAlmostEqual(new_current_time + dt, self._timeline.get_current_time(), places=5)
        self._verify_evt(
            omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "currentTime", new_current_time + dt, exact=False
        )
        self._verify_evt(
            omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "dt", dt, exact=False
        )
        self._settings.set(USE_FIXED_TIMESTEP_PATH, True)

        ## Pause
        self._timeline.pause()
        self._assert_no_change_then_commit(self._timeline.is_playing(), True)
        self._verify_evt(omni.timeline.TimelineEventType.PAUSE)
        self.assertFalse(self._timeline.is_playing())
        self.assertFalse(self._timeline.is_stopped())

        # current time should not change
        await self._app.next_update_async()
        self.assertAlmostEqual(new_current_time + dt, self._timeline.get_current_time(), places=5)

        # permanent update event is still ticking
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT)

        ## Stop
        self._timeline.stop()
        self._assert_no_change_then_commit(self._timeline.is_stopped(), False)
        self._verify_evt(omni.timeline.TimelineEventType.STOP)
        self.assertFalse(self._timeline.is_playing())
        self.assertTrue(self._timeline.is_stopped())
        self.assertEqual(start_time, self._timeline.get_current_time())

        ## Loop
        # self._timeline.set_looping(True)  # it was already set
        self._timeline.play()
        self._timeline.commit()

        dt = 1.0 / time_code_per_sec  # timeline uses fixed dt by default
        elapsed_time = 0.0
        while elapsed_time < end_time * 1.5:
            await self._app.next_update_async()
            elapsed_time += dt

        self._timeline.pause()
        self._timeline.commit()
        self._clear_evt_queue()  # don't care

        # time is looped
        loopped_time = elapsed_time % (end_time - start_time) + start_time
        self.assertAlmostEqual(loopped_time, self._timeline.get_current_time(), places=5)

        ## Non-loop
        self._timeline.set_looping(False)
        self._assert_no_change_then_commit(self._timeline.is_looping(), True)
        self._verify_evt(omni.timeline.TimelineEventType.LOOP_MODE_CHANGED, "looping", False)
        self._timeline.stop()
        self._timeline.play()
        self._timeline.commit()

        elapsed_time = 0.0
        while elapsed_time < end_time * 1.5:
            dt = await self._app.next_update_async()
            elapsed_time += dt

        # timeline paused when reached the end
        self.assertFalse(self._timeline.is_playing())
        self.assertFalse(self._timeline.is_stopped())
        self.assertAlmostEqual(end_time, self._timeline.get_current_time(), places=5)

        ## Change end time that should change current time because current time was > end time
        self._clear_evt_queue()
        end_time = 1.5
        current_time = self._timeline.get_current_time()
        self._timeline.set_end_time(end_time)
        self._timeline.commit()
        self._verify_evt(omni.timeline.TimelineEventType.END_TIME_CHANGED, "endTime", end_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "currentTime", end_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "currentTime", end_time)
        # OM-75796: changing the end time moves current time to end when timeline is not playing
        self.assertTrue(self._buffered_evts.empty())
        self.assertEqual(end_time, self._timeline.get_end_time())
        self.assertEqual(end_time, self._timeline.get_current_time())
        self._timeline.stop()
        # OM-75796: changing the end time moves current time to end when timeline is playing
        self._timeline.play()
        self._timeline.set_current_time(end_time)  # someting after the new end time
        self._timeline.commit()
        self._clear_evt_queue()  # don't care
        end_time = 1.25
        self._timeline.set_end_time(end_time)
        self._timeline.commit()
        self._verify_evt(omni.timeline.TimelineEventType.END_TIME_CHANGED, "endTime", end_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "currentTime", end_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "currentTime", end_time)
        self.assertTrue(self._buffered_evts.empty())
        self.assertEqual(end_time, self._timeline.get_end_time())
        self.assertEqual(end_time, self._timeline.get_current_time())
        # OM-75796: changing the start time moves current time to start when timeline is playing
        end_time = 100
        self._timeline.set_end_time(end_time)
        self._timeline.commit()
        self._clear_evt_queue()  # don't care
        start_time = 2.0
        self._timeline.set_start_time(start_time)
        self._timeline.commit()
        self._verify_evt(omni.timeline.TimelineEventType.START_TIME_CHANGED, "startTime", start_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "currentTime", start_time)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "currentTime", start_time)
        self.assertTrue(self._buffered_evts.empty())
        self.assertEqual(start_time, self._timeline.get_start_time())
        self.assertEqual(start_time, self._timeline.get_current_time())
        self._timeline.stop()
        self._timeline.commit()

        ## Auto update
        self._clear_evt_queue()
        self._timeline.set_auto_update(False)
        self._assert_no_change_then_commit(self._timeline.is_auto_updating(), True)
        self._verify_evt(omni.timeline.TimelineEventType.AUTO_UPDATE_CHANGED, "autoUpdate", False)
        self.assertFalse(self._timeline.is_auto_updating())

        self._timeline.set_looping(True)
        self._timeline.play()
        for i in range(5):
            await self._app.next_update_async()
        self.assertEqual(start_time, self._timeline.get_current_time())

        ## Prerolling
        self._clear_evt_queue()
        self._timeline.set_prerolling(True)
        self._assert_no_change_then_commit(self._timeline.is_prerolling(), False)
        self.assertTrue(self._timeline.is_prerolling())
        self._verify_evt(omni.timeline.TimelineEventType.PREROLLING_CHANGED, "prerolling", True)

        ## Change TimeCodesPerSeconds and verify if CurrentTime is properly refitted.
        time_codes_per_second = 24
        timecode = 50
        self._timeline.set_time_codes_per_second(time_codes_per_second)
        self._timeline.set_start_time(0)
        self._timeline.set_end_time(100)
        self._timeline.set_current_time(timecode)
        self._timeline.set_time_codes_per_second(100)
        self._timeline.commit()
        # we stay the same timecode after change TimeCodesPerSeconds
        self.assertEqual(timecode, self._timeline.get_current_time())

        ## Play in range
        self._timeline.stop()
        self._timeline.set_auto_update(True)
        start_time_seconds = 0
        range_start_timecode = 20
        range_end_timecode = 30
        end_time_seconds = 40
        self._timeline.set_start_time(start_time_seconds)
        self._timeline.set_end_time(end_time_seconds)
        self._timeline.commit()
        self._clear_evt_queue()
        self._timeline.play(range_start_timecode, range_end_timecode, False)
        self._assert_no_change_then_commit(True, True)
        self._verify_evt(omni.timeline.TimelineEventType.PLAY)
        self.assertTrue(self._timeline.is_playing())
        self.assertFalse(self._timeline.is_stopped())

        await asyncio.sleep(5)

        self.assertEqual(start_time_seconds, self._timeline.get_start_time())
        self.assertEqual(end_time_seconds, self._timeline.get_end_time())
        self.assertEqual(range_end_timecode, self._timeline.get_current_time() * self._timeline.get_time_codes_per_seconds())

        ## tentative time
        current_time = 2.0
        tentative_time = 2.5
        self._timeline.set_current_time(current_time)
        self._timeline.commit()
        self._clear_evt_queue()
        self._timeline.set_tentative_time(tentative_time)
        self._assert_no_change_then_commit(self._timeline.get_tentative_time(), current_time)
        self._verify_evt(omni.timeline.TimelineEventType.TENTATIVE_TIME_CHANGED)
        self.assertEqual(tentative_time, self._timeline.get_tentative_time())
        self.assertEqual(current_time, self._timeline.get_current_time())
        self._timeline.clear_tentative_time()
        self._assert_no_change_then_commit(self._timeline.get_tentative_time(), tentative_time)
        self.assertEqual(self._timeline.get_tentative_time(), self._timeline.get_current_time())

        ## tentative time and events
        tentative_time = 3.5
        self._timeline.set_tentative_time(tentative_time)
        self._timeline.commit()
        self._clear_evt_queue()
        self._timeline.forward_one_frame()
        self._assert_no_change_then_commit(True, True)
        self._verify_evt(omni.timeline.TimelineEventType.PLAY)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT)
        self._verify_evt(omni.timeline.TimelineEventType.PAUSE)
        self.assertTrue(self._buffered_evts.empty())  # tentative time was used, no other event
        self._timeline.set_tentative_time(tentative_time)
        self._timeline.commit()
        self._clear_evt_queue()
        self._timeline.rewind_one_frame()
        self._assert_no_change_then_commit(True, True)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT)
        self.assertTrue(self._buffered_evts.empty())  # tentative time was used, no other event

        ## Forward one frame while the timeline is playing: only time is ticked, no play/pause
        self._timeline.play()
        self._timeline.commit()
        self._clear_evt_queue() # don't care
        old_current_time = self._timeline.get_current_time()
        tcps_current = self._timeline.get_time_codes_per_seconds()
        self._timeline.forward_one_frame()
        self._assert_no_change_then_commit(self._timeline.get_current_time(), old_current_time)
        self._verify_evt(
            omni.timeline.TimelineEventType.CURRENT_TIME_TICKED,
            "currentTime", old_current_time + 1.0 / tcps_current
        )
        self._verify_evt(
            omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT,
            "currentTime", old_current_time + 1.0 / tcps_current
        )
        self.assertTrue(self._buffered_evts.empty())
        self.assertAlmostEqual(old_current_time + 1.0 / tcps_current, self._timeline.get_current_time(), places=5)
        self._timeline.stop()
        self._timeline.commit()
        self._clear_evt_queue() # don't care

        ## substepping
        subsample_rate = 3
        old_subsample_rate = self._timeline.get_ticks_per_frame()
        self._timeline.set_ticks_per_frame(subsample_rate)
        self._assert_no_change_then_commit(self._timeline.get_ticks_per_frame(), old_subsample_rate)
        self._verify_evt(
            omni.timeline.TimelineEventType.TICKS_PER_FRAME_CHANGED, "ticksPerFrame", subsample_rate, exact=True
        )
        self.assertEqual(self._timeline.get_ticks_per_frame(), subsample_rate)
        self.assertEqual(self._timeline.get_ticks_per_second(), subsample_rate * self._timeline.get_time_codes_per_seconds())
        self._timeline.play()
        self._timeline.commit()
        self._verify_evt(omni.timeline.TimelineEventType.PLAY)
        await self._app.next_update_async()
        for i in range(subsample_rate):
            self._verify_evt(
                omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "tick", i, exact=True
            )
            self._verify_evt(
                omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "tick", i, exact=True
            )
        tick_dt = 1.0 / (self._timeline.get_time_codes_per_seconds() * subsample_rate)
        await self._app.next_update_async()
        for i in range(subsample_rate):
            self._verify_evt(
                omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, "dt", tick_dt, exact=False
            )
            self._verify_evt(
                omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, "dt", tick_dt, exact=False
            )
        start_time = self._timeline.get_current_time()
        await self._app.next_update_async()
        for i in range(subsample_rate):
            self._verify_evt(
                omni.timeline.TimelineEventType.CURRENT_TIME_TICKED,
                "currentTime",
                start_time + (i + 1) * tick_dt,
                exact=False
            )
            self._verify_evt(
                omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT,
                "currentTime",
                start_time + (i + 1) * tick_dt,
                exact=False
            )
        self._timeline.stop()
        self._timeline.commit()

        ## substepping with event handling and event firing in the kit runloop
        self._tick = True
        def pause(e: carb.events.IEvent):
            if e.type == int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED):
                if self._tick:
                    self._timeline.pause()
                else:
                    self._timeline.play()
                self._tick = not self._tick

        pause_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(pause, order=1)
        start_time = self._timeline.get_current_time()
        self._timeline.play()
        self._timeline.commit()
        self._clear_evt_queue()
        # callbacks call stop and pause but we still finish the frame
        await self._app.post_update_async()
        for i in range(subsample_rate):
            self._verify_evt(
                omni.timeline.TimelineEventType.CURRENT_TIME_TICKED,
                "currentTime",
                start_time + (i + 1) * tick_dt,
                exact=False
            )
            self._verify_evt(
                omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT,
                "currentTime",
                start_time + (i + 1) * tick_dt,
                exact=False
            )
        # No events until the next frame
        self.assertTrue(self._buffered_evts.empty())
        # wait a until the next update, events are then re-played
        await self._app.next_update_async()
        self._tick = True
        for i in range(subsample_rate):
            if self._tick:
                self._verify_evt(omni.timeline.TimelineEventType.PAUSE)
            else:
                self._verify_evt(omni.timeline.TimelineEventType.PLAY)
            self._tick = not self._tick
        self.assertEqual(self._timeline.is_playing(), self._tick)
        pause_sub = None
        # stop for the next test
        self._timeline.stop()
        self._timeline.commit()
        self._clear_evt_queue()

        ## frame skipping
        self.assertFalse(self._timeline.get_play_every_frame())  # off by default
        self.assertAlmostEqual(self._settings.get(COMPENSATE_PLAY_DELAY_PATH), 0.0)  # No compensation by default
        self._timeline.set_time_codes_per_second(time_codes_per_second)
        self._timeline.set_ticks_per_frame(1)
        self._timeline.set_target_framerate(3.0 * time_code_per_sec)
        self._timeline.play()
        self._timeline.commit()
        self._clear_evt_queue()
        await self._app.next_update_async()
        # events are fired on the first call
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT)
        # 2 frames are skipped
        await self._app.next_update_async()
        self.assertTrue(self._buffered_evts.empty())
        await self._app.next_update_async()
        self.assertTrue(self._buffered_evts.empty())
        # firing events again
        await self._app.next_update_async()
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT)
        self._timeline.stop()
        self._timeline.commit()
        self._clear_evt_queue()  # don't care

        # fast mode, target frame rate is still 3 * time_code_per_sec, but frames should not be skipped
        self._timeline.set_play_every_frame(True)
        self._assert_no_change_then_commit(self._timeline.get_play_every_frame(), False)
        self._verify_evt(
            omni.timeline.TimelineEventType.PLAY_EVERY_FRAME_CHANGED, "playEveryFrame", True, exact=True
        )
        self._timeline.play()
        self._timeline.commit()
        self._verify_evt(omni.timeline.TimelineEventType.PLAY)
        await self._app.next_update_async()
        for i in range(5):
            await self._app.next_update_async()
            # events are fired for every call
            self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED)
            self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT)
        self._timeline.set_play_every_frame(False)
        self._timeline.commit()
        self._clear_evt_queue()  # don't care

        ## test multiple pipelines
        self._timeline.stop()
        self._timeline.commit()
        default_timeline_current_time = self._timeline.get_current_time()
        new_timeline_name = "new_timeline"
        self._new_timeline = omni.timeline.get_timeline_interface(new_timeline_name)
        self._new_timeline.set_current_time(default_timeline_current_time + 1.0)
        self._new_timeline.set_end_time(default_timeline_current_time + 10.0)
        self._new_timeline.commit()
        new_timeline_current_time = self._new_timeline.get_current_time()
        self.assertNotEqual(new_timeline_current_time, self._timeline.get_current_time())
        self._new_timeline.play()
        self._new_timeline.commit()
        self.assertFalse(self._timeline.is_playing())
        self.assertTrue(self._new_timeline.is_playing())
        for i in range(10):
            await self._app.next_update_async()
        self.assertNotEqual(new_timeline_current_time, self._new_timeline.get_current_time())
        self.assertEqual(default_timeline_current_time, self._timeline.get_current_time())

        # OM-76359: test that cleaning works
        self._new_timeline = None
        self._dummy_timeline = omni.timeline.get_timeline_interface('dummy')
        self._new_timeline = omni.timeline.get_timeline_interface(new_timeline_name)
        self.assertAlmostEqual(0.0, self._new_timeline.get_current_time(), places=5)

        omni.timeline.destroy_timeline(new_timeline_name)
        omni.timeline.destroy_timeline('dummy')

        ## commit and its silent version
        self._clear_evt_queue()
        self._timeline.set_target_framerate(17)
        self._timeline.set_time_codes_per_second(1)
        self._timeline.set_ticks_per_frame(19)
        self._timeline.play()
        self._timeline.stop()
        self._timeline.set_current_time(15)
        self._timeline.rewind_one_frame()

        self._timeline.commit_silently()

        self.assertTrue(self._buffered_evts.empty())
        self.assertAlmostEqual(self._timeline.get_target_framerate(), 17)
        self.assertAlmostEqual(self._timeline.get_time_codes_per_seconds(), 1)
        self.assertAlmostEqual(self._timeline.get_ticks_per_frame(), 19)
        self.assertFalse(self._timeline.is_playing())
        self.assertAlmostEqual(self._timeline.get_current_time(), 14)

        # Revert
        self._timeline.set_ticks_per_frame(1)
        await self._app.next_update_async()
        self._clear_evt_queue()

        self._timeline.set_start_time(1)
        self._timeline.set_end_time(10)
        self._timeline.set_current_time(5)
        self._timeline.play()
        self._timeline.forward_one_frame()
        self._timeline.rewind_one_frame()
        self.assertAlmostEqual(self._timeline.get_current_time(), 14)

        self._timeline.commit()

        self._verify_evt(omni.timeline.TimelineEventType.START_TIME_CHANGED, 'startTime', 1)
        self._verify_evt(omni.timeline.TimelineEventType.END_TIME_CHANGED, 'endTime', 10)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, 'currentTime', 10)  # currentTime is clamped to endTime from 14
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, 'currentTime', 10)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, 'currentTime', 5)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, 'currentTime', 5)
        self._verify_evt(omni.timeline.TimelineEventType.PLAY)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, 'currentTime', 6)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, 'currentTime', 6)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED, 'currentTime', 5)
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT, 'currentTime', 5)
        self.assertTrue(self._buffered_evts.empty())
        self.assertAlmostEqual(self._timeline.get_current_time(), 5)
        self.assertTrue(self._timeline.is_playing())

        self._timeline.stop()
        self._timeline.commit()
        self._clear_evt_queue()

        # calling manually to make sure they come after the API test
        #   independently of the test env
        await self._test_runloop_integration()

        await self._test_director()

    async def _test_runloop_integration(self):
        """ Test how the run loop behaves when it is controlled by the timeline
               and test proper behavior when runloop slows down
        """

        # make sure other tests do not interfere
        TIMELINE_FPS = 25.0
        RUNLOOP_FPS = TIMELINE_FPS * 4.0  # 100, 1/4 frame skipping
        self._timeline.stop()
        self._timeline.set_current_time(0.0)
        self._timeline.set_start_time(0.0)
        self._timeline.set_end_time(1000.0)
        self._timeline.set_target_framerate(RUNLOOP_FPS)
        self._timeline.set_time_codes_per_second(TIMELINE_FPS)
        self._timeline.set_play_every_frame(False)
        self._timeline.set_ticks_per_frame(1)
        self._timeline.play()
        self._timeline.commit()

        # Run loop is expected to run with 100 FPS, nothing should slow it down.
        # Timeline relies on this so we test this here.
        self.assertEqual(self._settings.get(RUNLOOP_RATE_LIMIT_PATH), RUNLOOP_FPS)
        FPS_TOLERANCE_PERCENT = 10
        runloop_dt_min = (1.0 / RUNLOOP_FPS) * (1 - FPS_TOLERANCE_PERCENT * 0.01)
        runloop_dt_max = (1.0 / RUNLOOP_FPS) * (1 + FPS_TOLERANCE_PERCENT * 0.01)
        update_sub = self._ed.observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._save_runloop_dt,
            observer_name="TimelineTest save dt"
        )
        for i in range(10):
            await self._app.next_update_async()  # warm up, "consume" old FPS
        for i in range(5):
            await self._app.next_update_async()
            self.assertTrue(self._runloop_dt >= runloop_dt_min,
                            "Run loop dt is too far from expected: {} vs {}"
                            .format(self._runloop_dt, (1.0 / RUNLOOP_FPS)))
            self.assertTrue(self._runloop_dt <= runloop_dt_max,
                            "Run loop dt is too far from expected: {} vs {}"
                            .format(self._runloop_dt, (1.0 / RUNLOOP_FPS)))

        # Timeline wants to keep up with real time if run loop gets too slow (no frame skipping)
        self._settings.set(COMPENSATE_PLAY_DELAY_PATH, 1000.0)  # set something high, e.g. 1000s
        pre_update_sub = self._ed.observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_PRE_UPDATE,
            on_event=self._sleep,
            observer_name="[TimelineTest sleep]"
        )
        self._timeline.stop()
        self._timeline.play()
        self._timeline.commit()
        self._clear_evt_queue()
        await self._app.next_update_async()
        for i in range(5):
            await self._app.next_update_async()
            self.assertTrue(self._runloop_dt > 0.99)  # sleep
            # run loop is slow, no frame skipping even though fast mode is off
            self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED)
            self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT)
        self._timeline.stop()
        self._timeline.commit()
        self._clear_evt_queue()

    async def _test_director(self):
        self._timeline.stop()
        self._timeline.set_current_time(0)
        self._timeline.set_end_time(10)
        self._timeline.set_start_time(0)
        self._timeline.set_time_codes_per_second(24)
        self._timeline.set_looping(False)
        self._timeline.set_prerolling(True)
        self._timeline.set_auto_update(False)
        self._timeline.set_play_every_frame(True)
        self._timeline.set_ticks_per_frame(2)
        self._timeline.set_target_framerate(24)
        self._timeline.commit()
        self._clear_evt_queue()

        self.assertIsNone(self._timeline.get_director())

        self._director_timeline = omni.timeline.get_timeline_interface('director')
        # Make sure they have the same parameters
        self._director_timeline.stop()
        self._director_timeline.set_current_time(self._timeline.get_current_time())
        self._director_timeline.set_end_time(self._timeline.get_end_time())
        self._director_timeline.set_start_time(self._timeline.get_start_time())
        self._director_timeline.set_time_codes_per_second(self._timeline.get_time_codes_per_seconds())
        self._director_timeline.set_looping(self._timeline.is_looping())
        self._director_timeline.set_prerolling(self._timeline.is_prerolling())
        self._director_timeline.set_auto_update(self._timeline.is_auto_updating())
        self._director_timeline.set_play_every_frame(self._timeline.get_play_every_frame())
        self._director_timeline.set_ticks_per_frame(self._timeline.get_ticks_per_frame())
        self._director_timeline.set_target_framerate(self._timeline.get_target_framerate())
        self._director_timeline.commit()

        self._timeline.set_director(self._director_timeline)
        self._timeline.commit()
        self._verify_evt(omni.timeline.TimelineEventType.DIRECTOR_CHANGED, 'directorName', 'director')

        self._director_timeline.play()
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertTrue(self._timeline.is_playing())

        self._director_timeline.pause()
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertFalse(self._timeline.is_playing())

        self._director_timeline.stop()
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertTrue(self._timeline.is_stopped())

        self._director_timeline.set_current_time(2)
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertAlmostEqual(self._timeline.get_current_time(), 2, places=4)

        self._director_timeline.set_end_time(5)
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertAlmostEqual(self._timeline.get_end_time(), 5, places=4)

        self._director_timeline.set_start_time(1)
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertAlmostEqual(self._timeline.get_start_time(), 1, places=4)

        self._director_timeline.set_time_codes_per_second(30)
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertAlmostEqual(self._timeline.get_time_codes_per_seconds(), 30, places=4)

        self._director_timeline.set_looping(True)
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertTrue(self._timeline.is_looping())

        self._director_timeline.set_prerolling(False)
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertFalse(self._timeline.is_prerolling())

        self._director_timeline.set_auto_update(True)
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertTrue(self._timeline.is_auto_updating())

        self._director_timeline.set_play_every_frame(False)
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertFalse(self._timeline.get_play_every_frame())

        self._director_timeline.set_ticks_per_frame(1)
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertEqual(self._timeline.get_ticks_per_frame(), 1)

        self._director_timeline.set_target_framerate(30)
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertAlmostEqual(self._timeline.get_target_framerate(), 30, places=4)

        self.assertFalse(self._timeline.is_zoomed())
        zoom_start = self._timeline.get_start_time() + 1
        zoom_end = self._timeline.get_end_time() - 1
        self._director_timeline.set_zoom_range(zoom_start, zoom_end)
        self._director_timeline.commit()
        self._timeline.commit()
        await self._app.next_update_async()
        self.assertAlmostEqual(self._timeline.get_zoom_start_time(), zoom_start)
        self.assertAlmostEqual(self._timeline.get_zoom_end_time(), zoom_end)
        self.assertTrue(self._timeline.is_zoomed())

        self._clear_evt_queue()  # don't care

        # Make sure we still get the permanent tick from the timeline
        # It might be delayed by one frame
        await self._app.next_update_async()
        await self._app.next_update_async()
        self._verify_evt(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT)
        self._clear_evt_queue()  # don't care

        self._timeline.set_director(None)
        self._timeline.commit()
        await self._app.next_update_async()

        self._verify_evt_exists(omni.timeline.TimelineEventType.DIRECTOR_CHANGED, 'hasDirector', False)

        omni.timeline.destroy_timeline('director')

    async def test_zoom(self):
        timeline_name = 'zoom_test'
        # create a new timeline so we don't interfere with other tests.
        timeline = omni.timeline.get_timeline_interface(timeline_name)
        timeline.set_time_codes_per_second(30)
        start_time = 0
        end_time = 10
        timeline.set_start_time(start_time)
        timeline.set_end_time(end_time)

        # initial state: no zoom
        self.assertAlmostEqual(timeline.get_start_time(), timeline.get_zoom_start_time())
        self.assertAlmostEqual(timeline.get_end_time(), timeline.get_zoom_end_time())
        self.assertFalse(timeline.is_zoomed())

        # setting start and end time keeps the non-zoomed state
        start_time = 1  # smaller interval than the current
        end_time = 9
        timeline.set_start_time(start_time)
        self.assertAlmostEqual(timeline.get_start_time(), timeline.get_zoom_start_time())
        self.assertFalse(timeline.is_zoomed())
        timeline.commit()
        timeline.set_end_time(end_time)
        timeline.commit()
        self.assertAlmostEqual(timeline.get_end_time(), timeline.get_zoom_end_time())
        self.assertFalse(timeline.is_zoomed())

        start_time = 0  # larger interval
        end_time = 10
        timeline.set_start_time(start_time)
        self.assertAlmostEqual(timeline.get_start_time(), timeline.get_zoom_start_time())
        self.assertFalse(timeline.is_zoomed())
        timeline.commit()
        timeline.set_end_time(end_time)
        timeline.commit()
        self.assertAlmostEqual(timeline.get_end_time(), timeline.get_zoom_end_time())
        self.assertFalse(timeline.is_zoomed())

        # changes are not immediate
        timeline.set_zoom_range(start_time + 1, end_time - 1)
        self.assertAlmostEqual(timeline.get_zoom_start_time(), start_time)
        self.assertAlmostEqual(timeline.get_zoom_end_time(), end_time)
        self.assertFalse(timeline.is_zoomed())
        timeline.commit()
        self.assertAlmostEqual(timeline.get_zoom_start_time(), start_time + 1)
        self.assertAlmostEqual(timeline.get_zoom_end_time(), end_time - 1)
        self.assertTrue(timeline.is_zoomed())

        # clear
        timeline.clear_zoom()
        self.assertAlmostEqual(timeline.get_zoom_start_time(), start_time + 1)
        self.assertAlmostEqual(timeline.get_zoom_end_time(), end_time - 1)
        self.assertTrue(timeline.is_zoomed())
        timeline.commit()
        self.assertAlmostEqual(timeline.get_zoom_start_time(), start_time)
        self.assertAlmostEqual(timeline.get_zoom_end_time(), end_time)
        self.assertFalse(timeline.is_zoomed())

        # set zoom ranges inside the timeline's range
        timeline_sub = timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event
        )
        self._test_zoom_change(timeline, start_time + 1, end_time - 1, True, start_time + 1, end_time - 1,
                               "startTime", start_time + 1, False)
        self._test_zoom_change(timeline, start_time + 1, end_time - 2, True, start_time + 1, end_time - 2,
                               "endTime", end_time - 2, False)
        self._test_zoom_change(timeline, start_time + 2, end_time - 1, True, start_time + 2, end_time - 1,
                               "cleared", False)

        # invalid input
        zoom_start, zoom_end = timeline.get_zoom_start_time(), timeline.get_zoom_end_time()
        timeline.set_zoom_range(start_time + 3, start_time + 1)  # end < start
        timeline.commit()
        self.assertAlmostEqual(timeline.get_zoom_start_time(), zoom_start)
        self.assertAlmostEqual(timeline.get_zoom_end_time(), zoom_end)

        # setting the same values should fire no events
        timeline.set_zoom_range(timeline.get_zoom_start_time(), timeline.get_zoom_end_time())
        timeline.commit()
        self.assertTrue(self._buffered_evts.empty())

        # set zoom ranges fully or partially outside the timeline's range, should be clipped
        self._test_zoom_change(timeline, start_time + 1, end_time + 1, True, start_time + 1, end_time,
                               "endTime", end_time, False)
        self._test_zoom_change(timeline, start_time - 1, end_time - 1, True, start_time, end_time - 1,
                               "startTime", start_time, False)
        self._test_zoom_change(timeline, start_time - 1, end_time + 1, False, start_time, end_time,
                               "cleared", True)

        # passing an empty interval should set a 1 frame long zoom range
        self.assertGreater(timeline.get_time_codes_per_seconds(), 0)
        dt = 1.0 / timeline.get_time_codes_per_seconds()
        self._test_zoom_change(timeline, end_time, end_time, True, end_time - dt, end_time,
                               "startTime", end_time - dt)
        self._test_zoom_change(timeline, start_time + 1, start_time + 1, True, start_time + 1, start_time + 1 + dt,
                               "endTime", start_time + 1 + dt)

        # changing start/end time should not affect the zoom when setting a larger range
        old_zoom_start = timeline.get_zoom_start_time()
        old_zoom_end = timeline.get_zoom_end_time()
        start_time = -1
        timeline.set_start_time(start_time)
        timeline.commit()
        self.assertAlmostEqual(timeline.get_zoom_start_time(), old_zoom_start)
        self.assertAlmostEqual(timeline.get_zoom_end_time(), old_zoom_end)
        self.assertTrue(timeline.is_zoomed())
        self._verify_evt(omni.timeline.TimelineEventType.START_TIME_CHANGED)
        self.assertTrue(self._buffered_evts.empty())

        end_time = 9
        timeline.set_end_time(end_time)
        timeline.commit()
        self.assertAlmostEqual(timeline.get_zoom_start_time(), old_zoom_start)
        self.assertAlmostEqual(timeline.get_zoom_end_time(), old_zoom_end)
        self.assertTrue(timeline.is_zoomed())
        self._verify_evt(omni.timeline.TimelineEventType.END_TIME_CHANGED)
        self.assertTrue(self._buffered_evts.empty())

        # zoom range should shrink with start and end time
        timeline.set_zoom_range(start_time + 1, end_time - 1)  # preparations for this test
        timeline.commit()
        old_zoom_start = timeline.get_zoom_start_time()
        old_zoom_end = timeline.get_zoom_end_time()
        self.assertTrue(timeline.is_zoomed())
        self._clear_evt_queue()  # don't care

        start_time = timeline.get_zoom_start_time() + 1
        timeline.set_start_time(start_time)
        timeline.commit()
        self.assertAlmostEqual(timeline.get_zoom_start_time(), start_time)
        self.assertAlmostEqual(timeline.get_zoom_end_time(), old_zoom_end)
        self._verify_evt(omni.timeline.TimelineEventType.START_TIME_CHANGED)
        self._verify_evt(omni.timeline.TimelineEventType.ZOOM_CHANGED, "startTime", start_time, False)

        end_time = timeline.get_zoom_end_time() - 1
        timeline.set_end_time(end_time)
        timeline.commit()
        self.assertAlmostEqual(timeline.get_zoom_start_time(), start_time)
        self.assertAlmostEqual(timeline.get_zoom_end_time(), end_time)
        self._verify_evt(omni.timeline.TimelineEventType.END_TIME_CHANGED)
        self._verify_evt(omni.timeline.TimelineEventType.ZOOM_CHANGED, "endTime", end_time, False)

        # playback is affected by zoom
        timeline_sub = None  # don't care anymore
        zoom_start = start_time + 1
        zoom_end = end_time - 1
        timeline.set_zoom_range(zoom_start, zoom_end)
        timeline.commit()
        self.assertTrue(timeline.is_zoomed())

        timeline.play()
        timeline.commit()
        self.assertAlmostEqual(timeline.get_current_time(), zoom_start)
        timeline.rewind_one_frame()
        timeline.commit()
        self.assertAlmostEqual(timeline.get_current_time(), zoom_end)
        timeline.forward_one_frame()
        timeline.commit()
        self.assertAlmostEqual(timeline.get_current_time(), zoom_start)
        timeline.set_current_time(zoom_start + 1)
        timeline.stop()
        timeline.commit()
        self.assertAlmostEqual(timeline.get_current_time(), zoom_start)

        omni.timeline.destroy_timeline(timeline_name)

    def _on_timeline_event(self, e: carb.events.IEvent):
        self._buffered_evts.put(e)

    def _verify_evt(
        self, type: omni.timeline.TimelineEventType, payload_key: str = None, payload_val=None, exact=False
    ):
        try:
            evt = self._buffered_evts.get_nowait()
            if evt:
                self.assertEqual(evt.type, int(type))
                if payload_key and payload_val:
                    if exact:
                        self.assertEqual(evt.payload[payload_key], payload_val)
                    else:
                        self.assertAlmostEqual(evt.payload[payload_key], payload_val, places=4)
        except queue.Empty:
            self.assertTrue(False, "Expect event in queue but queue is empty")

    # verifies that the an event of the given type exists in the queue, and its payload matches
    def _verify_evt_exists(
        self, type: omni.timeline.TimelineEventType, payload_key: str = None, payload_val=None, exact=False
    ):
        found = False
        while not self._buffered_evts.empty():
            evt = self._buffered_evts.get_nowait()
            if evt and evt.type == int(type):
                found = True
                if payload_key and payload_val:
                    if exact:
                        self.assertEqual(evt.payload[payload_key], payload_val)
                    else:
                        self.assertAlmostEqual(evt.payload[payload_key], payload_val, places=4)
        self.assertTrue(found, f"Event {type} was not found in the queue.")

    def _clear_evt_queue(self):
        while not self._buffered_evts.empty():
            # clear the buffer
            self._buffered_evts.get_nowait()

    def _sleep(self, _):
        sleep(1.0)

    def _save_runloop_dt(self, e: carb.eventdispatcher.Event):
        self._runloop_dt = e['dt']

    def _assert_no_change_then_commit(self, old_value, new_value):
        self.assertEqual(old_value, new_value)
        self.assertTrue(self._buffered_evts.empty())
        self._timeline.commit()

    def _test_zoom_change(
        self,
        timeline,
        start_time,
        end_time,
        expected_is_zoomed,
        expected_start_time,
        expected_end_time,
        payload_key,
        payload_value,
        exact=True
    ):
        timeline.set_zoom_range(start_time, end_time)
        timeline.commit()
        self.assertAlmostEqual(timeline.get_zoom_start_time(), expected_start_time)
        self.assertAlmostEqual(timeline.get_zoom_end_time(), expected_end_time)
        self.assertEqual(expected_is_zoomed, timeline.is_zoomed())
        self._verify_evt(omni.timeline.TimelineEventType.ZOOM_CHANGED, payload_key, payload_value, exact)
        self.assertTrue(self._buffered_evts.empty())
