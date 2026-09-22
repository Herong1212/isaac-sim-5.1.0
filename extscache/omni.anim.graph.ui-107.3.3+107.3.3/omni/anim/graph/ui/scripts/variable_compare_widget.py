import omni.ui as ui
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
from pxr import Sdf, Usd
import AnimGraphSchema
from typing import List
from omni.kit.property.usd.usd_attribute_model import TfTokenAttributeModel
from .utils import refresh_property_window, find_anim_graph_prim, find_anim_graph_parent

VARIABLE_PREFIX = "anim:graph:variable:"
VARIABLE_NAME = "inputs:variableName"
VARIABLE_VALUE = "inputs:value"
VARIABLE_PREFIX_LEN = len(VARIABLE_PREFIX)


def _valid_type_name(attr_type_name: str):
    return attr_type_name == Sdf.ValueTypeNames.String or \
        attr_type_name == Sdf.ValueTypeNames.Int or \
        attr_type_name == Sdf.ValueTypeNames.Bool or \
        attr_type_name == Sdf.ValueTypeNames.Float


class CompareVariableNameModel(TfTokenAttributeModel):
    """Model for selecting the target attribute for the write/read operation. We modify the list to show attributes
    which are available on the target prim.
    """
    class AllowedTokenItem(ui.AbstractItem):
        def __init__(self, item, label):
            """
            Args:
                item: the attribute name token to be shown
                label: the label to show in the drop-down
            """
            super().__init__()
            self.token = item
            self.model = ui.SimpleStringModel(label)

    def __init__(
        self,
        stage: Usd.Stage,
        variable_paths: List[Sdf.Path],
        self_refresh: bool,
        metadata: dict,
        graph_prim_path: Sdf.Path,
    ):
        """
        Args:
            stage: The current stage
            variable_paths: The list of full variable paths
            self_refresh: ignored
            metadata: pass-through metadata for model
            node_prim_path: The path of the compute node
        """
        self._stage = stage
        self._graph_prim_path = graph_prim_path
        super().__init__(stage, variable_paths, self_refresh, metadata)

    def _get_allowed_tokens(self, _):
        # override of TfTokenAttributeModel to specialize what tokens to be shown
        variables = [""]

        graph_prim = self._stage.GetPrimAtPath(self._graph_prim_path)
        if graph_prim:
            attributes = graph_prim.GetAttributes()
            for attr in attributes:
                attr_type = attr.GetTypeName()
                attr_name = attr.GetName()
                if _valid_type_name(attr_type) and attr_name.startswith(VARIABLE_PREFIX):
                    var_name = attr_name[VARIABLE_PREFIX_LEN:]
                    variables.append(var_name)

        return variables

    def _update_value(self, force=False):
        # override of TfTokenAttributeModel to refresh the allowed token cache
        self._update_allowed_token()
        super()._update_value(force)

    def _item_factory(self, item):
        # construct the item for the model
        label = item
        return CompareVariableNameModel.AllowedTokenItem(item, label)

    def _update_allowed_token(self):
        # override of TfTokenAttributeModel to specialize the model items
        super()._update_allowed_token(token_item=self._item_factory)


class CompareVariableOperationModel(TfTokenAttributeModel):
    """Model for selecting the target attribute for the write/read operation. We modify the list to show attributes
    which are available on the target prim.
    """
    class AllowedTokenItem(ui.AbstractItem):
        def __init__(self, item, label):
            """
            Args:
                item: the attribute name token to be shown
                label: the label to show in the drop-down
            """
            super().__init__()
            self.token = item
            self.model = ui.SimpleStringModel(label)

    def __init__(
        self,
        stage: Usd.Stage,
        prim_paths,
        variable_paths: List[Sdf.Path],
        self_refresh: bool,
        metadata: dict,
    ):
        """
        Args:
            stage: The current stage
            variable_paths: The list of full variable paths
            self_refresh: ignored
            metadata: pass-through metadata for model
            node_prim_path: The path of the compute node
        """
        self._stage = stage
        self._prim_paths = prim_paths
        super().__init__(stage, variable_paths, self_refresh, metadata)

    def _get_allowed_tokens(self, _):
        if sum(self._stage.GetPrimAtPath(x).IsA(AnimGraphSchema.ConditionSpeed) for x in self._prim_paths) == len(self._prim_paths):
            return ["<=", ">"]

        variable_name = None
        prim = self._stage.GetPrimAtPath(self._prim_paths[0])
        if prim:
            variable_attr = prim.GetAttribute(VARIABLE_NAME)
            if variable_attr:
                variable_name = variable_attr.Get()

        graph_prim = find_anim_graph_parent(prim)
        if graph_prim and variable_name:
            variable = graph_prim.GetAttribute(VARIABLE_PREFIX + variable_name)
            if variable:
                var_type = variable.GetTypeName()
                if var_type == Sdf.ValueTypeNames.String or var_type == Sdf.ValueTypeNames.Bool:
                    return ["==", "!="]
                elif var_type == Sdf.ValueTypeNames.Int or var_type == Sdf.ValueTypeNames.Float:
                    return ["==", "!=", "<", "<=", ">", ">="]

        return ["==", "!="]

    def _update_value(self, force=False):
        # override of TfTokenAttributeModel to refresh the allowed token cache
        self._update_allowed_token()
        super()._update_value(force)

    def _item_factory(self, item):
        # construct the item for the model
        label = item
        return CompareVariableOperationModel.AllowedTokenItem(item, label)

    def _update_allowed_token(self):
        # override of TfTokenAttributeModel to specialize the model items
        super()._update_allowed_token(token_item=self._item_factory)


