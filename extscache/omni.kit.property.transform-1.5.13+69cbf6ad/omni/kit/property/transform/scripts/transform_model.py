"""A module providing VecAttributeModel, a UI model for editing vector attributes with mathematical operations support."""

import weakref
from typing import Callable

import omni.ui as ui
from pxr import Gf

# TODO: will add controlstate


class VecAttributeModel(ui.AbstractItemModel):
    """A class representing a model for vector attributes with editable string fields.

    This model is designed to parse string values for vector attributes, allowing for
    mathematical operations to be performed on the vector's components. It uses
    internal string models to represent float values as strings. It provides
    callbacks for beginning and ending edit operations on vector components.

        Args:
            default_value: The default value to initialize each component of the vector.
            begin_edit_callback (Callable[[None], None]): Optional; a callback function
                that is invoked when editing of a component begins.
            end_edit_callback (Callable[[Gf.Vec3d], None]): Optional; a callback function
                that is invoked when editing of a component ends, receiving the edited
                value as an argument."""

    def __init__(
        self,
        default_value,
        begin_edit_callback: Callable[[None], None] = None,
        end_edit_callback: Callable[[Gf.Vec3d], None] = None,
    ):
        """Initializer for VecAttributeModel."""
        super().__init__()

        # We want to parse the values of this model to look for math operations,
        # so its items need to use string models instead of float models
        class StringModel(ui.SimpleStringModel):
            def __init__(self, parent, index):
                super().__init__()
                self._parent = weakref.ref(parent)
                self.index = index

            def begin_edit(self):
                parent = self._parent()
                parent.begin_edit(self)

            def end_edit(self):
                parent = self._parent()
                parent.end_edit(self)

        class VectorItem(ui.AbstractItem):
            def __init__(self, model):
                super().__init__()
                self.model = model

        dimension = 3
        self._items = [VectorItem(StringModel(self, i)) for i in range(dimension)]
        self._default_value = default_value
        self._begin_edit_callback = begin_edit_callback
        self._end_edit_callback = end_edit_callback

        for item in self._items:
            item.model.set_value(self._default_value)

        self._root_model = ui.SimpleStringModel()
        self._root_model.add_value_changed_fn(lambda a: self._item_changed(None))

    def get_item_children(self, item):
        """Get the child items of a given item.

        Args:
            item: The item whose children are to be retrieved."""
        return self._items

    def get_item_value_model(self, item, column_id):
        """Gets the value model for a given item and column.

        Args:
            item: The item for which the value model is needed.
            column_id: The identifier for the column."""
        if item is None:
            return self._root_model
        return item.model

    def _on_value_changed(self, item):
        pass

    def begin_edit(self, item):
        """Begins the editing process for the given item.

        Args:
            item: The item that is being edited."""
        index = item.index
        if self._begin_edit_callback:
            self._begin_edit_callback(index)

    def end_edit(self, model):
        """Ends the editing process for the given model.

        Args:
            model: The model that was being edited."""
        text = model.get_value_as_string()
        index = model.index

        for item in self._items:
            item.model.set_value(self._default_value)

        if self._end_edit_callback:
            self._end_edit_callback(text, index)
