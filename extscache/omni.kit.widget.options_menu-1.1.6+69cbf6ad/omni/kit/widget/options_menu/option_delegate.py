"""This module provides a custom menu item delegate with additional spacing for use in UI menus."""

import omni.ui as ui


class OptionLabelMenuItemDelegate(ui.MenuDelegate):
    """A delegate class for a normal menu item with an additional spacer at the end.

    This class inherits from ui.MenuDelegate and is specialized to provide a custom appearance
    for menu items in a UI. It includes a spacer at the end to ensure proper layout
    within the menu.

        Args:
            width (ui.Length): Menu item width."""

    def __init__(self, width: ui.Length = ui.Fraction(1)):
        """Initializer for OptionLabelMenuItemDelegate."""
        self._width = width
        super().__init__(propagate=True)

    def build_item(self, item: ui.MenuItem):
        """Builds the menu item visual representation.

        Args:
            item (ui.MenuItem): The menu item to build a visual for."""
        self._container = ui.HStack(height=24, width=self._width, content_clipping=False)
        with self._container:
            ui.Spacer(width=24)
            self.build_widget(item)
            ui.Spacer(width=16)

    def build_widget(self, item: ui.MenuItem) -> None:
        """Builds the widget for the given menu item.

        Args:
            item (ui.MenuItem): The menu item to create a widget for."""
        ui.Label(
            item.text,
            style_type_name_override="MenuItem.Label",
        )
