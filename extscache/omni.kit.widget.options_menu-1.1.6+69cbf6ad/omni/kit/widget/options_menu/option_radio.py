"""This module provides UI components to create radio button options menus within the Omniverse Kit."""

from typing import Dict, List, Optional, Tuple, Union

import omni.ui as ui

from .checkable_delegate import CheckableMenuItemDelegate
from .option_item import AbstractOptionItem
from .option_separator import OptionSeparatorMenuItem
from .setting_model import SettingModel


class RadioDelegate(CheckableMenuItemDelegate):
    """Delegate for a radio menu item.

    This delegate manages the state and behavior of a radio menu item, ensuring that only one item in a group can be selected at a time.

    Args:
        model (RadioModel): The model containing the radio items.
        item (RadioItem): The specific radio item to delegate.
        enabled (bool): Specifies whether the radio item is enabled. Defaults to True."""

    def __init__(self, model: ui.SimpleStringModel, value: str, enabled: bool = True):
        """Constructor for RadioDelegate."""
        self._model = model
        self._value = value

        super().__init__(checked=self._model.as_string == self._value, enabled=enabled)

    def build_item_icon(self):
        """Creates the icon for the menu item."""
        ui.ImageWithProvider(width=24, style_type_name_override="MenuItem.Radio")

    def on_triggered(self):
        """Action performed when the radio item is triggered."""
        # Never set to unchecked by mouse click
        if self._model.as_string != self._value:
            self._model.set_value(self._value)


class OptionRadios(AbstractOptionItem):
    """Item for a list of radios.

    Args:
        radios (List[Union[str, Tuple[str]]]): List of radios.
            Could be a simple string where text and value are the same,
            or a Tuple in the format (text, value).
            If the Tuple's value is None, it signifies a separator with 'text' as the title.
        model (Optional[ui.SimpleStringModel]): String model representing the radio value.
        setting_path (Optional[str]): Setting path representing the radio value.
        default (Optional[str]): Default radio value. None uses the current value from the radio model.
        menu_text (Optional[str]): None to show radios directly. If not None, show radios as a menu with radios as sub-menu items.
        enabled (bool): Whether the menu item is enabled. Defaults to True.
        tooltips (Optional[List[str]]): Tooltips for each radio. None means no tooltips.
        hide_on_click (bool): Whether to hide the menu item when clicked. Defaults to False."""

    def __init__(
        self,
        radios: List[Union[str, Tuple[str]]],
        model: Optional[ui.SimpleStringModel] = None,
        setting_path: Optional[str] = None,
        default: Optional[str] = None,
        menu_text: Optional[str] = None,
        enabled: bool = True,
        tooltips: Optional[List[str]] = None,
        hide_on_click: bool = False,
    ):
        """Initializes the OptionRadios item with provided parameters."""
        self.radios = radios
        if model:
            self._model = model
        elif setting_path:
            self._model = SettingModel(setting_path)
        else:
            self._model = ui.SimpleStringModel(default if default else "")
        self.default = self._model.as_string if default is None else default

        self._enabled = enabled
        self._menu_text = menu_text
        self._tooltips = tooltips
        self._hide_on_click = hide_on_click

        self._delegates: Dict[str, ui.MenuDelegate] = {}
        self._menu_items: List[Union[ui.Menu, ui.MenuItem]] = []
        self.__sub = self._model.subscribe_value_changed_fn(self.__on_radio_changed)

        super().__init__()

    def destroy(self):
        """Cleans up the resources and delegates associated with the OptionRadios item."""
        for name, delegate in self._delegates.items():
            delegate.destroy()
        self._delegates = {}
        self.__sub = None

    def build_menu_item(self, **menu_item_kwargs: dict) -> None:
        """Builds a menu item with the given radio options.

        Keyword Args:
            enabled (bool): Whether the menu item is enabled.
            hide_on_click (bool): Whether to hide the menu on item click.
            text (str): The text to display for the menu item.
            checkable (bool): If the menu item is checkable."""
        menu_item_kwargs["hide_on_click"] = self._hide_on_click
        if self._menu_text:
            # Menu has no title in sub menu window, use general menu delegate
            menu = ui.Menu(self._menu_text, delegate=ui.MenuDelegate(), enabled=self._enabled)
            self._menu_items.append(menu)
            with menu:
                self._build_radio_items(**menu_item_kwargs)
        else:
            menu_items = self._build_radio_items(enabled=self._enabled, **menu_item_kwargs)
            self._menu_items.extend(menu_items)

    def _build_radio_items(self, **menu_item_kwargs: dict) -> List[ui.MenuItem]:
        # Create menu items for every radio
        menu_items = []
        for index, radio in enumerate(self.radios):
            if isinstance(radio, str):
                (text, value) = (radio, radio)
            else:
                (text, value) = radio
            if value is None:
                OptionSeparatorMenuItem(text)
            else:
                enabled = menu_item_kwargs.pop("enabled", True)
                self._delegates[value] = RadioDelegate(self._model, value, enabled=enabled)
                menu_item = ui.MenuItem(
                    text, delegate=self._delegates[value], checkable=True, enabled=enabled, **menu_item_kwargs
                )
                if self._tooltips and len(self._tooltips) > index:
                    tooltip = self._tooltips[index]
                    if tooltip:
                        menu_item.set_tooltip(tooltip)

                menu_items.append(menu_item)
        return menu_items

    @property
    def enabled(self) -> bool:
        """Gets the enabled state of the OptionRadios item.

        Returns:
            bool: The current enabled state."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Sets the enabled state of the OptionRadios item.

        Args:
            value (bool): The enabled state to set."""
        self._enabled = value
        for menu in self._menu_items:
            menu.enabled = value
            if hasattr(menu.delegate, "enabled"):
                menu.delegate.enabled = value

    @property
    def model(self) -> ui.SimpleStringModel:
        """Gets the model associated with the OptionRadios item.

        Returns:
            ui.SimpleStringModel: The current model."""
        return self._model

    @property
    def dirty(self) -> bool:
        """Gets the dirty state indicating if the OptionRadios value has changed.

        Returns:
            bool: Whether the OptionRadios value has changed."""
        return self.model.as_string != self.default

    def reset(self) -> None:
        """Resets the OptionRadios to its default value."""
        self.model.set_value(self.default)

    def __on_radio_changed(self, model: ui.SimpleStringModel) -> None:
        current_value = model.as_string
        for value, delegate in self._delegates.items():
            checked = value == current_value
            if delegate.checked != checked:
                delegate.checked = checked
