# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["CompoundShadingNode", "register_compound", "nodes"]

from pathlib import Path
from typing import Dict, List, Optional

import carb
from pxr import Usd, UsdShade, UsdUI

from .shader_registry import ShaderRegistry


class CompoundShadingNode:
    def __init__(self, prim: Usd.Prim, path: str):
        schema = None

        if prim.IsA(UsdShade.NodeGraph):
            schema = UsdShade.NodeGraph(prim)

        else:
            schema = UsdShade.Shader(prim)

        self._outputs = {}

        for output in schema.GetOutputs():
            name = output.GetBaseName()
            usdType = output.GetTypeName()
            renderType = output.GetRenderType()
            self._outputs[name] = ShaderRegistry().Get("mdl").createPropertyType(renderType, usdType)

        self._sourceAsset = path
        self._subIdentifier = prim.GetPath().pathString
        self._name = prim.GetPath().name

        self._category = None
        display_group_attr = prim.GetAttribute(UsdUI.Tokens.uiDisplayGroup)
        if display_group_attr:
            self._category = display_group_attr.Get()
        if not self._category:
            self._category = "Material Graphs"

        self._description = None
        description_attr = prim.GetAttribute(UsdUI.Tokens.uiDescription)
        if description_attr:
            self._description = description_attr.Get()
        if not self._description:
            self._description = f"Compound from {Path(path).stem}"

        ui_order_attr = prim.GetAttribute("ui:order")
        if ui_order_attr:
            self._uiOrder = ui_order_attr.Get()
        else:
            self._uiOrder = None

        display_name_attr = prim.GetAttribute(UsdUI.Tokens.uiDisplayName)
        if display_name_attr:
            self._displayName = display_name_attr.Get()
        else:
            self._displayName = self._name

        self._thumbnail = None
        icon_attr = prim.GetAttribute(UsdUI.Tokens.uiNodegraphNodeIcon)
        if icon_attr:
            asset_path = icon_attr.Get()
            if asset_path:
                resolved = asset_path.resolvedPath
                if not resolved:
                    resolved = asset_path.path

                self._thumbnail = resolved

    @property
    def customData(self):
        return {}

    @property
    def colorSpace(self):
        return None

    @property
    def sdrMetaData(self):
        return {}

    @property
    def name(self):
        return self._name

    @property
    def parameters(self):
        return []

    @property
    def category(self):
        return self._category

    @property
    def description(self):
        return self._description

    @property
    def sourceAsset(self):
        return self._sourceAsset

    @property
    def subIdentifier(self):
        return self._subIdentifier

    @property
    def uiOrder(self):
        return self._uiOrder

    @property
    def tags(self):
        return None

    @property
    def outputs(self):
        return self._outputs

    @property
    def displayName(self):
        return self._displayName

    @property
    def thumbnail(self):
        return self._thumbnail


def _get_shading_nodes(path: str):
    nodes = []
    stage = Usd.Stage.Open(path)

    it = iter(Usd.PrimRange.Stage(stage, Usd.PrimIsLoaded & ~Usd.PrimIsAbstract))
    for prim in it:
        if prim.IsA(UsdShade.NodeGraph) or prim.IsA(UsdShade.Shader):
            nodes.append(CompoundShadingNode(prim, path))
            it.PruneChildren()

    if not nodes:
        carb.log_info(f"Compound Registry] File doesn't contain compound {path}")

    return nodes


_registered_nodes: Dict[str, CompoundShadingNode] = {}


class _CompoundRegistrySubscription:
    """
    Registration subscription. The registration exists while this object
    exists.
    """

    def __init__(self, path: str):
        self.__identifiers = []

        nodes = _get_shading_nodes(path)

        self.__identifiers = [node.subIdentifier for node in nodes]
        # Avoiding duplicates
        self.__identifiers = [f"@{path}@</{i}>" if i in _registered_nodes else i for i in self.__identifiers]
        for identifier, node in zip(self.__identifiers, nodes):
            _registered_nodes[identifier] = node

    def __del__(self):
        """Called by GC."""
        for identifier in self.__identifiers:
            _deregister_compound(identifier)

    @property
    def valid(self):
        return bool(self.__identifiers)


def _deregister_compound(identifier: str):
    _registered_nodes.pop(identifier, None)


def register_compound(path: str):
    """Register path that has a shader compound"""
    return _CompoundRegistrySubscription(path)


def nodes():
    """Get node by identifier"""
    return list(_registered_nodes.values())
