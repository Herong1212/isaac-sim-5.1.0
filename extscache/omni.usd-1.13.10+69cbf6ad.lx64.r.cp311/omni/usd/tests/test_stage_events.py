# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import os
import tempfile
import omni.kit.test
import omni.usd
from carb.eventdispatcher import get_eventdispatcher

from pathlib import Path
from omni.usd import StageEventType
from pxr import Usd, Sdf


class TestStageEvents(omni.kit.test.AsyncTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._test_scene = str(Path(__file__).parent.joinpath("data").joinpath("test_scene.usda"))
        self._interested_events = (
            StageEventType.SAVING,
            StageEventType.SETTINGS_SAVING,
            StageEventType.SAVED,
            StageEventType.CLOSING,
            StageEventType.CLOSED,
            StageEventType.OPENING,
            StageEventType.OPENED,
            StageEventType.SAVE_FAILED
        )
        self._stage_is_not_null_during_closing = True
        self._cancel_save_stage = False
        self._cancel_save_settings = False

    async def setUp(self):
        usd_context = omni.usd.get_context()
        # Open and close to make sure no stage is created.
        usd_context.new_stage()
        await usd_context.close_stage_async()

        usd_context.set_pending_edit(False)
        self.usd_context = usd_context

        self._stage_event_sub = [
            get_eventdispatcher().observe_event(
                observer_name="omni.usd test_stage_events",
                event_name=usd_context.stage_event_name(e),
                on_event=self._on_stage_event
            )
            for e in self._interested_events
        ]
        self._events_received = []
        self._opened_stage = ""

    async def tearDown(self):
        self._events_received.clear()
        self._opened_stage = ""
        self._stage_event_sub = None

    def _on_stage_event(self, e):
        event = omni.usd.stage_event_type(e.event_name)
        self._events_received.append(int(event))
        if event == StageEventType.CLOSING:
            stage = self.usd_context.get_stage()
            self._stage_is_not_null_during_closing = stage != None
        elif event == StageEventType.OPENING:
            self._opened_stage = e["val"]
        elif event == StageEventType.SAVING:
            if self._cancel_save_stage:
                self.usd_context.try_cancel_save()
                self._cancel_save_stage = False
        elif event == StageEventType.SETTINGS_SAVING:
            if self._cancel_save_settings:
                self.usd_context.try_cancel_save()
                self._cancel_save_settings = False

    async def test_usd_stage_events(self):
        # New and close stage
        self.usd_context.new_stage()
        self.assertEqual(self._events_received, [int(StageEventType.OPENING), int(StageEventType.OPENED)])

        self._events_received.clear()
        await self.usd_context.new_stage_async()
        self.assertEqual(self._events_received, [int(StageEventType.CLOSING), int(StageEventType.CLOSED), int(StageEventType.OPENING), int(StageEventType.OPENED)])
        self.assertTrue(self._stage_is_not_null_during_closing, "Stage should not be null during closing.")
        self.assertEqual(self._opened_stage, "")

        self._events_received.clear()
        await self.usd_context.close_stage_async()
        self.assertEqual(self._events_received, [int(StageEventType.CLOSING), int(StageEventType.CLOSED)])
        self.assertTrue(self._stage_is_not_null_during_closing, "Stage should not be null during closing.")

        # Attach stage
        self._events_received.clear()
        stage = Usd.Stage.CreateInMemory()
        await self.usd_context.attach_stage_async(stage)
        self.assertEqual(self._events_received, [int(StageEventType.OPENING), int(StageEventType.OPENED)])

        self._events_received.clear()
        another_stage = Usd.Stage.CreateInMemory()
        await self.usd_context.attach_stage_async(another_stage)
        self.assertEqual(self._events_received, [int(StageEventType.CLOSING), int(StageEventType.CLOSED), int(StageEventType.OPENING), int(StageEventType.OPENED)])
        self.assertTrue(self._stage_is_not_null_during_closing, "Stage should not be null during closing.")

        # Open stage
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_file_path = os.path.join(tmpdirname, "tmp.usda")
            Sdf.Layer.CreateNew(tmp_file_path)
            tmp_file_path2 = os.path.join(tmpdirname, "tmp2.usda")
            Sdf.Layer.CreateNew(tmp_file_path2)

            self._events_received.clear()
            await self.usd_context.close_stage_async()
            self.assertEqual(self._events_received, [int(StageEventType.CLOSING), int(StageEventType.CLOSED)])
            self.assertTrue(self._stage_is_not_null_during_closing, "Stage should not be null during closing.")

            self._events_received.clear()
            await self.usd_context.open_stage_async(tmp_file_path)
            self.assertEqual(self._events_received, [int(StageEventType.OPENING), int(StageEventType.OPENED)])
            self.assertEqual(os.path.normpath(self._opened_stage), os.path.normpath(tmp_file_path))

            self._events_received.clear()
            await self.usd_context.open_stage_async(tmp_file_path2)
            self.assertEqual(self._events_received, [int(StageEventType.CLOSING), int(StageEventType.CLOSED), int(StageEventType.OPENING), int(StageEventType.OPENED)])
            self.assertTrue(self._stage_is_not_null_during_closing, "Stage should not be null during closing.")

            stage = self.usd_context.get_stage()
            stage.DefinePrim("/World/test")

            self._events_received.clear()
            self.usd_context.save_stage()
            self.assertEqual(
                self._events_received,
                [
                    int(StageEventType.SAVING),
                    int(StageEventType.SETTINGS_SAVING),
                    int(StageEventType.SAVED)
                ]
            )

            # Simulates cancelling
            self._cancel_save_stage = True
            self._events_received.clear()
            stage = self.usd_context.get_stage()
            stage.DefinePrim("/World/test3")
            await self.usd_context.save_stage_async()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(
                self._events_received,
                [
                    int(StageEventType.SAVING),
                    int(StageEventType.SAVE_FAILED)
                ]
            )

            self._cancel_save_settings = True
            self._events_received.clear()
            await self.usd_context.save_stage_async()
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            self.assertEqual(
                self._events_received,
                [
                    int(StageEventType.SAVING),
                    int(StageEventType.SETTINGS_SAVING),
                    int(StageEventType.SAVE_FAILED)
                ]
            )

            self._events_received.clear()
            stage.DefinePrim("/World/test2")
            await self.usd_context.save_stage_async()
            self.assertEqual(
                self._events_received,
                [
                    int(StageEventType.SAVING),
                    int(StageEventType.SETTINGS_SAVING),
                    int(StageEventType.SAVED)
                ]
            )

            self._events_received.clear()
            tmp_file_path3 = os.path.join(tmpdirname, "tmp3.usda")
            await self.usd_context.save_layers_async(tmp_file_path3, [])
            if Usd.GetVersion() < (0, 24, 5):
                # If it's the same format, it will do in-place save so no re-open is sent.
                self.assertEqual(
                    self._events_received,
                    [
                        int(StageEventType.SAVING),
                        int(StageEventType.SETTINGS_SAVING),
                        int(StageEventType.SAVED)
                    ]
                )
            else:
                # USD v24.05 cannot do in-place save.
                # See NVBug 5149437 for more details.
                self.assertEqual(self._events_received, [
                    int(StageEventType.SAVING),
                    int(StageEventType.SETTINGS_SAVING),
                    int(StageEventType.CLOSING),
                    int(StageEventType.CLOSED),
                    int(StageEventType.OPENING),
                    int(StageEventType.OPENED),
                    int(StageEventType.SAVED)]
                )

            # For format change, it will open stage.
            tmp_file_path4 = os.path.join(tmpdirname, "tmp3.usd")
            self._events_received.clear()
            await self.usd_context.save_layers_async(tmp_file_path4, [])
            # Copy to avoid later close events.
            events_received = self._events_received[:]
            self.assertEqual(events_received, [
                int(StageEventType.SAVING),
                int(StageEventType.SETTINGS_SAVING),
                int(StageEventType.CLOSING),
                int(StageEventType.CLOSED),
                int(StageEventType.OPENING),
                int(StageEventType.OPENED),
                int(StageEventType.SAVED)]
            )
            self.assertTrue(self._stage_is_not_null_during_closing, "Stage should not be null during closing.")

            # It should be successful for another save without format change.
            tmp_file_path4 = os.path.join(tmpdirname, "tmp4.usd")
            self._events_received.clear()
            success, err, saved_layers = await self.usd_context.save_layers_async(tmp_file_path4, [])
            self.assertTrue(success)
            await self.usd_context.close_stage_async()
