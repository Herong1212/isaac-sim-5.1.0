"""This module provides a radio menu widget for the Omniverse Kit with radio button groups, individual radio buttons, and their associated models and delegates."""

from typing import Dict, List, Optional, Union

import omni.ui as ui

from .checkable_delegate import CheckableMenuItemDelegate
from .option_separator import OptionSeparatorMenuItem
from .popup_menu import AbstractPopupMenu, PopupMenuDelegate


class RadioItem(ui.AbstractItem):
    """A class representing a single radio button item.

    This class is used to create an item that can be used in a radio button group, where only one item can be selected at a time.

        Args:
            text (str): The text label displayed next to the radio button."""

    def __init__(self, text: str):
        """Initializer for the RadioItem."""
        self.model = ui.SimpleStringModel(text)
        super().__init__()

    @property
    def text(self) -> str:
        """Gets the text of the RadioItem.

        Returns:
            str: The text associated with the RadioItem."""
        return self.model.as_string


class RadioModel(ui.AbstractItemModel):
    """A class that represents a model for radio buttons, allowing the selection of a single option from a list.

    Args:
        texts (List[str]): A list of strings representing the options.
        default_index (int): The index of the initially selected option."""

    def __init__(self, texts: List[str], default_index: int = 0):
        """Initializes a new instance of RadioModel."""
        self._texts = texts
        self._items = [RadioItem(text) for text in texts]
        self._default_index = default_index
        self._index_model = ui.SimpleIntModel(default_index)
        super().__init__()

    @property
    def dirty(self) -> bool:
        """Gets whether the current selected index is not the default one.

        Returns:
            bool: True if the current index is not the default, False otherwise."""
        return self.index != self._default_index

    @property
    def index_model(self) -> ui.SimpleIntModel:
        """Gets the model of the current index.

        Returns:
            ui.SimpleIntModel: The model representing the current index."""
        return self._index_model

    @property
    def index(self) -> int:
        """Gets the current index value.

        Returns:
            int: The current index value."""
        return self._index_model.as_int

    @index.setter
    def index(self, value: int) -> None:
        """Sets the current index to a new value.

        Args:
            value (int): The new index to set."""
        self._index_model.set_value(value)

    @property
    def index_text(self) -> str:
        """Gets the text of the currently selected string.

        Returns:
            str: The text of the current selection."""
        return self._texts[self.index]

    def reset(self) -> None:
        """Resets the index to the default value."""
        self.index = self._default_index

    def get_item_children(self, item: Optional[RadioItem] = None) -> List[RadioItem]:
        """Gets the children items of a given item or all items if no item is provided.

        Args:
            item (Optional[RadioItem]): The parent item or None for all items.

        Returns:
            List[RadioItem]: A list of child items."""
        return self._items if item is None else []


class RadioMenuItemDelegate(CheckableMenuItemDelegate):
    """Delegate for radio menu item.
    While only one radio item in a radio model could be checked at the same time.

    Args:
        model (RadioModel): Radio Model includes the radio item.
        item (RadioItem): Radio item."""

    def __init__(self, model: RadioModel, item: RadioItem):
        """Constructor for RadioMenuItemDelegate."""
        self._model = model
        self._item = item
        items = self._model.get_item_children()
        self._index = items.index(item)
        self.__sub = self._model.index_model.subscribe_value_changed_fn(self._on_index_changed)
        super().__init__(checked=self._index == self._model.index_model.as_int)

    def destroy(self):
        """Cleans up the resources held by the delegate."""
        self.__sub = None
        super().destroy()

    def _on_index_changed(self, model: ui.SimpleIntModel):
        index = model.as_int
        checked = index == self._index
        if self.checked != checked:
            self.checked = checked

    def on_triggered(self):
        """Sets the current index of the model to this item's index."""
        if self._model.index != self._index:
            self._model.index = self._index


class RadioMenuItem(ui.MenuItem):
    """Represent a menu item for a single radio item.

    Args:
        model (RadioModel): Radio Model that includes the radio item.
        item (RadioItem): Radio item."""

    def __init__(self, model: RadioModel, item: RadioItem):
        """Constructor for RadioMenuItem."""
        self._delegate = RadioMenuItemDelegate(model, item)
        super().__init__(item.text, delegate=self._delegate, hide_on_click=False, checkable=True)

    def destroy(self):
        """Destroys the radio menu item and cleans up resources."""
        self._delegate.destroy()


class RadioMenuDelegate(PopupMenuDelegate):
    """Delegate for a radio menu.

    This delegate allows for managing multiple radio models within a menu, ensuring that only one radio item can be checked at a time.

        Args:
            radio_models (List[RadioModel]): List of RadioModels to be displayed in the menu."""

    def __init__(self, radio_models: List[RadioModel]):
        """Constructor for RadioMenuDelegate."""
        self._models = radio_models
        self.__subs = {}
        for model in self._models:
            self.__subs[model] = model.index_model.subscribe_value_changed_fn(self._on_index_changed)
        super().__init__()

    def destroy(self):
        """Clean up resources and subscriptions."""
        for model in self._models:
            self.__subs[model] = None
        self.__subs = {}

        super().destroy()

    @property
    def dirty(self) -> bool:
        """Gets the dirty state of the radio models.

        Returns:
            bool: True if any model's selected index is not default, else False."""
        for model in self._models:
            if model.dirty:
                return True
        return False

    def build_title(self, item: ui.Menu) -> None:
        """Builds the title for the radio menu.

        Args:
            item (ui.Menu): The menu to which the title will be built."""
        super().build_title(item)
        self.enable_reset_all(self.dirty)

    def on_reset_all(self) -> None:
        """Resets all radio models to their default indices."""
        for model in self._models:
            model.reset()

    def _on_index_changed(self, model: ui.SimpleIntModel) -> None:
        self.enable_reset_all(self.dirty)


class RadioMenu(AbstractPopupMenu):
    """Represent a menu for radios.

    Args:
        title (str): Title shown in header.
        radio_model (Union[RadioModel, List[RadioModel]]): Radio Models."""

    def __init__(self, title: str, radio_model: Union[RadioModel, List[RadioModel]]):
        """Initializer for RadioMenu."""
        self._models = [radio_model] if isinstance(radio_model, RadioModel) else radio_model
        self._menu_items: Dict[RadioModel, List[ui.MenuItem]] = {}
        self._delegate = RadioMenuDelegate(self._models)
        super().__init__(title, delegate=self._delegate)

    def destroy(self):
        """Cleans up resources used by the RadioMenu instance."""
        for model in self._menu_items:
            for menu_item in self._menu_items[model]:
                menu_item.destroy()
        self._menu_items = {}
        self._delegate.destroy()

    def build_menu_items(self):
        """Generates and populates the menu items for each radio model."""
        for index, model in enumerate(self._models):
            if index > 0:
                OptionSeparatorMenuItem()
            self._menu_items[model] = []
            for item in model.get_item_children():
                menu_item = RadioMenuItem(model, item)
                self._menu_items[model].append(menu_item)
