## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import carb
import os
import tempfile
import shutil
import omni.kit.app
import omni.kit.commands
import omni.kit.test
import stat
import carb.settings
from carb.eventdispatcher import get_eventdispatcher

from pathlib import Path
from unittest.mock import Mock, patch
from omni.kit import ui_test
from omni.kit.window.file_exporter.test_helper import FileExporterTestHelper
from omni.kit.test_suite.helpers import StageEventHandler
from omni.kit.test_suite.helpers import open_stage, get_test_data_path, wait_stage_loading, StageEventHandler
from ..file_window import FileUtils, get_file_utils_instance as get_window_file
from ..app_ui import SHOW_SAVE_OPTIONS
from .test_base import TestFileBase
from pxr import Usd, Gf
import unittest


class TestFileSave(TestFileBase):
    async def setUp(self):
        await super().setUp()

    async def tearDown(self):
        await super().tearDown()

    async def test_file_save(self):
        """Testing that save should write to stage url"""
        await omni.usd.get_context().new_stage_async()
        omni.usd.get_context().set_pending_edit(False)

        test_file = "test_file.usda"
        temp_path = os.path.join(tempfile.gettempdir(), test_file)
        shutil.copyfile(os.path.join(self._usd_path, test_file), temp_path)

        omni.kit.window.file.open_stage(temp_path)
        await self.wait_for_update()

        mock_callback = Mock()
        omni.kit.window.file.save(mock_callback)
        await self.wait_for_update()

        self.assertEqual(omni.usd.get_context().get_stage_url(), temp_path.replace("\\", "/"))
        self.assertTrue(os.path.isfile(temp_path))
        mock_callback.assert_called_once()
        self.remove_file(temp_path)

    async def test_file_save_with_render_setting_changes_only(self):
        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        self.assertFalse(usd_context.has_pending_edit())

        with tempfile.TemporaryDirectory() as tmp_dir_name:
            await omni.kit.app.get_app().next_update_async()

            # save
            tmp_file_path = Path(tmp_dir_name) / "tmp.usda"
            result = usd_context.save_as_stage(str(tmp_file_path))
            self.assertTrue(result)
            self.assertFalse(usd_context.has_pending_edit())

            # save the file with customized key value
            settings = carb.settings.get_settings()
            setting_key_ao = "/rtx/post/aa/op"
            settings.set_int(setting_key_ao, 3)
            await omni.kit.app.get_app().next_update_async()

            # After changing render settings, it will be dirty.
            self.assertTrue(usd_context.has_pending_edit())

            # Saves stage, although no layers are dirty except render settings.
            omni.kit.window.file.save(None)

            # Waiting for save to be done as it's asynchronous.
            for _ in range(10):
                await omni.kit.app.get_app().next_update_async()

            # Making sure that render settings are saved into root layer.
            self.assertFalse(usd_context.has_pending_edit())

            # Reloading stage will reload the settings also.
            await usd_context.reopen_stage_async()
            await omni.kit.app.get_app().next_update_async()
            self.assertFalse(usd_context.has_pending_edit())

            setting_value_ao = settings.get(setting_key_ao)

            self.assertEqual(setting_value_ao, 3)

            # New stage to release temp file.
            await usd_context.new_stage_async()

    async def test_file_save_read_only_file(self):
        """Test saving read-only file calls save_as instead"""
        await omni.usd.get_context().new_stage_async()
        omni.usd.get_context().set_pending_edit(False)

        test_file = "test_file.usda"
        temp_path = os.path.join(tempfile.gettempdir(), test_file)
        shutil.copyfile(os.path.join(self._usd_path, test_file), temp_path)

        omni.kit.window.file.open_stage(temp_path)
        await self.wait_for_update()

        class ListEntry:
            def __init__(self) -> None:
                self.flags = 0

        mock_callback = Mock()
        with patch.object(omni.usd.UsdContext, 'is_new_stage', return_value=False),\
            patch.object(omni.client, "stat_async", return_value=(omni.client.Result.OK, ListEntry())),\
            patch.object(FileUtils, "save_as") as mock_save_as:
                omni.kit.window.file.save(mock_callback)
                await self.wait_for_update()

        mock_save_as.assert_called_once_with(False, mock_callback, allow_skip_sublayers=False)
        self.remove_file(temp_path)

    async def test_file_saveas(self):
        """Testing save as"""

        usd_context = omni.usd.get_context()
        await usd_context.new_stage_async()
        usd_context.set_pending_edit(False)

        temp_path = self._temp_path.replace('.usda', '.usd')
        mock_callback = Mock()

        captured_saving_layer = None
        def _on_stage_event(event):
            nonlocal captured_saving_layer

            captured_saving_layer = event["savingRootLayer"]

        subscription = get_eventdispatcher().observe_event(
            observer_name="omni.kit.window.file:test_file_saveas",
            event_name=usd_context.stage_event_name(omni.usd.StageEventType.SAVING),
            on_event=_on_stage_event
        )

        async with FileExporterTestHelper() as file_export_helper:
            with patch.object(omni.usd.UsdContext, 'is_new_stage', return_value=False):
                omni.kit.window.file.save_as(False, mock_callback)
                await self.wait_for_update()

                await file_export_helper.click_apply_async(filename_url=temp_path)
                await self.wait_for_update()

        self.assertEqual(captured_saving_layer, temp_path)

        mock_callback.assert_called_once()
        self.assertTrue(os.path.isfile(temp_path))
        self.remove_file(temp_path)

    async def _test_file_saveas_with_empty_filename(self): # pragma: no cover
        """Testing save as with an empty filename, should not allow saving."""
        await omni.usd.get_context().new_stage_async()
        omni.usd.get_context().set_pending_edit(False)

        temp_path = self._temp_path.replace('.usda', '.usd')
        mock_callback = Mock()

        async with FileExporterTestHelper() as file_export_helper:
            with patch.object(omni.usd.UsdContext, 'is_new_stage', return_value=False):
                omni.kit.window.file.save_as(False, mock_callback)
                await self.wait_for_update()

                await file_export_helper.click_apply_async()
                await self.wait_for_update()

        mock_callback.assert_not_called()
        self.assertFalse(os.path.isfile(temp_path))

    async def _test_file_saveas_flattened_internal(self, include_session_layer):
        """Testing save as flatten"""
        await omni.usd.get_context().new_stage_async()
        omni.usd.get_context().set_pending_edit(False)

        mock_callback = Mock()

        base, ext = os.path.splitext(self._temp_path)
        temp_path = base + str(include_session_layer) + ext
        temp_path = self._temp_path.replace('.usda', '.usd')
        async with FileExporterTestHelper() as file_export_helper:
            with patch.object(omni.usd.UsdContext, 'is_new_stage', return_value=False):
                omni.kit.window.file.save_as(True, mock_callback)
                await self.wait_for_update()

                import omni.kit.ui_test as ui_test
                file_picker = ui_test.find("Save File As...")
                self.assertTrue(file_picker)
                await file_picker.focus()

                include_session_layer_checkbox = file_picker.find(
                    "**/CheckBox[*].identifier=='include_session_layer'"
                )
                self.assertTrue(include_session_layer_checkbox)
                include_session_layer_checkbox.model.set_value(include_session_layer)

                await file_export_helper.click_apply_async(filename_url=temp_path)
                await self.wait_for_update()
                await self.wait_for_update()

        stage = Usd.Stage.Open(temp_path)
        prim = stage.GetPrimAtPath("/OmniverseKit_Persp")
        if include_session_layer:
            self.assertTrue(prim)
        else:
            self.assertFalse(prim)
        stage = None

        mock_callback.assert_called_once()
        self.assertTrue(os.path.isfile(temp_path))
        self.remove_file(temp_path)

    async def test_file_saveas_flattened_with_session_layer(self):
        await self._test_file_saveas_flattened_internal(True)

    async def test_file_saveas_flattened_without_session_layer(self):
        await self._test_file_saveas_flattened_internal(False)

    async def test_show_save_layers_failed_prompt(self):
        await omni.usd.get_context().new_stage_async()
        prompt = get_window_file().ui_handler.show_save_layers_failed_prompt()
        await self.wait_for_update()
        prompt.hide()

    async def test_file_saveas_existed_filename(self):
        """Testing save as with a filename which is already existed, should not allow saving."""
        # create an empty stage
        await omni.usd.get_context().new_stage_async()
        omni.usd.get_context().set_pending_edit(False)

        file_name = f"4Lights.usda"
        temp_path = os.path.join(tempfile.gettempdir(), file_name)
        shutil.copyfile(os.path.join(self._usd_path, file_name), temp_path)

        # save the current stage to the temp path where the file name already exists
        async with FileExporterTestHelper() as file_export_helper:
            with patch.object(omni.usd.UsdContext, 'is_new_stage', return_value=False):
                omni.kit.window.file.save_as(False, Mock())
                await self.wait_for_update()

                await file_export_helper.click_apply_async(filename_url=temp_path)
                await self.wait_for_update()

        # check 4Lights.usda is not empty, which means saveas didn't happen
        stage = Usd.Stage.Open(str(temp_path))
        await self.wait_for_update()

        prim = stage.GetPrimAtPath("/Stage/SphereLight_01")
        self.assertTrue(prim)
        self.remove_file(temp_path)

    async def test_invalid_save(self):
        """Test no valid stage save"""
        if omni.usd.get_context().get_stage():
            await omni.usd.get_context().close_stage_async()
        mock_callback = Mock()
        omni.kit.window.file.save(mock_callback)
        mock_callback.assert_not_called()

