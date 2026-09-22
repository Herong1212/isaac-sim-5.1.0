# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import unittest

from omni.asset_validator.simready import VehicleCapabilityChecker
from pxr import Sdf

from .simready_common import AsyncValidationRuleTestCase, IsAFailure, IsAWarning, get_url

__all__ = ["VehicleCapabilityCheckerTest"]


class VehicleCapabilityCheckerTest(AsyncValidationRuleTestCase):
    async def test_vehicle_success(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicle.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[],
        )

    async def test_vehicle_off_center(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleOffCenter.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Bounding box of the asset root prim .* is not centered at the origin. Bounding box center: .*",
                    at=Sdf.Path("/vehicle"),
                ),
            ],
        )

    async def test_vehicle_no_wheels(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleNoWheels.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[IsAFailure("No wheels found under asset prim .*.", at=Sdf.Path("/vehicle"))],
        )

    async def test_vehicle_off_ground(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleOffGround.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Bounding box of the wheel .* does not sit on the ground. Bounding box bottom: .*",
                    at=Sdf.Path("/vehicle/Xform/collections/wheel_fl"),
                ),
                IsAFailure(
                    "Bounding box of the wheel .* does not sit on the ground. Bounding box bottom: .*",
                    at=Sdf.Path("/vehicle/Xform/collections/wheel_fr"),
                ),
                IsAFailure(
                    "Bounding box of the wheel .* does not sit on the ground. Bounding box bottom: .*",
                    at=Sdf.Path("/vehicle/Xform/collections/wheel_rl"),
                ),
                IsAFailure(
                    "Bounding box of the wheel .* does not sit on the ground. Bounding box bottom: .*",
                    at=Sdf.Path("/vehicle/Xform/collections/wheel_rr"),
                ),
            ],
        )

    async def test_vehicle_wheels_not_aligned(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleRotate.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Bounding box of the asset root prim .* is not centered at the origin. Bounding box center: .*",
                    at=Sdf.Path("/vehicle"),
                ),
                IsAWarning(
                    "Only one wheel component found - .*. Skip validating vehicle axis alignment.",
                    at=Sdf.Path("/vehicle/Xform/collections/wheel_fr"),
                ),
                IsAWarning(
                    "Only one wheel component found - .*. Skip validating vehicle axis alignment.",
                    at=Sdf.Path("/vehicle/Xform/collections/wheel_fl"),
                ),
                IsAWarning(
                    "Only one wheel component found - .*. Skip validating vehicle axis alignment.",
                    at=Sdf.Path("/vehicle/Xform/collections/wheel_rr"),
                ),
                IsAWarning(
                    "Only one wheel component found - .*. Skip validating vehicle axis alignment.",
                    at=Sdf.Path("/vehicle/Xform/collections/wheel_rl"),
                ),
            ],
        )

    async def test_vehicle_wheels(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleWheelsOne.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAWarning(
                    "Only one wheel component found - .*. Skip validating vehicle axis alignment.",
                    at=Sdf.Path("/vehicle/collections/wheel_fr"),
                ),
            ],
        )
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleWheelsTwo.usda"), rule=VehicleCapabilityChecker, asserts=[]
        )
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleWheelsTwoInvalid.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAWarning(
                    "Only one wheel component found - .*. Skip validating vehicle axis alignment.",
                    at=Sdf.Path("/vehicle/collections/wheel_fr"),
                ),
                IsAWarning(
                    "Only one wheel component found - .*. Skip validating vehicle axis alignment.",
                    at=Sdf.Path("/vehicle/collections/wheel_rl"),
                ),
            ],
        )
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleWheelsThree.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAWarning(
                    "Only one wheel component found - .*. Skip validating vehicle axis alignment.",
                    at=Sdf.Path("/vehicle/collections/wheel_fr"),
                ),
            ],
        )
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleWheelsFiveInvalid.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAWarning(
                    "Only one wheel component found - .*. Skip validating vehicle axis alignment.",
                    at=Sdf.Path("/vehicle/collections/wheel_fifth"),
                ),
            ],
        )
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleWheelsFive.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[],
        )
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleWheelsSix.usda"), rule=VehicleCapabilityChecker, asserts=[]
        )

    async def test_vehicle_tilt(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleTilt.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Bounding box of the asset root prim .* is not centered at the origin. Bounding box center: .*",
                    at=Sdf.Path("/vehicle"),
                ),
                IsAFailure(
                    "Bounding box of the wheel .* does not sit on the ground. Bounding box bottom: .*",
                    at=Sdf.Path("/vehicle/Xform/collections/wheel_fl"),
                ),
                IsAFailure(
                    "Bounding box of the wheel .* does not sit on the ground. Bounding box bottom: .*",
                    at=Sdf.Path("/vehicle/Xform/collections/wheel_fr"),
                ),
                IsAFailure(
                    "Bounding box of the wheel .* does not sit on the ground. Bounding box bottom: .*",
                    at=Sdf.Path("/vehicle/Xform/collections/wheel_rl"),
                ),
                IsAFailure(
                    "Bounding box of the wheel .* does not sit on the ground. Bounding box bottom: .*",
                    at=Sdf.Path("/vehicle/Xform/collections/wheel_rr"),
                ),
            ],
        )

    async def test_vehicle_root_transformed(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleXformRoot.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Asset root prim .* can not have non identity matrix transformation.",
                    at=Sdf.Path("/vehicle"),
                ),
                IsAFailure(
                    "Bounding box of the asset root prim .* is not centered at the origin. Bounding box center: .*",
                    at=Sdf.Path("/vehicle"),
                ),
            ],
        )
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleXformRootTRS.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Asset root prim .* can not have non identity matrix transformation.",
                    at=Sdf.Path("/vehicle"),
                ),
                IsAFailure(
                    "Bounding box of the asset root prim .* is not centered at the origin. Bounding box center: .*",
                    at=Sdf.Path("/vehicle"),
                ),
            ],
        )
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleXformRootIdentity.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[],
        )
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleXformRootTRSIdentity.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[],
        )
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleXformRootNoXformOps.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[],
        )

    async def test_vehicle_orphan_prims(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleOrphanPrim.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Prim .* is not included in any component group.",
                    at=Sdf.Path("/vehicle/invalid_out_of_scope/invalid_part"),
                ),
            ],
        )

        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleOrphanPrims.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Prims .* are not included in any component group.",
                    at=Sdf.Path("/vehicle/invalid_out_of_scope/invalid_part"),
                ),
            ],
        )

    async def test_vehicle_no_semantic_labels(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleNoSemanticLabel.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Prim .* in component .* of type .* is not semantic labeled.",
                    at=Sdf.Path("/vehicle/Geometry/other/other"),
                ),
            ],
        )

    async def test_vehicle_no_semantic_labelsSuccess(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleNoSemanticLabelSuccess.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[],
        )

    async def test_vehicle_attributes_success(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleAttributesSuccess.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[],
        )

    @unittest.skip("Skipping test_vehicle_attributes_incorrect_allowed_tokens")
    async def test_vehicle_attributes_incorrect_allowed_tokens(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleAttributesIncorrectAllowedTokens.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAWarning(
                    "Incorrect allowed values found: [negX_incorrect, negY, negZ_incorrect, posX, posY, posZ]. Expected: ['negX', 'negY', 'negZ', 'posX', 'posY', 'posZ'].",
                    at=Sdf.Path("/vehicle.omni:simready:vehicle:longitudinalAxis"),
                ),
                IsAWarning(
                    "Incorrect allowed values found: [4WD_incorrect, AWD_incorrect, FWD, RWD]. Expected: ['4WD', 'AWD', 'FWD', 'RWD'].",
                    at=Sdf.Path("/vehicle.omni:simready:vehicle:drivetrain"),
                ),
                IsAWarning(
                    "Incorrect allowed values found: [front, back, all, tank, none_incorrect]. Expected: ['front', 'back', 'all', 'tank', 'none'].",
                    at=Sdf.Path("/vehicle.omni:simready:vehicle:steering"),
                ),
            ],
        )

    async def test_vehicle_attributes_incorrect_types(self):
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleAttributesIncorrectTypes.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Invalid attribute type 'string' found. Expected 'token'.",
                    at=Sdf.Path("/vehicle.omni:simready:vehicle:longitudinalAxis"),
                ),
                IsAFailure(
                    "Invalid attribute type 'string' found. Expected 'token'.",
                    at=Sdf.Path("/vehicle.omni:simready:vehicle:drivetrain"),
                ),
                IsAFailure(
                    "Invalid attribute type 'string' found. Expected 'token'.",
                    at=Sdf.Path("/vehicle.omni:simready:vehicle:steering"),
                ),
                IsAFailure(
                    "Invalid attribute type 'string' found. Expected 'token'.",
                    at=Sdf.Path("/vehicle/Geometry/body.omni:simready:vehicle"),
                ),
                IsAFailure(
                    "Invalid attribute type 'string[]' found. Expected 'token[]'.",
                    at=Sdf.Path("/vehicle/Geometry/body/brakeLights.omni:simready:light"),
                ),
                IsAFailure(
                    "Invalid attribute type 'float2[]' found. Expected one of: '['float2', 'double2']'.",
                    at=Sdf.Path("/vehicle/Geometry/body/brakeLights.omni:simready:light:intensityDomain:brakeLights"),
                ),
                IsAFailure(
                    "Invalid attribute type 'color3d[]' found. Expected one of: '['color3f', 'color3d']'.",
                    at=Sdf.Path("/vehicle/Geometry/body/brakeLights.omni:simready:light:color:brakeLights"),
                ),
                IsAFailure(
                    "Invalid attribute type 'float[]' found. Expected 'float'.",
                    at=Sdf.Path("/vehicle/Geometry/body/brakeLights.omni:simready:light:duration:brakeLights"),
                ),
                IsAFailure(
                    "Invalid attribute type 'string' found. Expected 'token'.",
                    at=Sdf.Path("/vehicle/Geometry/group_test.omni:simready:vehicle:pivot"),
                ),
                IsAFailure(
                    "Invalid attribute type 'string' found. Expected 'token'.",
                    at=Sdf.Path("/vehicle/Geometry/group_test.omni:simready:vehicle:parent"),
                ),
                IsAFailure(
                    "Invalid attribute type 'string' found. Expected 'token'.",
                    at=Sdf.Path("/vehicle/Geometry/group_test.omni:simready:vehicle:group"),
                ),
                IsAFailure(
                    "Invalid attribute type 'string' found. Expected 'token'.",
                    at=Sdf.Path("/vehicle/Geometry/group_test.omni:simready:vehicle:subgroup"),
                ),
                IsAFailure(
                    "Invalid attribute type 'string' found. Expected 'token'.",
                    at=Sdf.Path("/vehicle/Geometry/group_test.omni:simready:vehicle:parent"),
                ),
                IsAFailure(
                    "Invalid attribute type 'string[]' found. Expected 'token[]'.",
                    at=Sdf.Path("/vehicle/Geometry/task_test.omni:simready:tasks"),
                ),
                IsAFailure(
                    "Invalid attribute type 'string' found. Expected 'token'.",
                    at=Sdf.Path("/vehicle/Geometry/task_test.omni:simready:tasks:effector"),
                ),
            ],
        )

    async def test_vehicle_steering_tank_allowed_values(self):
        """Test that vehicle validator correctly handles 'tank' as 'none'
        in allowedTokens metadata of omni:simready:vehicle:steering attribute.
        """
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleAttributesSuccessTankSteering.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[],
        )

    async def test_vehicle_steering_tank_and_none_allowed_values(self):
        """Test that vehicle validator correctly handles 'tank' and 'none'
        in allowedTokens metadata of omni:simready:vehicle:steering attribute.
        """
        await self.assertRuleAsync(
            asset=get_url("vehicle/vehicleAttributesSuccessTankAndNoneSteering.usda"),
            rule=VehicleCapabilityChecker,
            asserts=[],
        )
