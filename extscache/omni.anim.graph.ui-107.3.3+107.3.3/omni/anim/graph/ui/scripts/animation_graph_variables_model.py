import json
import omni.ui as ui
import weakref

from enum import Enum
from functools import partial
from pxr import Usd, Tf, Sdf
from typing import List, Set, Optional

from .node_graph import NodeGraphRoot


EMPTY_STRING_MODEL = ui.SimpleStringModel("")


class VariableNameModel(ui.AbstractValueModel):
    """The model that changes the variable name"""

    def __init__(self, label: str, node_graph: NodeGraphRoot):
        super().__init__()
        self._label = label or ""
        self._label_on_begin = None
        self._node_graph = node_graph

    def get_value_as_string(self):
        """Reimplemented get string"""
        return self._label

    def set_value(self, value):
        """Reimplemented set"""
        try:
            value = str(value)
        except ValueError:
            value = ""
        if value != self._label:
            # replacing invalid characters with '_'
            self._label = Tf.MakeValidIdentifier(value)
            # Tell the widget that the model is changed
            self._value_changed()

    def begin_edit(self):
        self._label_on_begin = self._label

    def end_edit(self):
        if self._label_on_begin == self._label or not self._node_graph:
            return

        # Get the unique name
        new_variable_name = self._node_graph.get_next_variable_name(self._label)

        # Move the variable to the new name
        self._node_graph.rename_variable(self._label_on_begin, new_variable_name)

        self._value_changed()


class VariableTypeModel(ui.AbstractValueModel):
    """The model that changes the variable type"""

    def __init__(self, variable_name_model: VariableNameModel, node_graph: NodeGraphRoot):
        super().__init__()
        self._type_name = node_graph.get_variable_type(variable_name_model.as_string)
        self._variable_name_model = variable_name_model
        self._node_graph = node_graph

    def get_value_as_string(self):
        """Reimplemented get string"""
        return str(self._type_name)

    def set_value(self, value):
        """Reimplemented set"""
        try:
            value = str(value)
        except ValueError:
            value = ""
        if value != self.get_value_as_string():
            self._type_name = Sdf.ValueTypeNames.Find(value)
            if self._type_name:
                # Move the variable to the new type
                self._node_graph.change_variable_type(self._variable_name_model.as_string, self._type_name)

                # Tell the widget that the model is changed
                self._value_changed()


class VariableDescriptionModel(ui.AbstractValueModel):
    """The model that changes the variable description/tooltip"""

    def __init__(self, variable_name_model: VariableNameModel, node_graph: NodeGraphRoot):
        super().__init__()
        self._label = node_graph.get_variable_description(variable_name_model.as_string) or ""
        self._label_on_begin = None
        self._variable_name_model = variable_name_model
        self._node_graph = node_graph

    def get_value_as_string(self):
        """Reimplemented get string"""
        return self._label

    def set_value(self, value):
        """Reimplemented set"""
        try:
            value = str(value)
        except ValueError:
            value = ""
        if value != self._label:
            self._label = value
            # Tell the widget that the model is changed
            self._value_changed()

    def begin_edit(self):
        self._label_on_begin = self._label

    def end_edit(self):
        if self._label_on_begin == self._label or not self._node_graph:
            return

        self._node_graph.set_variable_description(self._variable_name_model.as_string, self._label)

        self._value_changed()


class VariableItem(ui.AbstractItem):
    class VariableItemModelType(Enum):
        Name = 0
        Type = 1
        DefaultValue = 2
        Description = 3

    def __init__(self, node_graph: NodeGraphRoot, var_name: str):
        super().__init__()

        name_model = VariableNameModel(var_name, node_graph)
        type_model = VariableTypeModel(name_model, node_graph)
        description_model = VariableDescriptionModel(name_model, node_graph)
        self.value_models = [name_model, type_model, None, description_model]
        self.in_filter = True

    def filter_by_text(self, filter_name_text: str):
        """Specify the filter string that is used to reduce the model"""

        if not filter_name_text:
            self.in_filter = True
        else:
            filter_name_text = filter_name_text.lower()
            value_model = self.value_models[VariableItem.VariableItemModelType.Name.value]
            self.in_filter = filter_name_text in value_model.as_string.lower()

        return self.in_filter