class CompareVariableNameWidget:
    def __init__(self, stage, attr_name, prim_paths, metadata, additional_widget_kwargs):
        self._graph_prim = find_anim_graph_prim(stage, prim_paths)

        self._model = CompareVariableNameModel(
            stage, [path.AppendProperty(attr_name) for path in prim_paths], True, metadata, self._graph_prim.GetPath()
        )

        def changed_fn(model, item):
            variable_type = None
            prim = stage.GetPrimAtPath(prim_paths[0])
            variable_attr = prim.GetAttribute(VARIABLE_NAME)
            if variable_attr:
                variable_name = variable_attr.Get()
                graph_prim = find_anim_graph_parent(prim)
                if graph_prim and variable_name:
                    variable = graph_prim.GetAttribute(VARIABLE_PREFIX + variable_name)
                    if variable:
                        variable_type = variable.GetTypeName()

            if variable_type:
                prim.RemoveProperty(VARIABLE_VALUE)
                prim.CreateAttribute(VARIABLE_VALUE, variable_type, True, Sdf.VariabilityUniform)

            refresh_property_window()

        self._model.add_item_changed_fn(changed_fn)

        self._prim_paths = prim_paths

        self._combo_box = None

        self._frame = ui.Frame()
        self._frame.set_build_fn(self._build)

    def clean(self):
        self._model.clean()
        self._frame = None
        self._graph_prim = None
        self._combo_box = None

    def _build(self):
        self._combo_box = ui.ComboBox(self._model)

    def _set_dirty(self):
        self._frame.rebuild()


class CompareOperationWidget:
    def __init__(self, stage, attr_name, prim_paths, metadata, additional_widget_kwargs):
        self._model = CompareVariableOperationModel(
            stage, prim_paths, [path.AppendProperty(attr_name) for path in prim_paths], True, metadata
        )

        self._combo_box = None

        self._frame = ui.Frame()
        self._frame.set_build_fn(self._build)

    def clean(self):
        self._model.clean()
        self._frame = None
        self._combo_box = None

    def _build(self):
        self._combo_box = ui.ComboBox(self._model)

    def _set_dirty(self):
        self._frame.rebuild()


from omni.kit.window.property.templates import (
    HORIZONTAL_SPACING,
    LABEL_WIDTH,
)


def build_compare_variable_name_prop(
    stage,
    attr_name,
    metadata,
    property_type,
    prim_paths: List[Sdf.Path],
    additional_label_kwargs=None,
    additional_widget_kwargs=None,
):
    with ui.HStack(spacing=HORIZONTAL_SPACING):
        with ui.VStack(width=LABEL_WIDTH):
            UsdPropertiesWidgetBuilder._create_label(attr_name, metadata, additional_label_kwargs)
        ui.Spacer(width=5)
        return CompareVariableNameWidget(stage, attr_name, prim_paths, metadata, additional_widget_kwargs)


def build_compare_operation_prop(
    stage,
    attr_name,
    metadata,
    property_type,
    prim_paths: List[Sdf.Path],
    additional_label_kwargs=None,
    additional_widget_kwargs=None,
):
    with ui.HStack(spacing=HORIZONTAL_SPACING):
        with ui.VStack(width=LABEL_WIDTH):
            UsdPropertiesWidgetBuilder._create_label(attr_name, metadata, additional_label_kwargs)
        ui.Spacer(width=5)
        return CompareOperationWidget(stage, attr_name, prim_paths, metadata, additional_widget_kwargs)
