# Copyright (c) 2022-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import omni.kit.stagerecorder.core as recorder
import omni.kit.ui_test as ui_test
import omni.ui as ui
import omni.usd

from .base_test import BaseTest

WINDOW_NAME = "Stage Recorder"

START_RECORDING_COMMAND = "StartRecording"
STOP_RECORDING_COMMAND = "StopRecording"

# RECORD_TO_STAGE = "STAGE"
RECORD_TO_FILE = "FILE"
RECORD_TO_NEW_LAYER = "NEW_LAYER"

SIMPLE_TEST_CASE_FILENAME = "SkelCylinder.usda"
SIMPLE_TEST_CASE_PRIMPATH = "/Root/BLENDWEIGHT_group1"


class StageRecorderTest(BaseTest):
    async def setUp(self):
        await super().setUp()

    async def tearDown(self):
        await super().tearDown()

    # Test(s)
    async def test_recorder_ui(self):
        ui.Workspace.show_window("Property", False)
        ui.Workspace.show_window(WINDOW_NAME)
        recorder_window = ui.Workspace.get_window(WINDOW_NAME)
        await self.docked_test_window(
            window=recorder_window,
            width=631,
            height=800,
            restore_window=ui.Workspace.get_window("Layer") or ui.Workspace.get_window("Stage"),
            restore_position=ui.DockPosition.BOTTOM,
        )

        await ui_test.human_delay(100)

        # Recorder UI in its initial state should match the golden image
        record_folder = ui_test.find(f"{WINDOW_NAME}//Frame/**/StringField[*].name=='record_folder'")
        self.assertTrue(record_folder)
        record_folder.model.set_value("")
        await self.snapshot_test("test_recorder_ui_initial_state")

        # Prim list should initially be empty
        prim_list = ui_test.find(f"{WINDOW_NAME}//Frame/**/TreeView[*].name=='prim_list'")
        self.assertTrue(prim_list)
        self.assertTrue(prim_list.model.is_empty())

        # Prim list should not be empty after adding a prim
        await self.load_stage(SIMPLE_TEST_CASE_FILENAME)
        self._context.get_selection().set_selected_prim_paths([SIMPLE_TEST_CASE_PRIMPATH], True)
        add_selection = ui_test.find(f"{WINDOW_NAME}//Frame/**/Button[*].name=='add_selection'")
        self.assertTrue(add_selection)
        await add_selection.click()
        await ui_test.human_delay(100)
        self.assertFalse(prim_list.model.is_empty())

        # Display is initially in units of Frames
        display_units = ui_test.find(f"{WINDOW_NAME}//Frame/**/ComboBox[*].name=='display_units'")
        self.assertTrue(display_units)
        self.assertEqual(display_units.model.get_item_value_model().get_value_as_int(), 1)
        record_time = ui_test.find(f"{WINDOW_NAME}//Frame/**/Label[*].name=='record_time'")
        self.assertTrue(record_time)

        # Take Name increment is initially Multi-Take
        increment = ui_test.find(f"{WINDOW_NAME}//Frame/**/ComboBox[*].name=='increment'")
        self.assertTrue(increment)
        self.assertEqual(increment.model.get_item_value_model().get_value_as_int(), 0)

        # Record-to is initially File
        recordto = ui_test.find(f"{WINDOW_NAME}//Frame/**/ComboBox[*].name=='recordto'")
        self.assertTrue(recordto)
        self.assertEqual(recordto.model.get_item_value_model().get_value_as_int(), 0)

        # Use custom range is initially off
        use_custom_range = ui_test.find(f"{WINDOW_NAME}//Frame/**/CheckBox[*].name=='use_custom_range'")
        self.assertTrue(use_custom_range)
        self.assertFalse(use_custom_range.model.as_bool)

        # Range start and end fields are initially populated
        custom_range_start = ui_test.find(f"{WINDOW_NAME}//Frame/**/StringField[*].name=='custom_range_start'")
        self.assertTrue(custom_range_start)
        self.assertTrue(custom_range_start.model.as_string)
        self.assertFalse(custom_range_start.widget.enabled)
        custom_range_end = ui_test.find(f"{WINDOW_NAME}//Frame/**/StringField[*].name=='custom_range_end'")
        self.assertTrue(custom_range_end)
        self.assertTrue(custom_range_end.model.as_string)
        self.assertFalse(custom_range_end.widget.enabled)

        # Use pre-roll is initially off
        use_pre_roll = ui_test.find(f"{WINDOW_NAME}//Frame/**/CheckBox[*].name=='use_pre_roll'")
        self.assertTrue(use_pre_roll)
        self.assertFalse(use_pre_roll.model.as_bool)

        # Pre-roll start field is initially populated
        pre_roll_start = ui_test.find(f"{WINDOW_NAME}//Frame/**/StringField[*].name=='pre_roll_start'")
        self.assertTrue(pre_roll_start)
        self.assertTrue(pre_roll_start.model.as_string)
        self.assertFalse(pre_roll_start.widget.enabled)

        # Live Mode is initially off
        live_mode = ui_test.find(f"{WINDOW_NAME}//Frame/**/CheckBox[*].name=='live_mode'")
        self.assertTrue(live_mode)
        self.assertFalse(live_mode.model.as_bool)

        # Max FPS is initially 29.97
        max_fps = ui_test.find(f"{WINDOW_NAME}//Frame/**/ComboBox[*].name=='max_fps'")
        self.assertTrue(max_fps)
        self.assertEqual(max_fps.model.get_item_value_model().get_value_as_int(), 1)
        self.assertFalse(max_fps.widget.enabled)

        # Bake root motion is initially on
        bake_root_motion = ui_test.find(f"{WINDOW_NAME}//Frame/**/CheckBox[*].name=='bake_root_motion'")
        self.assertTrue(bake_root_motion)
        self.assertTrue(bake_root_motion.model.as_bool)

        # Should start recording in non-Live Mode
        (status, ret_val) = omni.kit.commands.execute(
            START_RECORDING_COMMAND,
            target_paths=[(SIMPLE_TEST_CASE_PRIMPATH, True)],
            live_mode=False,
            use_frame_range=False,
            start_frame=0,
            end_frame=100,
            use_preroll=False,
            preroll_frame=0,
            record_to=RECORD_TO_FILE,
            take_name="Fake Take Name",
            record_folder=self._test_output_dir,
            increment_name=True,
            apply_root_anim=True,
            fps=0,
        )

        self.assertTrue(status)
        self.assertIsNone(ret_val["error"])

        # Should stop recording on command
        (status, ret_val) = omni.kit.commands.execute(STOP_RECORDING_COMMAND)
        self.assertTrue(status)
        self.assertEqual(ret_val, recorder.RecordingReturnCode.NO_CHANGES_DETECTED)

        # Should start recording in Live Mode
        (status, ret_val) = omni.kit.commands.execute(
            START_RECORDING_COMMAND,
            target_paths=[(SIMPLE_TEST_CASE_PRIMPATH, True)],
            live_mode=True,
            use_frame_range=False,
            start_frame=0,
            end_frame=100,
            use_preroll=False,
            preroll_frame=0,
            record_to=RECORD_TO_FILE,
            take_name="Fake Take Name",
            record_folder=self._test_output_dir,
            increment_name=True,
            apply_root_anim=True,
            fps=0,
        )

        self.assertTrue(status)
        self.assertIsNone(ret_val["error"])

        # Should stop recording on command
        (status, ret_val) = omni.kit.commands.execute(STOP_RECORDING_COMMAND)
        self.assertTrue(status)
        self.assertEqual(ret_val, recorder.RecordingReturnCode.NO_CHANGES_DETECTED)

        # Should return error if frame range exceeds max recording length
        (status, ret_val) = omni.kit.commands.execute(
            START_RECORDING_COMMAND,
            target_paths=[(SIMPLE_TEST_CASE_PRIMPATH, True)],
            live_mode=False,
            use_frame_range=True,
            start_frame=0,
            end_frame=1000000,
            use_preroll=False,
            preroll_frame=0,
            record_to=RECORD_TO_FILE,
            take_name="Fake Take Name",
            record_folder=self._test_output_dir,
            increment_name=True,
            apply_root_anim=True,
            fps=0,
        )

        self.assertTrue(status)
        self.assertTrue(ret_val["error"])

        # Should stop recording on command
        (status, ret_val) = omni.kit.commands.execute(STOP_RECORDING_COMMAND)
        self.assertTrue(status)
        self.assertEqual(ret_val, recorder.RecordingReturnCode.NO_CHANGES_DETECTED)

        # Should return error if pre-roll exceeds max recording length
        (status, ret_val) = omni.kit.commands.execute(
            START_RECORDING_COMMAND,
            target_paths=[(SIMPLE_TEST_CASE_PRIMPATH, True)],
            live_mode=False,
            use_frame_range=False,
            start_frame=0,
            end_frame=100,
            use_preroll=True,
            preroll_frame=1000000,
            record_to=RECORD_TO_FILE,
            take_name="Fake Take Name",
            record_folder=self._test_output_dir,
            increment_name=True,
            apply_root_anim=True,
            fps=0,
        )

        self.assertTrue(status)
        self.assertTrue(ret_val["error"])

        # Should stop recording on command
        (status, ret_val) = omni.kit.commands.execute(STOP_RECORDING_COMMAND)
        self.assertTrue(status)
        self.assertEqual(ret_val, recorder.RecordingReturnCode.NO_CHANGES_DETECTED)

        # Should clear prim list after deactivating root path
        self.assertFalse(prim_list.model.is_empty())
        prim_list.model.activate_all_for_prefix("/", False)
        await ui_test.human_delay(150)
        self.assertTrue(prim_list.model.is_empty())
