# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["TestWindow"]

import json

from ..activity_extension import ActivityWindowExtension, get_instance
from ..activity_menu import ActivityMenuOptions
from ..activity_progress_bar import ActivityProgressBarWindow
from ..activity_window import ActivityWindow
from ..activity_model import ActivityModelRealtime, ActivityModelDumpForProgress
from ..activity_progress_model import ActivityProgressModel
from ..activity_report import ActivityReportWindow
from ..style import get_shade_from_name

from omni.ui.tests.test_base import OmniUiTest
import omni.kit.ui_test as ui_test
from omni.kit.ui_test.input import emulate_mouse, emulate_mouse_slow_move, human_delay
from omni.ui import color as cl
from pathlib import Path
from unittest.mock import MagicMock
import omni.client
import omni.usd
import omni.kit.app
import omni.kit.test
import math
from carb.input import KeyboardInput, MouseEventType


EXTENSION_FOLDER_PATH = Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))
TEST_DATA_PATH = EXTENSION_FOLDER_PATH.joinpath("data/tests")
TEST_FILE_NAME = "test.activity"
TEST_SMALL_FILE_NAME = "test_small.activity"


def calculate_duration(events):
    duration = 0
    for i in range(0, len(events), 2):
        if events[i]['type'] == 'BEGAN' and events[i+1]['type'] == 'ENDED':
            duration += (events[i+1]['time'] - events[i]['time']) / 10000000
    return duration

def add_duration(node):
    total_duration = 0
    if 'children' in node:
        for child in node['children']:
            child_duration = add_duration(child)
            total_duration += child_duration
            if 'events' in child and child['events']:
                event_duration = calculate_duration(child['events'])
                child['duration'] = event_duration
                total_duration += event_duration
    node['duration'] = total_duration
    return total_duration

def process_json(json_data):
    add_duration(json_data['root'])
    return json_data


