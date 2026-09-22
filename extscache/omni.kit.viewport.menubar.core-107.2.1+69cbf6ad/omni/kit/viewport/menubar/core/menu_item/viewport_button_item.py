# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportButtonItem"]

import asyncio
from typing import Callable, Dict, Optional, List

import omni.kit.app
import omni.ui as ui

from ..viewport_menu_model import AbstractViewportMenuItem, ViewportMenuModel
from ..style import VIEWPORT_MENUBAR_STYLE


class ViewportButtonItem(AbstractViewportMenuItem):
    """
    A menu item has a button with flyout window or drop-down menu:
        Left click: toggle

        Right click: show flyout window or menu options
    """
    def __init__(
        self,
        text: str = "",
        name: str = "",
        onclick_fn: Callable = None,
        build_menu_fn: Callable[[None], List[ui.MenuItem]] = None,
        build_window_fn: Callable[[None], ui.Window] = None,
        visible_setting_path: Optional[str] = None,
        order_setting_path: Optional[str] = None,
        expand_setting_path: Optional[str] = None,
        alignment: ui.Alignment = ui.Alignment.RIGHT_BOTTOM,
        enabled: bool = True,
        has_triangle: bool = False,
        triangle_size: float = 6,
        style: Optional[Dict] = None,
    ):
        """
        Constructor.

        Keyword args:
            text (str): Button text, defaults to "".
            name (str): Button name, defaults to "".
            onclick_fn (Callable): Callback when button clicked, defaults to None
            build_menu_fn (Callable[[None], List[ui.MenuItem]]): Callback to create flyout menu when right click, defaults to None.
            build_window_fn (Callable[[None], ui.Window]): Callback to create flyout window when right click, defaults to None.
            visible_setting_path (Optional[str]): Setting path for button visibility, defaults to None.
            order_setting_path (Optional[str]): Setting path for button order in menu bar, defaults to None.
            expand_setting_path (Optional[str]): Setting path for button expand state in menu bar, defaults to None.
            alignment (ui.Alignment): Flyout window/menu alignment with button, defaults to ui.Alignment.RIGHT_BOTTOM.
            enabled (bool): Button enabled state, defaults to True.
            has_triangle (bool): Show drop-down carrot, defaults to False.
            triangle_size (float): Size of drop-down carrot, defaults to 6 pixels.
            style (Optional[Dict]): Button additional UI style, defaults to None.
        """
        self._text = text
        self._onclick_fn = onclick_fn
        self._build_menu_fn = build_menu_fn
        self._build_window_fn = build_window_fn
        self._style = style if style is not None else {}
        self._alignment = alignment
        self._enabled = enabled
        self._selected = False
        self._checked = False
        self._has_triangle = has_triangle
        self._triangle_size = triangle_size

        self._menu: Optional[ui.MenuItem] = None
        self._window: Optional[ui.Window] = None
        self._button: Optional[ui.Button] = None
        self._container: Optional[ui.ZStack] = None
        self._menu_items: List[ui.MenuItem] = []

        super().__init__(
            name,
            visible_setting_path=visible_setting_path,
            order_setting_path=order_setting_path,
            expand_setting_path=expand_setting_path,
        )

        # When visible and order changed, trigger UI updates
        self._visible_sub = self.visible_model.subscribe_value_changed_fn(lambda m: self._invalidate())
        self._order_sub = self.order_model.subscribe_value_changed_fn(lambda m: self._invalidate())

    def destroy(self) -> None:
        """Release resources"""
        self._visible_sub = None
        self._order_sub = None
        self._onclick_fn = None
        if self._menu:
            self._menu.hide()
            self._menu = None
        if self._window:
            self._window.visible = False
            self._window = None
        super().destroy()

    @property
    def visible(self) -> bool:
        """Button visibility"""
        return self.visible_model.as_bool

    @visible.setter
    def visible(self, value: bool) -> None:
        self.visible_model.set_value(value)
        if self._menu:
            self._menu.hide()

    @property
    def button(self) -> Optional[ui.Button]:
        """Button widget"""
        return self._button

    @property
    def menu_item(self) -> ui.Menu:
        """Menu item widget"""
        return self._menu

    @property
    def window(self) -> ui.Window:
        """Flyout window"""
        return self._window

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Button name"""
        self._name = value
        if self._button:
            self._button.name = value

    @property
    def enabled(self) -> bool:
        """Button enable state"""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value
        if self._button:
            self._button.enabled = value

    @property
    def selected(self) -> bool:
        """Button selected state"""
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        self._selected = value
        if self._button:
            self._button.selected = value

    @property
    def checked(self) -> bool:
        """Button checked state"""
        return self._checked

    @checked.setter
    def checked(self, value: bool) -> None:
        self._checked = value
        if self._button:
            self._button.checked = value

    def build_fn(self, factory: Dict) -> None:
        """
        Callback when build this button menu item. Reimplement it to have own customized item.

        Args:
            factory (dict): Argument related to viewport.
        """
        self._container = ui.ZStack(width=0)
        with self._container:
            if self._has_triangle:
                with ui.VStack():
                    with ui.HStack():
                        ui.Spacer()
                        with ui.VStack(width=self._triangle_size):
                            ui.Spacer()
                            ui.Triangle(
                                width=self._triangle_size,
                                height=self._triangle_size,
                                alignment=ui.Alignment.RIGHT_TOP,
                                style_type_name_override="MenuBar.Item.Triangle",
                            )
                        ui.Spacer(width=2)
                    ui.Spacer(height=2)
            ui.Rectangle(style_type_name_override="MenuBar.Item.Background")
            self._button = ui.Button(
                self._text,
                name=self.name,
                enabled=self._enabled,
                selected=self._selected,
                checked=self._checked,
                width=0,
                image_width=20,
                visible=self.visible_model.as_bool,
                style=self._style,
                style_type_name_override="Menu.Button",
            )
            ui.Rectangle(style_type_name_override="Menubar.Hover")

        self._container.set_mouse_pressed_fn(lambda x, y, b, a: self._on_mouse_clicked_fn(b))

    def _build_menu(self) -> None:
        style = VIEWPORT_MENUBAR_STYLE.copy()
        style.update(self._style)
        self._menu = ui.Menu("Button_Menu_" + str(hash(self)), menu_compatibility=False, style=style)
        with self._menu:
            self._menu_items = self._build_menu_fn()

    def invalidate(self) -> None:
        """Refresh menu"""
        if self._menu:
            self._menu.invalidate()

    def _on_mouse_clicked_fn(self, button):
        if button == 1:
            self.on_right_clicked_fn()
        elif button == 0 and self._onclick_fn:
            self._onclick_fn()

    def on_right_clicked_fn(self):
        """Show flyout window/menu when right click on button"""
        if self._build_menu_fn:
            self._show_menu()
        elif self._build_window_fn:
            self._show_window()

    def _show_menu(self):
        if self._menu is None:
            self._build_menu()

        (x, y) = (0, 0)
        if self._alignment == ui.Alignment.RIGHT_BOTTOM:
            x = self._container.screen_position_x + self._container.computed_content_width
            y = self._container.screen_position_y + self._container.computed_content_height

            if self._menu_items:
                menu_window_width = self._menu_items[0].computed_content_width
                if menu_window_width <= 0:
                    self._menu.show_at(-500, -100)
                    self._menu.hide()

                    async def __delay_change_menu_window_position(x, y):
                        await omni.kit.app.get_app().next_update_async()
                        x -= self._menu_items[0].computed_content_width
                        self._menu.show_at(x, y)

                    asyncio.ensure_future(__delay_change_menu_window_position(x, y))
                    return
                x -= self._menu_items[0].computed_content_width

        elif self._alignment == ui.Alignment.LEFT_BOTTOM:
            x = self._container.screen_position_x
            y = self._container.screen_position_y + self._container.computed_content_height

        self._menu.show_at(x, y)

    def _show_window(self):
        if self._window is None:
            self._window = self._build_window_fn()

        (x, y) = (0, 0)
        if self._alignment == ui.Alignment.RIGHT_BOTTOM:
            x = self._container.screen_position_x + self._container.computed_content_width
            y = self._container.screen_position_y + self._container.computed_content_height

            if self._window:
                window_width = self._window.frame.computed_width
                if window_width <= 0:
                    self._window.position_x = -500
                    self._window.position_y = -100
                    self._window.visible = True

                    async def __delay_change_window_position(x, y):
                        while self._window.frame.computed_width <= 0:
                            await omni.kit.app.get_app().next_update_async()
                        x -= self._window.frame.computed_width
                        self._window.position_x = x
                        self._window.position_y = y
                        self._window.visible = True

                    asyncio.ensure_future(__delay_change_window_position(x, y))
                    return
                x -= window_width

        elif self._alignment == ui.Alignment.LEFT_BOTTOM:
            x = self._container.screen_position_x
            y = self._container.screen_position_y + self._container.computed_content_height

        self._window.position_x = x
        self._window.position_y = y
        self._window.visible = True

    def _invalidate(self) -> None:
        ViewportMenuModel()._item_changed(None)  # noqa PLW0212
