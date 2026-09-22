# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["CheckboxMenuDelegate"]

from typing import Optional
import omni.ui as ui
from .abstract_widget_menu_delegate import AbstractWidgetMenuDelegate


class CheckboxMenuDelegate(AbstractWidgetMenuDelegate):
    """A menu delegate that creates checkbox within a viewport menubar."""

    def __init__(
        self,
        model: Optional[ui.SimpleBoolModel] = None,
        tooltip: Optional[str] = None,
        width: ui.Length = 300,
        height: ui.Length = 0,
        enabled: bool = True,
        use_in_menubar: bool = False,
        has_reset: bool = False,
    ):
        """
        Constructor.

        Keyword Args:
            model (Optional[ui.SimpleBoolModel]): Checkbox data model.
            tooltip (Optional[str]): Delegate tooltip text, defaults to None means no tooltip.
            width (ui.Length): Delegate width, defaults to 300 pixels.
            height (ui.Length): Delegate height, defaults to 0 means auto.
            enabled (bool): Delegate enabled state, defaults to True.
            use_in_menubar (bool): Show delegate in menu bar, defaults to False.
            has_reset (bool): Show reset button, defaults to False.
        """
        super().__init__(model, width=width, height=height, enabled=enabled, has_reset=has_reset, use_in_menubar=use_in_menubar)
        self.__checkbox_width = 90 if width > 90 else 0
        self.__model = model
        self.__tooltip = tooltip or ""

    def __del__(self):
        self.destroy()

    def destroy(self) -> None:
        """Release resources."""
        self.__model = None

    def build_widget(self, item: ui.MenuHelper) -> None:
        """
        Build checkbox.

        Args:
            item (ui.MenuItem): Menu item.
        """
        ui.Label(item.text, tooltip=self.__tooltip, style_type_name_override="Menu.Item.Label")
        with ui.VStack(width=self.__checkbox_width):
            ui.Spacer()
            ui.CheckBox(self.__model, height=0)
            ui.Spacer()
