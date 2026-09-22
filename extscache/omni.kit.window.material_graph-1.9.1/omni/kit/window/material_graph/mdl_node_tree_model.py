# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "CompoundComponentItem",
    "MdlFamilyGroupItem",
    "MdlNodeItem",
    "MdlNodeItem",
    "MdlNodeTreeDelegate",
    "MdlNodeTreeModel",
    "MdlNodeTreeQuickSearchModel",
    "MiscellaneousGroupItem",
    "MiscellaneousItem",
]

import asyncio
import json
import sys
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Any, List

import omni.ui as ui
import omni.usd
from pxr import Sdf, Sdr, Usd, UsdShade, UsdUI

from . import compound_registry
from .shader_registry import ShaderRegistry

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("icons")
FAMILY_TO_ICON = {
    "Materials": "Materials_category_dark.png",
    "Materials, modifiers": "Materials_category_dark.png",
    "Texturing, high level": "Texture_category_dark.png",
    "Texturing, basic": "Texture_category_dark.png",
    "Math functions": "Math_category_dark.png",
    "Constants, State and Primvars": "State_Data_category_dark.png",
    "Constructors, conversions and swizzles": "Conversions_category_dark.png",
}


class MdlBaseItem(ui.AbstractItem):
    """Base item for for all items in the model"""

    def __init__(self, item_name: str, item_info: str, item_icon: str, item_tooptip: str):
        super().__init__()

        self.name_model = ui.SimpleStringModel(item_name)

        info = item_info
        if not item_info:
            info = item_name

        self.info_model = ui.SimpleStringModel(info)

        self.icon_model = ui.SimpleStringModel(item_icon)

        self.tooltip_model = ui.SimpleStringModel(item_tooptip)

        self.filtered = True


class MdlGroupItem(MdlBaseItem):
    """Base item for for all group items in the model"""

    def __init__(self, item_name: str):
        super().__init__(item_name, "", "", "")


class MdlNodeItem(MdlBaseItem):
    """Base item for for all node items in the model"""

    def __init__(
        self,
        item_name: str,
        item_info: str,
        item_icon: str,
        item_tooptip: str,
        prim_type,
        source_asset: str,
        sub_identifier: str,
    ):
        super().__init__(item_name, item_info, item_icon, item_tooptip)

        self.prim_type = prim_type
        self.source_asset = source_asset
        self.sub_identifier = sub_identifier


class SdrNodeItem(MdlBaseItem):
    """Base item for for all node items in the model"""

    def __init__(self, sdr_node):
        self.identifier = sdr_node.GetIdentifier()
        self.name = self.identifier
        self.family = "UsdPreviewSurface"
        self.tags = []
        self.ui_order = None
        self.prim_type = "Shader"

        thumbnail = ICON_PATH.joinpath("mdl-thumbnails/Custom_user_category_dark.png")
        tooltip = ""
        super().__init__(self.identifier, f"{sdr_node.GetFamily()}", f"{thumbnail}", tooltip)


class MdlShaderNodeItem(MdlNodeItem):
    """Shader node item of the model"""

    def __init__(self, node):
        self.name = node.name
        self.family = node.category
        self.tags = node.tags
        self.ui_order = node.uiOrder

        thumbnail = node.thumbnail
        if thumbnail is not None:
            thumbnail = Path(thumbnail)
            if not thumbnail.is_absolute():
                thumbnail = ICON_PATH.joinpath("mdl-thumbnails").joinpath(thumbnail)
        else:
            source_asset_name = Path(node.sourceAsset).stem
            thumbnail = ICON_PATH.joinpath(f"mdl-thumbnails/{source_asset_name}.{node.name}.png")
            if not thumbnail.exists():
                family_icon = FAMILY_TO_ICON.get(self.family, None)
                if family_icon:
                    thumbnail = ICON_PATH.joinpath(f"mdl-thumbnails/{family_icon}")
                else:
                    thumbnail = ICON_PATH.joinpath("mdl-thumbnails/Custom_user_category_dark.png")

        if node.sourceAsset.lower().endswith(".usd") or node.sourceAsset.lower().endswith(".usda"):
            prim_type = "ImportCompound"

        else:
            prim_type = "Shader"

        tooltip = node.description
        super().__init__(
            node.displayName, node.description, f"{thumbnail}", tooltip, prim_type, node.sourceAsset, node.subIdentifier
        )

    def __repr__(self):
        return f'"{self.name_model.as_string}"'


