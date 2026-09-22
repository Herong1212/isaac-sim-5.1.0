import asyncio
import json
from typing import List, Optional, Union

import omni.graph.core as og
import omni.kit.commands
import omni.kit.undo
import omni.ui as ui
import omni.usd
from omni.kit.property.usd.usd_model_base import UsdBase
from pxr import Sdf, Tf, Usd

GRAPH_VARIABLE_PREFIX = "graph:variable:"
READ_VARIABLE_NODES = ["omni.graph.core.ReadVariable", "omni.graph.instancing.ReadGraphVariable"]
WRITE_VARIABLE_NODES = ["omni.graph.core.WriteVariable", "omni.graph.instancing.WriteGraphVariable"]
VARIABLE_NODES = READ_VARIABLE_NODES + WRITE_VARIABLE_NODES


class VariableNameModel(ui.AbstractValueModel):
    """The model that changes the variable name"""

    def __init__(self, label: str, variables_model: "OmniGraphVariablesModel"):
        super().__init__()
        self._label = label or ""
        self._label_on_begin = None
        self._variables_model = variables_model

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

    def begin_edit(self):
        self._label_on_begin = self._label

    def end_edit(self):
        if self._label_on_begin == self._label or not self._variables_model:
            return

        old_var = self._variables_model.graph.find_variable(self._label_on_begin)
        new_var_name = self._variables_model.get_next_variable_name(self._label)

        # Update self._label to the validated value so the model continues to match the variable name.
        self.set_value(new_var_name)

        stage = omni.usd.get_context().get_stage()
        attr = stage.GetAttributeAtPath(old_var.source_path)
        old_var_value = attr.Get() if attr else None

        with omni.kit.undo.group():
            og.cmds.CreateVariable(
                graph=self._variables_model.graph,
                variable_name=new_var_name,
                variable_type=old_var.type,
                variable_value=old_var_value,
            )
            new_var = self._variables_model.graph.find_variable(new_var_name)
            if new_var and old_var:
                new_var.tooltip = old_var.tooltip
            og.cmds.RemoveVariable(graph=self._variables_model.graph, variable=old_var)

            # OM-107884: find all instances of variable in graph, update the name
            for inst in self._variables_model.get_variable_instances(self._label_on_begin):
                name_attr = inst.get_attribute("inputs:variableName")
                og.Controller.set(name_attr, new_var_name, update_usd=True)

        self._value_changed()


class VariableTypeModel(ui.AbstractValueModel):
    """The model that changes the variable type"""

    def __init__(
        self,
        type_name: Sdf.ValueTypeName,
        variable_name_model: VariableNameModel,
        variables_model: "OmniGraphVariablesModel",
    ):
        super().__init__()
        self._type_name = type_name
        self._variable_name_model = variable_name_model
        self._variables_model = variables_model

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
            if self._type_name and self._variables_model:
                variable_name = self._variable_name_model.as_string
                old_variable = self._variables_model.graph.find_variable(variable_name)
                tooltip = None
                if old_variable:
                    tooltip = old_variable.tooltip

                variable_type = og.AttributeType.type_from_sdf_type_name(self.get_value_as_string())
                # introduced in kit 105
                if hasattr(og.cmds, "ChangeVariableType"):
                    (success, _) = og.cmds.ChangeVariableType(variable=old_variable, variable_type=variable_type)
                    if success:
                        self._value_changed()

                else:
                    # Move the variable to the new type
                    with omni.kit.undo.group():
                        og.cmds.RemoveVariable(graph=self._variables_model.graph, variable=old_variable)
                        og.cmds.CreateVariable(
                            graph=self._variables_model.graph, variable_name=variable_name, variable_type=variable_type
                        )
                        new_variable = self._variables_model.graph.find_variable(variable_name)
                        if new_variable and tooltip:
                            new_variable.tooltip = tooltip

                    # Tell the widget that the model is changed
                    self._value_changed()


class VariableDescriptionModel(ui.AbstractValueModel):
    """The model that changes the variable description/tooltip"""

    def __init__(self, label: str, variable_name_model: VariableNameModel, variables_model: "OmniGraphVariablesModel"):
        super().__init__()
        self._label = label or ""
        self._label_on_begin = None
        self._variable_name_model = variable_name_model
        self._variables_model = variables_model

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
        if self._label_on_begin == self._label or not self._variables_model:
            return

        variable = self._variables_model.graph.find_variable(self._variable_name_model.as_string)
        if variable:
            og.cmds.SetVariableTooltip(variable=variable, tooltip=self._label)

        self._value_changed()


