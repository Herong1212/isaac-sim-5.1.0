## Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
##
## NVIDIA CORPORATION and its licensors retain all intellectual property
## and proprietary rights in and to this software, related documentation
## and any modifications thereto.  Any use, reproduction, disclosure or
## distribution of this software and related documentation without an express
## license agreement from NVIDIA CORPORATION is strictly prohibited.
##
import omni.kit.test
import pathlib
import carb
import omni.ui as ui
from omni.kit.test.async_unittest import AsyncTestCase
from omni.kit import ui_test
from omni.kit.widget.searchable_combobox import build_searchable_combo_widget, ComboBoxListDelegate


class TestSearchableComboWidget(AsyncTestCase):
    async def test_searchable_combo_widget(self):
        delegate_called = False

        class TestDelegate(ComboBoxListDelegate):
            def build_widget(self, model, item, column_id, level, expanded):
                nonlocal delegate_called
                delegate_called = True
                ui.Label(
                    model.get_item_value_model(item, column_id).as_string,
                    skip_draw_when_clipped=True,
                    elided_text=True,
                    height=18,
                )

        callback_calls = 0
        callback_value = None

        window = ui.Window("WidgetTest", width=1000, height=700)
        with window.frame:
            with ui.VStack(height=0, spacing=8, style={"margin_width": 2}):
                ui.Spacer()
                with ui.HStack():
                    ui.Label("Component", width=140)

                    def on_combo_click_fn(model):
                        nonlocal callback_calls
                        callback_calls += 1
                        self.assertTrue(model.get_value_as_string() == callback_value)

                    component_list = [
                        "3d Reconstruction",
                        "AEC Experience",
                        "AI Framework",
                        "AI Toybox",
                        "AR Experience",
                        "ArtTech",
                        "Asset Converter Service",
                        "Asset Management",
                        "Physics Research",
                        "PhysX Third Party Integrations",
                        "Pinocchio",
                        "PLC",
                        "Point Clouds",
                        "Pose Tracker",
                        "QA Builds",
                        "QA Needs Repro",
                        "Repo Tools",
                        "Reshade",
                        "Resolvers",
                        "RTX",
                        "RTX Hydra",
                        "RTX MGPU",
                        "RTX Renderer",
                        "Sample Content",
                        "SDG",
                        "Sequencer",
                        "Server Installer",
                        "Showroom",
                        "Synthetic Data",
                        "USD",
                        "USD Delta Library",
                        "USD Hydra",
                        "Kit",
                        "USDRT",
                        "UX",
                        "UX / UI",
                        "Virtual Production",
                        "XR",
                    ]
                    component_index = -1
                    component_combo = build_searchable_combo_widget(
                        component_list,
                        component_index,
                        on_combo_click_fn,
                        widget_height=18,
                        default_value="Kit",
                        window_id="SearchableComboBoxWindow##test_searchable_combo_widget",
                        delegate=TestDelegate(),
                    )

        # test set_text & get_text
        await ui_test.human_delay()
        callback_value = "USD"
        component_combo.set_text("USD")
        await ui_test.human_delay()
        self.assertTrue(component_combo.get_text() == "USD")
        self.assertTrue(callback_calls == 1)

        # test clear & default
        clear_widget = ui_test.find("WidgetTest//Frame/**/Button[*].name=='remove_popup'")
        callback_value = "Kit"
        await clear_widget.click()
        self.assertTrue(component_combo.get_text() == "Kit")
        self.assertTrue(callback_calls == 2)

        # test combo open and typing
        text_field = ui_test.find("WidgetTest//Frame/**/StringField[*]")
        await text_field.click()
        # TODO: text_field.input("ArtTech") don't work here as it does a double_click
        await ui_test.emulate_char_press("ArtTech")
        await ui_test.human_delay()
        treeview_widget = ui_test.find("SearchableComboBoxWindow##test_searchable_combo_widget//Frame/**/TreeView[*]")
        callback_value = "ArtTech"
        # y+8 to make sure mouse pointer is on popup window (combobox item list), so 1st item is selected
        await ui_test.emulate_mouse_move_and_click(
            ui_test.Vec2(treeview_widget.center.x, treeview_widget.widget.screen_position_y + 8)
        )
        self.assertTrue(component_combo.get_text() == callback_value)
        self.assertTrue(callback_calls == 3)
        # holding onto this varaible prevents ComboListBoxWidget from getting garbage collected.
        treeview_widget = None

        # test combo open button and typing
        open_widget = ui_test.find("WidgetTest//Frame/**/Button[*].name=='listbox'")
        await open_widget.click()
        # as this opens popup window, need to wait for that to be created and ready to use
        await ui_test.human_delay()
        await ui_test.emulate_char_press("Pinocchio")
        treeview_widget = ui_test.find("SearchableComboBoxWindow##test_searchable_combo_widget//Frame/**/TreeView[*]")
        callback_value = "Pinocchio"
        # y+8 to make sure mouse pointer is on popup window (combobox item list), so 1st item is selected
        await ui_test.emulate_mouse_move_and_click(
            ui_test.Vec2(treeview_widget.center.x, treeview_widget.widget.screen_position_y + 8)
        )
        self.assertTrue(component_combo.get_text() == callback_value)
        self.assertTrue(callback_calls == 4)
        # holding onto this varaible prevents ComboListBoxWidget from getting garbage collected.
        treeview_widget = None

        # test search clear
        await text_field.click()
        await ui_test.emulate_char_press("this will be cleared...")
        await ui_test.human_delay()
        clear_widget = ui_test.find(
            "SearchableComboBoxWindow##test_searchable_combo_widget//Frame/**/Button[*].name=='remove'"
        )
        await clear_widget.click()
        await ui_test.emulate_char_press("Asset Converter Service")
        treeview_widget = ui_test.find("SearchableComboBoxWindow##test_searchable_combo_widget//Frame/**/TreeView[*]")
        callback_value = "Asset Converter Service"
        await ui_test.emulate_mouse_move_and_click(
            ui_test.Vec2(treeview_widget.center.x, treeview_widget.widget.screen_position_y + 8)
        )
        self.assertTrue(component_combo.get_text() == "Asset Converter Service")
        self.assertTrue(callback_calls == 5)
        # holding onto this varaible prevents ComboListBoxWidget from getting garbage collected.
        treeview_widget = None

        # test delegate was called
        self.assertTrue(delegate_called)
