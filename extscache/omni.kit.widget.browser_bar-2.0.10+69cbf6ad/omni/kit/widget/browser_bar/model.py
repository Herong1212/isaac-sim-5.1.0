# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides the implementation for a string queue model and a visited history tracking system, designed to manage and interact with collections of strings representing items and a history of visited items respectively."""


import sys, os
import omni.ui as ui


class StringQueueItem(ui.AbstractItem):
    """A class representing an item in a string queue.

    This class encapsulates a string value as part of a queue, providing a simple interface to access the string value. It is designed to be used within a queue structure that manages multiple instances of `StringQueueItem`s, allowing for operations such as enqueueing and dequeueing of string values.

    Args:
        value (str): The string value to be encapsulated by the `StringQueueItem`."""

    def __init__(self, value: str):
        """Initializes a new instance of StringQueueItem."""
        super().__init__()
        self._model = ui.SimpleStringModel(value)

    @property
    def model(self):
        """Gets the model associated with this StringQueueItem.

        Returns:
            :obj:`ui.SimpleStringModel`: The model of the item."""
        return self._model

    @property
    def value(self):
        """Gets the value of the StringQueueItem as a string.

        Returns:
            str: The value of the item."""
        return self._model.get_value_as_string()


class StringQueueModel(ui.AbstractItemModel):
    """A class that manages a queue of string items with a maximum size.

    This model is designed to handle a collection of StringQueueItem objects,
    providing methods to enqueue new items, dequeue the oldest item,
    and to access items based on index or value.
    It also maintains the selection state of items in the queue.

    Args:
        max_items (int): The maximum number of items allowed in the queue. Defaults to 4.
        value_changed_fn (Optional[Callable[[ui.AbstractValueModel], None]]):
                            A callback function that gets called when the selected index changes.
    """

    def __init__(self, max_items: int = 4, value_changed_fn=None):
        """Initializes the StringQueueModel with optional max items and a value changed callback."""
        super().__init__()
        self._value_changed_fn = value_changed_fn
        self._max_items = max_items
        self._items = []
        self._selected_index = ui.SimpleIntModel(0)
        # TODO: There's a bug that if the item selected doesn't have a different
        # index, then it doesn't trigger this callback. It's better to trigger on
        # mouse pressed but we don't have this option.
        self._selected_index.add_value_changed_fn(self._on_selection_changed)

    def __getitem__(self, idx: int) -> StringQueueItem:
        if idx < len(self._items):
            return self._items[idx]
        return None

    @property
    def selected_index(self) -> int:
        """Gets the currently selected index.

        Returns:
            int: The current selected index."""
        return self._selected_index.get_value_as_int()

    @selected_index.setter
    def selected_index(self, index: int):
        """Sets the selected index.

        Args:
            index (int): The new index to set as selected."""
        self._selected_index.set_value(index)

    def get_selected_item(self) -> StringQueueItem:
        """Retrieves the currently selected item.

        Returns:
            :obj:`StringQueueItem`: The selected item if any, None otherwise."""
        index = self._selected_index.get_value_as_int()
        if index >= 0 and index < len(self._items):
            return self._items[index]
        return None

    def get_item_children(self, item) -> [StringQueueItem]:
        """Gets the children of a specified item.

        Args:
            item (:obj:`StringQueueItem`): The item to get children for.

        Returns:
            List[:obj:`StringQueueItem`]: List of child items."""
        if item is None:
            return self._items
        return []

    def get_item_value_model(self, item, column_id) -> ui.AbstractValueModel:
        """Gets the value model for an item and column.

        Args:
            item (:obj:`StringQueueItem`): The item to get the model for.
            column_id (int): The ID of the column.

        Returns:
            :obj:`ui.AbstractValueModel`: The value model for the specified item and column."""
        if item is None:
            return self._selected_index
        return item.model

    def find_item(self, value: str) -> StringQueueItem:
        """Finds an item by its value.

        Args:
            value (str): The value to search for.

        Returns:
            :obj:`StringQueueItem`: The found item, or None if not found."""
        for item in self._items:
            if item.value == value:
                return item
        return None

    def size(self) -> int:
        """Returns the number of items in the queue.

        Returns:
            int: The size of the queue."""
        return len(self._items)

    def peek(self) -> StringQueueItem:
        """Peeks at the first item in the queue without removing it.

        Returns:
            :obj:`StringQueueItem`: The first item if the queue is not empty, None otherwise."""
        if self._items:
            return self._items[0]
        return None

    def enqueue(self, value: str):
        """Enqueues a new value to the queue.

        Args:
            value (str): The value to enqueue."""
        if not value:
            return
        found = self.find_item(value)
        if not found:
            item = StringQueueItem(value)
            self._items.insert(0, item)
            while len(self._items) > self._max_items:
                self.dequeue()
            self.selected_index = 0
            self._item_changed(None)

    def dequeue(self):
        """Dequeues the last item from the queue."""
        if self._items:
            self._items.pop(-1)
            self.selected_index = min(self.selected_index, self.size() - 1)
            self._item_changed(None)

    def _on_selection_changed(self, model: ui.AbstractValueModel):
        if self._value_changed_fn:
            self._value_changed_fn(model)
        self._item_changed(None)

    def destroy(self):
        """Destroys the queue, clearing all items and selected index."""
        self._items = None
        self._selected_index = None


