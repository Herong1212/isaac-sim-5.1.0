from pathlib import Path

import omni.kit.test
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription, MenuItemOrder
from omni.kit.test_suite.helpers import get_test_data_path
from omni.ui.tests.compare_utils import CompareMetric
from omni.ui.tests.test_base import OmniUiTest


class TestMenuAppearAfter(OmniUiTest):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_menu_appear_after(self):
        golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))

        # menu lists
        submenu_list = [MenuItemDescription(name="Menu Item")]
        menu_list1 = [MenuItemDescription(name="New"), MenuItemDescription(name="Open")]
        menu_list2 = [MenuItemDescription(name="Recent Items", sub_menu=submenu_list, appear_after=["Open"])]
        menu_list3 = [MenuItemDescription(name="New test", appear_after=["Recent Items", "New"])]
        menu_list4 = [MenuItemDescription(name="Better test", appear_after=["New test", "Open"])]

        # add menus
        omni.kit.menu.utils.add_menu_items(menu_list1, "Order Test", 99)
        omni.kit.menu.utils.rebuild_menus()
        omni.kit.menu.utils.add_menu_items(menu_list4, "Order Test")
        omni.kit.menu.utils.rebuild_menus()
        omni.kit.menu.utils.add_menu_items(menu_list3, "Order Test")
        omni.kit.menu.utils.rebuild_menus()
        omni.kit.menu.utils.add_menu_items(menu_list2, "Order Test")
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(10)

        await ui_test.menu_click("Order Test", human_delay_speed=4)
        await ui_test.human_delay(10)

        try:
            await self.finalize_test(
                golden_img_dir=golden_img_dir,
                golden_img_name="test_menu_appear_after.png",
                hide_menu_bar=False,
                cmp_metric=CompareMetric.MEAN_ERROR_SQUARED,
                threshold=0.001,
            )
            await ui_test.human_delay(50)
        finally:
            omni.kit.menu.utils.remove_menu_items(menu_list1, "Order Test")
            omni.kit.menu.utils.remove_menu_items(menu_list2, "Order Test")
            omni.kit.menu.utils.remove_menu_items(menu_list3, "Order Test")
            omni.kit.menu.utils.remove_menu_items(menu_list4, "Order Test")

        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_menu_appear_after_first_last(self):
        golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))

        # menu lists
        submenu_list = [MenuItemDescription(name="Menu Item")]
        menu_list1 = [MenuItemDescription(name="New"), MenuItemDescription(name="Open")]
        menu_list2 = [
            MenuItemDescription(
                name="Open Something Else", sub_menu=submenu_list, appear_after=["missing", MenuItemOrder.LAST]
            )
        ]
        menu_list3 = [MenuItemDescription(name="Create Stage", appear_after=["missing", MenuItemOrder.FIRST])]
        menu_list4 = [MenuItemDescription(name="Better test", appear_after=["New test", "Open"])]

        # add menus
        omni.kit.menu.utils.add_menu_items(menu_list1, "Order Test", 99)
        omni.kit.menu.utils.rebuild_menus()
        omni.kit.menu.utils.add_menu_items(menu_list2, "Order Test")
        omni.kit.menu.utils.rebuild_menus()
        omni.kit.menu.utils.add_menu_items(menu_list3, "Order Test")
        omni.kit.menu.utils.rebuild_menus()
        omni.kit.menu.utils.add_menu_items(menu_list4, "Order Test")
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(10)

        await ui_test.menu_click("Order Test", human_delay_speed=4)
        await ui_test.human_delay(10)

        try:
            await self.finalize_test(
                golden_img_dir=golden_img_dir,
                golden_img_name="test_menu_appear_after_first_last.png",
                hide_menu_bar=False,
                cmp_metric=CompareMetric.MEAN_ERROR_SQUARED,
                threshold=0.001,
            )
            await ui_test.human_delay(50)
        finally:
            omni.kit.menu.utils.remove_menu_items(menu_list1, "Order Test")
            omni.kit.menu.utils.remove_menu_items(menu_list2, "Order Test")
            omni.kit.menu.utils.remove_menu_items(menu_list3, "Order Test")
            omni.kit.menu.utils.remove_menu_items(menu_list4, "Order Test")

        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

    async def test_menu_appear_after_nolist(self):
        golden_img_dir = Path(get_test_data_path(__name__, "golden_img"))

        # menu lists
        submenu_list = [MenuItemDescription(name="Menu Item")]
        menu_list1 = [MenuItemDescription(name="New"), MenuItemDescription(name="Open")]
        menu_list2 = [MenuItemDescription(name="New Items", sub_menu=submenu_list, appear_after="New")]

        # add menus
        omni.kit.menu.utils.add_menu_items(menu_list1, "Order Test", 99)
        omni.kit.menu.utils.rebuild_menus()
        omni.kit.menu.utils.add_menu_items(menu_list2, "Order Test")
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(10)

        await ui_test.menu_click("Order Test", human_delay_speed=4)
        await ui_test.human_delay(10)

        try:
            await self.finalize_test(
                golden_img_dir=golden_img_dir,
                golden_img_name="test_menu_appear_after_nolist.png",
                hide_menu_bar=False,
                cmp_metric=CompareMetric.MEAN_ERROR_SQUARED,
                threshold=0.001,
            )
            await ui_test.human_delay(50)
        finally:
            omni.kit.menu.utils.remove_menu_items(menu_list1, "Order Test")
            omni.kit.menu.utils.remove_menu_items(menu_list2, "Order Test")

        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})
