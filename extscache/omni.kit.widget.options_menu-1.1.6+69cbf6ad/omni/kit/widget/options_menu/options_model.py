"""Provides a model for managing and interacting with a collection of option items in a menu."""

from typing import List, Optional

import omni.ui as ui

from .option_item import AbstractOptionItem


class OptionsModel(ui.AbstractItemModel):
    """Model for options items.

    This class represents a model for managing a collection of option items within a menu.
    The model provides functionality to manage the lifecycle of the items, track changes, and notify subscribers of updates.

    Args:
        name (str): Model name to display in the menu header.
        items (List[AbstractOptionItem]): Items to be displayed in the menu."""

    def __init__(self, name: str, items: List[AbstractOptionItem]):
        """Initializes the OptionsModel."""
        self.name = name
        self._items = items
        self.__subs = {}
        for item in self._items:
            if item.model:
                self.__subs[item] = item.model.subscribe_value_changed_fn(
                    lambda m, i=item: self.__on_value_changed(i, m)
                )
        super().__init__()

    def destroy(self):
        """Cleans up the model, preparing for destruction."""
        self.__clean_items()

    @property
    def dirty(self) -> bool:
        """Gets the dirty state of the options model.

        Returns:
            bool: True if any item is not in its default value, False otherwise."""
        for item in self._items:
            if item.dirty:
                return True
        return False

    def rebuild_items(self, items: List[AbstractOptionItem]) -> None:
        """Rebuilds the internal list of option items.

        Args:
            items (List[AbstractOptionItem]): The new list of items to show in the model."""
        self.__clean_items()
        self._items = items
        for item in self._items:
            if item.model:
                self.__subs[item] = item.model.subscribe_value_changed_fn(
                    lambda m, i=item: self.__on_value_changed(i, m)
                )

        self._item_changed(None)

    def reset(self) -> None:
        """Resets all items in the model to their default values."""
        for item in self._items:
            item.reset()

    def get_item_children(self, item: Optional[AbstractOptionItem] = None) -> List[AbstractOptionItem]:
        """Retrieves the children of a given item or all items if none specified.

        Args:
            item (Optional[AbstractOptionItem]): The parent item whose children to retrieve."""
        return self._items if item is None else []

    def __on_value_changed(self, item: AbstractOptionItem, model: ui.SimpleBoolModel):
        self._item_changed(item)

    def __clean_items(self):
        self.__subs.clear()
        for item in self._items:
            item.destroy()
