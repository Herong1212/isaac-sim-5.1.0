# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
from omni.kit.property.usd.placeholder_attribute import PlaceholderAttribute
from pxr import UsdShade

from .utils import get_sdr_shader_node_for_prim, get_sdr_shader_property_default_value


class UsdShadeInputPlaceholderAttribute(PlaceholderAttribute):
    def Get(self, time_code=0):  # noqa: N802
        """
        Override to get the default value of the property this class acts as a stand in for from the default value metadata.
        """

        sdr_shader_node = get_sdr_shader_node_for_prim(self._prim)
        if not sdr_shader_node:  # pragma: no cover
            carb.log_error(f"Cannot get Sdr.ShaderNode for prim at: '{self._prim.GetPath()}'")
            return None

        input_name = self._name.replace(UsdShade.Tokens.inputs, "")
        sdr_shader_property = sdr_shader_node.GetInput(input_name)
        if not sdr_shader_property:  # pragma: no cover
            carb.log_error(f"Cannot get Sdr.ShaderProperty input: '{input_name}' for prim at: '{self._prim.GetPath()}'")
            return None

        return get_sdr_shader_property_default_value(sdr_shader_property, self._metadata)
