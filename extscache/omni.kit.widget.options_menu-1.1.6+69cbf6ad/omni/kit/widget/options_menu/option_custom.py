"""This module defines a custom option item class for user interfaces, supporting custom build functions and optional models for value storage."""

from typing import Any, Optional

import omni.ui as ui

from .option_item import AbstractOptionItem


class OptionCustom(AbstractOptionItem):
    """A class that represents a custom option item with a build function and a model.

    This class allows for the creation of a custom option item within a user interface, using
    a provided build function to construct the menu item. It supports an optional model
    to hold the value of the option and an optional default value to be used when resetting.

        Args:
            build_fn (callable): The function used to build the menu item.
            model (Optional[ui.AbstractValueModel]): The model used to store the value of the option item.
            default (Optional[Any]): The default value of the option item if not provided by the model."""

    def __init__(
        self, build_fn: callable, model: Optional[ui.AbstractValueModel] = None, default: Optional[Any] = None
    ):
        """Initializes the custom option with the provided build function and model."""
        self.build_fn = build_fn
        self._model = model
        if default is not None:
            self.default = default
        elif model is not None:
            if isinstance(model, ui.SimpleIntModel):
                self.default = model.as_int
            elif isinstance(model, ui.SimpleBoolModel):
                self.default = model.as_bool
            else:
                self.default = model.as_string
        super().__init__()

    def build_menu_item(self, **kwargs) -> None:
        """Builds a menu item with the specified attributes."""
        self.build_fn()

    @property
    def name(self) -> str:
        """Gets the name of the custom option.

        Returns:
            str: The name of the custom option."""
        return ""

    @property
    def model(self) -> ui.SimpleBoolModel:
        """Gets the model associated with the custom option.

        Returns:
            ui.SimpleBoolModel: The current model of the custom option."""
        return self._model

    @property
    def dirty(self) -> bool:
        """Gets the dirty status of the custom option.

        Returns:
            bool: True if the value has changed from the default, False otherwise."""
        if self.model:
            if isinstance(self.model, ui.SimpleIntModel):
                return self.model.as_int != self.default
            elif isinstance(self.model, ui.SimpleBoolModel):
                return self.model.as_bool != self.default
            else:
                return self.model.as_string != self.default
        else:
            return False

    def reset(self) -> None:
        """Resets the custom option's value to its default."""
        if self.model:
            self.model.set_value(self.default)
