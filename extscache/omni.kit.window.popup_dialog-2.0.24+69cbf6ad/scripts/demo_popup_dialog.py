# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ui as ui
from omni.kit.window.popup_dialog import MessageDialog, InputDialog, FormDialog, OptionsDialog, OptionsMenu


class DemoApp:
    def __init__(self):
        self._window = None
        self._popups = []
        self._cur_popup_index = 0
        self._build_ui()

    def _build_ui(self):
        window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR
        self._window = ui.Window("DemoPopup", width=600, height=80, flags=window_flags)
        with self._window.frame:
            builders = [
                ("Message", self._build_message_popup),
                ("String Input", self._build_string_input),
                ("Form Dialog", self._build_form_dialog),
                ("Options Dialog", self._build_options_dialog),
                ("Options Menu", self._build_options_menu),
            ]
            with ui.VStack(spacing=10):
                with ui.HStack(height=30):
                    collection = ui.RadioCollection()
                    for i, builder in enumerate(builders):
                        button = ui.RadioButton(text=builder[0], radio_collection=collection, width=120)
                        self._popups.append(builder[1]())
                        button.set_clicked_fn(lambda i=i, parent=button: self._on_show_popup(i, parent))
                    ui.Spacer()
                ui.Spacer()

    def _build_message_popup(self) -> MessageDialog:
        #BEGIN-DOC-message-dialog
        message = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        dialog = MessageDialog(
            title="Message",
            message=message,
            ok_handler=lambda dialog: print(f"Message acknowledged"),
        )
        #END-DOC-message-dialog
        return dialog

    def _build_string_input(self) -> InputDialog:
        #BEGIN-DOC-input-dialog
        dialog = InputDialog(
            title="String Input",
            message="Please enter a string value:",
            pre_label="LDAP Name:  ",
            post_label="@nvidia.com",
            ok_handler=lambda dialog: print(f"Input accepted: '{dialog.get_value()}'"),
        )
        #END-DOC-input-dialog
        return dialog

    def _build_form_dialog(self) -> FormDialog:
        #BEGIN-DOC-form-dialog
        field_defs = [
            FormDialog.FieldDef("string", "String:  ", ui.StringField, "default"),
            FormDialog.FieldDef("int", "Integer:  ", ui.IntField, 1),
            FormDialog.FieldDef("float", "Float:  ", ui.FloatField, 2.0),
            FormDialog.FieldDef(
                "tuple", "Tuple:  ", lambda **kwargs: ui.MultiFloatField(column_count=3, h_spacing=2, **kwargs), None
            ),
            FormDialog.FieldDef("slider", "Slider:  ", lambda **kwargs: ui.FloatSlider(min=0, max=10, **kwargs), 3.5),
            FormDialog.FieldDef("bool", "Boolean:  ", ui.CheckBox, True),
        ]
        dialog = FormDialog(
            title="Form Dialog",
            message="Please enter values for the following fields:",
            field_defs=field_defs,
            ok_handler=lambda dialog: print(f"Form accepted: '{dialog.get_values()}'"),
        )
        #END-DOC-form-dialog
        return dialog

    def _build_options_dialog(self) -> OptionsDialog:
        #BEGIN-DOC-options-dialog
        field_defs = [
            OptionsDialog.FieldDef("hard", "Hard place", False),
            OptionsDialog.FieldDef("harder", "Harder place", True),
            OptionsDialog.FieldDef("hardest", "Hardest place", False),
        ]
        dialog = OptionsDialog(
            title="Options Dialog",
            message="Please make your choice:",
            field_defs=field_defs,
            width=300,
            radio_group=True,
            ok_handler=lambda choice: print(f"Choice: '{dialog.get_choice()}'"),
        )
        #END-DOC-options-dialog
        return dialog

    def _build_options_menu(self) -> OptionsMenu:
        #BEGIN-DOC-options-menu
        field_defs = [
            OptionsMenu.FieldDef("audio", "Audio", None, False),
            OptionsMenu.FieldDef("materials", "Materials", None, True),
            OptionsMenu.FieldDef("scripts", "Scripts", None, False),
            OptionsMenu.FieldDef("textures", "Textures", None, False),
            OptionsMenu.FieldDef("usd", "USD", None, True),
        ]
        menu = OptionsMenu(
            title="Options Menu",
            field_defs=field_defs,
            width=150,
            value_changed_fn=lambda dialog, name: print(f"Value for '{name}' changed to {dialog.get_value(name)}"),
        )
        #END-DOC-options-menu
        return menu

    def _on_show_popup(self, popup_index: int, parent: ui.Widget):
        self._popups[self._cur_popup_index].hide()
        self._popups[popup_index].show(offset_x=-1, offset_y=26, parent=parent)
        self._cur_popup_index = popup_index


if __name__ == "__main__":
    app = DemoApp()
