"""Provides a customizable popup menu with a delegate system for handling menu items and actions in the Omniverse Kit."""

import abc
from typing import Optional

import carb
import omni.ui as ui

from .style import OPTIONS_MENU_STYLE


class PopupMenuItemDelegate(ui.MenuDelegate):
    """Delegate for general popup menu item.
    A general popup item includes a selected icon and item text.

    Args:
        width (ui.Length): Menu item width. Default ui.Fraction(1)."""

    def __init__(self, width: ui.Length = ui.Fraction(1)):
        """Initializes the popup menu item delegate."""
        self._width = width
        super().__init__(propagate=True)

    def destroy(self):
        """Cleans up resources used by the delegate."""
        self.__sub = None

    def build_item(self, item: ui.MenuItem):
        """Builds UI components for the menu item.

        Args:
            item (ui.MenuItem): The menu item to build UI components for."""
        self._container = ui.HStack(height=24, width=self._width, content_clipping=False, checked=False)
        with self._container:
            ui.ImageWithProvider(width=24, style_type_name_override="MenuItem.Icon")
            ui.Label(
                item.text,
                style_type_name_override="MenuItem.Label",
            )
            ui.Spacer(width=16)

        self._container.set_mouse_pressed_fn(lambda x, y, b, a: self.on_trigger())
        self._container.set_mouse_hovered_fn(self._on_mouse_hovered)

    def on_trigger(self) -> None:
        """Handles the trigger action for the menu item."""
        self._container.checked = not self._container.checked

    def _on_mouse_hovered(self, hovered: bool) -> None:
        # Here to set selected instead of hovered status for icon.
        # Because there is margin in icon, there will be some blank at top/bottom as a result icon does not become hovered if mouse on these area.
        self._container.selected = hovered


class PopupMenuDelegate(ui.MenuDelegate):
    """Delegate for popup menu.
    It has a header to show label and reset button.

        Keyword Args:
            propagate (bool): Whether the event propagation is allowed. Default True.
            style_type_name_override (str): The name of the style type override. Default None."""

    def __init__(self, **kwargs):
        """Initializes the popup menu delegate."""
        self._reset_all: Optional[ui.Button] = None
        super().__init__(**kwargs)

    def destroy(self) -> None:
        """Cleans up any resources held by the delegate."""
        pass

    def build_title(self, item: ui.Menu) -> None:
        """Builds the title section of the popup menu.

        Args:
            item (ui.Menu): The menu item for which to build the title."""
        with ui.ZStack(content_clipping=True, height=24):
            ui.Rectangle(style_type_name_override="Title.Background")
            with ui.HStack(style_type_name_override="Title.Header"):
                if item.text:
                    ui.Label(self.get_title(item), width=0, style_type_name_override="Title.Label")

                # Extra spacer here to make sure menu window has min width
                ui.Spacer(width=45)
                ui.Spacer()
                self._reset_all = ui.Button(
                    "Reset All",
                    width=0,
                    height=24,
                    enabled=False,
                    style_type_name_override="ResetButton",
                    clicked_fn=self.on_reset_all,
                    identifier="reset_all",
                )

    def get_title(self, item: ui.Menu) -> str:
        """Retrieves the title for the given menu item.

        Args:
            item (ui.Menu): The menu item to retrieve the title for.

        Returns:
            str: The title of the menu item."""
        return item.text

    def on_reset_all(self) -> None:
        """Handles the reset all action."""
        pass

    def enable_reset_all(self, enabled: bool) -> None:
        """Enables or disables the reset all button.

        Args:
            enabled (bool): True to enable, False to disable the reset all button."""
        if self._reset_all:
            self._reset_all.enabled = enabled


class AbstractPopupMenu(ui.Menu):
    """Represent a popup menu.
    A popup menu includes a header and a list of menu items.

    Args:
        title (str): Title in header
        delegate (Optional[PopupMenuDelegate]): Menu delegate. Default None to use PopupMenuDelegate
        style (dict): Additional style. Default empty."""

    def __init__(self, title: str, delegate: Optional[PopupMenuDelegate] = None, style: dict = {}):
        """Initializes an abstract popup menu instance."""
        menu_style = OPTIONS_MENU_STYLE.copy()
        menu_style.update(style)

        self._delegate = delegate or PopupMenuDelegate()
        super().__init__(
            title,
            delegate=self._delegate,
            menu_compatibility=False,
            on_build_fn=self.build_menu_items,
            style=menu_style,
        )

    def destroy(self):
        """Destroys the popup menu and its delegate."""
        self._delegate.destroy()

    def show_by_widget(self, widget: ui.Widget, alignment: ui.Alignment = ui.Alignment.LEFT_BOTTOM) -> None:
        """Displays the popup menu adjacent to the specified widget.

        Args:
            widget (ui.Widget): The widget to align the popup menu with.
            alignment (ui.Alignment): The preferred alignment for the popup menu."""
        if widget:
            if alignment == ui.Alignment.RIGHT_TOP:
                x = widget.screen_position_x + widget.computed_width
                y = widget.screen_position_y
            elif alignment == ui.Alignment.LEFT_BOTTOM:
                x = widget.screen_position_x
                y = widget.screen_position_y + widget.computed_height
            else:
                carb.warning("Unsupport alignment '{alignment}' for Options menu!")
                x = None
                y = None
            if x is None or y is None:
                self.show()
            else:
                self.show_at(x, y)
        else:
            self.show()

    @abc.abstractmethod
    def build_menu_items(self):
        """Abstract method to build menu items for the popup menu."""
        pass
