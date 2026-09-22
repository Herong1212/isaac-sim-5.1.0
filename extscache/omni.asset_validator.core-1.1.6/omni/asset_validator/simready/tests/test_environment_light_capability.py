# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = ["EnvironmentLightCapabilityTests"]

from omni.asset_validator.simready import EnvironmentLightCapabilityChecker
from pxr import Sdf

from .simready_common import AsyncValidationRuleTestCase, IsAFailure, IsAWarning, get_url


class EnvironmentLightCapabilityTests(AsyncValidationRuleTestCase):
    async def test_env_light_success(self):
        await self.assertRuleAsync(
            asset=get_url("environment_light/env_light_success.usda"),
            rule=EnvironmentLightCapabilityChecker,
            asserts=[],
        )

    async def test_env_light_no_signal_order(self):
        await self.assertRuleAsync(
            asset=get_url("environment_light/env_light_no_lights.usda"),
            rule=EnvironmentLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid environment light: no light bulbs found.",
                    f"Stage <{get_url('environment_light/env_light_no_lights.usda')}>",
                ),
            ],
        )

    async def test_env_light_incorrect_behaviors_attributes(self):
        await self.assertRuleAsync(
            asset=get_url("environment_light/env_light_incorrect_behaviors_attributes.usda"),
            rule=EnvironmentLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Attribute has invalid type token. Expected: token[]",
                    at=Sdf.Path("/RootNode/behaviors_attr_not_array_type/disk_light.omni:simready:behaviors"),
                ),
                IsAFailure(
                    "Attribute cannot be time varying.",
                    at=Sdf.Path("/RootNode/behaviors_attr_time_varying/disk_light.omni:simready:behaviors"),
                ),
                IsAWarning(
                    "Attribute 'omni:simready:behaviors' not expected on prim of type Scope. Only prims of type UsdLux or Meshes with default or render purpose are expected to have this attribute.",
                    at="Prim </RootNode/behaviors_attr_on_scope>",
                ),
                IsAFailure(
                    "Invalid attribute value: '[unexpected value]'. Expected: ['TimeOfDay']",
                    at=Sdf.Path("/RootNode/behaviors_attr_unexpected_value/mesh_light_bulb.omni:simready:behaviors"),
                ),
                IsAFailure(
                    "Invalid environment light: no light bulbs found.",
                    f"Stage <{get_url('environment_light/env_light_incorrect_behaviors_attributes.usda')}>",
                ),
            ],
        )

    async def test_env_light_incorrect_material_on_mesh(self):
        await self.assertRuleAsync(
            asset=get_url("environment_light/env_light_incorrect_material_on_mesh.usda"),
            rule=EnvironmentLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid environment light: no materials found on mesh used as light.",
                    at=Sdf.Path("/RootNode/env_light_no_mtl_binding/mesh_light_bulb"),
                ),
                IsAFailure(
                    "Invalid environment light: material bound to mesh used as light must use one of the supported shaders ['OmniGlass.mdl', 'OmniPBR.mdl', 'SimPBR.mdl', 'SimPBR_Translucent.mdl'].",
                    at=Sdf.Path("/RootNode/env_light_ups_mtl/materials/emission"),
                ),
                IsAFailure(
                    "Invalid environment light: material bound to mesh mesh used as light does not have emissiveness turned on.",
                    at=Sdf.Path("/RootNode/env_light_emission_off/materials/emission"),
                ),
                IsAFailure(
                    "Mesh with attribute 'omni:simready:behaviors' must have render purpose 'default' or 'render'. The mesh will be ignored.",
                    at=Sdf.Path("/RootNode/behaviors_attr_on_guide_mesh"),
                ),
                IsAFailure(
                    "Invalid environment light: no light bulbs found.",
                    at=f"Stage <{get_url('environment_light/env_light_incorrect_material_on_mesh.usda')}>",
                ),
            ],
        )
