# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ColorMenuDelegate"]

from typing import Optional
import omni.ui as ui
from .abstract_widget_menu_delegate import AbstractWidgetMenuDelegate
from ..model.list_model import ColorModel


class ColorMenuDelegate(AbstractWidgetMenuDelegate):
    """A menu delegate that creates color picker within a viewport menubar."""

    def __init__(self, model: Optional[ColorModel] = None, tooltip: Optional[str] = None, has_reset: bool = False):
        """
        Constructor.

        Keyword Args:
            model (Optional[ColorModel]): Color data model.
            tooltip (Optional[str]): Delegate tooltip, defaults to None means no tooltip.
            has_reset (bool): Show reset button, defaults to False.
        """
        super().__init__(model=model, width=210 + 90, has_reset=has_reset)
        self.__color_widget_width = 20
        self.__model = model
        self.__tooltip = tooltip or ""

    def __del__(self):
        self.destroy()

    def destroy(self) -> None:
        """Release resources."""
        self.__model = None

    def build_widget(self, item: ui.MenuHelper) -> None:
        """
        Build color picker.

        Args:
            item (ui.MenuHelper): Menu item.
        """
        ui.Label(item.text, tooltip=self.__tooltip, style_type_name_override="Menu.Item.Label")
        ui.ColorWidget(self.__model, width=self.__color_widget_width, height=0)
        ui.Spacer(width=70)
