# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from pathlib import Path

import carb.input
import carb.settings
import omni.kit.app
import omni.kit.context_menu
import omni.ui as ui
from omni.kit.widget.toolbar import WidgetGroup

ICON_FOLDER_PATH = Path(
    f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons"
)


class PivotButtonGroup(WidgetGroup):
    # Can't be tested from within kit since it's used by omni.explore.toolbar which is outside of kit repo
    """
    Toolbar entry for pivot placement
    """

    def __init__(self):
        super().__init__()
        self._input = carb.input.acquire_input_interface()
        self._settings = carb.settings.get_settings()

    def clean(self):
        super().clean()

    def __del__(self):
        self.clean()

    def get_style(self):
        style = {"Button.Image::pivot_placement": {"image_url": f"{ICON_FOLDER_PATH}/pivot_location.svg"}}
        return style

    def get_button(self) -> ui.ToolButton:
        return self._button

    def create(self, default_size):
        self._button = ui.Button(
            name="pivot_placement",
            width=default_size,
            height=default_size,
            tooltip="Pivot Placement",
            mouse_pressed_fn=lambda x, y, b, _: self._on_mouse_pressed(b, "multi_sel_pivot", min_menu_entries=1),
            mouse_released_fn=lambda x, y, b, _: self._on_mouse_released(b),
        )
        return {"pivot": self._button}

    def _on_mouse_pressed(self, button, button_id: str, min_menu_entries: int = 2):
        # override default behavior, left or right click will show menu without delay
        self._acquire_toolbar_context()
        if button == 0 or button == 1:
            self._invoke_context_menu(button_id, min_menu_entries)

    def _invoke_context_menu(self, button_id: str, min_menu_entries: int = 1):
        """
        Function to invoke context menu.

        Args:
            button_id: button_id of the context menu to be invoked.
            min_menu_entries: minimal number of menu entries required for menu to be visible (default 1).
        """
        button_id = "multi_sel_pivot"

        context_menu = omni.kit.context_menu.get_instance()

        objects = {"widget_name": button_id, "main_toolbar": True}
        menu_list = omni.kit.context_menu.get_menu_dict(button_id, "omni.kit.manipulator.prim.core")
        context_menu.show_context_menu(button_id, objects, menu_list, min_menu_entries, delegate=ui.MenuDelegate())
