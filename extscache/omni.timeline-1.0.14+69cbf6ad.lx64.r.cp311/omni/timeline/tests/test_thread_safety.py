# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
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

import random

from threading import get_ident, Lock, Thread
from time import sleep
from typing import List


class TestTimelineThreadSafety(omni.kit.test.AsyncTestCase):
    async def setUp(self):
        self._app = omni.kit.app.get_app()
        self._timeline = omni.timeline.get_timeline_interface()
        self._timeline.stop()  # make sure other tests do not interfere
        await self._app.next_update_async()
        self._timeline.set_end_time(100)
        self._timeline.set_start_time(0)
        self._timeline.set_current_time(0)
        self._timeline.set_time_codes_per_second(30)
        self._timeline.clear_zoom()
        await self._app.next_update_async()

        self._buffered_evts = []
        self._timeline_sub = self._timeline.get_timeline_event_stream().create_subscription_to_pop(
            self._on_timeline_event
        )
        self._setter_to_event_map = {
            'set_auto_update': [omni.timeline.TimelineEventType.AUTO_UPDATE_CHANGED], 
            'set_prerolling': [omni.timeline.TimelineEventType.PREROLLING_CHANGED], 
            'set_looping': [omni.timeline.TimelineEventType.LOOP_MODE_CHANGED], 
            'set_fast_mode': [omni.timeline.TimelineEventType.FAST_MODE_CHANGED], 
            'set_target_framerate': [omni.timeline.TimelineEventType.TARGET_FRAMERATE_CHANGED],
            'set_current_time': [omni.timeline.TimelineEventType.CURRENT_TIME_TICKED],
            # when current time is smaller than start time, it'll be reset to start time and emit CURRENT_TIME_TICKED event
            'set_start_time': [omni.timeline.TimelineEventType.START_TIME_CHANGED, omni.timeline.TimelineEventType.CURRENT_TIME_TICKED],
            'set_end_time': [omni.timeline.TimelineEventType.END_TIME_CHANGED],
            'set_time_codes_per_second': [omni.timeline.TimelineEventType.TIME_CODE_PER_SECOND_CHANGED],
            'set_ticks_per_frame': [omni.timeline.TimelineEventType.TICKS_PER_FRAME_CHANGED],
            'set_tentative_time': [omni.timeline.TimelineEventType.TENTATIVE_TIME_CHANGED],
            'play': [omni.timeline.TimelineEventType.PLAY],
            'pause': [omni.timeline.TimelineEventType.PAUSE],
            'stop': [omni.timeline.TimelineEventType.STOP],
            'rewind_one_frame': [omni.timeline.TimelineEventType.CURRENT_TIME_TICKED],
            'forward_one_frame': [omni.timeline.TimelineEventType.CURRENT_TIME_TICKED],
        }

    async def tearDown(self):
        self._timeline = None
        self._timeline_sub = None

    async def test_setters(self):
        self._main_thread_id = get_ident()

        all_setters = ['set_auto_update', 'set_prerolling', 'set_looping', 'set_fast_mode', 'set_target_framerate', 
            'set_current_time', 'set_start_time', 'set_end_time', 'set_time_codes_per_second', 'set_ticks_per_frame',
            'set_tentative_time']
        all_getters = ['is_auto_updating', 'is_prerolling', 'is_looping', 'get_fast_mode', 'get_target_framerate',
            'get_current_time', 'get_start_time', 'get_end_time', 'get_time_codes_per_seconds', 'get_ticks_per_frame',
            'get_tentative_time']
        all_values_to_set = [[True, False], [True, False], [True, False], [True, False], [24, 30, 60, 100],
            [0, 10, 12, 20], [0, 10], [20, 100], [24, 30, 60], [1, 2, 4],
            [0, 10, 12, 20]]
        self.assertEqual(len(all_getters), len(all_setters))
        self.assertEqual(len(all_getters), len(all_values_to_set))
        
        # Run for every attribute individually
        for i in range(len(all_setters)):
            print(f'Thread safety test for timeline method {all_setters[i]}')
            # Trying all values
            await self.do_multithreaded_test([[all_setters[i]]], [[all_getters[i]]], [[all_values_to_set[i]]], 200, 100)
            
            # Setting a single value, no other values should appear. Making sure the initial value is what we'll set.
            getattr(self._timeline, all_setters[i])(all_values_to_set[i][0])
            await self._app.next_update_async()
            await self.do_multithreaded_test([[all_setters[i]]], [[all_getters[i]]], [[[all_values_to_set[i][0]]]], 50, 50)
            
        # Run for all attributes
        print('Thread safety test for all timeline methods')
        await self.do_multithreaded_test([all_setters], [all_getters], [all_values_to_set], 100, 100)

    async def test_time_control(self):
        self._main_thread_id = get_ident()

        all_methods = ['play', 'pause', 'stop', 'rewind_one_frame', 'forward_one_frame']
        await self.do_multithreaded_test([all_methods], [None], [None], 50, 50)

    async def do_multithreaded_test(
        self,
        setters: List[List[str]],
        getters: List[List[str]],
        values_to_set: List[list],
        thread_count_per_type: int = 50,
        thread_runs: int = 50):

        MIN_SLEEP = 0.01
        SLEEP_RANGE = 0.05

        self.assertEqual(len(setters), len(getters))
        for i, setter_list in enumerate(setters):
            if values_to_set[i] is not None:
                self.assertEqual(len(setter_list), len(values_to_set[i]))

        lock = Lock()
        running_threads = 0

        def do(runs: int, thread_id: int, setters: List[str], getters: List[str], values_to_set: list, running_threads: int):
            with lock:
                running_threads = running_threads + 1
            if getters is not None:
                self.assertEqual(len(setters), len(getters))
            if values_to_set is not None:
                self.assertEqual(len(setters), len(values_to_set))
            timeline = omni.timeline.get_timeline_interface()
            rnd = random.Random()
            rnd.seed(thread_id)
            for run in range(runs):
                i_attr = rnd.randint(0, len(setters) - 1)
                if values_to_set is not None:  # setter is a setter method that accepts a value
                    values = values_to_set[i_attr]
                    i_value = rnd.randint(0, len(values) - 1)
                    getattr(timeline, setters[i_attr])(values[i_value])

                    # We might want to see this when running tests, commented out for now
                    # print(f'Thread {thread_id} has called {setters[i_attr]}({values[i_value]})')
                else:  # "setter" is a method with no parameter (e.g. play())
                    getattr(timeline, setters[i_attr])()
                
                sleep(MIN_SLEEP + rnd.random() * SLEEP_RANGE)
                
                if getters is not None and values_to_set is not None:
                    current_value = getattr(timeline, getters[i_attr])()
                    self.assertTrue(current_value in values, f'Invalid value in thread {thread_id}: {current_value} is not in {values}')
            with lock:
                running_threads = running_threads - 1

        thread_id = 0
        threads = []
        for thread_type_idx, setter in enumerate(setters):
            for i in range(thread_count_per_type):
                threads.append(
                    Thread(
                        target = do, 
                        args = (
                            thread_runs, 
                            thread_id, 
                            setters[thread_type_idx], 
                            getters[thread_type_idx], 
                            values_to_set[thread_type_idx],
                            running_threads
                        )
                    )
                )
                threads[-1].start()
                thread_id = thread_id + 1

        self._buffered_evts = []
        threads_running = True
        while threads_running:
            await self._app.next_update_async()
            with lock:
                threads_running = running_threads > 0
        for thread in threads:
            thread.join()

        # an extra update to trigger last callbacks
        await self._app.next_update_async()
        
        # validate that we received only the expected events
        all_setters = []
        for setter_list in setters:
            for setter in setter_list:
                all_setters.append(setter)
        allowed_events = [int(omni.timeline.TimelineEventType.CURRENT_TIME_TICKED_PERMANENT)]
        for setter in all_setters:
            allowed_events += [int(event) for event in self._setter_to_event_map[setter]]
        for evt in self._buffered_evts:
            self.assertTrue(evt in allowed_events, f'Error: event {evt} is not in allowed events {allowed_events} for setters {all_setters}')


    def _on_timeline_event(self, e: carb.events.IEvent):
        # callbacks are on the main thread
        self.assertEqual(get_ident(), self._main_thread_id)
        # save event type
        self._buffered_evts.append(e.type)
