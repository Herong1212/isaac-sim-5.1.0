# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["IconMenuDelegate"]
import weakref
from typing import Callable, Optional

import omni.ui as ui


class IconMenuDelegate(ui.MenuDelegate):
    """A menu delegate that creates icon and optionally text within a viewport menubar."""

    def __init__(
        self,
        name: str,
        text: bool = False,
        width: ui.Length = 30,
        height: ui.Length = 30,
        has_triangle: bool = True,
        triangle_size: float = 6,
        checked: bool = False,
        enabled: bool = True,
        triggered_fn: Callable[[None], None] = None,
        right_clicked_fn: Callable[[None], None] = None,
        tooltip: Optional[str] = None,
        build_custom_widgets: Callable[[ui.MenuItem], None] = None,
    ):
        """
        Constructor.

        Args:
            name: (str): Icon Name of "Menu.Item.Icon" in UI style definition.
            text (bool): Show text before icon, defaults to False.
            width (ui.Length): Delegate width, defaults to 30 pixels.
            height (ui.Length): Delegate height, defaults to 30 pixels.
            has_triangle (bool): Show drop-down carrot, defaults to True.
            triangle_size (float): Size of drop-down carrot, defaults to 6 pixels.
            checked (bool): Delegate checked state, defaults to False.
            enabled (bool): Delegate enabled state, defaults to True.
            triggered_fn (Callable[[None], None]): Callback when menu item clicked, defaults to None.
            right_clicked_fn (Callable[[None], None]): Callback when right click on this menu item, defaults to None.
            tooltip (Optional[str]): Delegate tooltip, Default None means no tooltip.
            build_custom_widget (Callable[[ui.MenuItem], None]): Callback to build more widgets, defaults to None.
        """
        super().__init__(propagate=False)
        self._name = name
        self._text = text
        self._width = width
        self._icon_width = width
        self._height = height
        self._has_triangle = has_triangle
        self._triangle_size = triangle_size
        self._checked = checked
        self._enabled = enabled
        self.__label = None
        self.__tooltip = tooltip or ""

        self._triggered_fn = triggered_fn
        self._right_clicked_fn = right_clicked_fn

        self.icon: Optional[ui.Widget] = None
        self._container: Optional[ui.Widget] = None
        self.__label_container: Optional[ui.Widget] = None
        self.__label_size = 0
        self.__build_custom_widgets = build_custom_widgets

    def build_item(self, item: ui.MenuItem) -> None:
        """
        Build icon with optional drop-down carrot and label.

        Args:
            item (ui.MenuItem): Menu item.
        """
        self._container = ui.ZStack(checked=self._checked, height=self._height)
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
            spacer_width = 4
            with ui.HStack(height=self._height, spacing=spacer_width):
                self.icon = self._build_icon()
                if self._text:
                    self.__label_container = ui.HStack(spacing=4)
                    with self.__label_container:
                        self.__label = ui.Label(item.text, height=self._height)
                        if self.__build_custom_widgets:
                            self.__build_custom_widgets(item)
                        ui.Spacer(width=4)

                    def __label_size_changed(menu_item, _self=weakref.ref(self)):
                        if (self := _self()) is None:
                            return
                        if self.__label_container.computed_width + spacer_width > self.__label_size:
                            self.__label_size = self.__label_container.computed_width + spacer_width

                    self.__label_container.set_computed_content_size_changed_fn(lambda m=item: __label_size_changed(m))

            ui.Rectangle(style_type_name_override="Menubar.Hover")

        if self._triggered_fn or self._right_clicked_fn:

            def _on_mouse_released(button: int, _self=weakref.ref(self)) -> None:
                if (self := _self()) is None:
                    return
                self._on_mouse_released(button)

            self._container.set_mouse_released_fn(lambda x, y, b, a: _on_mouse_released(b))

    @property
    def text_size(self) -> float:
        """
        Label size.
        """
        return self.__label_size

    @property
    def text_visible(self) -> bool:
        """
        Label visibility.
        """
        return self._text

    @text_visible.setter
    def text_visible(self, value: bool) -> None:
        # Here only set status but need menu invilidate outside to refresh
        self._text = value

    @property
    def checked(self) -> bool:
        """
        Delegate checked state.
        """
        return self._container.checked if self._container else self._checked

    @checked.setter
    def checked(self, value) -> None:
        self._checked = value
        if self._container:
            self._container.checked = value

    @property
    def enabled(self) -> bool:
        """
        Delegate enabled state.
        """
        return self._enabled

    @enabled.setter
    def enabled(self, value) -> None:
        self._enabled = value
        if self._container:
            self._container.enabled = value

    @property
    def text(self) -> str:
        """Label text"""
        return self.__label.text if self.__label else ""

    @text.setter
    def text(self, txt: str):
        if self.__label:
            self.__label.text = str(txt)

    def destroy(self):
        """Release resources."""
        self.__build_custom_widgets = None

    def _on_mouse_released(self, button: int) -> None:
        if button == 0 and self._triggered_fn:
            self._triggered_fn()
        elif button == 1 and self._right_clicked_fn:
            self._right_clicked_fn()

    def _build_icon(self) -> None:
        return ui.ImageWithProvider(
            style_type_name_override="Menu.Item.Icon",
            name=self._name,
            width=self._icon_width,
            height=self._height,
            tooltip=self.__tooltip,
        )
