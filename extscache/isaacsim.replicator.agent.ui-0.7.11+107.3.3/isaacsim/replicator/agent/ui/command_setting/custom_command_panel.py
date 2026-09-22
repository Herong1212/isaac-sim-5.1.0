# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import __main__
import carb
from omni import ui
import omni.kit.app
from omni.anim.people.scripts.custom_command.command_manager import CustomCommandManager
from omni.anim.people.scripts.custom_command.defines import CustomCommand, CustomCommandTemplate
from omni.kit.window.filepicker import FilePickerDialog
from isaacsim.replicator.agent.ui.ui_util import *
from omni.metropolis.utils.ui_util import UIUtil

STYLE = {
    "TreeView:selected": {"background_color": 0x66FFFFFF},
    "TreeView.Item": {"color": 0xFFCCCCCC},
    "TreeView.Item:selected": {"color": 0xFFCCCCCC},
    "TreeView.Header": {"background_color": 0xFF000000},
}


class CustomCommandPanel:
    def __init__(self):
        self.cmd_manager: CustomCommandManager = CustomCommandManager.get_instance()
        self._file_picker = None
        self._folder_picker_stringfield = None
        self._folder_picker_btn = None
        self._folder_picker_goto = None

    def shutdown(self):
        self._folder_picker_stringfield = None
        self._folder_picker_btn = None
        self._folder_picker_goto = None

    def build_ui_frame(self):
        self._frame = ui.CollapsableFrame(
            title="Custom Command",
            collapsed=False,
            style=get_collapsable_frame_style(),
            name="subFrame",
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
        )
        with self._frame:
            with ui.VStack():
                # Tracking file picker
                with ui.HStack(height=30):
                    self._folder_picker_stringfield, self._folder_picker_btn, self._folder_picker_goto = build_folder_picker(
                        label="Tracking File",
                        dialog_title="Select A Custom Command Tracking File",
                        default_val="",
                        file_extension_type=FOLDER_PICKER_TYPE.JSON,
                        on_folder_picked=self._load_file_callback,
                    )
                    self._folder_picker_stringfield.model.add_end_edit_fn(self._on_file_path_edit)
                    curr_path = self.cmd_manager.get_tracking_file_path()
                    self._folder_picker_stringfield.model.set_value(curr_path)
                # Tracking file content
                self._custom_commands_model = CustomCommandPanel.UICustomCommandModel(self.cmd_manager)
                self._custom_commands_delegate = CustomCommandPanel.UICustomCommandDelegate()
                self._tree_view = ui.TreeView(
                    self._custom_commands_model,
                    delegate=self._custom_commands_delegate,
                    column_widths=[160, 120, ui.Fraction(1.0)],
                    root_visible=False,
                    header_visible=True,
                    # style=STYLE,
                )
                ui.Spacer(height=10)
                # Buttons
                with ui.HStack(spacing=30, height=30):
                    ui.Button(f"{UIUtil.get_plus_glyph()} Add", width=120).set_clicked_fn(self._on_add_btn)
                    ui.Button(f"{UIUtil.get_minus_glyph()} Del", width=120).set_clicked_fn(self._on_remove_btn)
                    ui.Button("Save", width=120).set_clicked_fn(self.cmd_manager.save_tracking_file)

    def _load_file_callback(self, filename, path):
        new_path = filename if not path else f"{path}/{filename}"
        self.cmd_manager.load_tracking_file(new_path)
        self._custom_commands_model.fetch_commands()

    def _on_file_path_edit(self, model):
        curr_path = self.cmd_manager.get_tracking_file_path()
        new_path = model.get_value_as_string()
        if curr_path != new_path:
            self._load_file_callback(new_path, "")

    def _on_add_btn(self):
        # Avoid opening multiple file picker (Not sure if gc will take care of it)
        if self._file_picker is not None:
            self._file_picker.hide()
            self._file_picker = None

        def on_selected(filename, path):
            if filename == None or filename == "":
                return
            full_path = None
            if not path:
                full_path = filename
            else:
                full_path = os.path.join(path, filename)
            if self.cmd_manager.add_custom_command(full_path):
                self._custom_commands_model.fetch_commands()
            if self._file_picker:
                self._file_picker.hide()
                self._file_picker = None

        def on_canceled(a, b):
            if self._file_picker:
                self._file_picker.hide()
                self._file_picker = None

        def check_is_usd_path(path):
            return path.endswith(".usd") or path.endswith(".usda") or path.endswith(".usdc")

        def filter_usd(item):
            if not item or item.is_folder:
                return True
            return check_is_usd_path(item.path)

        def on_apply_path(url: str):
            import omni.client

            result, entry = omni.client.stat(url)
            if result != omni.client.Result.OK:
                return
            # When input is folder, navigate to it
            if (entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN) != 0:
                self._file_picker.navigate_to(url)
                return
            if check_is_usd_path(url):
                on_selected(url, None)
            else:
                self._file_picker.navigate_to(url)

        self._file_picker = FilePickerDialog(
            "Add a custom command animation USD",
            allow_multi_selection=False,
            apply_button_label="Select",
            click_apply_handler=lambda a, b: on_selected(a, b),
            click_cancel_handler=lambda a, b: on_canceled(a, b),
            item_filter_fn=filter_usd,
            file_extension_options=[("*.usd; *.usda; *.usdc", "Universal Scene Description")],
            apply_path_handler=on_apply_path,
        )

    def _on_remove_btn(self):
        if len(self._tree_view.selection) == 0:
            carb.log_warn("Please select a custom command to remove.")
            return
        for select in self._tree_view.selection:
            anim_path = select.anim_usd_model.get_value_as_string()
            self.cmd_manager.remove_custom_command(anim_path)
        self._custom_commands_model.fetch_commands()

    class UICustomCommand(ui.AbstractItem):
        def __init__(self, item: CustomCommand):
            super().__init__()
            self.name_model = ui.SimpleStringModel(item.name)
            self.template_model = ui.SimpleStringModel(item.template.value)
            self.anim_usd_model = ui.SimpleStringModel(item.anim_path)

        def __repr__(self):
            return f'"{self.name_model.as_string} {self.template_model.as_string} {self.anim_usd_model.as_string}"'

    class UICustomCommandModel(ui.AbstractItemModel):
        def __init__(self, cmd_manager):
            super().__init__()
            self._children = []
            self.cmd_manager = cmd_manager
            self.fetch_commands()

        def fetch_commands(self):
            self._children.clear()
            items_list = self.cmd_manager.get_all_custom_commands()
            self._children = [CustomCommandPanel.UICustomCommand(item) for item in items_list]
            self._item_changed(None)

        def get_item_children(self, item):
            if item is not None:
                return []
            return self._children

        def get_item_value_model_count(self, item):
            return 3  # Column count

        def get_item_value_model(self, item, column_id):
            model = None
            if column_id == 0:
                model = item.name_model
            elif column_id == 1:
                model = item.template_model
            elif column_id == 2:
                model = item.anim_usd_model
            return model

    class UICustomCommandDelegate(ui.AbstractItemDelegate):
        def __init__(self):
            super().__init__()

        def build_branch(self, model, item, column_id, level, expanded):
            pass

        def build_header(self, column_id):
            if column_id == 0:
                ui.Label("Command Name", height=30)
            elif column_id == 1:
                ui.Label("Template", height=30)
            else:
                ui.Label("USD Path", height=30)

        def build_widget(self, model, item, column_id, level, expanded):
            stack = ui.ZStack(height=20)
            with stack:
                value_model = model.get_item_value_model(item, column_id)
                label = ui.Label(value_model.as_string)
