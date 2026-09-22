from typing import List, Callable, Optional, Union
from omni import ui
from .reset_button import ResetHelper

__all__ = ["SimpleListItem", "SimpleListModel", "ColorModel"]


class SimpleListItem(ui.AbstractItem):
    """A single item in list model"""
    def __init__(self, value: Union[float, int, str, ui.AbstractValueModel], text: Optional[str] = None):
        """
        Constructor.

        Args:
            value (Union[float, int, str, ui.AbstractValueModel]): Item value.

        Keyword Args:
            text (Optional[str]): Item text, defaults to None means using value.
        """
        super().__init__()
        self.model = ui.SimpleStringModel(text) if text else ui.SimpleStringModel(str(value))
        self.value = value
        if isinstance(value, ui.AbstractValueModel):
            self.value_model = value
        elif isinstance(value, float):
            self.value_model = ui.SimpleFloatModel(value)
        elif isinstance(value, int):
            self.value_model = ui.SimpleIntModel(value)
        elif isinstance(value, str):
            self.value_model = ui.SimpleStringModel(value)

    def __repr__(self):
        return f"[SimpleListItem]: {self.model.as_string}: {self.value}"  # pragma: no cover


class SimpleListModel(ui.AbstractItemModel):
    """A simple data model contains list of values"""
    def __init__(self, values: List[float], texts: Optional[List[str]] = None):
        """
        Constructor.

        Args:
            values (List[float]): Item values.

        Keyword Args:
            texts (Optional[List[str]]): Item texts, defaults to None means using values.
        """
        super().__init__()

        # Create root model
        self._root_model = ui.SimpleIntModel()
        self._root_model.add_value_changed_fn(lambda a: self._item_changed(None))

        if texts:
            self._items = [SimpleListItem(value, text) for value, text in zip(values, texts)]
        else:
            self._items = [SimpleListItem(value) for value in values]

        for item in self._items:
            item.value_model.add_value_changed_fn(lambda a, item=item: self._on_value_changed(item))

    def destroy(self) -> None:
        """Release resources"""
        self._items = []

    def get_item_children(self, item: Optional[ui.AbstractItem] = None) -> List[ui.AbstractItem]:
        """Returns all the children when the widget asks it."""
        return self._items

    def get_item_value_model_count(self) -> int:
        """The number of columns"""
        return 1

    def get_item_value_model(self, item: SimpleListItem, column_id: int):
        if item is None:
            return self._root_model
        return item.value_model

    def _on_value_changed(self, item: SimpleListItem):
        """Called when the sub model is changed"""
        self._item_changed(item)
        self._on_item_value_changed(item)

    def _on_item_value_changed(self, item: SimpleListItem):
        pass  # pragma: no cover


class ColorModel(SimpleListModel, ResetHelper):
    """A simple color model with reset supported"""
    def __init__(self, colors: List[float], default: Optional[List[float]] = None, on_color_changed_fn: Callable[[List[float]], None] = None):
        """
        Constructor.

        Args:
            colors (List[float]): colors.

        Keyword Args:
            default (default: Optional[List[float]]): Default color values, defaults to None.
            on_color_changed_fn (Callable[[List[float]], None]): Callback when color changed, defaults to None.
        """
        SimpleListModel.__init__(self, colors)
        ResetHelper.__init__(self)

        self.__default = default
        self._on_color_changed_fn = on_color_changed_fn

        # Create root model
        self._root_model = ui.SimpleIntModel()
        self._root_model.add_value_changed_fn(lambda a: self._item_changed(None))

        self._reset_button = None
        self._editing = False

    def destroy(self) -> None:
        """Release resources"""
        self._root_model = None
        super().destroy()

    @property
    def colors(self) -> List[float]:
        """Colors"""
        return [item.value_model.as_float for item in self._items]

    @colors.setter
    def colors(self, values: List[float]) -> None:
        for index, item in enumerate(self._items):
            print(f"set {index}: {item}, {item.value_model}, {values}")
            item.value_model.set_value(values[index])

    def _on_item_value_changed(self, item: SimpleListItem):
        """Called when the sub model is changed"""
        colors = [item.value_model.as_float for item in self._items]
        if self._on_color_changed_fn:
            self._on_color_changed_fn(colors)

        self._update_reset_button()

    def begin_edit(self, item):
        """Called when the user starts editing. Reimplemented from the base class."""
        # Must define here otherwise crash happens when click on the color widget
        return  # pragma: no cover

    def end_edit(self, item):
        """Called when the user finishes editing. Reimplemented from the base class."""
        return  # pragma: no cover

    # for ResetHelper
    def get_default(self) -> List[float]:
        """Get default colors"""
        return self.__default

    def restore_default(self) -> None:
        """Restore default colors"""
        if self.__default is not None:
            self.colors = self.__default

    def get_value(self) -> List[float]:
        """Get current colors"""
        return self.colors