class VariableGroupItem(ui.AbstractItem):
    def __init__(self, name):
        super().__init__()

        self.name_model = ui.SimpleStringModel(name)
        self.variables: List[VariableItem] = []
        self.in_filter = True

    def filter_by_text(self, filter_name_text: str):
        """Specify the filter string that is used to reduce the model"""

        if not filter_name_text:
            for item in self.variables:
                item.in_filter = True

            self.in_filter = True
        else:
            group_visible = False
            for item in self.variables:
                group_visible |= item.filter_by_text(filter_name_text)

            self.in_filter = group_visible


class AnimationGraphVariablesModel(ui.AbstractItemModel):
    def __init__(self, node_graph: Optional[NodeGraphRoot]):
        super().__init__()

        self._node_graph = None
        self._variable_items: List[ui.AbstractItem] = []
        self._variables_changed_callback_id = None

        self.node_graph = node_graph
        self._last_filter_text = None

    def destroy(self):
        self.node_graph = None
        self._variable_items = None
        self._variables_changed_callback_id = None
        self._last_filter_text = None

    @property
    def node_graph(self):
        return self._node_graph

    @node_graph.setter
    def node_graph(self, graph: NodeGraphRoot):
        if graph == self._node_graph:
            return

        if self._node_graph:
            self._node_graph.remove_variables_changed_callback(self._variables_changed_callback_id)
            self._variables_changed_callback_id = None

        self._node_graph = graph
        self._variable_items.clear()
        if graph:
            variable_names = graph.get_variable_names()
            for name in variable_names:
                self._add_variable(name)

            def variables_changed(variable_name, weak_self):
                weak_self = weak_self()
                if not weak_self:
                    return

                weak_self._update_variables()

            self._variables_changed_callback_id = graph.add_variables_changed_callback(
                partial(variables_changed, weak_self=weakref.ref(self))
            )

        self._item_changed(None)

    def get_item_children(self, parent_item=None):
        if parent_item is None:
            return [item for item in self._variable_items if item.in_filter]

        if isinstance(parent_item, VariableGroupItem):
            return [item for item in parent_item.variables if item.in_filter]

        return []

    def remove_item(self, item):
        if item is not None and isinstance(item, VariableItem):
            self._node_graph.delete_variable(
                item.value_models[VariableItem.VariableItemModelType.Name.value].get_value_as_string()
            )

    def get_item_value_model_count(self, item=None):
        if item is not None:
            if isinstance(item, VariableGroupItem):
                return 1

            if isinstance(item, VariableItem):
                return len(item.value_models)

        return 1

    def get_item_value_model(self, item=None, column_id=0):
        if item is not None:
            if isinstance(item, VariableGroupItem):
                if column_id == 0:
                    return item.name_model
            elif isinstance(item, VariableItem) and column_id < len(item.value_models):
                return item.value_models[column_id]

        return None

    def drop_accepted(self, item_target, item_source, drop_location=-1):
        return False

    def get_drag_mime_data(self, item=None):
        if item is not None and isinstance(item, VariableItem):
            data = {
                "variable_name": item.value_models[VariableItem.VariableItemModelType.Name.value].get_value_as_string()
            }
            return json.dumps(data)

        return None

    def filter_by_text(self, filter_name_text: str):
        self._last_filter_text = filter_name_text

        """Specify the filter string that is used to reduce the model"""
        for item in self._variable_items:
            item.filter_by_text(filter_name_text)

        self._item_changed(None)

    def _add_variable(self, name):
        new_item = VariableItem(
            self._node_graph,
            name
        )

        self._variable_items.append(new_item)
        new_item.filter_by_text(self._last_filter_text)

    def _update_variables(self):
        variable_items = self._variable_items.copy()
        found_items: Set[VariableItem] = set()

        variable_names = self._node_graph.get_variable_names()
        for name in variable_names:
            found = False
            for item in variable_items:
                if item.value_models[VariableItem.VariableItemModelType.Name.value].get_value_as_string() == name:
                    found = True
                    item.value_models[VariableItem.VariableItemModelType.Type.value].set_value(
                        str(self._node_graph.get_variable_type(name))
                    )
                    item.value_models[VariableItem.VariableItemModelType.Description.value].set_value(
                        self._node_graph.get_variable_description(name)
                    )
                    found_items.add(item)
                    break

            if not found:
                self._add_variable(name)

        deleted_variable_items: Set[VariableItem] = set(variable_items).difference(found_items)
        for deleted_item in deleted_variable_items:
            self._variable_items.remove(deleted_item)

        self._item_changed(None)
        for item in self._variable_items:
            self._item_changed(item)
