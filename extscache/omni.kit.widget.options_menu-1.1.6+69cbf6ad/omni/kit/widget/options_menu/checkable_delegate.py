"""This module provides a CheckableMenuItemDelegate class for creating checkable menu items with custom behavior in the Omni UI."""

from typing import Optional

import omni.ui as ui


class CheckableMenuItemDelegate(ui.MenuDelegate):
    """Delegate for checkable menu item.
    A general checkable item includes a checked icon and item text.

    Args:
        checked (bool): If item is checked. Default False.
        width (ui.Length): Menu item width. Default ui.Fraction(1).
        enabled (bool): If item is enabled. Default True."""

    def __init__(self, checked: bool = False, width: ui.Length = ui.Fraction(1), enabled: bool = True):
        """Constructor for CheckableMenuItemDelegate."""
        self._width = width
        self._checked = checked
        self._enabled = enabled
        self._container: Optional[ui.HStack] = None
        super().__init__(propagate=True)

    def destroy(self):
        """Destroys the delegate and cleans up resources."""
        self.__sub = None

    @property
    def checked(self) -> bool:
        """Gets the checked status of the menu item.

        Returns:
            bool: The current checked status."""
        return self._checked

    @checked.setter
    def checked(self, value: bool) -> None:
        """Sets the checked status of the menu item.

        Args:
            value (bool): The new checked status to be set."""
        self._checked = value
        if self._container:
            self._container.checked = value
            if hasattr(self, "_icon"):
                self._icon.name = self.get_icon_name()

    @property
    def enabled(self) -> bool:
        """Gets the enabled status of the menu item.

        Returns:
            bool: The current enabled status."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Sets the enabled status of the menu item.

        Args:
            value (bool): The new enabled status to be set."""
        self._enabled = value
        if self._container:
            self._container.enabled = value
            if hasattr(self, "_icon"):
                self._icon.name = self.get_icon_name()

    def build_item(self, item: ui.MenuItem):
        """Builds the menu item with given properties.

        Args:
            item (ui.MenuItem): The menu item to build."""
        self._container = ui.HStack(
            height=24, width=self._width, content_clipping=False, checked=self._checked, enabled=self._enabled
        )
        with self._container:
            self.build_item_icon()
            self.build_widget(item)
            ui.Spacer(width=16)

        item.set_triggered_fn(self.on_triggered)
        self._container.set_mouse_hovered_fn(self._on_mouse_hovered)

    def build_widget(self, item: ui.MenuItem) -> None:
        """Builds the widget for the menu item.

        Args:
            item (ui.MenuItem): The menu item for which to build the widget."""
        ui.Label(
            item.text,
            style_type_name_override="MenuItem.Label",
        )

    def on_triggered(self):
        """Callback method for when the menu item is triggered."""
        if self._enabled:
            self.checked = not self.checked

    def build_item_icon(self):
        """Builds the icon for the menu item."""
        self._icon = ui.ImageWithProvider(width=24, style_type_name_override="MenuItem.Icon", name=self.get_icon_name())

    def get_icon_name(self):
        """Determines the icon name based on the item's state.

        Returns:
            str: The name of the icon."""
        # Show disabled check icon if item checked and disabled
        return "disabled" if self.checked and not self._enabled else ""

    def _on_mouse_hovered(self, hovered: bool) -> None:
        # Here to set selected instead of hovered status for icon.
        # Because there is margin in icon, there will be some blank at top/bottom as a result icon does not become hovered if mouse on these area.
        self._container.selected = hovered
