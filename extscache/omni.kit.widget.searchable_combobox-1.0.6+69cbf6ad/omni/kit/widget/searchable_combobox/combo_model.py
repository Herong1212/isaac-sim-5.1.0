"""This module provides classes for creating and managing a searchable ComboBox with custom item and model representations."""

__all__ = ["ComboBoxListItem", "ComboBoxListModel", "ComboBoxListDelegate"]

import omni.ui as ui
import omni.kit.app


class ComboBoxListItem(ui.AbstractItem):
    """Single item of the model.

    Args:
        text (str): The text to be displayed by the item."""

    def __init__(self, text):
        """Initializes a new instance of ComboBoxListItem with the specified text."""
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)
        # True when the item is visible
        self.filtered = True

    def prefilter(self, filter_name_text: str):
        """Filters this item based on the provided filter name text.

        Args:
            filter_name_text (str): The text to filter by. If empty, the item is marked as visible."""
        if not filter_name_text:
            self.filtered = True
        else:
            self.filtered = filter_name_text in self.name_model.as_string.lower()

    def __repr__(self):
        return f'"{self.name_model.as_string}"'


class ComboBoxListModel(ui.AbstractItemModel):
    """A model for managing a list of items in a ComboBox.

    Args:
        item_list (list of str): The list of items to populate the model with."""

    _instance = None

    def __init__(self, item_list):
        """Initializes a new ComboBoxListModel with a list of items."""
        super().__init__()
        self._children = [ComboBoxListItem(item) for item in item_list]
        global _instance
        _instance = self

    def clean(self):
        """Cleans up the ComboBoxListModel instance by resetting the global instance variable."""
        global _instance
        _instance = None

    def get_item_children(self, item):
        """Retrieves all the filtered children of the given item.

        Args:
            item (ui.AbstractItem): The parent item to get children for.

        Returns:
            list[ComboBoxListItem]: A list of filtered children items."""
        if item is not None:
            return []
        return [c for c in self._children if c.filtered]

    def get_item_value_model_count(self, item):
        """Returns the number of columns for a given item.

        Args:
            item (ui.AbstractItem): The item to query.

        Returns:
            int: The number of columns."""
        return 1

    def get_drag_mime_data(self, item):
        """Gets the MIME data for an item to enable drag-and-drop operations.

        Args:
            item (ComboBoxListItem): The item for which to get the MIME data.

        Returns:
            str: The MIME data as a string."""
        # As we don't do Drag and Drop to the operating system, we return the string.
        return item.name_model.as_string

    def get_item_value_model(self, item, column_id):
        """Retrieves the value model for a particular item and column.

        Args:
            item (ui.AbstractItem): The item to get the value model for.
            column_id (int): The column id for the item.

        Returns:
            ui.SimpleStringModel: The value model of the item."""
        return item.name_model

    def filter_by_text(self, filter_name_text: str):
        """Filters the items in the model based on the given text.

        Args:
            filter_name_text (str): The text to filter the items by."""
        for c in self._children:
            c.prefilter(filter_name_text.lower())
        self._item_changed(None)

    def get_index_for_item(self, item_text: str):
        """Finds the index of an item in the model by its text representation.

        Args:
            item_text (str): The text representation of the item to find.

        Returns:
            int: The index of the item if found, -1 otherwise."""
        for index, item in enumerate(self._children):
            if item.name_model.get_value_as_string() == item_text:
                return index
        return -1


class ComboBoxListDelegate(ui.AbstractItemDelegate):
    """A delegate for custom widget representation in a TreeView.

    Args:
        flat: bool
            Determines the flatness of the delegate's appearance."""

    def __init__(self, flat=False):
        """Initializes the ComboBoxListDelegate with an optional flat layout.

        Args:
            flat (bool): If True, the delegate uses a flat layout. Defaults to False."""
        super().__init__()

    def clean(self):
        """Cleans up any resources or references used by the delegate."""
        pass

    def build_branch(self, model, item, column_id, level, expanded):
        """Creates a branch widget that can be expanded or collapsed to show or hide children items.

        Args:
            model (ComboBoxListModel): The model that provides data and structure.
            item (ComboBoxListItem): The item for which to create the branch.
            column_id (int): The column identifier where the branch is to be created.
            level (int): The level of indentation for the branch.
            expanded (bool): Indicates whether the branch is expanded."""
        pass

    def build_widget(self, model, item, column_id, level, expanded):
        """Builds the widget representing an item in the ComboBoxList.

        Args:
            model (ComboBoxListModel): The model that provides data and structure.
            item (ComboBoxListItem): The item for which the widget is built.
            column_id (int): The column identifier where the widget is placed.
            level (int): The level of indentation for the item.
            expanded (bool): Indicates whether the item's branch is expanded."""
        ui.Label(
            model.get_item_value_model(item, column_id).as_string,
            skip_draw_when_clipped=True,
            elided_text=True,
            height=18,
        )
