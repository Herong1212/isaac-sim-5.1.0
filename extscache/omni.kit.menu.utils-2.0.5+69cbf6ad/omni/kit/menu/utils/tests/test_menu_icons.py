from pathlib import Path

import omni.kit.test
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription, MenuLayout
from omni.kit.test_suite.helpers import get_test_data_path
from omni.ui.tests.compare_utils import CompareMetric
from omni.ui.tests.test_base import OmniUiTest


class TestMenuIcon(OmniUiTest):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_menu_icon(self):
        icon_path = Path(
            omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        ).joinpath("data/tests/icons/audio_record.svg")
        golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))

        submenu_list = [MenuItemDescription(name="Menu Item", glyph=str(icon_path))]
        menu_list = [MenuItemDescription(name="Icon Menu Test", glyph=str(icon_path), sub_menu=submenu_list)]
        omni.kit.menu.utils.add_menu_items(menu_list, "Icon Test", 99)
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(50)

        await ui_test.menu_click("Icon Test/Icon Menu Test", human_delay_speed=4)
        await ui_test.human_delay(50)

        try:
            await self.finalize_test(
                golden_img_dir=golden_img_dir,
                golden_img_name="test_menu_icon.png",
                cmp_metric=CompareMetric.MEAN_ERROR_SQUARED,
                threshold=0.001,
                hide_menu_bar=False,
            )
        finally:
            await ui_test.human_delay(50)

            omni.kit.menu.utils.remove_menu_items(menu_list, "Icon Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_menu_header(self):
        golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))

        submenu_list = [
            MenuItemDescription(name="Menu Item 1", header="Item 1"),
            MenuItemDescription(name="Menu Item 2", header="Item2"),
            MenuItemDescription(),
            MenuItemDescription(name="Menu Item 3", header=""),
        ]
        menu_list = [MenuItemDescription(name="Icon Menu Test", sub_menu=submenu_list)]
        omni.kit.menu.utils.add_menu_items(menu_list, "Header Test", 99)
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(50)

        await ui_test.menu_click("Header Test/Icon Menu Test", human_delay_speed=4)
        await ui_test.human_delay(10)

        try:
            await self.finalize_test(
                golden_img_dir=golden_img_dir,
                golden_img_name="test_menu_header.png",
                cmp_metric=CompareMetric.MEAN_ERROR_SQUARED,
                threshold=0.001,
                hide_menu_bar=False,
            )
        finally:
            await ui_test.human_delay(50)

            omni.kit.menu.utils.remove_menu_items(menu_list, "Header Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_menu_layout_icon(self):
        icon_path = Path(
            omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        ).joinpath("data/tests/icons/audio_record.svg")
        golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))

        submenu_list = [MenuItemDescription(name="Menu Item", glyph=str(icon_path))]
        menu_list = [MenuItemDescription(name="Icon Menu Test", glyph=str(icon_path), sub_menu=submenu_list)]
        omni.kit.menu.utils.add_menu_items(menu_list, "Icon Test", 99)

        # ----------------------------------------------------
        # simple layout test
        # ----------------------------------------------------
        menu_layout = [
            MenuLayout.Menu(
                "Icon Test",
                [
                    MenuLayout.Item("Moved 1", source="Icon Test/Icon Menu Test/Menu Item", glyph="cog.svg"),
                    MenuLayout.Item(
                        "Moved 2", source="Icon Test/Icon Menu Test/Menu Item", duplicate=True, glyph="flow_dark.svg"
                    ),
                ],
            ),
        ]
        omni.kit.menu.utils.add_layout(menu_layout)

        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(50)

        await ui_test.menu_click("Icon Test", human_delay_speed=4)
        await ui_test.human_delay(50)

        try:
            await self.finalize_test(
                golden_img_dir=golden_img_dir,
                golden_img_name="test_menu_icon2.png",
                cmp_metric=CompareMetric.MEAN_ERROR_SQUARED,
                threshold=0.001,
                hide_menu_bar=False,
            )
        finally:
            await ui_test.human_delay(50)

            omni.kit.menu.utils.remove_layout(menu_layout)
            omni.kit.menu.utils.remove_menu_items(menu_list, "Icon Test")
            self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