class VisitedHistory:
    """A class for maintaining a history of visited items.

    This class is designed to keep track of a list of items (e.g., URLs, file paths) that have been visited, allowing for easy access to recently visited items. It supports operations such as insertion and retrieval of items, enabling or disabling the history tracking, and managing the maximum number of items to retain in history.

    Args:
        max_items (int, optional): The maximum number of items to retain in the visited history. Defaults to 100."""

    def __init__(self, max_items: int = 100):
        """Initializes the VisitedHistory object."""
        self._max_items = max_items
        self._items = []
        self._selected_index = 0
        # the activation state for the visited history; when we are jumping between history entries, the visited history
        # should not change; for example, when we click the prev/next button, the path field would update to that entry
        # but those should not be counted in visited history.
        self._active = True

    def __getitem__(self, idx: int) -> str:
        if idx < len(self._items):
            return self._items[idx]
        return None

    def activate(self):
        """Activates the history tracking."""
        self._active = True

    def deactivate(self):
        """Deactivates the history tracking."""
        self._active = False

    @property
    def selected_index(self) -> int:
        """Gets the currently selected index.

        Returns:
            int: The current selected index."""
        return self._selected_index

    @selected_index.setter
    def selected_index(self, index: int):
        """Sets the currently selected index.

        Args:
            index (int): The new index to set as selected."""
        self._selected_index = index

    def get_selected_item(self) -> str:
        """Retrieves the currently selected item from history.

        Returns:
            str: The selected item or None if not selected."""
        index = self._selected_index
        if index >= 0 and index < len(self._items):
            return self._items[index]
        return None

    def size(self) -> int:
        """Returns the size of the visited history.

        Returns:
            int: The number of items in the history."""
        return len(self._items)

    def insert(self, value: str):
        """Inserts a new value into the visited history.

        Args:
            value (str): The value to insert."""
        if self._active is False:
            return
        if not value:
            return
        # avoid adding the same entry twice
        # this could happen when actions on top sets the browser bar path to the same path twice
        if self.size() > 0 and self._items[0] == value:
            return
        self._items.insert(0, value)
        while self.size() > self._max_items:
            self.pop()
        self.selected_index = 0

    def pop(self):
        """Pops the last item from the visited history."""
        if self._items:
            self._items.pop()
            self.selected_index = min(self.selected_index, self.size() - 1)

    def destroy(self):
        """Destroys the visited history, clearing all items."""
        self._items.clear()
