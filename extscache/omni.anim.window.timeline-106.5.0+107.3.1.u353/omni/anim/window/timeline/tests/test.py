from pathlib import Path

import omni.kit.app
import omni.kit.test
import omni.kit.ui_test as ui_test
import omni.timeline
import omni.ui as ui
import omni.usd
from omni.ui.tests.test_base import OmniUiTest
from pxr import Usd

from ..scripts.utils import remove_all_keys


class TimelineTests(OmniUiTest):
    async def setUp(self):
        await super().setUp()
        extension_root_folder = Path(
            omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        )
        self._GOLDEN_IMG_DIR = extension_root_folder.joinpath("data/golden_img")
        self._MAP_DIR = extension_root_folder.joinpath("data/test_map")

    """
    The first test case load
    """

    async def test_timeline_basic(self):
        # Load the USD map
        usd_context = omni.usd.get_context()
        test_file_path = self._MAP_DIR.joinpath("basic_curve_cube.usda").absolute()
        await usd_context.open_stage_async(str(test_file_path))
        timeline = omni.timeline.get_timeline_interface()

        await omni.kit.app.get_app().next_update_async()

        stage = usd_context.get_stage()
        # select prim
        usd_context.get_selection().set_selected_prim_paths(["/World/Cube"], False)

        # delay more frames to fix the division by zero issue (timeline not init fps)
        await ui_test.human_delay(10)

        # dock the timeline
        ui.Workspace.show_window("Property", False)
        ui.Workspace.show_window("Timeline toolbar")

        control_buttons = ui_test.find_all("Timeline toolbar//Frame/**/Button[*]")

        # next key
        for button in control_buttons:
            if button.widget.image_url.endswith("next_keyframe.svg"):
                await button.click()

        await ui_test.human_delay(5)

        cur_time = timeline.get_current_time()
        self.assertAlmostEqual(cur_time, 1.25)

        # pre frame
        for button in control_buttons:
            if button.widget.image_url.endswith("previous_frame.svg"):
                for i in range(6):
                    await button.click()
                    await ui_test.human_delay()

        cur_time = timeline.get_current_time()
        # 6/24fps = 0.25s
        self.assertAlmostEqual(cur_time, 1.0)

        # add key
        for button in control_buttons:
            if button.widget.image_url.endswith("Add_Key.svg"):
                await button.click()

        await ui_test.human_delay(5)

        # next frame
        for button in control_buttons:
            if button.widget.image_url.endswith("next_frame.svg"):
                await button.click()

        await ui_test.human_delay(5)

        # pre key
        for button in control_buttons:
            if button.widget.image_url.endswith("previous_keyframe.svg"):
                await button.click()

        await ui_test.human_delay(5)

        cur_time = timeline.get_current_time()
        self.assertAlmostEqual(cur_time, 1.0)

        # fps
        fps_widget = ui_test.find("Timeline toolbar//Frame/**/ComboBox[*].identifier=='edit_combobox'")
        self.assertIsNotNone(fps_widget)
        fps_widget.model.get_item_value_model().set_value(2)  # 30fps
        await ui_test.human_delay(5)

        # remove key
        remove_all_keys(["/World/Cube"], stage, Usd.TimeCode(29), Usd.TimeCode(31))

        await ui_test.human_delay(5)

        # opition menu
        for button in control_buttons:
            if button.widget.image_url.endswith("details_options.png") or button.widget.identifier == "settings_icon":
                await button.click()

        # context menu
        await ui_test.select_context_menu("SMPTE", offset=ui_test.Vec2(10, 10))

        scene_end_widget = ui_test.find("Timeline toolbar//Frame/**/StringField[*].identifier=='scene_end'")
        self.assertIsNotNone(scene_end_widget)
        text = scene_end_widget.model.as_string
        self.assertEqual(text, "00:00:04:04")

        # auto key
        selection = omni.usd.get_context().get_selection()
        selection.set_selected_prim_paths(["/World/Camera"], False)

        auto_button = ui_test.find("Timeline toolbar//Frame/**/ToolButton[*].name=='AutoFrame'")
        self.assertIsNotNone(auto_button)
        await auto_button.click()

        await ui_test.human_delay(5)

        # zoom
        await ui_test.emulate_mouse_move(ui_test.Vec2(500, 500))
        await ui_test.emulate_mouse_scroll(ui_test.Vec2(100, 100))

        await ui_test.human_delay(200)
        await auto_button.click()
        await ui_test.human_delay(10)

        # Do the golden image comparison
        # await self.finalize_test(golden_img_dir=self._GOLDEN_IMG_DIR, golden_img_name="timeline.png")
