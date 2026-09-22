# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pathlib import Path
from typing import Optional

import carb.dictionary
import carb.settings
import omni.kit.context_menu
import omni.ui as ui
from omni.kit.widget.toolbar import WidgetGroup

from .menu import SnapMenu
from .models import SettingModel
from .settings_constants import SNAP_ENABLED_SETTING

ICON_FOLDER_PATH = Path(
    f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons"
)

SNAP_TOOL_NAME = "Snap"


class SnapButtonGroup(WidgetGroup):
    """A class that represents a group of buttons for snap functionality in a UI toolbar.

    This class is responsible for creating and managing a UI button that interacts with the snap settings and functionality. It utilizes a SnapMenu to provide additional options and settings for the snap tool.

    Args:
        hotkey: str
            The key combination used to activate the snap functionality.
        menu: SnapMenu
            An instance of the SnapMenu class that provides additional options for the snap tool."""

    def __init__(self, hotkey, menu: SnapMenu):
        """Initializes the SnapButtonGroup with a hotkey and a SnapMenu.

        Args:
            hotkey: The hotkey associated with the snap functionality.
            menu (SnapMenu): An instance of the SnapMenu to be used with the button group."""
        super().__init__()
        self._settings = carb.settings.get_settings()
        self._settings.set_default_bool(SNAP_ENABLED_SETTING, False)
        self._hotkey = hotkey
        self._menu = menu

        self._dict = carb.dictionary.get_dictionary()
        self._snap_setting_model = SettingModel(SNAP_ENABLED_SETTING)

    def clean(self):
        """Cleans up the SnapButtonGroup by destroying the snap setting model."""
        super().clean()
        if self._snap_setting_model:
            self._snap_setting_model.destroy()
            self._snap_setting_model = None

    def __del__(self):
        self.clean()

    def get_style(self):
        """Returns the style of the snap button.

        Returns:
            dict: A dictionary representing the style of the snap button."""
        style = {"Button.Image::snap": {"image_url": f"{ICON_FOLDER_PATH}/toolbar_snap.svg"}}
        return style

    def get_button(self) -> ui.ToolButton:
        """Retrieves the UI tool button associated with the snap functionality.

        Returns:
            ui.ToolButton: The UI tool button instance."""
        return self._button

    def create(self, default_size):
        """Creates the UI tool button for the snap functionality with the specified default size.

        Args:
            default_size (int): The default width and height for the button.

        Returns:
            dict: A dictionary containing the created ui.ToolButton with 'snap' as the key."""
        self._button = ui.ToolButton(
            model=self._snap_setting_model,
            name="snap",
            tooltip=f"{SNAP_TOOL_NAME} ({self._hotkey.get_as_string('S')})",
            width=default_size,
            height=default_size,
            mouse_pressed_fn=lambda x, y, b, _: self._on_mouse_pressed(b, "snap", min_menu_entries=1),
            mouse_released_fn=lambda x, y, b, _: self._on_mouse_released(b),
            checked=self._snap_setting_model.get_value_as_bool(),
        )
        return {"snap": self._button}

    def _invoke_context_menu(self, button_id: str, min_menu_entries: int = 1):
        """Invokes the context menu for the given button id.

        Args:
            button_id (str): The identifier of the button for which to invoke the context menu.
            min_menu_entries (int, optional): The minimum number of menu entries required for the menu to be visible. Defaults to 1.
        """
        menu = self._menu.get_options_menu()
        if menu:
            menu.show_by_widget(self._button, alignment=ui.Alignment.RIGHT_TOP)
