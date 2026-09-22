import omni.kit.test
from omni.kit import ui_test
from omni.kit.menu.utils import MenuItemDescription
from omni.ui.tests.test_base import OmniUiTest


class TestRadioButtons(OmniUiTest):
    async def setUp(self):
        pass

    async def tearDown(self):
        pass

    async def test_radio_buttons1(self):
        radio_one_value = -1
        radio_two_value = -1

        def radio_one_func(value):
            nonlocal radio_one_value
            radio_one_value = value

        def radio_two_func(value):
            nonlocal radio_two_value
            radio_two_value = value

        # register actions
        action_registry = omni.kit.actions.core.get_action_registry()
        for index in range(10):
            action_registry.register_action(
                "test.radio.buttons", f"clicked_one_{index}", lambda v=index: radio_one_func(v)
            )
            action_registry.register_action(
                "test.radio.buttons", f"clicked_two_{index}", lambda v=index: radio_two_func(v)
            )

        submenu_list = [
            MenuItemDescription(
                name=f"Radio One {index}",
                radio_group="test1",
                onclick_action=("test.radio.buttons", f"clicked_one_{index}"),
                ticked_value=index == 1,
            )
            for index in range(10)
        ]
        submenu_list += [MenuItemDescription()]
        submenu_list += [
            MenuItemDescription(
                name=f"Radio Two {index}",
                radio_group="test2",
                onclick_action=("test.radio.buttons", f"clicked_two_{index}"),
                ticked_value=index == 0,
            )
            for index in range(10)
        ]

        menu_list = [MenuItemDescription(name="Tear-off Menu Test", sub_menu=submenu_list)]
        omni.kit.menu.utils.add_menu_items(menu_list, "Tear-off-Test", 99)
        omni.kit.menu.utils.rebuild_menus()
        await ui_test.human_delay(50)

        # menu widgets
        menu_widget = None
        for w in ui_test.get_menubar().find_all("**/"):
            if isinstance(w.widget, omni.kit.menu.core.uiMenu) and w.widget.text == "Tear-off Menu Test":
                menu_widget = w

        self.assertTrue(menu_widget)

        try:
            # tear off menu
            menu_widget.widget.tear_at(100, 200)

            buttons = {}
            for w in menu_widget.find_all("**/"):
                if isinstance(w.widget, omni.kit.menu.core.uiMenuItem):
                    buttons[w.widget.text] = w

            for name, item in buttons.items():
                await item.click(human_delay_speed=10)
                if "One " in name:
                    self.assertEqual(int(name.replace("Radio One ", "")), radio_one_value)
                elif "Two " in name:
                    self.assertEqual(int(name.replace("Radio Two ", "")), radio_two_value)

        finally:
            omni.kit.menu.utils.remove_menu_items(menu_list, "Tear-off-Test", 99)

        # verify menus removed
        self.assertTrue(omni.kit.menu.utils.get_merged_menus() == {})

        # free actions
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_all_actions_for_extension("test.radio.buttons")
