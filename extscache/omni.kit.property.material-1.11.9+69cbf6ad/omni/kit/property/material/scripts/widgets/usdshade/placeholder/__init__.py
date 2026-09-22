# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides functionality to retrieve UsdShadePropertyPlaceholder objects for USD prims to drive UI components."""

__all__ = ["GetPlaceholderPropertiesForPrim"]

from typing import List, Optional

import carb
from pxr import Usd, UsdShade

from .placeholder import UsdShadePropertyPlaceholder


def GetPlaceholderPropertiesForPrim(prim: Usd.Prim, args: Optional[dict] = {}) -> List[UsdShadePropertyPlaceholder]:
    """Retrieves a list of UsdShadePropertyPlaceholder objects for a given USD prim.

    This function builds placeholders used for driving the UI by examining the
    type of USD prim provided. Depending on whether the prim is a Shader, Material,
    or NodeGraph, it delegates to the corresponding builder class to construct
    the placeholders.

    Args:
        prim (Usd.Prim): The USD primitive for which to retrieve property placeholders.
        args (dict): A dictionary of arguments that are passed to the builder classes.

    Returns:
        List[:obj:`UsdShadePropertyPlaceholder`]: A list of UsdShadePropertyPlaceholder objects
        that represent the properties of the given prim within the UI.

    Raises:
        A warning is logged if the provided prim is not of type Shader, Material, or NodeGraph.
    """

    from .material_builder import MaterialPropertiesBuilder
    from .nodegraph_builder import NodeGraphPropertiesBuilder
    from .shader_builder import ShaderPropertiesBuilder

    if prim.IsA(UsdShade.Shader):
        return ShaderPropertiesBuilder(prim, args).build()

    elif prim.IsA(UsdShade.Material):
        return MaterialPropertiesBuilder(prim, args).build()

    elif prim.IsA(UsdShade.NodeGraph):
        return NodeGraphPropertiesBuilder(prim, args).build()

    carb.log_warn(f"Expected UsdShade prim at: '{prim.GetPath()}'")  # pragma: no cover
    return []  # pragma: no cover
