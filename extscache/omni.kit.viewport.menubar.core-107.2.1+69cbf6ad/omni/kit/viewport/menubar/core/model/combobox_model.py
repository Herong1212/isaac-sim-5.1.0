__all__ = ["ComboBoxItem", "ComboBoxModel", "SettingComboBoxModel"]

import collections
from typing import Any, List, Optional
import weakref

import carb
import carb.settings
from omni import ui


class ComboBoxItem(ui.AbstractItem):
    """A data item for a single item in combobox drop list."""
    def __init__(self, text: str, value: Any) -> None:
        """
        Constructor.

        Args:
            text (str): Item text.
            value (Any): Item value.
        """
        super().__init__()
        self.model = ui.SimpleStringModel(text)
        self.value = value


class ComboBoxModel(ui.AbstractItemModel):
    """A data model for items in combobox drop list."""
    def __init__(self, texts: List[str], values: Optional[List[Any]] = None, current_value: Any = None):
        """
        Constructor.

        Args:
            texts (List[str]): Texts displayed in combobox

        Keyword Args:
            values (Optional[List[Any]]): Values for combobox list, default to None to use text as value
            current_value (Any): Current value displayed in combobox, defaults to None to use first one.
        """
        super().__init__()

        # List items
        self._items = []
        for index, text in enumerate(texts):
            value = values[index] if values else text
            self._items.append(ComboBoxItem(text, value))

        # Current value
        current = self._get_current_index_by_value(current_value)
        self.current_index = ui.SimpleIntModel(current)
        self._sub = self.current_index.subscribe_value_changed_fn(
            lambda _, this=weakref.proxy(self): this.on_current_changed()
        )

    def destroy(self) -> None:
        """Release resources"""
        self._sub = None
        self.current_index = None
        self._items = []

    def get_item_children(self, item: Optional[ComboBoxItem]) -> List[ComboBoxItem]:
        """
        Returns all the children when the widget asks it.

        Args:
            item (Optional[ComboBoxItem]): Parent itemd, defaults to None means to retrieve root items.
        """
        return self._items

    def get_item_value_model(self, item: Optional[ComboBoxItem], column_id: int):
        """
        Retrieve item value model.

        Args:
            item (Optional[ComboBoxItem]): Combobox item.
            column_id (int): Column index.
        """
        if item is None:
            return self.current_index
        if isinstance(item, ComboBoxItem):
            return item.model
        return ui.SimpleStringModel("Unknown")  # pragma: no cover

    def on_current_changed(self):
        """Callback when current selection in combobox changed"""
        current_index = self.current_index.as_int
        items = self.get_item_children(None)
        self._on_current_item_changed(items[current_index])

        self._item_changed(None)

    def _get_current_index_by_value(self, value: Any, default: int = 0) -> int:
        if value is None:
            current = default
        else:
            items = self.get_item_children(None)
            if isinstance(value, float):
                current = next((i for i, item in enumerate(items) if abs(item.value - value) < 0.0001), default)
            else:
                if isinstance(value, list):
                    value = tuple(value)
                current = next((i for i, item in enumerate(items) if item.value == value), default)

        return current

    def _on_current_item_changed(self, item: ComboBoxItem) -> None:
        pass  # pragma: no cover


class SettingComboBoxModel(ComboBoxModel):
    """A data model for items in combobox drop list and get/set value from/to a setting path."""
    def __init__(self, setting_path: str, texts: List[str], values: Optional[List[Any]] = None,
                 current_value: Any = None):
        """
        Constructor.

        Args:
            setting_path (str): Setting path
            texts (List[str]): Texts displayed in combobox

        keyword Args:
            values (Optional[List[Any]]): Values for combobox list, defaults to None to use text as value.
        """
        self._path = setting_path
        self.__setting_subs = []
        self.__future = None
        self._settings = carb.settings.get_settings()
        if current_value is None:
            current_value = self._settings.get(self._path)

        super().__init__(texts, values=values, current_value=current_value)

        if not isinstance(current_value, str) and isinstance(current_value, collections.abc.Sequence):
            for i in range(len(current_value)):
                self.__setting_subs.append(
                    self._settings.subscribe_to_tree_change_events(f"{self._path}/{i}", self.__on_seq_change)
                )
        else:
            self.__setting_subs.append(
                self._settings.subscribe_to_tree_change_events(self._path, lambda t, c, e: self._on_change(t, e))
            )

    def destroy(self) -> None:
        """Release resources."""
        setting_subs, self.__setting_subs = self.__setting_subs, None
        if setting_subs and self._settings:
            for sub in setting_subs:
                self._settings.unsubscribe_to_change_events(sub)
            self._settings = None
        super().destroy()

    def _on_current_item_changed(self, item: ComboBoxItem) -> None:
        self._settings.set(self._path, item.value)

    def __on_seq_change(self, tree_item, changed_item, event_type) -> None:
        # carb settings change handler to collapse a sequencec of changes (from an array) into a single event
        if event_type != carb.settings.ChangeEventType.CHANGED:
            return

        import asyncio
        if not self.__future or self.__future.done():
            self.__future = asyncio.Future()

        async def collapse_changes(tree_item, event_type):
            if self.__future.done():
                return
            self.__future.set_result(True)
            self._on_change(tree_item, event_type)

        asyncio.ensure_future(collapse_changes(tree_item, event_type))

    def _on_change(self, tree_item, event_type) -> None:
        current_value = self._settings.get(self._path)
        current = self._get_current_index_by_value(current_value)
        if current != self.current_index.as_int:
            self.current_index.set_value(current)
