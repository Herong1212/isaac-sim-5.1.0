# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides widgets for manipulating USD material properties, including backdrop, material binding, and various USD shade components."""


from .backdrop_widget import UsdUIBackdropWidget
from .material_binding import MaterialBindingWidget, get_binding_from_prims
from .usdshade import (
    UsdShadeAttributeWidget,
    UsdShadeMaterialWidget,
    UsdShadeNodeGraphWidget,
    UsdShadeShaderWidget,
    remove_properties_and_connections,
)
