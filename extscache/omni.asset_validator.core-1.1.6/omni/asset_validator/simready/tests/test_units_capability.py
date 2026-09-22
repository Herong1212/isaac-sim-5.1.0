# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

import unittest

import omni.capabilities as cap
from omni.asset_validator.core.tests import IsAFailure, ValidationTestCase
from pxr import Usd, UsdGeom

from .._units_capability import MetersPerUnit1Checker, UpAxisZChecker


class TestUpAxisZChecker(ValidationTestCase):
    """Test cases for UpAxisZChecker validator."""

    def test_stage_with_z_upaxis_passes(self):
        """Test that a stage with upAxis = Z passes validation."""
        stage = Usd.Stage.CreateInMemory()
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

        self.assertRule(stage=stage, rule=UpAxisZChecker, asserts=[])  # No failures expected

    def test_stage_with_y_upaxis_fails(self):
        """Test that a stage with upAxis = Y fails validation."""
        stage = Usd.Stage.CreateInMemory()
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

        self.assertRule(
            stage=stage,
            rule=UpAxisZChecker,
            asserts=[
                IsAFailure(
                    message="Stage has upAxis of 'Y', not 'Z'.", requirement=cap.UnitsRequirements.UN_006, at=stage
                )
            ],
        )

    def test_stage_without_upaxis_fails(self):
        """Test that a stage without upAxis metadata fails validation."""
        stage = Usd.Stage.CreateInMemory()
        # Don't set any upAxis metadata

        self.assertRule(
            stage=stage,
            rule=UpAxisZChecker,
            asserts=[
                IsAFailure(message="Stage has no upAxis specified.", requirement=cap.UnitsRequirements.UN_006, at=stage)
            ],
        )


class TestMetersPerUnit1Checker(ValidationTestCase):
    """Test cases for MetersPerUnit1Checker validator."""

    def test_stage_with_mpu_1_passes(self):
        """Test that a stage with metersPerUnit = 1.0 passes validation."""
        stage = Usd.Stage.CreateInMemory()
        UsdGeom.SetStageMetersPerUnit(stage, 1.0)
        stage.SetDefaultPrim(stage.DefinePrim("/World"))

        self.assertRule(stage=stage, rule=MetersPerUnit1Checker, asserts=[])  # No failures expected

    def test_stage_with_mpu_0_01_fails(self):
        """Test that a stage with metersPerUnit = 0.01 fails validation."""
        stage = Usd.Stage.CreateInMemory()
        UsdGeom.SetStageMetersPerUnit(stage, 0.01)
        stage.SetDefaultPrim(stage.DefinePrim("/World"))

        self.assertRule(
            stage=stage,
            rule=MetersPerUnit1Checker,
            asserts=[
                IsAFailure(
                    message="Stage has metersPerUnit of 0.01, not 1.0.",
                    requirement=cap.UnitsRequirements.UN_007,
                    at=stage,
                )
            ],
        )

    def test_stage_without_mpu_fails(self):
        """Test that a stage without metersPerUnit metadata fails validation."""
        stage = Usd.Stage.CreateInMemory()
        # Don't set any metersPerUnit metadata
        stage.SetDefaultPrim(stage.DefinePrim("/World"))

        self.assertRule(
            stage=stage,
            rule=MetersPerUnit1Checker,
            asserts=[
                IsAFailure(
                    message="Stage has no metersPerUnit specified.", requirement=cap.UnitsRequirements.UN_007, at=stage
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
