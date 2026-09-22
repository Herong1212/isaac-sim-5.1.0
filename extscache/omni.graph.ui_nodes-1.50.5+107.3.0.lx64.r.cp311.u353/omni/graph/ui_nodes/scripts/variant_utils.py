# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import re
from typing import Any, Optional

import omni.graph.core as og
import omni.ui as ui
from omni.kit.property.usd.usd_attribute_widget import UsdPropertyUiEntry
from usdrt import Sdf, Usd


def print_widget_tree(widget: ui.Widget, level: int = 0):
    # Prints the widget tree to the console
    for child in ui.Inspector.get_children(widget):
        print_widget_tree(child, level + 1)


def get_descendants(widget: ui.Widget):
    # Returns a list of all descendants of the given widget
    kids = []
    local_kids = ui.Inspector.get_children(widget)
    kids.extend(local_kids)
    for k in local_kids:
        child_kids = get_descendants(k)
        kids.extend(child_kids)
    return kids


def get_attr_value(prim: Usd.Prim, attr_name: str) -> Any:
    # Returns the value of the given attribute from usdrt
    if prim:
        attr = prim.GetAttribute(attr_name)
        if attr:
            return og.Controller().get(attribute=prim.GetAttribute(attr_name))
    return False


def get_use_path(stage: Usd.Stage, node_prim_path: Sdf.Path) -> bool:
    # Returns the value of the usePath input attribute
    prim = stage.GetPrimAtPath(node_prim_path)
    if prim:
        return get_attr_value(prim, "inputs:usePath")
    return False


def get_attr_has_connections(prim: Usd.Prim, attr_name: str) -> bool:
    # Returns True if the attribute has authored connections
    if prim:
        attr = prim.GetAttribute(attr_name)
        if attr:
            return attr.HasAuthoredConnections()
    return False


def get_target_prim(stage: Usd.Stage, node_prim_path: Sdf.Path) -> Optional[Usd.Prim]:
    # Return the target prim if it exists depending on the value of the usePath input attribute.
    # If usePath is True, the target prim is the prim at the path specified by the primPath input attribute.
    # If usePath is False, the target prim is the first target of the prim relationship.
    prim = stage.GetPrimAtPath(node_prim_path)
    if prim:
        if get_attr_value(prim, "inputs:usePath"):
            prim_path = get_attr_value(prim, "inputs:primPath")
            if prim_path is not None:
                return stage.GetPrimAtPath(prim_path)
        else:
            rel = prim.GetRelationship("inputs:prim")
            if rel.IsValid():
                targets = rel.GetTargets()
                if targets:
                    return stage.GetPrimAtPath(targets[0])
    return None


def pretty_name(name: str) -> str:
    # Returns a pretty name for the given property
    name = name.split(":")[-1]
    name = name[0].upper() + name[1:]
    name = re.sub(r"([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))", r"\1 ", name)
    return name


def override_display_name(prop: UsdPropertyUiEntry):
    # Overrides the display name of the given property with a consistent format
    prop_name = pretty_name(prop.prop_name)
    prop.override_display_name(prop_name)
