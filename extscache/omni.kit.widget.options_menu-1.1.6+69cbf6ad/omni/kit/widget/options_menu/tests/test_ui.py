from pathlib import Path

import carb.settings
import omni.kit.ui_test as ui_test
from omni.ui.tests.test_base import OmniUiTest
import omni.ui as ui

from ..options_menu import OptionsMenu
from ..options_model import OptionsModel
from ..option_custom import OptionCustom
from ..option_item import OptionItem
from ..option_separator import OptionSeparator
from ..option_radio import OptionRadios
from ..radio_menu import RadioModel, RadioMenu

CURRENT_PATH = Path(__file__).parent.absolute()
TEST_DATA_PATH = CURRENT_PATH.parent.parent.parent.parent.parent.joinpath("data/tests")


class TestOptions(OmniUiTest):
    # Before running each test
    async def setUp(self):
        self._settings = carb.settings.get_settings()
        self._radio_settings = "/test/options_menu/radios"
        self._settings.set(self._radio_settings, "First")
        self._radio_value_model = ui.SimpleStringModel("First")
        radios = [
            ("Radios", None),
            "First",
            ("Second", "Second Radio"),
            "Third",
        ]
        self._custom_model = ui.SimpleIntModel(0)

        def _build_custom():
            ui.MenuItem("This is a custom menuitem")
    
        self._model = OptionsModel(
            "Options",
            [
                OptionItem("audio", text="Audio"),
                OptionItem("materials", text="Materials"),
                OptionItem("scripts", text="Scripts"),
                OptionItem("textures", text="Textures"),
                OptionItem("usd", text="USD"),

                OptionRadios(radios, model=self._radio_value_model, default = "First"),
                OptionRadios(radios, setting_path=self._radio_settings, default = "First", menu_text="Radios"),

                OptionSeparator(),
                OptionCustom(_build_custom, self._custom_model),

                OptionSeparator(),
                OptionItem("Disabled", enabled=False),
                OptionItem("Disabled and checked", default=True, enabled=False),
            ]
        )
        self._model.get_item_children()[-1].value = True

        self._golden_img_dir = TEST_DATA_PATH.absolute().joinpath("golden")

        await super().setUp()

    # After running each test
    async def tearDown(self):
        await super().tearDown()

    async def finalize_test(self, golden_img_name: str):
        await self.wait_n_updates()
        await super().finalize_test(golden_img_dir=self._golden_img_dir, golden_img_name=golden_img_name)
        await self.wait_n_updates()
    
    async def test_option_item(self):
        value_model = ui.SimpleBoolModel(True)
        setting_path = "/test/options_menu/optionItem"
        self._settings.set(setting_path, True)

        self.__new_value = None
        def __on_value_changed_fn(value: bool):
            self.__new_value = value
        
        class CustomOptionItem(OptionItem):
            def build_custom_widget(self, item: ui.MenuItem) -> None:
                ui.Label("NEW WIDGETS")

        model = OptionsModel(
            "OptionItems",
            [
                OptionItem("general", text="General", on_value_changed_fn=__on_value_changed_fn),
                OptionItem("value model", model=value_model, default=True),
                OptionItem("value setting", setting_path=setting_path, default=True),

                OptionSeparator(),
                OptionItem("Disabled", enabled=False),
                OptionItem("Disabled and checked", default=True, enabled=False),
        
                OptionSeparator(title="Custom widgets"),
                CustomOptionItem("custom"),
            ]
        )
        items = model.get_item_children()
        self.__changed_items = []

        def _on_item_changed(_, item: OptionItem):
            self.__changed_items.append(item)

        self._sub = model.subscribe_item_changed_fn(_on_item_changed)
            
        menu = OptionsMenu(model)
        menu.show_at(0, 0)
        try:
            # Initial UI
            await ui_test.emulate_mouse_move(ui_test.Vec2(0, 0))
            await ui_test.human_delay()
            await self.finalize_test("option_items.png")

            # Click 1st item
            await ui_test.human_delay()
            self.assertIsNone(self.__new_value)
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(50, 45))
            self.assertTrue(self.__new_value)

            # Click 2nd item
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(50, 65))
            self.assertFalse(value_model.as_bool)
        
            # Click 3rd item
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(50, 85))
            self.assertFalse(self._settings.get(setting_path))

            # Click 4th and 5th items
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(50, 115))
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(50, 135))

            await ui_test.human_delay()
            await self.finalize_test("option_items_click.png")
            self.assertEqual(len(self.__changed_items), 3)
            self.assertEqual(self.__changed_items[0], items[0])
            self.assertEqual(self.__changed_items[1], items[1])
            self.assertEqual(self.__changed_items[2], items[2])
            
            # Reset all
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(160, 20))
            await ui_test.human_delay()
            await self.finalize_test("option_items.png")

            # Change 2nd item via model
            value_model.set_value(False)
            self._settings.set(setting_path, False)
            
            # enable 4th and 5th items
            items[4].enabled = True
            items[5].enabled = True
            await self.finalize_test("option_items_changed.png")

        finally:
            menu.destroy()
            self._sub = None

    async def test_ui_layout(self):
        """Test ui, reset and API to get/set value"""
        items = self._model.get_item_children()
        self._changed_items = []

        def _on_item_changed(_, item: OptionItem):
            self._changed_items.append(item)

        self._sub = self._model.subscribe_item_changed_fn(_on_item_changed)

        menu = OptionsMenu(self._model)
        menu.show_at(0, 0)
        try:
            # Initial UI
            await ui_test.emulate_mouse_move(ui_test.Vec2(0, 0))
            await ui_test.human_delay()
            await self.finalize_test("options_menu.png")

            # Change first and last general option item via mouse click
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(50, 45))
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(50, 145))
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(50, 195))
            await ui_test.human_delay()
            self.assertEqual(len(self._changed_items), 3)
            self.assertEqual(self._changed_items[0], items[0])
            self.assertEqual(self._changed_items[1], items[4])
            self.assertEqual(self._changed_items[2], items[5])
            await self.finalize_test("options_menu_click.png")

            # Change value via item property
            items[2].value = not items[2].value
            items[3].value = not items[3].value
            items[5].model.set_value("Third")
            await self.finalize_test("options_menu_value_changed.png")

            # Reset all
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(120, 20))
            await self.finalize_test("options_menu.png")

        finally:
            menu.destroy()

    async def test_radios_menu(self):
        self._radio_settings = "/test/options_menu/radios"
        self._settings.set(self._radio_settings, "First")
        self._radio_value_model = ui.SimpleStringModel("First")
        radios = [
            ("Radios", None),
            "First",
            ("Second", "Second Radio"),
            "Third",
        ]
        model = OptionsModel(
            "RadioItems",
            [
                OptionRadios(radios, default="Second Radio"),
                OptionRadios(radios, model=self._radio_value_model, default="First"),
                OptionSeparator(title="Radios in sub menu"),
                OptionRadios(radios, setting_path=self._radio_settings, default="First", menu_text="Radios", tooltips=["First radio", "Second radio", "Third radio"]),
            ]
        )
        items = model.get_item_children()      
        menu = OptionsMenu(model)
        menu.show_at(0, 0)
        try:
            # Initial UI
            await ui_test.emulate_mouse_move(ui_test.Vec2(0, 0))
            await ui_test.human_delay()
            await self.finalize_test("radio_items.png")

            # Show radios sub menu
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move(ui_test.Vec2(50, 225))
            await self.finalize_test("radio_items_sub.png")

            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(215, 265))
            await self.finalize_test("radio_items_click.png")
            self.assertEqual(self._settings.get(self._radio_settings), "Second Radio")

            self._settings.set(self._radio_settings, "Third")
            self._radio_value_model.set_value("Second Radio")
            await self.finalize_test("radio_items_change.png")

            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(0, 0))
            items[0].enabled = False
            items[-1].enabled = False
            await self.finalize_test("radio_items_disabled.png")
            
            # Reset all
            items[0].enabled = True
            items[-1].enabled = True
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(150, 20))
            await ui_test.human_delay()
            await self.finalize_test("radio_items.png")

        finally:
            menu.destroy()

    async def test_ui_rebuild_items(self):
        """Test ui, reset and API to get/set value"""
        items = self._model.get_item_children()
        
        menu = OptionsMenu(self._model)
        menu.show_at(0, 0)
        try:
            # Initial UI
            await ui_test.emulate_mouse_move(ui_test.Vec2(0, 0))
            await ui_test.human_delay()
            await self.finalize_test("options_menu.png")

            self._model.rebuild_items(
                [
                    OptionItem("Test"),
                    OptionSeparator(),
                    OptionItem("More"),
                ]
            )
            await ui_test.human_delay()
            await self.finalize_test("options_menu_rebuild.png")

            menu.rebuild_items(items)
            await ui_test.human_delay()
            await self.finalize_test("options_menu.png")
        finally:
            menu.destroy()

    async def test_radio_menu(self):
        self._field_model = RadioModel(["Name", "Date", "Price"], default_index=1)
        self._order_model = RadioModel(["Ascending", "Descending", "Random"])
        
        menu = RadioMenu("Sort By", [self._field_model, self._order_model])
        menu.show_at(0, 0)

        try:
            # Initial UI
            await ui_test.emulate_mouse_move(ui_test.Vec2(0, 0))
            await ui_test.human_delay()
            await self.finalize_test("radio_menu.png")

            # Change first and last item via mouse click
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(50, 45))
            await ui_test.human_delay()
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(50, 145))
            await ui_test.human_delay()
            self.assertEqual(self._field_model.index, 0)
            self.assertEqual(self._order_model.index, 1)
            await self.finalize_test("radio_menu_click.png")

            # Change value via item property
            self._field_model.index = 2
            self._order_model.index = 2
            await self.finalize_test("radio_menu_value_changed.png")

            # Reset all
            await ui_test.emulate_mouse_move_and_click(ui_test.Vec2(120, 20))
            await self.finalize_test("radio_menu.png")

        finally:
            menu.destroy()

