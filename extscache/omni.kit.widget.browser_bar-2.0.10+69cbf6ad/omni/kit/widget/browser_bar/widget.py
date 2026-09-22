# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module defines the BrowserBar class, which extends the PathField UI widget with navigation history and branching options for directory browsing."""


import sys, os
import omni.ui as ui

from omni.kit.widget.path_field import PathField
from .model import StringQueueModel, VisitedHistory
from .style import UI_STYLES, ICON_PATH


class BrowserBar:
    """A class that extends the :obj:`PathField` UI widget for navigating tree views via
    the keyboard by adding navigation history, similar to modern-day browsers. This allows users
    to directly jump to any previously visited path.

    Keyword Args:
        visited_history_size (int): Maximum number of previously visited paths to queue up. Default is 10.
        apply_path_handler (Callable): Function called when the user updates the path, expected to
            update the caller app accordingly. The path can be updated by hitting Enter on the
            input field, selecting a path from the dropdown, or clicking on the "prev" or "next"
            buttons. Function signature: void apply_path_handler(path: str).
        branching_options_handler (Callable): Function required to provide a list of possible branches
            whenever prompted with a path. For example, if path = "C:", the list of values might be
            ["Program Files", "temp", ..., "Users"]. Function signature: list(str)
            branching_options_handler(path: str, callback: func).
        modal (bool): Indicates if this is used for a modal window. Default is False."""

    def __init__(self, **kwargs):
        """Initializes the BrowserBar with optional UI customization parameters."""
        self._path_field = None
        self._next_button = None
        self._prev_button = None
        self._visited_menu = None
        self._visited_queue = None
        self._visited_history = None
        self._visited_menu_bg = None

        import carb.settings

        theme = carb.settings.get_settings().get_as_string("/persistent/app/window/uiStyle") or "NvidiaDark"

        self._style = UI_STYLES[theme]
        self._icon_path = f"{ICON_PATH}/{theme}"
        self._visited_max_size = kwargs.get("visited_history_size", 10)
        self._visited_history_max_size = kwargs.get("visited_history_max_size", 100)
        self._apply_path_handler = kwargs.get("apply_path_handler", None)
        self._branching_options_handler = kwargs.get("branching_options_handler", None)
        # OM-49484: Add subscription to begin edit and apply callback, for example we could add callback to cancel
        #   initial navigation upon user edit
        self._begin_edit_handler = kwargs.get("begin_edit_handler", None)
        self._branching_options_provider = kwargs.get("branching_options_provider", None)  # OBSOLETE
        self._prefix_separator = kwargs.get("prefix_separator", None)
        self._modal = kwargs.get("modal", False)
        self._build_ui()

    @property
    def path(self) -> str:
        """Gets the current path as entered in the field box.

        Returns:
            str: The current path if available, otherwise None."""
        if self._path_field:
            return self._path_field.path
        return None

    def set_path(self, path: str):
        """Sets the path and adds it to the history queue.

        Args:
            path (str): The full path name."""
        if not path:
            return
        if self._path_field:
            self._path_field.set_path(path)
        self._update_visited(path)

    def _build_ui(self):
        import carb.settings

        font_size = carb.settings.get_settings().get("/app/font/size") or 0

        with ui.HStack(height=0, style=self._style):
            self._prev_button = ui.Button(
                image_url=f"{self._icon_path}/angle_left.svg",
                image_height=16,
                width=24,
                clicked_fn=self._on_prev_button_pressed,
                enabled=False,
            )
            self._next_button = ui.Button(
                image_url=f"{self._icon_path}/angle_right.svg",
                image_height=16,
                width=24,
                clicked_fn=self._on_next_button_pressed,
                enabled=False,
            )
            with ui.ZStack():
                ui.Rectangle()
                # OM-66124: Update look for browser bar, use full width combobox and hide beneath Pathfield;
                #  FIXME: this is because currently we cannot control the menu width for arrow_only combo box;
                with ui.ZStack():
                    # OM-66124: manually add combo box drop down background, since it is hard to control combo box height
                    #  FIXME: Ideally should fix in ui.ComboBox directly
                    combo_dropdown_size = font_size + 8
                    with ui.HStack():
                        ui.Spacer()
                        with ui.VStack(width=combo_dropdown_size):
                            ui.Spacer()
                            self._visited_menu_bg = ui.Rectangle(
                                height=22, style=self._style, style_type_name_override="ComboBox.Bg"
                            )
                            ui.Spacer()
                    with ui.HStack():
                        self._path_field = PathField(
                            apply_path_handler=self._apply_path_handler,
                            branching_options_handler=self._branching_options_handler,
                            prefix_separator=self._prefix_separator,
                            modal=self._modal,
                            begin_edit_handler=self._begin_edit_handler,
                        )
                        ui.Spacer(width=combo_dropdown_size)
                    self._build_visited_menu()

    def _build_visited_menu(self):
        self._visited_queue = StringQueueModel(
            max_items=self._visited_max_size, value_changed_fn=self._on_menu_item_selected
        )
        self._visited_history = VisitedHistory(max_items=self._visited_history_max_size)
        self._visited_menu = ui.ComboBox(self._visited_queue, arrow_only=False, style=self._style)
        # Note: This callback is needed to trigger a refresh
        self._visited_menu.model.add_item_changed_fn(lambda model, item: None)

    def _update_visited(self, path: str):
        if self._visited_queue:
            self._visited_queue.enqueue(path)
            self._visited_menu.style_type_name_override = "ComboBox.Active"
            self._visited_menu_bg.style_type_name_override = "ComboBox.Bg.Active"

        # update visited history
        self._visited_history.insert(path)

        self._update_nav_buttons()
        self._visited_history.activate()

    def _on_prev_button_pressed(self):
        self._visited_history.deactivate()
        selected_index = self._visited_history.selected_index
        if selected_index >= self._visited_history.size() - 1:
            return
        else:
            self._visited_history.selected_index = selected_index + 1
            if self._path_field:
                self._path_field.set_path(self._visited_history.get_selected_item())
            if self._apply_path_handler:
                self._apply_path_handler(self._visited_history.get_selected_item())
            self._update_nav_buttons()

    def _on_next_button_pressed(self):
        self._visited_history.deactivate()
        selected_index = self._visited_history.selected_index
        if selected_index <= 0:
            return
        else:
            self._visited_history.selected_index = selected_index - 1
            if self._path_field:
                self._path_field.set_path(self._visited_history.get_selected_item())
            if self._apply_path_handler:
                self._apply_path_handler(self._visited_history.get_selected_item())
            self._update_nav_buttons()

    def _update_nav_buttons(self):
        if self._visited_history.selected_index > 0:
            self._next_button.enabled = True
        else:
            self._next_button.enabled = False

        if self._visited_history.selected_index < self._visited_history.size() - 1:
            self._prev_button.enabled = True
        else:
            self._prev_button.enabled = False

    def _on_menu_item_selected(self, model: ui.SimpleIntModel):
        if not model:
            return
        menu_item = self._visited_queue[model.get_value_as_int()]
        if menu_item:
            if self._path_field:
                self._path_field.set_path(menu_item.value)
            if self._apply_path_handler:
                self._apply_path_handler(menu_item.value)

    def destroy(self):
        """Cleans up the BrowserBar, destroying UI components and clearing memory."""
        if self._path_field:
            self._path_field.destroy()
            self._path_field = None
        self._next_button = None
        self._prev_button = None
        self._visited_menu = None
        self._visited_queue = None
        if self._visited_history:
            self._visited_history.destroy()
        self._visited_menu_bg = None
        self._style = None
        self._apply_path_handler = None
        self._branching_options_handler = None
        self._begin_edit_handler = None
        self._branching_options_provider = None
