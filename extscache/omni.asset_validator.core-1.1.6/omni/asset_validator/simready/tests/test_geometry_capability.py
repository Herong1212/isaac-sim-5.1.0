# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = ["GeometryCapabilityCheckerTests"]

from pxr import Sdf, Usd, UsdGeom

from .._geometry_capability import ContainsMeshChecker
from .simready_common import AsyncValidationRuleTestCase, IsAFailure, IsAWarning


class GeometryCapabilityCheckerTests(AsyncValidationRuleTestCase):
    """Test cases for ContainsMeshChecker validator."""

    async def test_stage_with_mesh_passes(self):
        """Test that a stage with a mesh passes validation."""
        stage = Usd.Stage.CreateInMemory()
        UsdGeom.Mesh.Define(stage, "/World/Mesh")

        await self.assertRuleAsync(asset=stage, rule=ContainsMeshChecker, asserts=[])  # No failures expected

    async def test_stage_with_other_geometry_fails(self):
        """Test that a stage with other geometry fails validation."""
        stage = Usd.Stage.CreateInMemory()
        UsdGeom.Sphere.Define(stage, "/World/Sphere")

        expected_failure = IsAFailure(
            ContainsMeshChecker._MESH_NOT_FOUND_MESSAGE,
            at=f"Stage <{stage.GetRootLayer().identifier}>",
        )
        await self.assertRuleAsync(asset=stage, rule=ContainsMeshChecker, asserts=[expected_failure])

    async def test_stage_with_mesh_and_other_geometry_warns(self):
        """Test that a stage with a mesh and other geometry warns."""
        stage = Usd.Stage.CreateInMemory()
        UsdGeom.Mesh.Define(stage, "/World/Mesh")
        UsdGeom.Sphere.Define(stage, "/World/Sphere")

        expected_warning = IsAWarning(
            ContainsMeshChecker._OTHER_GEOMETRY_WARNING_MESSAGE,
            at=Sdf.Path("/World/Sphere"),
        )
        await self.assertRuleAsync(
            asset=stage,
            rule=ContainsMeshChecker,
            asserts=[expected_warning],
        )
