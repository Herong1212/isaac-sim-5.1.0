"""Provides a customizable options menu widget for the Omniverse Kit UI."""

from typing import List, Optional

import omni.ui as ui

from .option_item import AbstractOptionItem
from .options_model import OptionsModel
from .popup_menu import AbstractPopupMenu, PopupMenuDelegate
from .style import OPTIONS_MENU_STYLE


class OptionsMenuDelegate(PopupMenuDelegate):
    """Delegate for options menu.
    It has a header to show label and reset button.

    Args:
        model (OptionsModel): Model for options to show in this menu."""

    def __init__(self, model: OptionsModel, **kwargs):
        """Initializes the options menu delegate."""
        self._model = model
        self.__sub = self._model.subscribe_item_changed_fn(self.__on_item_changed)

        super().__init__(**kwargs)

    def destroy(self) -> None:
        """Cleans up resources."""
        self.__sub = None

    def build_title(self, item: ui.Menu) -> None:
        """Builds the title for the given menu item.

        Args:
            item (ui.Menu): The menu item to build the title for."""
        super().build_title(item)
        self.enable_reset_all(self._model.dirty)

    def get_title(self, item: ui.Menu) -> str:
        """Retrieves the title for the given menu item.

        Args:
            item (ui.Menu): The menu item to get the title for."""
        return item._model.name

    def on_reset_all(self) -> None:
        """Resets all options to their default values."""
        self._model.reset()

    def __on_item_changed(self, model: OptionsModel, item: AbstractOptionItem) -> None:
        if self._reset_all:
            self._reset_all.enabled = self._model.dirty


class OptionsMenu(AbstractPopupMenu):
    """Represent a menu to show options.

    A options menu includes a header and a list of menu items for options.

        Args:
            model (OptionsModel): Model of option items to show in this menu.
            hide_on_click (bool): Hide menu when item clicked. Default False.
            width (ui.Length): Width of menu item. Default ui.Fraction(1).
            style (dict): Additional style. Default empty."""

    def __init__(
        self, model: OptionsModel, hide_on_click: bool = False, width: ui.Length = ui.Fraction(1), style: dict = {}
    ):
        """Initializes the options menu with the given parameters."""
        self._model = model
        self._hide_on_click = hide_on_click
        self._width = width

        self._delegate = OptionsMenuDelegate(self._model)
        super().__init__(self._model.name, delegate=self._delegate, style=style)
        self.__sub = self._model.subscribe_item_changed_fn(self.__on_model_changed)

    def destroy(self):
        """Cleans up the resources and subscriptions."""
        self.__sub = None
        self._delegate.destroy()
        self._model.destroy()

    @property
    def model(self) -> OptionsModel:
        """Gets the model associated with the options menu.

        Returns:
            OptionsModel: The model of the options menu."""
        return self._model

    def rebuild_items(self, items: List[AbstractOptionItem]) -> None:
        """Rebuilds the menu items based on the provided items list.

        Args:
            items (List[AbstractOptionItem]): The items to rebuild the menu with."""
        self._model.rebuild_items(items)

    def build_menu_items(self):
        """Builds the menu items from the model's item children."""
        for item in self._model.get_item_children():
            item.build_menu_item(hide_on_click=self._hide_on_click, width=self._width)

    def __on_model_changed(self, model: OptionsModel, item: Optional[AbstractOptionItem]) -> None:
        if item is None:
            self.invalidate()
