"""Provides classes to represent and manage option items and delegates for an OptionsMenu in the Omniverse Kit."""

from typing import Any, List, Optional, Callable, Union

import omni.ui as ui

from .checkable_delegate import CheckableMenuItemDelegate
from .setting_model import SettingModel


class AbstractOptionItem(ui.AbstractItem):
    """Represents an abstract item for an OptionsMenu."""

    def destroy(self):
        """Destroys the option item."""
        pass

    def build_menu_item(self, **menu_item_kwargs) -> None:
        """Builds a menu item for the option.

        Keyword Args:
            enabled (bool): If the menu item is enabled.
            checkable (bool): If the menu item is checkable.
            hide_on_click (bool): If the menu item hides when clicked."""
        return None

    @property
    def model(self) -> ui.AbstractValueModel:
        """Gets the value model for this item.

        Returns:
            ui.AbstractValueModel: The associated value model."""
        return None

    @property
    def dirty(self) -> bool:
        """Gets the dirty flag indicating if the item's value has changed.

        Returns:
            bool: True if the value has changed, False otherwise."""
        return False

    def reset(self) -> None:
        """Resets the option item to its default state."""
        pass


class OptionMenuItemDelegate(CheckableMenuItemDelegate):
    """Delegate for a general option menu item.
    A general option item includes a selected icon and item text.

    Args:
        option_item (OptionItem): The option item to show as a menu item.
        width (ui.Length): The width of the menu item. Defaults to ui.Fraction(1)."""

    def __init__(self, option_item: "OptionItem", width: ui.Length = ui.Fraction(1)):
        """Initializer for OptionMenuItemDelegate."""
        self._option_item = option_item
        super().__init__(width=width, checked=self._option_item.model.as_bool, enabled=self._option_item.enabled)

    def destroy(self):
        """Cleans up resources and subscriptions."""
        self.__sub_value = None

    def build_item(self, item: ui.MenuItem):
        """Builds the UI representation for the menu item.

        Args:
            item (ui.MenuItem): The menu item to build a UI for."""
        self.__sub_value = self._option_item.model.subscribe_value_changed_fn(self._on_value_changed)
        super().build_item(item)
        self._on_value_changed(self._option_item.model)

    def build_widget(self, item: ui.MenuItem):
        """Builds the custom widget associated with the menu item.

        Args:
            item (ui.MenuItem): The menu item to build a custom widget for."""
        super().build_widget(item)
        self._option_item.build_custom_widget(item)

    def on_triggered(self):
        """Executes the action associated with the menu item when triggered."""
        self._option_item.on_triggered()

    def _on_value_changed(self, model: ui.SimpleBoolModel) -> None:
        self.checked = model.as_bool

    def _on_mouse_hovered(self, hovered: bool) -> None:
        # If not checkable, do not show check icon when hovered
        if self._option_item.checkable:
            super()._on_mouse_hovered(hovered)


class OptionMenuItem(ui.MenuItem):
    """Represent a menu item for a single option.

    Args:
        option_item (OptionItem): Option item to show as menu item.
        width (ui.Length): Menu item width. Default ui.Fraction(1).
        hide_on_click (bool): Whether the menu item should hide after a click. Default is False.

    Keyword Args:
        checkable (bool): If the menu item can be checked. Default True.
        enabled (bool): If the menu item is enabled. Default True.
        icon (Union[str, ui.Icon]): Icon to be displayed next to the menu item. Default None.
        shortcut (str): Shortcut key combination for the menu item. Default None.
        tooltip (str): Text to be displayed as a tooltip. Default None."""

    def __init__(
        self, option_item: "OptionItem", width: ui.Length = ui.Fraction(1), hide_on_click: bool = False, **kwargs
    ):
        """Initialize the OptionMenuItem instance."""
        self._delegate = OptionMenuItemDelegate(option_item, width=width)
        super().__init__(
            option_item.text, delegate=self._delegate, checkable=True, hide_on_click=option_item.hide_on_click, **kwargs
        )

    def destroy(self):
        """Destroy the OptionMenuItem, cleaning up any resources."""
        self._delegate.destroy()


