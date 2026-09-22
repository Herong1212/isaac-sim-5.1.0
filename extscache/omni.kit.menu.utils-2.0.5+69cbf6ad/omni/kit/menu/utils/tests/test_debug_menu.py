import json
import pathlib
import tempfile

import carb.input
import omni.kit.test
import omni.ui as ui
from omni.kit import ui_test
from omni.kit.menu.utils import LayoutSourceSearch, MenuItemDescription, MenuLayout
from omni.kit.test_suite.helpers import get_test_data_path
from omni.kit.window.file_exporter.test_helper import FileExporterTestHelper
from omni.ui.tests.test_base import OmniUiTest


class TestDebugMenu(OmniUiTest):
    async def setUp(self):
        pass

    async def tearDown(self):
        # close window
        await ui_test.human_delay(50)
        ui.Workspace.show_window("omni.kit.menu.utils debug", False)

    async def test_debug_menu_golden(self):
        debug_window_name = "omni.kit.menu.utils debug"

        # hotkey - show_menu_debug_window
        await ui_test.emulate_keyboard_press(
            carb.input.KeyboardInput.M,
            carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL
            + carb.input.KEYBOARD_MODIFIER_FLAG_ALT
            + carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT,
        )
        await ui_test.human_delay(50)

        # golden image
        golden_img_dir = pathlib.Path(get_test_data_path(__name__, "golden_img"))
        await self.docked_test_window(window=ui.Workspace.get_window(debug_window_name), width=450, height=300)

        await self.finalize_test(golden_img_dir=golden_img_dir, golden_img_name="test_debug_window.png")
        await ui_test.human_delay(50)

    async def test_debug_menu_ui(self):
        debug_window_name = "omni.kit.menu.utils debug"

        # hotkey - show_menu_debug_window
        await ui_test.emulate_keyboard_press(
            carb.input.KeyboardInput.M,
            carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL
            + carb.input.KEYBOARD_MODIFIER_FLAG_ALT
            + carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT,
        )
        await ui_test.human_delay(50)

        # build menus to debug
        def dummy_func():  # pragma: no cover
            pass

        menu_dict = omni.kit.menu.utils.build_submenu_dict(
            [
                MenuItemDescription(name="File/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 1", original_svg_color=True),
                MenuItemDescription(
                    name="Edit/Root Item/SubMenu 1/SubMenu 2/SubMenu Item 2",
                    onclick_fn=dummy_func,
                    unclick_fn=dummy_func,
                ),
                MenuItemDescription(name="Window/Root Item/SubMenu 1/SubMenu Item 3"),
                MenuItemDescription(name="Help/Root Item/Item 4", onclick_right_fn=dummy_func),
            ]
        )

        # add menus
        for group in menu_dict:
            omni.kit.menu.utils.add_menu_items(menu_dict[group], group)
        await ui_test.human_delay(50)

        # add layout
        menu_layout = [
            MenuLayout.Menu(
                "File",
                [
                    MenuLayout.Item("Root Item"),
                    MenuLayout.Seperator(),
                    MenuLayout.Item("SubMenu Item 1"),
                    MenuLayout.SubMenu("SubMenu 2", remove=True),
                    MenuLayout.Sort(source_search=LayoutSourceSearch.EVERYWHERE, sort_submenus=True),
                ],
            ),
            MenuLayout.Menu("SubMenu Test", remove=True),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)

        # refresh groups
        for group in menu_dict:
            omni.kit.menu.utils.refresh_menu_items(group)
            await ui_test.menu_click(group, human_delay_speed=4)
            await ui_test.human_delay(10)

        # click refresh window
        await ui_test.find(f"{debug_window_name}//Frame/**/Button[*].identifier=='refresh_window'").click()
        await ui_test.human_delay(50)

        # click rebuild menus
        await ui_test.find(f"{debug_window_name}//Frame/**/Button[*].identifier=='rebuild_menus'").click()
        await ui_test.human_delay(50)

        # save menus
        await ui_test.find(f"{debug_window_name}//Frame/**/Button[*].identifier=='save_menus'").click()
        tmpdir = tempfile.mkdtemp()
        menu_file = f"{tmpdir}/menus.json"
        async with FileExporterTestHelper() as file_export_helper:
            await file_export_helper.click_apply_async(filename_url=menu_file)

        # verify file exists
        data = ""
        with open(menu_file, encoding="utf-8") as f:
            data = json.load(f)
        self.assertNotEqual(data, "")

        # save layout
        await ui_test.find(f"{debug_window_name}//Frame/**/Button[*].identifier=='save_menu_layout'").click()
        layout_file = f"{tmpdir}/layout.json"
        async with FileExporterTestHelper() as file_export_helper:
            await file_export_helper.click_apply_async(filename_url=layout_file)

        # verify file exists
        data = ""
        with open(layout_file, encoding="utf-8") as f:
            data = json.load(f)
        self.assertNotEqual(data, "")

        # verify layouts are removed
        omni.kit.menu.utils.remove_layout(menu_layout)
        self.assertTrue(omni.kit.menu.utils.get_menu_layout() == [])

        # verify menus are removed
        for group in menu_dict:
            omni.kit.menu.utils.remove_menu_items(menu_dict[group], group)
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
