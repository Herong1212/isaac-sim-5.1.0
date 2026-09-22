from typing import List

import omni.graph.core as og
import omni.ui as ui
from omni.kit.property.usd import AllowedTokenItem as BaseAllowedTokenItem
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_model import TfTokenAttributeModel
from omni.kit.window.property.templates import HORIZONTAL_SPACING, LABEL_WIDTH
from pxr import Sdf, Usd

ATTRIB_LABEL_STYLE = {"alignment": ui.Alignment.RIGHT_TOP}
GRAPH_VARIABLE_PREFIX = "graph:variable:"


def is_usable(type_name: Sdf.ValueTypeName) -> bool:
    # returns if the given type can be used by OG
    return og.AttributeType.type_from_sdf_type_name(str(type_name)).base_type != og.BaseDataType.UNKNOWN


def get_filtered_variables(prim: Usd.Prim) -> List[str]:
    # return only the USD attributes that start with the graph variable attribute prefix
    return [
        attr.GetName()[len(GRAPH_VARIABLE_PREFIX) :]
        for attr in prim.GetAttributes()
        if not attr.IsHidden() and is_usable(attr.GetTypeName()) and attr.GetName().startswith(GRAPH_VARIABLE_PREFIX)
    ]


class VariableNameListModel(TfTokenAttributeModel):
    """Model for selecting the target attribute for OnVariableChange. We modify the list to show attributes
    which are available on the target prim.
    """

    class AllowedTokenItem(BaseAllowedTokenItem):
        def __init__(self, item, label):
            """
            Args:
                item: the attribute name token to be shown
                label: the label to show in the drop-down
            """
            super().__init__(item)
            self.token = item
            self.model = ui.SimpleStringModel(label)

    def __init__(
        self,
        stage: Usd.Stage,
        variable_paths: List[Sdf.Path],
        self_refresh: bool,
        metadata: dict,
        node_prim_path: Sdf.Path,
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
        self._node_prim_path = node_prim_path
        self._target_graph = None
        self._target_prim = None
        super().__init__(stage, variable_paths, self_refresh, metadata)

    def _get_allowed_tokens(self, _):
        # override of TfTokenAttributeModel to specialize what tokens to be shown
        return self._get_variables_of_interest()

    def _update_value(self, force=False):
        # override of TfTokenAttributeModel to refresh the allowed token cache
        self._update_allowed_token()
        super()._update_value(force)

    def _item_factory(self, item):
        # construct the item for the model
        label = item
        return VariableNameListModel.AllowedTokenItem(item, label)

    def _update_allowed_token(self):
        # override of TfTokenAttributeModel to specialize the model items
        super()._update_allowed_token(token_item=self._item_factory)

    def _get_variables_of_interest(self) -> List[str]:
        # returns the attributes we want to let the user select from
        prim = self._stage.GetPrimAtPath(self._node_prim_path)
        variables = []

        target_prim = prim.GetParent()
        if target_prim:
            variables = get_filtered_variables(target_prim)
        self._target_prim = target_prim
        var_name_attr = prim.GetAttribute("inputs:variableName")
        if len(variables) > 0:
            current_value = var_name_attr.Get()
            if (current_value is not None) and (current_value != "") and (current_value not in variables):
                variables.append(current_value)
            variables.insert(0, "")
        else:
            var_name_attr.Set("")
        return variables


class CustomLayout:
    def __init__(self, compute_node_widget):
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.graph_rel_widget = None
        self.variables = []
        self.variable_name_model = None

    def _variable_name_build_fn(self, *args) -> ui.AbstractValueModel:
        # build the variableName widget
        stage = self.compute_node_widget.stage
        node_prim_path = self.compute_node_widget.payload[-1]
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            ui.Label("Variable Name", name="label", style=ATTRIB_LABEL_STYLE, width=LABEL_WIDTH)
            ui.Spacer(width=HORIZONTAL_SPACING)
            with ui.ZStack():
                attr_path = node_prim_path.AppendProperty("inputs:variableName")
                self.variable_name_model = VariableNameListModel(stage, [attr_path], False, {}, node_prim_path)
                ui.ComboBox(self.variable_name_model)
        return self.variable_name_model

    def apply(self, props):
        # called by compute_node_widget to apply UI when selection changes
        def find_prop(name):
            try:
                return next((p for p in props if p.prop_name == name))
            except StopIteration:
                return None

        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = find_prop("inputs:onlyPlayback")
                if prop is not None:
                    CustomLayoutProperty(prop.prop_name, display_name="Only Simulate On Play")
                CustomLayoutProperty(None, None, build_fn=self._variable_name_build_fn)

        return frame.apply(props)