class TestWindow(OmniUiTest):

    async def load_data(self, file_name):
        filename = TEST_DATA_PATH.joinpath(file_name)
        result, _, content = omni.client.read_file(filename.as_posix())
        self.assertEqual(result, omni.client.Result.OK)
        self._data = json.loads(memoryview(content).tobytes().decode("utf-8"))

    async def test_general(self):
        """Testing general look of section"""
        menu = ActivityMenuOptions()
        model = ActivityModelRealtime()
        window = ActivityWindow("Test", model=model, activity_menu=menu)
        await omni.kit.app.get_app().next_update_async()
        await self.docked_test_window(
            window=window,
            width=300,
            height=385,
        )

        # Wait for images
        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=TEST_DATA_PATH, golden_img_name="window.png")

        self.assertIsNotNone(window.get_data())
        window.destroy()
        model.destroy()
        menu.destroy()

    async def test_activity_chart_scroll(self):

        menu = ActivityMenuOptions()
        model = ActivityModelRealtime()
        window = ActivityWindow("Test", model=model, activity_menu=menu)
        await omni.kit.app.get_app().next_update_async()
        await self.docked_test_window(
            window=window,
            width=300,
            height=385,
            block_devices=False,
        )

        for _ in range(120):
            await omni.kit.app.get_app().next_update_async()

        self.assertEqual(100, math.floor(window._ActivityWindow__chart._ActivityChart__zoom_level))

        await ui_test.emulate_mouse_move(ui_test.Vec2(180, 200), human_delay_speed=3)

        await ui_test.emulate_mouse_scroll(ui_test.Vec2(0, 50), human_delay_speed=3)

        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()

        self.assertEqual(101, math.floor(window._ActivityWindow__chart._ActivityChart__zoom_level))

        await self.finalize_test_no_image()

        # Move outside the window
        await ui_test.emulate_mouse_move(ui_test.Vec2(400, 400), human_delay_speed=3)

        window.destroy()
        model.destroy()
        menu.destroy()

    async def test_activity_chart_drag(self):

        menu = ActivityMenuOptions()
        model = ActivityModelRealtime()
        window = ActivityWindow("Test", model=model, activity_menu=menu)
        await omni.kit.app.get_app().next_update_async()
        await self.docked_test_window(
            window=window,
            width=300,
            height=385,
            block_devices=False,
        )

        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()

        start_pos = ui_test.Vec2(180, 50)
        end_pos = ui_test.Vec2(230, 50)
        human_delay_speed = 2
        await ui_test.emulate_mouse_move(start_pos, human_delay_speed=human_delay_speed)
        await emulate_mouse(MouseEventType.MIDDLE_BUTTON_DOWN)
        await human_delay(human_delay_speed)
        await emulate_mouse_slow_move(start_pos, end_pos, human_delay_speed=human_delay_speed)
        await emulate_mouse(MouseEventType.MIDDLE_BUTTON_UP)

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=TEST_DATA_PATH, golden_img_name="test_activity_chart_drag.png")

        # Move outside the window
        await ui_test.emulate_mouse_move(ui_test.Vec2(400, 400), human_delay_speed=3)

        window.destroy()
        model.destroy()
        menu.destroy()

    async def test_selection(self):
        menu = ActivityMenuOptions()
        model = ActivityModelRealtime()
        window = ActivityWindow("Test", model=model, activity_menu=menu)
        await omni.kit.app.get_app().next_update_async()

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        self.assertIsNone(model.selection)
        model.selection = 2
        self.assertEqual(model.selection, 2)

        window.destroy()
        model.destroy()
        menu.destroy()

    async def test_activity_chart_pan(self):

        menu = ActivityMenuOptions()
        model = ActivityModelRealtime()
        window = ActivityWindow("Test", model=model, activity_menu=menu)
        await omni.kit.app.get_app().next_update_async()
        await self.docked_test_window(
            window=window,
            width=300,
            height=385,
            block_devices=False,
        )

        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()

        start_pos = ui_test.Vec2(180, 50)
        end_pos = ui_test.Vec2(230, 50)
        human_delay_speed = 2
        await ui_test.emulate_mouse_move(start_pos, human_delay_speed=human_delay_speed)
        await emulate_mouse(MouseEventType.RIGHT_BUTTON_DOWN)
        await human_delay(human_delay_speed)
        await emulate_mouse_slow_move(start_pos, end_pos, human_delay_speed=human_delay_speed)
        await emulate_mouse(MouseEventType.RIGHT_BUTTON_UP)

        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=TEST_DATA_PATH, golden_img_name="test_activity_chart_pan.png")

        # Move outside the window
        await ui_test.emulate_mouse_move(ui_test.Vec2(400, 400), human_delay_speed=3)

        window.destroy()
        model.destroy()
        menu.destroy()

    async def test_activities_tab(self):

        menu = ActivityMenuOptions()
        model = ActivityModelRealtime()
        window = ActivityWindow("Test", model=model, activity_menu=menu)
        await omni.kit.app.get_app().next_update_async()
        await self.docked_test_window(
            window=window,
            width=300,
            height=385,
            block_devices=False,
        )

        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()

        human_delay_speed = 10

        # Click on Activities tab
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(180, 15), human_delay_speed=2)
        await human_delay(human_delay_speed)
        # Click on Timeline tab
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(100, 15), human_delay_speed=2)
        await human_delay(human_delay_speed)
        # Click on Activities tab
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(180, 15), human_delay_speed=2)

        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=TEST_DATA_PATH, golden_img_name="test_activities_tab.png")

        # Move outside the window
        await ui_test.emulate_mouse_move(ui_test.Vec2(400, 400), human_delay_speed=3)

        window.destroy()
        model.destroy()
        menu.destroy()

    async def test_activity_menu_open(self):

        ext = get_instance()

        menu = ActivityMenuOptions(load_data=ext.load_data)
        model = ActivityModelRealtime()
        window = ActivityWindow("Test", model=model, activity_menu=menu)
        window_width = 300

        await omni.kit.app.get_app().next_update_async()
        await self.docked_test_window(
            window=window,
            width=window_width,
            height=385,
            block_devices=False,
        )

        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()

        human_delay_speed = 5

        # Click on Activity hamburger menu
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(window_width-20, 15), human_delay_speed=2)
        await human_delay(human_delay_speed)
        # Click on Open menu option
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(window_width-20, 30), human_delay_speed=2)
        await human_delay(human_delay_speed)
        # Cancel Open dialog
        await ui_test.emulate_keyboard_press(KeyboardInput.ESCAPE)
        await human_delay(human_delay_speed)
        # Do it all again to cover the case where it was open before, and has to be destroyed
        # Click on Activity hamburger menu
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(window_width-20, 15), human_delay_speed=2)
        await human_delay(human_delay_speed)
        # Click on Open menu option
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(window_width-20, 30), human_delay_speed=2)
        await human_delay(human_delay_speed)
        # Cancel Open dialog
        await ui_test.emulate_keyboard_press(KeyboardInput.ESCAPE)
        await human_delay(human_delay_speed)

        # simulate failure first
        menu._ActivityMenuOptions__menu_open_apply_filename("broken_test", str(TEST_DATA_PATH))
        await human_delay(human_delay_speed)
        self.assertIsNone(menu._current_filename)

        # simulate opening the file through file dialog
        menu._ActivityMenuOptions__menu_open_apply_filename(TEST_SMALL_FILE_NAME, str(TEST_DATA_PATH))
        await human_delay(human_delay_speed)
        self.assertIsNotNone(menu._current_filename)

        await self.finalize_test_no_image()

        # Move outside the window
        await ui_test.emulate_mouse_move(ui_test.Vec2(window_width+20, 400), human_delay_speed=3)

        ext = None
        window.destroy()
        model.destroy()
        menu.destroy()

    async def test_activity_menu_save(self):
        ext = get_instance()

        # await self.load_data(TEST_SMALL_FILE_NAME)
        menu = ActivityMenuOptions(get_save_data=ext.get_save_data)
        model = ActivityModelRealtime()
        window = ActivityWindow("Test", model=model, activity_menu=menu)
        window_width = 300

        await omni.kit.app.get_app().next_update_async()
        await self.docked_test_window(
            window=window,
            width=window_width,
            height=385,
            block_devices=False,
        )

        for _ in range(20):
            await omni.kit.app.get_app().next_update_async()

        human_delay_speed = 5

        # Click on Activity hamburger menu
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(window_width-20, 15), human_delay_speed=2)
        await human_delay(human_delay_speed)
        # Click on Save menu option
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(window_width-20, 50), human_delay_speed=2)
        await human_delay(human_delay_speed)
        # Cancel Open dialog
        await ui_test.emulate_keyboard_press(KeyboardInput.ESCAPE)
        await human_delay(human_delay_speed)
        # Do it all again to cover the case where it was open before, and has to be destroyed
        # Click on Activity hamburger menu
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(window_width-20, 15), human_delay_speed=2)
        await human_delay(human_delay_speed)
        # Click on Save menu option
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(window_width-20, 50), human_delay_speed=2)
        await human_delay(human_delay_speed)
        # Cancel Open dialog
        await ui_test.emulate_keyboard_press(KeyboardInput.ESCAPE)
        await human_delay(human_delay_speed)

        # Create a mock for omni.client.write_file, so we don't have to actually write out to a file
        mock_write_file = MagicMock()
        # Set the return value of the mock to omni.client.Result.OK
        mock_write_file.return_value = omni.client.Result.OK
        # Replace the actual omni.client.write_file with the mock
        omni.client.write_file = mock_write_file

        # simulate opening the file through file dialog
        menu._ActivityMenuOptions__menu_save_apply_filename("test", str(TEST_DATA_PATH))
        await human_delay(human_delay_speed)

        ext._save_current_activity()

        self.assertTrue(ext._ActivityWindowExtension__model)
        await self.finalize_test_no_image()

        # Move outside the window
        await ui_test.emulate_mouse_move(ui_test.Vec2(window_width+20, 400), human_delay_speed=3)

        mock_write_file.reset_mock()
        ext = None
        window.destroy()
        model.destroy()
        menu.destroy()

    async def test_activity_report(self):
        """Testing activity report window"""
        await self.load_data(TEST_SMALL_FILE_NAME)

        # Adding "duration" data for each child, as the test.activity files didn't already have that
        self._data = process_json(self._data)

        window = ActivityReportWindow("TestReport", path=TEST_SMALL_FILE_NAME, data=self._data)
        await omni.kit.app.get_app().next_update_async()
        await self.docked_test_window(
            window=window,
            width=600,
            height=450,
        )

        # Wait for images
        for _ in range(120):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=TEST_DATA_PATH, golden_img_name="report_window.png")

        window.destroy()
        window = None

    async def test_progress_window(self):
        """Test progress window with loaded activity"""
        await self.load_data(TEST_FILE_NAME)
        loaded_model = ActivityModelDumpForProgress(data=self._data)
        model = ActivityProgressModel(source=loaded_model)
        menu = ActivityMenuOptions()
        window = ActivityProgressBarWindow(ActivityWindowExtension.PROGRESS_WINDOW_NAME, model=model, activity_menu=menu)
        model.finished_loading()
        await omni.kit.app.get_app().next_update_async()
        await self.docked_test_window(
            window=window,
            width=415,
            height=355,
            block_devices=False,
        )

        # Wait for images
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        human_delay_speed = 10

        window.start_timer()
        await human_delay(30)
        window.stop_timer()
        await human_delay(5)

        # Click on Activities tab
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(250, 15), human_delay_speed=2)
        await human_delay(human_delay_speed)
        # Click on Timeline tab
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(180, 15), human_delay_speed=2)
        await human_delay(human_delay_speed)

        await self.finalize_test(golden_img_dir=TEST_DATA_PATH, golden_img_name="progress_window.png", threshold=.015)

        self.assertIsNotNone(model.get_data())
        report_data = loaded_model.get_report_data()
        data = loaded_model.get_data()
        self.assertIsNotNone(report_data)
        self.assertGreater(len(data), len(report_data))

        loaded_model.destroy()
        model.destroy()
        menu.destroy()
        window.destroy()

    async def test_chart_window_bars(self):
        ext = get_instance()
        ext.show_window(None, True)
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        width = 415
        height = 355
        await self.docked_test_window(
            window=ext._timeline_window,
            width=width,
            height=height,
            block_devices=False,
        )

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        ext._timeline_window._ActivityWindow__chart._activity_menu_option._ActivityMenuOptions__menu_open_apply_filename(TEST_FILE_NAME, str(TEST_DATA_PATH))

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=TEST_DATA_PATH, golden_img_name="chart_window_bars.png")
        ext.show_window(None, False)
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
        ext = None

    async def test_chart_window_activities(self):
        ext = get_instance()
        ext.show_window(None, True)
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        width = 415
        height = 355
        await self.docked_test_window(
            window=ext._timeline_window,
            width=width,
            height=height,
            block_devices=False,
        )

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        ext._timeline_window._ActivityWindow__chart._activity_menu_option._ActivityMenuOptions__menu_open_apply_filename(TEST_FILE_NAME, str(TEST_DATA_PATH))

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        # Click on Activities tab
        await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(240, 15), human_delay_speed=2)

        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        await self.finalize_test(golden_img_dir=TEST_DATA_PATH, golden_img_name="chart_window_activities.png")
        ext.show_window(None, False)
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()
        ext = None

    async def test_extension_start_stop(self):
        ext = get_instance()
        ext.show_window(None, True)
        for _ in range(10):
            await omni.kit.app.get_app().next_update_async()

        manager = omni.kit.app.get_app().get_extension_manager()
        ext_id = "omni.activity.ui"
        self.assertTrue(ext_id)
        self.assertTrue(manager.is_extension_enabled(ext_id))
        ext = None
        manager.set_extension_enabled(ext_id, False)
        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()
        self.assertTrue(not manager.is_extension_enabled(ext_id))
        manager.set_extension_enabled(ext_id, True)
        for _ in range(5):
            await omni.kit.app.get_app().next_update_async()
        self.assertTrue(manager.is_extension_enabled(ext_id))

    async def test_extension_level_progress_bar(self):
        ext = get_instance()
        ext._show_progress_window()

        await human_delay(5)

        ext.show_progress_bar(None, False)
        await human_delay(5)

        ext.show_progress_bar(None, True)
        await human_delay(5)

        self.assertTrue(ext._is_progress_visible())
        ext.show_progress_bar(None, False)

        ext = None

    async def test_extension_level_window(self):
        ext = get_instance()
        await human_delay(5)

        ext.show_window(None, False)
        await human_delay(5)

        ext.show_window(None, True)
        await human_delay(5)

        self.assertTrue(ext._timeline_window.visible)
        ext.show_window(None, False)

        ext = None

    async def test_extension_level_commands(self):
        await self.create_test_area(width=350, height=300)

        ext = get_instance()
        await human_delay(5)

        ext._on_command("AddReference", kwargs={})
        await human_delay(5)
        ext._on_command("CreatePayload", kwargs={})
        await human_delay(5)
        ext._on_command("CreateSublayer", kwargs={})
        await human_delay(5)
        ext._on_command("ReplacePayload", kwargs={})
        await human_delay(5)
        ext._on_command("ReplaceReference", kwargs={})
        await human_delay(5)

        self.assertTrue(ext._ActivityWindowExtension__activity_started)

        # Create a mock event object
        ext._on_stage_assets_loaded()
        self.assertFalse(ext._ActivityWindowExtension__activity_started)

        event = MagicMock()
        ext._on_stage_opening(event)
        self.assertTrue(ext._ActivityWindowExtension__activity_started)

        ext._on_stage_open_failed()
        self.assertFalse(ext._ActivityWindowExtension__activity_started)

        ext.show_asset_load_prompt()
        await human_delay(20)
        self.assertTrue(ext._asset_prompt.is_visible())
        ext._asset_prompt.set_text("Testing, testing")
        await human_delay(20)

        await self.finalize_test(golden_img_dir=TEST_DATA_PATH, golden_img_name="asset_load_prompt.png")

        ext.hide_asset_load_prompt()

        event.reset_mock()
        ext = None

    async def test_styles(self):

        # full name comparisons
        self.assertEqual(get_shade_from_name("USD"), cl("#2091D0"))
        self.assertEqual(get_shade_from_name("Read"), cl("#1A75A8"))
        self.assertEqual(get_shade_from_name("Resolve"), cl("#16648F"))
        self.assertEqual(get_shade_from_name("Stage"), cl("#d43838"))
        self.assertEqual(get_shade_from_name("Render Thread"), cl("#d98927"))
        self.assertEqual(get_shade_from_name("Execute"), cl("#A2661E"))
        self.assertEqual(get_shade_from_name("Post Sync"), cl("#626262"))
        self.assertEqual(get_shade_from_name("Textures"), cl("#4FA062"))
        self.assertEqual(get_shade_from_name("Load"), cl("#3C784A"))
        self.assertEqual(get_shade_from_name("Queue"), cl("#31633D"))
        self.assertEqual(get_shade_from_name("Materials"), cl("#8A6592"))
        self.assertEqual(get_shade_from_name("Compile"), cl("#5D4462"))
        self.assertEqual(get_shade_from_name("Create Shader Variations"), cl("#533D58"))
        self.assertEqual(get_shade_from_name("Load Textures"), cl("#4A374F"))
        self.assertEqual(get_shade_from_name("Meshes"), cl("#626262"))
        self.assertEqual(get_shade_from_name("Ray Tracing Pipeline"), cl("#8B8000"))

        # startswith comparisons
        self.assertEqual(get_shade_from_name("Opening_test"), cl("#A12A2A"))

        # endswith comparisons
        self.assertEqual(get_shade_from_name("test.usda"), cl("#13567B"))
        self.assertEqual(get_shade_from_name("test.hdr"), cl("#34A24E"))
        self.assertEqual(get_shade_from_name("test.png"), cl("#2E9146"))
        self.assertEqual(get_shade_from_name("test.jpg"), cl("#2B8741"))
        self.assertEqual(get_shade_from_name("test.JPG"), cl("#2B8741"))
        self.assertEqual(get_shade_from_name("test.ovtex"), cl("#287F3D"))
        self.assertEqual(get_shade_from_name("test.dds"), cl("#257639"))
        self.assertEqual(get_shade_from_name("test.exr"), cl("#236E35"))
        self.assertEqual(get_shade_from_name("test.wav"), cl("#216631"))
        self.assertEqual(get_shade_from_name("test.tga"), cl("#1F5F2D"))
        self.assertEqual(get_shade_from_name("test.mdl"), cl("#76567D"))

        # "in" comparisons
        self.assertEqual(get_shade_from_name('(test instance) 5'), cl("#694D6F"))

        # anything else
        self.assertEqual(get_shade_from_name("random_test_name"), cl("#555555"))
