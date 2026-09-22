from pathlib import Path

import carb
import omni.kit.test
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription
from omni.kit.test_suite.helpers import get_test_data_path
from omni.ui.tests.test_base import OmniUiTest


class TestCustomStyle(OmniUiTest):
    async def setUp(self):
        self.__screenshot_offset = carb.settings.get_settings().get("/exts/omni.kit.menu.utils/screenshot_offset") or 0

    async def tearDown(self):
        pass

    async def test_custom_style1(self):
        golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))

        sub_menu_list = [MenuItemDescription(name="None", enabled=False)]
        menu_list = [
            MenuItemDescription(name="Isaac Sim Robot Wizard", ticked_value=True),
            MenuItemDescription(),
            MenuItemDescription(
                name="New", hotkey=(carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL, carb.input.KeyboardInput.N)
            ),
            MenuItemDescription(name="New From Stage Template", sub_menu=sub_menu_list),
            MenuItemDescription(),
            MenuItemDescription(
                name="Open", hotkey=(carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL, carb.input.KeyboardInput.O)
            ),
            MenuItemDescription(name="Open Recent", sub_menu=sub_menu_list),
            MenuItemDescription(name="Re-open with New Edit Layer"),
            MenuItemDescription(),
            MenuItemDescription(
                name="Save", hotkey=(carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL, carb.input.KeyboardInput.S)
            ),
            MenuItemDescription(
                name="Save As...",
                hotkey=(
                    carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT + carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL,
                    carb.input.KeyboardInput.S,
                ),
            ),
            MenuItemDescription(
                name="Save With Options",
                hotkey=(
                    carb.input.KEYBOARD_MODIFIER_FLAG_ALT + carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL,
                    carb.input.KeyboardInput.S,
                ),
            ),
            MenuItemDescription(name="Save Flattened As..."),
            MenuItemDescription(name="Collect and Save As..."),
            MenuItemDescription(),
            MenuItemDescription(name="Import", enabled=False),
            MenuItemDescription(name="Export", enabled=False),
            MenuItemDescription(),
            MenuItemDescription(name="Add Reference"),
            MenuItemDescription(name="Add Payload"),
            MenuItemDescription(),
            MenuItemDescription(name="Exit"),
        ]

        omni.kit.menu.utils.add_menu_items(menu_list, "File", 99)
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(50)

        # menu widgets
        menu_widget = None
        for w in ui_test.get_menubar().find_all("**/"):
            if isinstance(w.widget, omni.kit.menu.core.uiMenu) and w.widget.text == "File":
                menu_widget = w

        self.assertTrue(menu_widget)

        try:
            # tear off menu
            menu_widget.widget.tear_at(100, 50)
            await ui_test.human_delay(10)

            await self.finalize_test(
                golden_img_dir=golden_img_dir,
                golden_img_name=f"test_custom_style_{self.__screenshot_offset+1}.png",
                hide_menu_bar=False,
            )
            await ui_test.human_delay(10)

        finally:
            omni.kit.menu.utils.remove_menu_items(menu_list, "File", 99)

        # verify menus removed
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_custom_style2(self):
        golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))

        sub_menu_list = [MenuItemDescription(name="None", enabled=False)]
        menu_list = [
            MenuItemDescription(header="Getting Started"),
            MenuItemDescription(name="Isaac Sim Robot Wizard", ticked_value=True),
            MenuItemDescription(name="Demos & Samples", sub_menu=sub_menu_list),
            MenuItemDescription(header="Issac Sim Reference"),
            MenuItemDescription(name="About"),
            MenuItemDescription(name="Online Guide"),
            MenuItemDescription(name="Scripting Manual"),
            MenuItemDescription(header="Omniverse Reference"),
            MenuItemDescription(name="Kit Programming Manual"),
            MenuItemDescription(name="Omni UI Docs"),
            MenuItemDescription(header="Warp Reference"),
            MenuItemDescription(name="Getting Started"),
            MenuItemDescription(name="Documentation"),
            MenuItemDescription(),
            MenuItemDescription(name="Isaac Sim App Selector"),
        ]

        omni.kit.menu.utils.add_menu_items(menu_list, "Help", 99)
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(50)

        # menu widgets
        menu_widget = None
        for w in ui_test.get_menubar().find_all("**/"):
            if isinstance(w.widget, omni.kit.menu.core.uiMenu) and w.widget.text == "Help":
                menu_widget = w

        self.assertTrue(menu_widget)

        try:
            # tear off menu
            menu_widget.widget.tear_at(100, 100)
            await ui_test.human_delay(10)

            await self.finalize_test(
                golden_img_dir=golden_img_dir,
                golden_img_name=f"test_custom_style_{self.__screenshot_offset+2}.png",
                hide_menu_bar=False,
            )
            await ui_test.human_delay(10)

        finally:
            omni.kit.menu.utils.remove_menu_items(menu_list, "Help", 99)

        # verify menus removed
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_custom_style3(self):
        golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))

        menu_list = [
            MenuItemDescription(name="Collision Group"),
            MenuItemDescription(name="Ground Plane"),
            MenuItemDescription(name="Physics Material"),
            MenuItemDescription(name="Physics Scheme"),
            MenuItemDescription(header="Robotic Joints"),
            MenuItemDescription(name="Fixed"),
            MenuItemDescription(name="Prismatic"),
            MenuItemDescription(name="Revolute"),
            MenuItemDescription(header="Joints"),
            MenuItemDescription(name="D6"),
            MenuItemDescription(name="Distance"),
            MenuItemDescription(name="Gear"),
            MenuItemDescription(name="Rack and Pinion"),
            MenuItemDescription(name="Spherical"),
        ]

        omni.kit.menu.utils.add_menu_items(menu_list, "Physics", 99)
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(50)

        # menu widgets
        menu_widget = None
        for w in ui_test.get_menubar().find_all("**/"):
            if isinstance(w.widget, omni.kit.menu.core.uiMenu) and w.widget.text == "Physics":
                menu_widget = w

        self.assertTrue(menu_widget)

        try:
            # tear off menu
            menu_widget.widget.tear_at(100, 100)
            await ui_test.human_delay(10)

            await self.finalize_test(
                golden_img_dir=golden_img_dir,
                golden_img_name=f"test_custom_style_{self.__screenshot_offset+3}.png",
                hide_menu_bar=False,
            )
            await ui_test.human_delay(10)

        finally:
            omni.kit.menu.utils.remove_menu_items(menu_list, "Physics", 99)

        # verify menus removed
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
