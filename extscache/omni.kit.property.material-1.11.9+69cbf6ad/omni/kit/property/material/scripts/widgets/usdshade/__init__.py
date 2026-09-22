# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides widgets for USD shade properties, including attribute, material, node graph, and shader widgets, along with utility functions."""


from .attribute_widget import UsdShadeAttributeWidget
from .material_widget import UsdShadeMaterialWidget
from .nodegraph_widget import UsdShadeNodeGraphWidget
from .shader_widget import UsdShadeShaderWidget
from .utils import get_sdr_shader_node_for_prim, property_name_to_display_name, remove_properties_and_connections
