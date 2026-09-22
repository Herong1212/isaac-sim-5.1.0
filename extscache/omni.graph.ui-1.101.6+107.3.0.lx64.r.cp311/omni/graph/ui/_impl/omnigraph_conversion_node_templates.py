# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from functools import partial
from typing import List

import omni.graph.core as og
import omni.graph.ui as ogui
import omni.ui as ui
from omni.kit.property.usd import AllowedTokenItem as BaseAllowedTokenItem
from omni.kit.property.usd.custom_layout_helper import CustomLayoutFrame, CustomLayoutGroup, CustomLayoutProperty
from omni.kit.property.usd.usd_attribute_model import TfTokenAttributeModel
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry
from omni.kit.window.property.templates import HORIZONTAL_SPACING, LABEL_WIDTH
from pxr import Sdf, Usd

ATTRIB_LABEL_STYLE = {"alignment": ui.Alignment.RIGHT_TOP}
ATTRIBUTE_ROLES = {
    og.BaseDataType.DOUBLE: {
        1: ["None", "Timecode"],
        2: ["None", "TexCoord"],
        3: ["None", "Color", "Normal", "Point", "TexCoord", "Vector"],
        4: ["None", "Color", "Matrix", "Quaternion"],
        9: ["None", "Matrix"],
        16: ["None", "Matrix", "Frame"],
    },
    og.BaseDataType.FLOAT: {
        1: ["None"],
        2: ["None", "TexCoord"],
        3: ["None", "Color", "Normal", "Point", "TexCoord", "Vector"],
        4: ["None", "Color", "Quaternion"],
    },
    og.BaseDataType.HALF: {
        1: ["None"],
        2: ["None", "TexCoord"],
        3: ["None", "Color", "Normal", "Point", "TexCoord", "Vector"],
        4: ["None", "Color", "Quaternion"],
    },
}


class AttributeRoleListModel(TfTokenAttributeModel):
    """Model for selecting the attribute role for conversion nodes. We modify the list to show attributes
    which are available on the target prim.
    """

    class AllowedTokenItem(BaseAllowedTokenItem):
        def __init__(self, item, label):
            """
            Args:
                item: the attribute role name token to be shown
                label: the label to show in the drop-down
            """
            super().__init__(item)
            self.token = item
            self.model = ui.SimpleStringModel(label)

    def __init__(
        self,
        stage: Usd.Stage,
        attribute_paths: List[Sdf.Path],
        self_refresh: bool,
        metadata: dict,
        node_prim_path: Sdf.Path,
        output_type: og.BaseDataType,
    ):
        """
        Args:
            stage: The current stage
            attribute_paths: The list of full variable paths
            self_refresh: ignored
            metadata: pass-through metadata for model
            node_prim_path: The path of the compute node
            output_type: output type of node
        """
        self._stage = stage
        self._node_prim_path = node_prim_path
        self._output_type = output_type
        super().__init__(stage, attribute_paths, self_refresh, metadata)

    def _get_allowed_tokens(self, _):
        # override of TfTokenAttributeModel to specialize what tokens to be shown
        prim = self._stage.GetPrimAtPath(self._node_prim_path)
        if prim:
            attr = og.Controller.attribute(f"{self._node_prim_path}.inputs:value")
            attr_type = attr.get_resolved_type()
            if attr_type.base_type != og.BaseDataType.UNKNOWN:
                return ATTRIBUTE_ROLES[self._output_type][attr_type.tuple_count]
        return ["None"]

    def _update_value(self, force=False):
        # override of TfTokenAttributeModel to refresh the allowed token cache
        self._update_allowed_token()
        super()._update_value(force)

    def _item_factory(self, item):
        # construct the item for the model
        label = item
        return AttributeRoleListModel.AllowedTokenItem(item, label)

    def _update_allowed_token(self):
        # override of TfTokenAttributeModel to specialize the model items
        super()._update_allowed_token(token_item=self._item_factory)


class ConversionNodeCustomLayoutBase:
    """Base class for ToDouble/Float/Half"""

    # Set set the correspondence between the component count and the available attribute roles
    _output_type = og.BaseDataType.UNKNOWN

    def __init__(self, compute_node_widget):
        self.enable = True
        self.compute_node_widget = compute_node_widget
        self.stage = compute_node_widget.stage
        self.node_prim_path: Sdf.Path = compute_node_widget._payload[-1]
        self.role_widget = None

    def _role_build_fn(self, ui_prop: UsdPropertyUiEntry, *args):
        with ui.HStack(spacing=HORIZONTAL_SPACING):
            ui.Label("role", name="label", style=ATTRIB_LABEL_STYLE, width=LABEL_WIDTH)
            ui.Spacer(width=HORIZONTAL_SPACING)
            with ui.ZStack():
                attr_path = self.node_prim_path.AppendProperty("inputs:role")
                self.role_widget = AttributeRoleListModel(
                    self.stage, [attr_path], False, {}, self.node_prim_path, self._output_type
                )
                ui.ComboBox(self.role_widget)
        return self.role_widget

    def apply(self, props):
        frame = CustomLayoutFrame(hide_extra=True)
        with frame:
            with CustomLayoutGroup("Inputs"):
                prop = ogui.find_prop(props, "inputs:value")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "value")

                prop = ogui.find_prop(props, "inputs:role")
                if prop:
                    CustomLayoutProperty(None, None, build_fn=partial(self._role_build_fn, prop))

            with CustomLayoutGroup("Outputs"):
                prop = ogui.find_prop(props, "outputs:converted")
                if prop:
                    CustomLayoutProperty(prop.prop_name, "Double")
        return frame.apply(props)
