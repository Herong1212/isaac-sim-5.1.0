# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = ["TrafficLightCapabilityTests"]

from omni.asset_validator.simready import TrafficLightCapabilityChecker
from pxr import Sdf

from .simready_common import AsyncValidationRuleTestCase, IsAFailure, IsAWarning, get_url


class TrafficLightCapabilityTests(AsyncValidationRuleTestCase):
    async def test_traffic_light_success(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_success.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[],
        )

    async def test_traffic_light_signals_missing(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_signals_missing.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid traffic light: no signals under directional box /RootNode.",
                    at=Sdf.Path("/RootNode"),
                ),
            ],
        )

    async def test_traffic_light_signals_extra(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_signals_extra.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid signal attribute value: 'amber'. Expected one of: [green]",
                    at=Sdf.Path("/RootNode/signal_amber/mesh_light_bulb.omni:simready:signal"),
                ),
            ],
        )

    async def test_traffic_light_signal_type_missing(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_signal_type_missing.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid traffic light: no directional boxes found.",
                    at=f"Stage <{get_url('traffic_light/traffic_light_signal_type_missing.usda')}>",
                ),
            ],
        )

    async def test_traffic_light_incorrect_signal_type_value(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_incorrect_signal_type_value.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Attribute 'omni:simready:signalType' has invalid value 'incorrect value'.Expected: 'trafficLight'.",
                    at=Sdf.Path("/RootNode.omni:simready:signalType"),
                ),
                IsAFailure(
                    "Invalid traffic light: no directional boxes found.",
                    at=f"Stage <{get_url('traffic_light/traffic_light_incorrect_signal_type_value.usda')}>",
                ),
            ],
        )

    async def test_traffic_light_incorrect_signal_type_type(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_incorrect_signal_type_type.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Attribute 'omni:simready:signalType' has invalid type string. Expected: token",
                    at=Sdf.Path("/RootNode.omni:simready:signalType"),
                ),
                IsAFailure(
                    "Invalid traffic light: no directional boxes found.",
                    at=f"Stage <{get_url('traffic_light/traffic_light_incorrect_signal_type_type.usda')}>",
                ),
            ],
        )

    async def test_traffic_light_incorrect_signal_order_values(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_incorrect_signal_order_values.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid signal order value: 'unknown'. Expected one of: ['amber', 'amber_turn', 'count', 'green', 'green_turn', 'red', 'red_turn', 'walk_green', 'walk_red']",
                    at=Sdf.Path("/RootNode.omni:simready:signalOrder"),
                ),
                IsAFailure(
                    "Invalid signal attribute value: 'unknown'. Expected one of: ['red', 'amber']",
                    at=Sdf.Path("/RootNode/signal_unknown.omni:simready:signal"),
                ),
                IsAFailure(
                    "Invalid traffic light: no signals under directional box /RootNode.",
                    at=Sdf.Path("/RootNode"),
                ),
            ],
        )

    async def test_traffic_light_incorrect_signal_order_type(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_incorrect_signal_order_type.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Attribute 'omni:simready:signalOrder' has invalid type string[]. Expected: token[]",
                    at=Sdf.Path("/RootNode.omni:simready:signalOrder"),
                ),
            ],
        )

    async def test_traffic_light_incorrect_signal_attributes(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_incorrect_signal_attributes.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Attribute has invalid type string. Expected: token",
                    at=Sdf.Path("/RootNode/signal_attr_string.omni:simready:signal"),
                ),
                IsAFailure(
                    "Attribute cannot be time varying.",
                    at=Sdf.Path("/RootNode/signal_attr_time_varying.omni:simready:signal"),
                ),
                IsAWarning(
                    "Attribute 'omni:simready:signal' not expected on prim of type Xform. Only prims of type UsdLux or Meshes with default or render purpose are expected to have a signal attribute.",
                    at=Sdf.Path("/RootNode/signal_attr_on_scope"),
                ),
                IsAFailure(
                    "Invalid signal attribute value: 'unsupported color'. Expected one of: ['amber', 'amber_turn', 'count', 'green', 'green_turn', 'red', 'red_turn', 'walk_green', 'walk_red']",
                    at=Sdf.Path("/RootNode/signal_attr_unsupported_value/mesh_light_bulb.omni:simready:signal"),
                ),
                IsAFailure(
                    "Invalid traffic light: no signals under directional box /RootNode.",
                    at=Sdf.Path("/RootNode"),
                ),
            ],
        )

    async def test_traffic_light_incorrect_material_on_mesh(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_incorrect_material_on_mesh.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid traffic light: no materials found on signal mesh.",
                    at=Sdf.Path("/RootNode/signal_no_mtl_binding/mesh_light_bulb"),
                ),
                IsAFailure(
                    "Invalid traffic light: material bound to a signal mesh must use one of the supported shaders ['OmniGlass.mdl', 'OmniPBR.mdl', 'SimPBR.mdl', 'SimPBR_Translucent.mdl'].",
                    at=Sdf.Path("/RootNode/signal_ups_mtl/materials/emission"),
                ),
                IsAFailure(
                    "Invalid traffic light: material bound to a signal mesh does not have emissiveness turned on.",
                    at=Sdf.Path("/RootNode/signal_emission_off/materials/emission"),
                ),
                IsAFailure(
                    "Mesh with attribute 'omni:simready:signal' must have render purpose 'default' or 'render'. The mesh will be ignored.",
                    at=Sdf.Path("/RootNode/signal_attr_on_guide_mesh"),
                ),
                IsAFailure(
                    "Invalid traffic light: no signals under directional box /RootNode.",
                    at=Sdf.Path("/RootNode"),
                ),
            ],
        )

    async def test_traffic_light_duplicate_signal_order(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_duplicate_signal_order.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Attribute 'omni:simready:signalOrder' has duplicate values.",
                    at=Sdf.Path("/RootNode.omni:simready:signalOrder"),
                ),
                IsAWarning(
                    "Invalid traffic light: item 'amber' in 'omni:simready:signalOrder' has no corresponding signal prims.",
                    at=Sdf.Path("/RootNode.omni:simready:signalOrder"),
                ),
            ],
        )

    async def test_traffic_light_incorrect_domain_intensiy_value(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_incorrect_domain_intensiy_value.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Attribute has invalid values. Expected the first value to be less than the second value.",
                    at=Sdf.Path("/RootNode.omni:simready:signal:domainIntensity"),
                ),
            ],
        )

    async def test_traffic_light_incorrect_domain_intensiy_type(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_incorrect_domain_intensiy_type.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Attribute has invalid type int2. Expected: float2",
                    at=Sdf.Path("/RootNode.omni:simready:signal:domainIntensity"),
                ),
            ],
        )

    async def test_traffic_light_incorrect_domain_intensiy_time_varying(self):
        await self.assertRuleAsync(
            asset=get_url("traffic_light/traffic_light_incorrect_domain_intensiy_time_varying.usda"),
            rule=TrafficLightCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Attribute cannot be time varying.",
                    at=Sdf.Path("/RootNode.omni:simready:signal:domainIntensity"),
                ),
            ],
        )
