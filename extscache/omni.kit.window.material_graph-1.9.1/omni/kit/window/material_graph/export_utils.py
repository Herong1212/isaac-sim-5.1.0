# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["export", "Export"]

import os
from pathlib import Path
from typing import List

import carb
import carb.tokens
import omni.client
from omni.kit.widget.stage.export_utils import ExportPrimUSD
from pxr import Sdf, Usd, UsdShade, UsdUI, UsdUtils

from .mdl_node_tree_model import MdlNodeItem


def export(path: str, prim: Usd.Prim):
    """Export prim to external USD file"""
    filename = Path(path).stem

    # TODO: stage.Flatten() is extreamly slow
    source_layer = prim.GetStage().Flatten()
    target_layer = Sdf.Layer.CreateNew(path)
    source_path = prim.GetPath()
    target_path = Sdf.Path.absoluteRootPath.AppendChild(source_path.name)

    # Copy
    Sdf.CopySpec(source_layer, source_path, target_layer, target_path)

    # Set default prim name
    target_layer.defaultPrim = target_path.name

    # Edit UI info of compound
    spec = target_layer.GetPrimAtPath(target_path)
    attributes = spec.attributes

    if UsdUI.Tokens.uiDisplayGroup not in attributes:
        attr = Sdf.AttributeSpec(spec, UsdUI.Tokens.uiDisplayGroup, Sdf.ValueTypeNames.Token)
        attr.default = "Material Graphs"

    if UsdUI.Tokens.uiDisplayName not in attributes:
        attr = Sdf.AttributeSpec(spec, UsdUI.Tokens.uiDisplayName, Sdf.ValueTypeNames.Token)
        attr.default = target_path.name

    if "ui:order" not in attributes:
        attr = Sdf.AttributeSpec(spec, "ui:order", Sdf.ValueTypeNames.Int)
        attr.default = 1024

    # Save
    target_layer.Save()

    carb.log_info(f"[MDL Material Graph]: {source_path} is exported to {path}")


def copy_input_metadata(source: UsdShade.Input, target: UsdShade.Input):
    """Copy metadata from input to input"""
    source_attr = source.GetAttr()
    target_attr = target.GetAttr()

    # Copy the display name
    display_name = source_attr.GetDisplayName()
    if display_name:
        target_attr.SetDisplayName(display_name)

    # Copy the display group
    display_group = source_attr.GetDisplayGroup()
    if display_group:
        target_attr.SetDisplayGroup(display_group)

    # Copy the metadata
    metadata = source_attr.GetCustomData()
    if metadata:
        target_attr.SetCustomData(metadata)

    # Copy ColorSpace
    if source_attr.HasColorSpace():
        color_space = source_attr.GetColorSpace()
        target_attr.SetColorSpace(color_space)

    # Copy SdrMetadata
    if source.HasSdrMetadata():
        sdr_metadata = source.GetSdrMetadata()
        target.SetSdrMetadata(sdr_metadata)

    # Copy RenderType
    if source.HasRenderType():
        render_type = source.GetRenderType()
        target.SetRenderType(render_type)


class Export(ExportPrimUSD):
    def __init__(self):
        super().__init__(select_msg="Select File to Save Compound", save_msg="Save", save_dir=self.__get_compound_dir())

    def __get_compound_dir(self) -> str:
        """Return the workspace file"""
        from .graph_extension import COMPOUND_DEFAULT_PATH

        token = carb.tokens.get_tokens_interface()
        dir = token.resolve(COMPOUND_DEFAULT_PATH)
        # FilePickerDialog needs the capital drive. In case it's linux, the
        # first letter will be / and it's still OK.
        dir = dir[:1].upper() + dir[1:]

        if not Path(dir).exists():
            os.mkdir(dir)

        return dir