class OptionItem(AbstractOptionItem):
    """Represents a general item for OptionsMenu.

    Args:
        name (str): The name of the menu item.
        text (str): The text to display for the menu item. Defaults to the name if not provided.
        default (bool): The initial value of the item. Defaults to False.
        on_value_changed_fn (Callable[[bool], None]): A callback function that is called when the item's value changes.
        model (Optional[ui.SimpleBoolModel]): The model associated with the item. If not provided, a new model is created.
        setting_path (Optional[str]): The path used to store the item's setting. If not provided, no setting is stored.
        enabled (bool): Indicates whether the menu item is enabled. Defaults to True.
        checkable (bool): Determines if the menu item can be checked. Defaults to True.
        hide_on_click (bool): Determines if the menu item should hide when clicked. Defaults to False."""

    def __init__(
        self,
        name: Optional[str],
        text: Optional[str] = None,
        default: bool = False,
        on_value_changed_fn: Callable[[bool], None] = None,
        model: Optional[ui.SimpleBoolModel] = None,
        setting_path: Optional[str] = None,
        enabled: bool = True,
        checkable: bool = True,
        hide_on_click: bool = False,
    ):
        """Constructor for OptionItem."""
        self.name = name
        self.text = text or name
        self.default = default
        self.checkable = checkable
        if model:
            self._model = model
        elif setting_path:
            self._model = SettingModel(setting_path)
        else:
            self._model = ui.SimpleBoolModel(default)
        self._enabled = enabled
        self.hide_on_click = hide_on_click
        if on_value_changed_fn:
            self.__on_value_changed_fn = on_value_changed_fn

            def __on_value_changed(model: ui.SimpleBoolModel):
                self.__on_value_changed_fn(model.as_bool)

            self.__sub = self._model.subscribe_value_changed_fn(__on_value_changed)

        self._menu_item: Optional[OptionMenuItem] = None

        super().__init__()

    def destroy(self):
        """Cleans up any resources held by the item."""
        if self._menu_item:
            self._menu_item.destroy()
        self.__sub = None

    def build_menu_item(self, **kwargs) -> None:
        """Builds the associated menu item with the given keyword arguments.

        Keyword Args:
            enabled (bool): If the menu item is enabled."""
        self._menu_item = OptionMenuItem(self, enabled=self._enabled, **kwargs)

    def build_custom_widget(self, item: ui.MenuItem) -> None:
        """Builds a custom widget for the associated menu item.

        Args:
            item (ui.MenuItem): The menu item associated with this option."""
        pass

    def on_triggered(self):
        """Executes the action associated with the item when it is triggered."""
        if self.enabled:
            self.model.set_value(not self.model.as_bool)

    @property
    def enabled(self) -> bool:
        """Gets the enabled state of the option item.

        Returns:
            bool: The current enabled state."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Sets the enabled state of the option item.

        Args:
            value (bool): The new enabled state to set."""
        self._enabled = value
        if self._menu_item:
            self._menu_item.enabled = value
            self._menu_item._delegate.enabled = value

    @property
    def value(self) -> bool:
        """Gets the current value of the option item.

        Returns:
            bool: The current value."""
        return self.model.as_bool

    @value.setter
    def value(self, new_value: bool) -> None:
        """Sets the current value of the option item.

        Args:
            new_value (bool): The new value to set."""
        self.model.set_value(new_value)

    @property
    def model(self) -> ui.SimpleBoolModel:
        """Gets the value model of the option item.

        Returns:
            ui.SimpleBoolModel: The current value model."""
        return self._model

    @property
    def dirty(self) -> bool:
        """Gets the dirty state indicating if the item's value has changed.

        Returns:
            bool: The current dirty state."""
        return self.model.as_bool != self.default

    def reset(self) -> None:
        """Resets the option item's value to its default state."""
        self.model.set_value(self.default)