class VariableItem(ui.AbstractItem):
    def __init__(self, variables_model: "OmniGraphVariablesModel", name: str):
        super().__init__()

        self._variables_model = variables_model
        name_model = VariableNameModel(name, variables_model)

        variable = variables_model.graph.find_variable(name)
        variable_type_name = og.AttributeType.sdf_type_name_from_type(variable.type)
        type_model = VariableTypeModel(variable_type_name, name_model, variables_model)
        description_model = VariableDescriptionModel(variable.tooltip, name_model, variables_model)

        self.value_models = [name_model, type_model, None, description_model]

        self.in_filter = True

        self._default_value_models: List[UsdBase] = []

    def update(self):
        variable = self._variables_model.graph.find_variable(self.value_models[0].as_string)
        self.value_models[1].set_value(og.AttributeType.sdf_type_name_from_type(variable.type))

        for model in self._default_value_models:
            model._set_dirty()  # noqa: protected-access

        self.value_models[3].set_value(variable.tooltip)

    def filter_by_text(self, filter_name_text: str):
        """Flag whether the item matches the given filter text"""

        if not filter_name_text:
            self.in_filter = True
        else:
            filter_name_text = filter_name_text.lower()
            value_model = self.value_models[0]
            self.in_filter = filter_name_text in value_model.as_string.lower()

        return self.in_filter

    @property
    def default_value_models(self):
        return self._default_value_models

    @default_value_models.setter
    def default_value_models(self, models):
        for model in self._default_value_models:
            model.clean()

        self._default_value_models.clear()

        if isinstance(models, list):
            self._default_value_models.extend(models)
        else:
            self._default_value_models.append(models)


class VariableGroupItem(ui.AbstractItem):
    def __init__(self):
        super().__init__()

        self.name_model = ui.SimpleStringModel("CategoryName")
        self.variables: List[VariableItem] = []
        self.in_filter = True

    def filter_by_text(self, filter_name_text: str):
        """Flag whether the group has items that match the given filter text"""

        group_visible = False
        for item in self.variables:
            group_visible |= item.filter_by_text(filter_name_text)

        self.in_filter = group_visible