class TestFileSaveOptions(TestFileBase):
    async def setUp(self):
        await super().setUp()

    async def tearDown(self):
        await super().tearDown()

    async def _test_save_options_setting_internal(self, action: str, setting_value: bool, finded: bool):
        settings = carb.settings.get_settings()
        show_stage_save_dialog_restore = settings.get(SHOW_SAVE_OPTIONS)
        settings.set(SHOW_SAVE_OPTIONS, setting_value)
        await open_stage(get_test_data_path(__name__, "physics_animation.usda"))

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

        # load stage

        # setup events
        stage_event_handler = StageEventHandler("omni.kit.window.file")
        tmpdir = str(Path(tempfile.mkdtemp()).resolve())
        new_file = f"{tmpdir}/physics_animation.usd".replace("\\", "/")

        # play anim
        play_anim()
        await ui_test.human_delay(2)

        # save as
        await stage_event_handler.reset_stage_event(omni.usd.StageEventType.SAVED)
        omni.kit.actions.core.get_action_registry().get_action("omni.kit.window.file", "save_as").execute()
        await ui_test.human_delay(2)
        async with FileExporterTestHelper() as file_export_helper:
            await ui_test.human_delay(8)
            await file_export_helper.click_apply_async(filename_url=new_file)
            await stage_event_handler.wait_for_stage_event()

        # play anim
        play_anim()
        await ui_test.human_delay(2)

        # save
        await stage_event_handler.reset_stage_event(omni.usd.StageEventType.SAVED)
        omni.kit.actions.core.get_action_registry().get_action("omni.kit.window.file", action).execute()
        await ui_test.human_delay(2)

        # check _check_and_select_all and _on_select_all_fn for StageSaveDialog
        if finded:
            check_box = ui_test.find("Select Files to Save##file.py//Frame/VStack[0]/ScrollingFrame[0]/VStack[0]/HStack[0]/CheckBox[0]")
            self.assertIsNotNone(check_box)
            await check_box.click(human_delay_speed=10)
            await ui_test.human_delay()

            await ui_test.find("Select Files to Save##file.py//Frame/**/Button[*].text=='Save Selected'").click()
            await ui_test.human_delay()
            await stage_event_handler.wait_for_stage_event()
        else:
            select_window = ui_test.find("Select Files to Save##file.py")
            if select_window:
                self.assertFalse(select_window.window.visible)
            else:
                self.assertIsNone(select_window)

        await ui_test.human_delay(2)
        timeline_event_sub = None
        await wait_stage_loading()
        await omni.usd.get_context().new_stage_async()
        settings = carb.settings.get_settings()
        settings.set(SHOW_SAVE_OPTIONS, show_stage_save_dialog_restore)
        await ui_test.human_delay(2)
        def remove_readonly(func, path, excinfo):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        try:
            shutil.rmtree(tmpdir, onerror=remove_readonly)
        except PermissionError as e:
            print(f"{e}")

    async def test_save_options_setting(self):
        """Test save options setting"""
        select_window = ui_test.find("Select Files to Save##file.py")
        if select_window:
            select_window.window.visible = False
        # save when save options setting value is False
        await self._test_save_options_setting_internal("save", False, False)
        # save with options when save options setting value is False
        await self._test_save_options_setting_internal("save_with_options", False, True)

        # save when save options setting value is True
        await self._test_save_options_setting_internal("save", True, True)
        # save with options when save options setting value is True
        await self._test_save_options_setting_internal("save_with_options", True, True)