class SdrFamilyGroupItem(MdlGroupItem):
    """Family item of the model"""

    def __init__(self, family: str, sdr_nodes: List):
        super().__init__(family)

        self.children = [SdrNodeItem(sdr_node) for sdr_node in sdr_nodes]

        # sort by sub_identifier and then by ui order
        self.children = sorted(self.children, key=lambda a: a.identifier)
        self.children = sorted(self.children, key=lambda a: a.ui_order if a.ui_order is not None else sys.maxsize)

        # Group UI order
        self.ui_order = [c.ui_order for c in self.children if isinstance(c.ui_order, int)]
        self.ui_order = min(self.ui_order) if self.ui_order else None

    def prefilter(self, filter_name_text: str):
        """
        Filter the children and display the ones that have the given pattern
        in the identifier.
        """
        group_visible = False
        for c in self.children:
            if not filter_name_text:
                c.filtered = True
            else:
                # Check the name
                filter_passed = filter_name_text in c.name.lower()
                # Check the display name
                filter_passed = filter_passed or filter_name_text in c.name_model.as_string.lower()
                # Check tags
                if not filter_passed and c.tags:
                    for tag in c.tags:
                        if filter_name_text in tag:
                            filter_passed = True
                            break

                c.filtered = filter_passed

            group_visible |= c.filtered

        self.filtered = group_visible

    def int_type_filter(self, filter_type: str):
        group_visible = True
        for c in self.children:

            # TODO: Victor you need to discuss best approach
            # Here we will need to get the list of input from the nodes and see if we match
            # we need to collect them into the item ( as currently they are generated dynamically by mdl)
            c.filtered = True
            group_visible |= c.filtered

        self.filtered = group_visible


class MdlFamilyGroupItem(MdlGroupItem):
    """Family item of the model"""

    def __init__(self, family: str, shader_nodes: List):
        super().__init__(family)

        self.children = [MdlShaderNodeItem(node) for node in shader_nodes]

        # sort by sub_identifier and then by ui order
        self.children = sorted(self.children, key=lambda a: a.sub_identifier)
        self.children = sorted(self.children, key=lambda a: a.ui_order if a.ui_order is not None else sys.maxsize)

        # Group UI order
        if family == "Advanced":
            # Put Advanced to the back
            self.ui_order = sys.maxsize
        else:
            self.ui_order = [c.ui_order for c in self.children if isinstance(c.ui_order, int)]
            self.ui_order = min(self.ui_order) if self.ui_order else None

    def prefilter(self, filter_name_text: str):
        """
        Filter the children and display the ones that have the given pattern
        in the identifier.
        """
        group_visible = False
        for c in self.children:
            if not filter_name_text:
                c.filtered = True
            else:
                # Check the name
                filter_passed = filter_name_text in c.name.lower()
                # Check the display name
                filter_passed = filter_passed or filter_name_text in c.name_model.as_string.lower()
                # Check tags
                if not filter_passed and c.tags:
                    for tag in c.tags:
                        if filter_name_text in tag:
                            filter_passed = True
                            break

                c.filtered = filter_passed

            group_visible |= c.filtered

        self.filtered = group_visible

    def int_type_filter(self, filter_type: str):
        group_visible = True
        for c in self.children:

            # TODO: Victor you need to discuss best approach
            # Here we will need to get the list of input from the nodes and see if we match
            # we need to collect them into the item ( as currently they are generated dynamically by mdl)
            c.filtered = True
            group_visible |= c.filtered

        self.filtered = group_visible


class MiscellaneousItem(MdlNodeItem):
    def __init__(self, prim_type: str, info: str):
        thumbnail = ICON_PATH.joinpath(f"mdl-thumbnails/{prim_type}.svg")
        tooltip = info
        super().__init__(prim_type, info, f"{thumbnail}", tooltip, prim_type, None, None)


class CompoundComponentItem(MdlNodeItem):
    def __init__(self, name: str, prim_type: str, info: str):
        thumbnail = ICON_PATH.joinpath(f"mdl-thumbnails/{prim_type}.svg")
        tooltip = info
        super().__init__(name, info, f"{thumbnail}", tooltip, "CompoundComponent", None, prim_type)


class MiscellaneousGroupItem(MdlGroupItem):
    """Has backdrop, compound, etc.."""

    def __init__(self):
        super().__init__("Miscellaneous")

        self.children = []
        self.children.append(MiscellaneousItem("Backdrop", "Provides a 'group-box' for node graph organization."))
        self.children.append(MiscellaneousItem("NodeGraph", "Container to encapsulate shading networks."))
        # TODO: use constants
        self.children.append(
            CompoundComponentItem("Input Node", "InputNode", "Provides access to the inputs of the current container.")
        )
        self.children.append(
            CompoundComponentItem(
                "Output Node", "OutputNode", "Provides access to the outputs of the current container."
            )
        )
        self.children.append(CompoundComponentItem("Material", "OutputNode", "Creates an empty material."))

    def prefilter(self, filter_name_text: str):
        """
        Filter the children and display the ones that have the given pattern
        in the identifier.
        """
        group_visible = False
        for c in self.children:
            if not filter_name_text:
                c.filtered = True
            else:
                c.filtered = filter_name_text in c.name_model.as_string.lower()

            group_visible |= c.filtered

        self.filtered = group_visible

    def int_type_filter(self, filter_type: str):
        group_visible = True
        for c in self.children:

            # TODO Victor you need to discuss best approach
            # Here we will need to get the list of input from the nodes and see if we match
            # we need to collect them into the item ( as currently they are generated dynamically by mdl)
            c.filtered = True
            group_visible |= c.filtered

        self.filtered = group_visible


