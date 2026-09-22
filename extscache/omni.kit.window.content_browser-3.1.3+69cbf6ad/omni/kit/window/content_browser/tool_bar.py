# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from typing import Optional
import omni.ui as ui

from omni.kit.window.filepicker import ToolBar as FilePickerToolBar, BaseContextMenu
from omni.kit.widget.filebrowser import FileBrowserItem
from omni.kit.widget.options_menu import OptionsModel, OptionItem
from omni.kit.widget.filter import FilterButton
from .style import get_style, ICON_PATH


class ImportMenu(BaseContextMenu):
    def __init__(self, **kwargs):
        super().__init__(title="Import menu", **kwargs)
        self._menu_dict = []
        self._offset_x = kwargs.get("offset_x", -1)
        self._offset_y = kwargs.get("offset_y", 1)

    def show_relative(self, parent: ui.Widget, item: Optional[FileBrowserItem] = None):
        if item and len(self._menu_dict) > 0:
            self.show(item)
            if parent:
                self.menu.show_at(
                    parent.screen_position_x + self._offset_x,
                    parent.screen_position_y + parent.computed_height + self._offset_y,
                )

    def destroy(self):
        super().destroy()
        self._menu_dict = []


class ToolBar(FilePickerToolBar):
    def __init__(self, **kwargs):
        self._import_button = None
        self._import_menu = None
        self._filter_button = None    
        self._filter_values_changed_handler = kwargs.get("filter_values_changed_handler", None)
        self._import_menu = kwargs.pop("import_menu", ImportMenu())
        super().__init__(**kwargs)

    def _build_ui(self):
        with ui.HStack(height=0, style=get_style(), style_type_name_override="ToolBar"):
            with ui.VStack(width=0):
                ui.Spacer()
                self._import_button = ui.Button(
                    "Import  ",
                    image_url=f"{ICON_PATH}/plus.svg",
                    image_width=12,
                    height=24,
                    spacing=4,
                    style_type_name_override="ToolBar.Button",
                    name="import",
                )
                self._import_button.set_clicked_fn(
                    lambda: self._import_menu
                    and self._import_menu.show_relative(self._import_button, self._current_directory_provider())
                )
                ui.Spacer()

            super()._build_ui()

    def _build_widgets(self):
        ui.Spacer(width=2)
        self._build_filter_button()
            
    def _build_filter_button(self):
        filter_items = [
            OptionItem("audio", text="Audio"),
            OptionItem("materials", text="Materials"),
            OptionItem("scripts", text="Scripts"),
            OptionItem("textures", text="Textures"),
            OptionItem("usd", text="USD"),
            OptionItem("volumes", text="Volumes"),
        ]

        with ui.VStack(width=0):
            ui.Spacer()
            self._filter_button = FilterButton(filter_items, menu_width=150)
            ui.Spacer()

        def on_filter_changed(model: OptionsModel, _):
            if self._filter_values_changed_handler:
                values = {}
                for item in self._filter_button.model.get_item_children():
                    values[item.name] = item.value
                self._filter_values_changed_handler(values)

        self.__sub_filter = self._filter_button.model.subscribe_item_changed_fn(on_filter_changed)
        

    @property
    def import_menu(self):
        return self._import_menu

    @property
    def filter_values(self):
        if self._filter_button:
            values = {}
            for item in self._filter_button.model.get_item_children():
                values[item.name] = item.value
            return values
        return {}

    def destroy(self):
        super().destroy()
        self._import_button = None
        if self._filter_button:
            self.__sub_filter = None
            self._filter_button.destroy()
            self._filter_button = None
        self._filter_values_changed_handler = None
