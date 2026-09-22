## Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import platform
import unittest
import os
import pathlib
import shutil
import tempfile
import omni.kit.app
import omni.usd
import omni.timeline
import carb.settings
from ..app_ui import SHOW_SAVE_OPTIONS
from omni.kit.test_suite.helpers import StageEventHandler
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from omni.kit.test_suite.helpers import open_stage, get_test_data_path, select_prims, wait_stage_loading, arrange_windows
from omni.kit.window.file_exporter.test_helper import FileExporterTestHelper
from pxr import Gf


class FileWindowStopAnimation(AsyncTestCase):
    # Before running each test
    async def setUp(self):
        await arrange_windows()

        # wait for material to be preloaded so create menu is complete & menus don't rebuild during tests
        await omni.kit.material.library.get_mdl_list_async()
        await ui_test.human_delay()

        # load stage
        await open_stage(get_test_data_path(__name__, "physics_animation.usda"))

        # setup events
        self._stage_event_handler = StageEventHandler("omni.kit.window.file")
        
        settings = carb.settings.get_settings()
        self.show_stage_save_dialog_restore = settings.get(SHOW_SAVE_OPTIONS)
        settings.set(SHOW_SAVE_OPTIONS, True)

    # After running each test
    async def tearDown(self):
        # free events
        self._future_test = None
        self._required_stage_event = -1
        self._stage_event_sub = None

        await wait_stage_loading()
        await omni.usd.get_context().new_stage_async()
        settings = carb.settings.get_settings()
        settings.set(SHOW_SAVE_OPTIONS, self.show_stage_save_dialog_restore)

    async def test_l1_stop_animation_save(self):
        def get_box_pos():
            stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath("/World/boxActor")
            attr = prim.GetAttribute("xformOp:translate")
            return attr.Get()

        def play_anim():
            timeline = omni.timeline.get_timeline_interface()
            if timeline:
                timeline.play()

        def on_timeline_event(e):
            if e.type == int(omni.timeline.TimelineEventType.PLAY):
                stage = omni.usd.get_context().get_stage()
                prim = stage.GetPrimAtPath("/World/boxActor")
                attr = prim.GetAttribute("xformOp:translate")
                attr.Set(attr.Get() + Gf.Vec3d(1.0))                
            elif e.type == int(omni.timeline.TimelineEventType.STOP):
                stage = omni.usd.get_context().get_stage()
                prim = stage.GetPrimAtPath("/World/boxActor")
                attr = prim.GetAttribute("xformOp:translate")
                attr.Set(attr.Get() - Gf.Vec3d(1.0))

        timeline_events = omni.timeline.get_timeline_interface().get_timeline_event_stream()
        timeline_event_sub = timeline_events.create_subscription_to_pop(on_timeline_event)

        # setup
        orig_pos = get_box_pos()
        tmpdir = tempfile.mkdtemp()
        orig_file = get_test_data_path(__name__, "physics_animation.usda").replace("\\", "/")
        new_file = f"{tmpdir}/physics_animation.usd".replace("\\", "/")

        # play anim
        play_anim()
        await ui_test.human_delay(100)

        # save as
        await self._stage_event_handler.reset_stage_event(omni.usd.StageEventType.SAVED)
        omni.kit.actions.core.get_action_registry().get_action("omni.kit.window.file", "save_as").execute()
        await ui_test.human_delay(10)
        async with FileExporterTestHelper() as file_export_helper:
            await file_export_helper.click_apply_async(filename_url=new_file)
            await self._stage_event_handler.wait_for_stage_event()

        # play anim
        play_anim()
        await ui_test.human_delay(100)

        # save
        await self._stage_event_handler.reset_stage_event(omni.usd.StageEventType.SAVED)
        omni.kit.actions.core.get_action_registry().get_action("omni.kit.window.file", "save").execute()
        await ui_test.human_delay(10)

        # check _check_and_select_all and _on_select_all_fn for StageSaveDialog
        check_box = ui_test.find("Select Files to Save##file.py//Frame/VStack[0]/ScrollingFrame[0]/VStack[0]/HStack[0]/CheckBox[0]")
        await check_box.click(human_delay_speed=10)
        await check_box.click(human_delay_speed=10)
        await ui_test.human_delay()

        await ui_test.find("Select Files to Save##file.py//Frame/**/Button[*].text=='Save Selected'").click()
        await ui_test.human_delay()
        await self._stage_event_handler.wait_for_stage_event()

        # load saved file
        await open_stage(new_file)
        await ui_test.human_delay()

        # verify boxActor is in same place
        new_pos = get_box_pos()
        self.assertAlmostEqual(orig_pos[0], new_pos[0], places=5)
        self.assertAlmostEqual(orig_pos[1], new_pos[1], places=5)
        self.assertAlmostEqual(orig_pos[2], new_pos[2], places=5)

        timeline_event_sub = None