class MdlNodeTreeModel(ui.AbstractItemModel):
    """Model that has all the shaders it's possible to create."""

    class Column(Enum):
        NAME = 0
        INFO = 1
        ICON = 2
        TOOLTIP = 3

    def __init__(self, *args):
        super().__init__()
        self._children = []
        self.clear()
        ShaderRegistry().Get("mdl").register_reload_callback(self.refresh)

    def __del__(self):
        ShaderRegistry().Get("mdl").deregister_reload_callback(self.refresh)

    def destroy(self):
        pass

    def reload(self):
        self.clear()
        asyncio.ensure_future(ShaderRegistry().Get("mdl").reload())

    def clear(self):
        self._children = []
        self._item_changed(None)

    def refresh(self, nodes=[]):
        self._children = []

        nodes = ShaderRegistry().Get("mdl").nodes
        nodes += compound_registry.nodes()
        sdr_nodes = self.getNodesFromSdr()

        if nodes or sdr_nodes:
            families = defaultdict(list)
            for node in nodes:
                families[node.category].append(node)

            self._children = [MdlFamilyGroupItem(family, families[family]) for family in sorted(families.keys())]

            if sdr_nodes:
                self._children += [SdrFamilyGroupItem("UsdPreviewSurface", sdr_nodes)]

            self._children = sorted(self._children, key=lambda a: a.ui_order if a.ui_order is not None else sys.maxsize)
            self._children.append(MiscellaneousGroupItem())

        self._item_changed(None)

    def getNodesFromSdr(self):
        nodes = []
        sdr = Sdr.Registry()

        for sdr_node_name in sdr.GetNodeNames():
            sdr_node = sdr.GetShaderNodeByNameAndType(sdr_node_name, "mdl")
            if not sdr_node or not sdr_node.GetResolvedImplementationURI().endswith("UsdPreviewSurface.mdl"):
                continue

            nodes.append(sdr_node)

        return nodes

    def get_item_children(self, item):
        """Returns all the children when the widget asks it."""
        if item is None:
            return [c for c in self._children if c.filtered]

        if isinstance(item, MdlGroupItem):
            return [c for c in item.children if c.filtered]

        return []

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 1

    def get_item_value_model(self, item, column_id):
        """
        Return value model.
        It's the object that tracks the specific value.
        In our case we use ui.SimpleStringModel for the first column
        and SimpleFloatModel for the second column.
        """
        if column_id == self.Column.NAME.value:
            return item.name_model
        if column_id == self.Column.INFO.value:
            return item.info_model
        if column_id == self.Column.ICON.value:
            return item.icon_model
        if column_id == self.Column.TOOLTIP.value:
            return item.tooltip_model

    def get_drag_mime_data(self, item):
        """Returns data for be able to drop this item somewhere"""
        if not (isinstance(item, MdlNodeItem) or isinstance(item, SdrNodeItem)):
            return None

        if isinstance(item, MdlNodeItem):
            # The data to drag
            data = {
                "prim_type": item.prim_type,
                "source_asset": item.source_asset,
                "sub_identifier": item.sub_identifier,
            }
        else:
            data = {
                "prim_type": item.prim_type,
                "source_asset": "SDR",
                "sub_identifier": item.identifier,
            }

        return json.dumps(data)

    def filter_by_text(self, filter_name_text: str):
        """Specify the filter string that is used to reduce the model"""
        for c in self._children:
            c.prefilter(filter_name_text.lower())
        self._item_changed(None)


class MdlNodeTreeQuickSearchModel(MdlNodeTreeModel):
    """
    The MDL Node model that returns children when the MDL Material Graph window
    is active.
    """

    def __init__(self, *args):
        super().__init__(*args)

        # The assumption here is that the MDLRegistery has already been populated, which
        # is a reasonable one to make considering that we wouldn't be initializing this model
        # unless the Material Graph has already been opened.
        self.refresh()

    def filter_by_text(self, filter_name_text: str):
        """Specify the filter string that is used to reduce the model"""

        # Create a new node in selection
        usd_context = omni.usd.get_context()
        if not usd_context:
            return

        selection = usd_context.get_selection()
        if not selection:
            return

        paths = selection.get_selected_prim_paths()
        if not paths or True:  # This is turned off until we fixed the inputs detection
            for c in self._children:
                c.prefilter(filter_name_text.lower())
        else:
            selection = Sdf.Path(paths[0])
            prim = usd_context.get_stage().GetPrimAtPath(selection)

            if isinstance(prim, Usd.Prim) and prim and prim.IsA(UsdShade.Shader) or prim.IsA(UsdShade.NodeGraph):
                # filer based on output
                # print(prim)
                conn = UsdShade.ConnectableAPI(prim)
                all_output_attributes = [c.GetAttr() for c in conn.GetOutputs()]
                for attr in all_output_attributes:
                    current_type = attr.GetTypeName()
                    for c in self._children:
                        c.int_type_filter(current_type)
            else:
                return []

        self._item_changed(None)

    def execute(self, item: Any):
        """The user pressed enter"""
        # Mime Data has the information about USD types.
        data = self.get_drag_mime_data(item)
        if not data:
            return

        from .graph_extension import GraphExtension

        GraphExtension.add_node(data)
