"""This module provides classes for creating separators with optional titles for option menus in Omniverse Kit."""

from typing import Optional

import omni.ui as ui

from .option_item import AbstractOptionItem


class SeparatorDelegate(ui.MenuDelegate):
    """A delegate class for creating a menu separator with an optional title.

    This class is used to create a visual separator between menu items, which can be optionally accompanied by a title. It extends the ui.MenuDelegate from the omni.ui module.

        Args:
            title (Optional[str]): The title text to display alongside the separator. If None, no title is displayed."""

    def __init__(self, title: Optional[str] = None):
        """Initializes the SeparatorDelegate."""
        self.__title = title
        super().__init__()

    def build_item(self, _):
        """Builds a UI item for the separator.

        Args:
            _ : Used as a placeholder, no direct usage."""
        with ui.HStack():
            if self.__title:
                ui.Spacer(width=8)
                ui.Label(self.__title, width=0, enabled=False, style_type_name_override="MenuItem.Label")
                ui.Spacer(width=8)
                ui.Line(height=10, style_type_name_override="MenuItem.Separator", alignment=ui.Alignment.BOTTOM)
            else:
                ui.Spacer(width=24)
                ui.Line(height=10, style_type_name_override="MenuItem.Separator")
            ui.Spacer(width=12)


class OptionSeparatorMenuItem(ui.MenuItem):
    """A class representing a menu item separator with an optional title.

    This class is a specialized menu item that acts as a visual separator. It can optionally include a title.

        Args:
            title (Optional[str]): The title text to display alongside the separator if provided."""

    def __init__(self, title: Optional[str] = None):
        """Initializes a new instance of the OptionSeparatorMenuItem."""
        super().__init__("##OPTION_SEPARATOR", delegate=SeparatorDelegate(title), enabled=False)


class OptionSeparator(AbstractOptionItem):
    """A simple option item represents a separator in menu item.

    Args:
        title (str, optional): The title of the separator."""

    def __init__(self, title: str = None):
        """Initializes an OptionSeparator with optional title."""
        self.title = title
        super().__init__()

    def build_menu_item(self, **menu_item_kwargs) -> None:
        """Creates a menu item for the OptionSeparator.

        Keyword Args:
            **menu_item_kwargs: Additional keyword arguments for menu item customization."""
        OptionSeparatorMenuItem(self.title)

    @property
    def name(self) -> str:
        """Gets the name of the OptionSeparator.

        Returns:
            str: The name of the OptionSeparator."""
        return ""  # pragma no cover
