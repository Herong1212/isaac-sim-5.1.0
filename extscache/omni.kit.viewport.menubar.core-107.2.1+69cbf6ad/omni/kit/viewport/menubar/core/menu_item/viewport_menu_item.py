# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportMenuItem"]

from typing import Callable, Dict, Optional

import omni.ui as ui

from ..viewport_menu_model import AbstractViewportMenuItem


class ViewportMenuItem(AbstractViewportMenuItem):
    """A general menu item within a viewport menubar"""
    def __init__(
        self,
        name: str = "",
        icon: str = "",  # glyph?
        hide_on_click: bool = True,
        appear_after: str = "",  # order/priority?
        onclick_fn: Optional[Callable] = None,
        delegate: Optional[ui.MenuDelegate] = None,
        visible_setting_path: Optional[str] = None,
        order_setting_path: Optional[str] = None,
        expand_setting_path: Optional[str] = None,
        style: Optional[Dict] = None,
        order: Optional[int] = None  # deprecated legacy interface
    ):
        """
        Constructor.

        Keyword Args:
            name (str): Menu item text, defaults to "".
            icon (str): Menu item icon. Defaults to "".
            hide_on_click (bool): Hide menu when radio menu item clicked, defaults to True.
            appear_after (str): Name of menu item position to be after, defaults to "".
            onclick_fn (Optional[Callable]): Callback when menu item clicked, defaults to None.
            delegate (Optional[ui.MenuDelegate]): Menu item delegate, defaults to None.
            visible_setting_path (Optional[str]): Setting path for menu item visibility, defaults to None.
            order_setting_path (Optional[str]): Setting path for menu item order in menu bar, defaults to None.
            expand_setting_path (Optional[str]): Setting path for menu item expand status in menu bar, defaults to None.
            style (Optional[Dict]): Menu item additional UI style, defaults to None.
            order (Optional[int]): Menu item order, deprecated. Using order_setting_path instead to be changed/saved.
        """
        self._icon = icon
        self._hide_on_click = hide_on_click
        self._appear_after = appear_after
        self._onclick_fn = onclick_fn
        self._delegate = delegate
        self._style = style if style is not None else {}

        self._menu_item: Optional[ui.MenuItem] = None

        super().__init__(
            name,
            visible_setting_path=visible_setting_path,
            order_setting_path=order_setting_path,
            expand_setting_path=expand_setting_path,
        )

        if (order_setting_path is None) and (order is not None):
            import carb
            carb.log_warn("ViewportMenuItem order argument is deprecated, use order_setting_path")
            self.order_model = ui.SimpleIntModel(order)

    def destroy(self) -> None:
        """Release resources"""
        self._onclick_fn = None
        self._delegate = None
        super().destroy()

    @property
    def visible(self) -> bool:
        """Menu item visibility"""
        return self.visible_model.as_bool

    @visible.setter
    def visible(self, value: bool) -> None:
        self.visible_model.set_value(value)
        if self._menu_item:
            self._menu_item.visible = value

    @property
    def menu_item(self) -> ui.MenuItem:
        """Menu item widget"""
        return self._menu_item

    def build_fn(self, factory_args: Dict):
        """
        Callback to build this menu item. Reimplement it to have own customized item.

        Args:
            factory_args (dict): Argument related to viewport.
        """
        self._menu_item = ui.MenuItem(
            self.name,
            triggered_fn=self._onclick_fn,
            delegate=self._delegate,
            hide_on_click=self._hide_on_click,
            visible=self.visible_model.as_bool,
            style=self._style,
        )

    def invalidate(self) -> None:
        """Refresh menu item"""
        return
