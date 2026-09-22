# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from dataclasses import dataclass
from typing import Any

import omni.capabilities as cap
from omni.asset_validator._impl import (
    MaterialUsdPreviewSurfaceChecker,
    get_sdf_type_for_shader_property,
    register_requirements,
)
from pxr import Sdf, Sdr, UsdShade

from ._engine import registerRule

__all__ = ["OmniMaterialUsdPreviewSurfaceChecker"]


@dataclass
class _InputValue:
    """Stores value of the underlying Usd.Attribute for a UsdShade.Input object.
    holds both static and time-sampled values.
    """

    value: Any
    time_samples: list[Any]

    @classmethod
    def create_from_input(cls, usd_shade_input: UsdShade.Input):
        """Get the value from the usd_shade_input.
        If the attr has time-sampled values store a list of tuples: [(time, value), ]
        """
        value = None
        time_samples = None

        attr = usd_shade_input.GetAttr()
        if attr and attr.HasAuthoredValue():
            value = attr.Get()

            if attr.GetNumTimeSamples():
                time_samples = []
                for sample_time in attr.GetTimeSamples():
                    time_samples.append((sample_time, attr.Get(sample_time)))

        return _InputValue(value, time_samples)


@registerRule("Omni:Material")
@register_requirements(cap.MaterialsRequirements.VM_PS_001, override=True)
class OmniMaterialUsdPreviewSurfaceChecker(MaterialUsdPreviewSurfaceChecker):
    """
    Rule ensuring that UsdShadeShader prims conform to the UsdPreviewSurface specification.
    """

    # Keep this docstring in sync with the parent class

    # inputs to skip/not process for whatever reason.
    INPUTS_TO_SKIP = [
        # Omniverse specific items to skip
        "excludeFromWhiteMode",
        "enable_opacity",
        "enable_specular_transmission",
        # other items to skip
        UsdShade.Tokens.sdrMetadata,
    ]

    def _should_input_be_filtered(self, shade_input: UsdShade.Input) -> bool:
        base_name = shade_input.GetBaseName()

        return base_name in self.INPUTS_TO_SKIP

    def _input_value_and_connections_transform(
        self, shade_input: UsdShade.Input, sdr_property: Sdr.ShaderProperty
    ) -> tuple[bool, Sdf.ValueTypeName, Any, list[UsdShade.ConnectionSourceInfo]]:
        # Nvidia Omniverse specific.
        # Older versions of our UsdPreviewSurface material networks
        # incorrectly set some parameters, whose type is float, to
        # color3f in certain circumstances, additionally it would incorrectly
        # connect them to the 'rgb' output of the UsdUVTexture node.
        base_name = shade_input.GetBaseName()
        input_value = _InputValue.create_from_input(shade_input)
        type_name = shade_input.GetTypeName()
        connections = shade_input.GetConnectedSources()
        transformed = False
        sdf_type = get_sdf_type_for_shader_property(sdr_property)

        if (
            (base_name in ["metallic", "roughness"])
            and (sdf_type == Sdf.ValueTypeNames.Float)
            and (type_name == Sdf.ValueTypeNames.Color3f)
        ):
            (input_value, connections) = self.convert_color3f_to_float(input_value, connections)
            type_name = Sdf.ValueTypeNames.Float
            transformed = True

        return transformed, type_name, input_value, connections