class OmniGraphVariablesModel(ui.AbstractItemModel):
    def __init__(self, graph: og.Graph = None):
        super().__init__()

        self._graph = None
        self._variable_items: List[ui.AbstractItem] = []

        self.graph = graph

        self._usd_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self.__process_usd_change, None)
        self._last_filter_text = None
        self.__prop_change_task = None

    def destroy(self):
        self._usd_listener = None
        self._graph = None
        self._variable_items = None
        self._last_filter_text = None

        if self.__prop_change_task:
            self.__prop_change_task.cancel()
            self.__prop_change_task = None

    @property
    def graph(self) -> Optional[og.Graph]:
        return self._graph

    @graph.setter
    def graph(self, value: Optional[og.Graph]):
        self._graph = value
        self._variable_items.clear()

        if self._graph:
            graph_variables = self._graph.get_variables()
            for variable in graph_variables:
                self._add_variable(variable.name)

        self._item_changed(None)

    def get_item_children(self, parent_item: Optional[VariableGroupItem] = None):
        if parent_item is None:
            return [item for item in self._variable_items if item.in_filter]

        if isinstance(parent_item, VariableGroupItem):
            return [item for item in parent_item.variables if item.in_filter]

        return []

    def remove_item(self, item: Union[VariableItem, VariableGroupItem]):
        if isinstance(item, VariableGroupItem):
            self._variable_items.extend(item.variables)
            self._variable_items.remove(item)
            self._item_changed(None)
        elif isinstance(item, VariableItem):
            variable = self._graph.find_variable(item.value_models[0].as_string)
            if variable:
                og.cmds.RemoveVariable(graph=self._graph, variable=variable)

    def duplicate_item(self, item: VariableItem):
        if isinstance(item, VariableItem):
            src_name = item.value_models[0].as_string
            src_var = self._graph.find_variable(src_name)
            new_var_name = self.get_next_variable_name(src_name)

            stage = omni.usd.get_context().get_stage()
            attr = stage.GetAttributeAtPath(src_var.source_path)
            src_var_value = attr.Get() if attr else None

            og.cmds.CreateVariable(
                graph=self._graph, variable_name=new_var_name, variable_type=src_var.type, variable_value=src_var_value
            )

    def get_item_value_model_count(self, item: Union[VariableItem, VariableGroupItem] = None):
        """Returns the number of columns of value data contained in the given item"""
        if item is not None:
            if isinstance(item, VariableGroupItem):
                return 1

            if isinstance(item, VariableItem):
                return len(item.value_models)

        return 1

    def get_item_value_model(self, item: Union[VariableItem, VariableGroupItem] = None, column_id: int = 0):
        if item is not None:
            if isinstance(item, VariableGroupItem):
                if column_id == 0:
                    return item.name_model
            elif isinstance(item, VariableItem) and column_id < len(item.value_models):
                return item.value_models[column_id]

        return None

    def drop_accepted(self, item_target: ui.AbstractItem, item_source: ui.AbstractItem, drop_location: int = -1):
        return False

    def get_drag_mime_data(self, item: VariableItem = None):
        if not item or not isinstance(item, VariableItem):
            return None

        data = {"variable_name": item.value_models[0].as_string}

        return json.dumps(data)

    def filter_by_text(self, filter_name_text: str):
        """Specify the filter string that is used to reduce the model"""

        self._last_filter_text = filter_name_text

        for item in self._variable_items:
            item.filter_by_text(filter_name_text)

        self._item_changed(None)

    def get_next_variable_name(self, name: str):
        new_variable_name = name
        counter = 1
        while True:
            if not self._graph.find_variable(new_variable_name):
                break

            new_variable_name = "{}{:02d}".format(name, counter)
            counter += 1

        return new_variable_name

    def _add_variable(self, name: str):
        for item in self._variable_items:
            if isinstance(item, VariableItem):
                if item.value_models[0].as_string == name:
                    item.update()
                    self._item_changed(item)
                    return False
            elif isinstance(item, VariableGroupItem):
                for child in item.variables:
                    if child.value_models[0].as_string == name:
                        self._item_changed(child)
                        return False

        new_item = VariableItem(self, name)

        self._variable_items.append(new_item)
        new_item.filter_by_text(self._last_filter_text)

        self._item_changed(None)

        return True

    def _remove_variable(self, name: str):
        for item in self._variable_items:
            if isinstance(item, VariableItem):
                if item.value_models[0].as_string == name:
                    self._variable_items.remove(item)
                    self._item_changed(None)
                    return
            elif isinstance(item, VariableGroupItem):
                for child in item.variables:
                    if child.value_models[0].as_string == name:
                        item.variables.remove(child)
                        self._item_changed(item)
                        return

    # get all instances of a variable, include subgraph
    def get_variable_instances(self, variable_name: str) -> List:

        instances = []

        def get_variable_instances_in_graph(graph: og.Graph):
            if graph:
                for node in graph.get_nodes():
                    if node.get_type_name() in VARIABLE_NODES:
                        name_attr = node.get_attribute("inputs:variableName")
                        if name_attr.get() == variable_name:
                            instances.append(node)
                            continue
                    if node.is_compound_node():
                        subgraph = node.get_compound_graph_instance()
                        get_variable_instances_in_graph(subgraph)

        get_variable_instances_in_graph(self.graph)
        return instances

    async def __process_property_change(self, path: Sdf.Path, stage):
        await omni.kit.app.get_app().next_update_async()

        if not self._graph or not self._graph.is_valid():
            return

        prop = stage.GetPropertyAtPath(path)
        if prop:
            self._add_variable(Sdf.Path.StripNamespace(path.name))
        else:
            self._remove_variable(Sdf.Path.StripNamespace(path.name))

    def __process_usd_change(self, objects_changed, stage):
        if not self._graph or not self._graph.is_valid():
            return

        def queue_property_change(path):
            if path.IsPropertyPath() and path.HasPrefix(graph_path) and path.name.startswith(GRAPH_VARIABLE_PREFIX):
                self.__prop_change_task = asyncio.ensure_future(self.__process_property_change(path, stage))

        graph_path = Sdf.Path(self._graph.get_path_to_graph())
        for resync_path in objects_changed.GetResyncedPaths():
            if resync_path == graph_path and not stage.GetPrimAtPath(resync_path):
                self.graph = None
                return

            queue_property_change(resync_path)

        for info_path in objects_changed.GetChangedInfoOnlyPaths():
            queue_property_change(info_path)
