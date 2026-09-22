# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = ["PedestrianCapabilityTests"]


from omni.asset_validator.simready import PedestrianCapabilityChecker
from pxr import Sdf

from .simready_common import AsyncValidationRuleTestCase, IsAFailure, IsAWarning, get_url


class PedestrianCapabilityTests(AsyncValidationRuleTestCase):
    async def test_pedestrian_not_centered(self):
        await self.assertRuleAsync(
            asset=get_url("pedestrian/pedestrianNotCentered.usda"),
            rule=PedestrianCapabilityChecker,
            asserts=[
                IsAFailure(
                    "SimReady pedestrians require the transform of root joint has zero translation.",
                    at=Sdf.Path("/Root/Skeleton"),
                ),
            ],
        )

    async def test_pedestrian_from_payload(self):
        await self.assertRuleAsync(
            asset=get_url("pedestrian/pedestrianFromPayload.usda"),
            rule=PedestrianCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Mesh's skeleton is separably loadable and may be missing for deformation.",
                    at=Sdf.Path("/World/Root/Skeleton"),
                ),
                IsAFailure(
                    "Character must stand on the ground plane.",
                    at=Sdf.Path("/World/Root/Skeleton"),
                ),
            ],
        )

    async def test_pedestrian_without_full_joints(self):
        await self.assertRuleAsync(
            asset=get_url("pedestrian/pedestrianWithoutFullJoints.usda"),
            rule=PedestrianCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Found matching Reallusion-style skeleton rig, "
                    "but the skeleton is missing the following joints: L_Foot.",
                    at=Sdf.Path("/Root/Skeleton"),
                ),
                IsAWarning(
                    "Cannot find foot joints to check if character is axis aligned.",
                    at=Sdf.Path("/Root/Skeleton"),
                ),
            ],
        )

    async def test_pedestrian_with_unbound_meshes(self):
        await self.assertRuleAsync(
            asset=get_url("pedestrian/pedestrianWithUnboundMeshes.usda"),
            rule=PedestrianCapabilityChecker,
            asserts=[
                IsAFailure(
                    "Skinnable prim must have UsdSkelBindingAPI applied.",
                    at=Sdf.Path("/World/Root/MeshWithoutBindingAPI"),
                ),
                IsAFailure(
                    "No binding to a skeleton rig.",
                    at=Sdf.Path("/World/Root/MeshWithoutSkeletonBinding"),
                ),
                IsAFailure(
                    "Skeleton or skinnable prim must be defined under SkelRoot.",
                    at=Sdf.Path("/World/SkeletonOutOfSkelRoot"),
                ),
                IsAFailure(
                    "Skeleton or skinnable prim must be defined under SkelRoot.",
                    at=Sdf.Path("/World/MeshOutOfSkelRoot"),
                ),
            ],
        )

    async def test_pedestrian_not_axis_aligned(self):
        await self.assertRuleAsync(
            asset=get_url("pedestrian/pedestrianNotAxisAligned.usda"),
            rule=PedestrianCapabilityChecker,
            asserts=[
                IsAWarning(
                    "The Bounding box of the pedestrian geometry prims is not symmetrical around the up-axis 'Z'.",
                    at=Sdf.Path("/Root/Skeleton"),
                ),
                IsAFailure(
                    "Character must stand on the ground plane.",
                    at=Sdf.Path("/Root/Skeleton"),
                ),
                IsAFailure(
                    "Vector between foot joints should be nearly perpendicular to up axis 'Z', while it's off 90.0 degrees (tolerance is 5.0 degrees).",
                    at=Sdf.Path("/Root/Skeleton"),
                ),
            ],
        )

    async def test_pedestrian_no_valid_skelroot(self):
        url = get_url("pedestrian/noValidSkelRoot.usda")

        await self.assertRuleAsync(
            asset=url,
            rule=PedestrianCapabilityChecker,
            asserts=[
                IsAFailure(
                    "No valid UsdSkelRoot presented under default prim in this layer.",
                    at=f"Stage <{url}>",
                ),
            ],
        )

    async def test_pedestrian_no_default_prim(self):
        url = get_url("pedestrian/noDefaultPrim.usda")

        await self.assertRuleAsync(
            asset=url,
            rule=PedestrianCapabilityChecker,
            asserts=[
                IsAFailure(
                    "No default prim presented in this layer.",
                    at=f"Stage <{url}>",
                ),
            ],
        )
