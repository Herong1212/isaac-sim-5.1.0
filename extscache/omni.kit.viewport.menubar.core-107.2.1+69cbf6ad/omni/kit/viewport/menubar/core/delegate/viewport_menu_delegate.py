from typing import Callable, Optional, Union

import omni.ui as ui

STATUS_ICON_WIDTH = 20
MENU_ARROW_SIZE = 8

__all__ = ["ViewportMenuDelegate"]


class ViewportMenuDelegate(ui.MenuDelegate):
    """A basic menu delegate within a viewport menubar"""

    def __init__(
        self,
        icon_name: str = "",
        icon_width: int = 16,
        reserve_status: bool = True,
        force_checked: bool = False,
        icon_clicked_fn: Callable[[None], None] = None,
        build_custom_widgets: Callable[[ui.MenuDelegate, Union[ui.MenuItem, ui.Menu]], None] = None,
        show_hotkey_placeholder: bool = False,
    ):
        """
        Constructor.

        Keyword Args:
            icon_name (str): Name of icon to show after menu text, defaults to "" means no icon.
            icon_width (int): Icon width, defaults to 16 pixels.
            reserve_status (bool): Show additional space before widgets, defaults to False. Used to align with other menu items which have status icon.
            force_checked (bool): Force to show checked status, defaults to False.
                It is strange that when a menu is checked, sub menu items checked flag will be cleared. Use this flag to show correct sub menu item status.
            icon_clicked_fn (Callable[[None], None]): Callback when icon clicked, defaults to None
            build_custom_widgets (Callable[[ui.MenuDelegate, Union[ui.MenuItem, ui.Menu]], None]): Callback to build custom widgets, defaults to None.
            show_hotkey_placeholder (bool): Show placeholder for hotkey text, defaults to False. Used to align with other menu items which have hotkeys.
        """
        self._icon_name = icon_name
        self._icon_width = icon_width
        self._reserve_status = reserve_status
        self._force_checked = force_checked
        self._icon_clicked_fn = icon_clicked_fn
        self.icon: Optional[ui.Widget] = None
        self._container: Optional[ui.Widget] = None
        self._build_custom_widgets = build_custom_widgets
        self._show_hotkey_placeholder = show_hotkey_placeholder

        super().__init__(propagate=False)

    def __icon_clicked(self, x, y, *arg, **kwargs) -> None:
        if self._icon_clicked_fn is None or self.icon is None:
            return
        left = self.icon.screen_position_x
        top = self.icon.screen_position_y
        if (x < left) or (y < top):
            return
        right = left + self.icon.computed_width
        bottom = top + self.icon.computed_height
        if (x > right) or (y > bottom):
            return
        self._icon_clicked_fn(x, y, *arg, **kwargs)

    def build_item(self, item: Union[ui.MenuItem, ui.Menu]) -> None:
        """
        Build widgets (from left to right):
         - Selected icon
         - Menu item label
         - Menu item Icon
         - Custom widgets (Optional)
         - Hotkey label
         - Arrow for sub menus (only for ui.Menu)

        Args:
            item Union[ui.MenuItem, ui.Menu]): Menu item.
        """
        icon_type = "Menu.Item.Status"
        if self._force_checked:
            item.checked = self._force_checked
        self._container = ui.HStack(
            style_type_name_override="MenuBar.Item", selected=item.selected, checked=(item.checkable and item.checked)
        )
        with self._container:
            selected = item.selected or (item.checkable and item.checked)
            # Status icon before menu text
            if selected or self._reserve_status:
                self.icon = ui.ImageWithProvider(style_type_name_override=icon_type, width=STATUS_ICON_WIDTH, mouse_released_fn=self.__icon_clicked)

            # Text
            ui.Label(item.text, style_type_name_override="Menu.Item.Text")

            if self._icon_name or self._build_custom_widgets or isinstance(item, ui.Menu):
                ui.Spacer()

            # Icon after menu text
            if self._icon_name:
                ui.Spacer(width=10)
                ui.ImageWithProvider(
                    style_type_name_override="Menu.Item.Icon", name=self._icon_name, width=self._icon_width
                )

            if self._build_custom_widgets:
                self._build_custom_widgets(self, item)

            # build hotkey text
            if item.hotkey_text:
                ui.Spacer(width=8)
                ui.Label(item.hotkey_text.title(), style_type_name_override="Menu.Item.Label", enabled=False, width=100)
            elif self._show_hotkey_placeholder:
                # Placeholder to align with menuitem with hotkey
                ui.Spacer(width=108)

            if isinstance(item, ui.Menu):
                # For menu, show arrow for children
                ui.Spacer(width=10)
                with ui.VStack(width=MENU_ARROW_SIZE / 2):
                    ui.Spacer()
                    ui.Triangle(
                        height=MENU_ARROW_SIZE,
                        alignment=ui.Alignment.RIGHT_CENTER,
                        style_type_name_override="MenuBar.Item.Triangle",
                    )
                    ui.Spacer()
                ui.Spacer(width=3)

    def get_selected(self) -> bool:
        """Delegate selected state"""
        return self._container.selected if self._container else False

    def set_selected(self, value: bool) -> bool:
        """Set delegate selected state and return whether it changed or not."""
        value = bool(value)
        if self._container and (self.get_selected() != value):
            self._container.selected = value
            return True
        return False

    def get_checked(self) -> bool:
        """Delegate checked state"""
        return self._container.checked if self._container else False

    def set_checked(self, value: bool) -> bool:
        """Set delegate checked state and return whether it changed or not."""
        value = bool(value)
        if self._container and (self.get_checked() != value):
            self._container.checked = value
            return True
        return False

    @property
    def selected(self) -> bool:
        """Delegate selected state"""
        return self.get_selected()

    @selected.setter
    def selected(self, value: bool) -> None:
        self.set_selected(value)

    @property
    def checked(self) -> bool:
        """Delegate checked state"""
        return self.get_checked()

    @checked.setter
    def checked(self, value: bool) -> None:
        self.set_checked(value)
