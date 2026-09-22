# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import omni.kit.test
from omni.asset_validator.core import NormalMapTextureChecker

from .engine_tests import getUrl
from .rule_test import AsyncValidationRuleTestCase, IsAFailure, IsAnError


class CheckZipFileErrorRule(omni.asset_validator.core.BaseRuleChecker):
    def CheckZipFile(self, zipFile, packagePath):
        raise ValueError("Error CheckZipFile.")


class NormalMapTextureCheckerTest(AsyncValidationRuleTestCase):
    async def test_validate(self):
        await self.assertRuleAsync(
            asset=getUrl("cleanNormalMapReader.usda"),
            rule=NormalMapTextureChecker,
            asserts=[],
        )

    async def test_normal_map_not_authored(self):
        await self.assertRuleAsync(
            asset=getUrl("normalMapNotAuthored.usda"),
            rule=NormalMapTextureChecker,
            asserts=[],
        )

    async def test_normal_map_authored_empty(self):
        await self.assertRuleAsync(
            asset=getUrl("normalMapAuthoredEmpty.usda"),
            rule=NormalMapTextureChecker,
            asserts=[
                IsAFailure(
                    message="UsdUVTexture prim </Root/Looks/Material/NormalTexture> has invalid or unresolvable inputs:file of @@",
                    at="Prim </Root/Looks/Material/NormalTexture>",
                )
            ],
        )


class CheckZipFileTest(AsyncValidationRuleTestCase):
    async def test_usdz(self):
        await self.assertRuleAsync(
            asset=getUrl("usdzPass.usdz"),
            rule=CheckZipFileErrorRule,
            asserts=[IsAnError("Uncaught error: Error CheckZipFile.")],
        )

    async def test_usdz_validate_with_callbacks(self):
        """Test OMPE-11167 - ensure BaseRuleChecker.CheckZipFile() is run when asset_progress_fn is provided."""
        engine = omni.asset_validator.core.ValidationEngine(init_rules=False)
        engine.enable_rule(CheckZipFileErrorRule)
        url = getUrl("usdzPass.usdz")
        results = []

        await engine.validate_with_callbacks(
            url,
            asset_validated_fn=lambda result: results.append(result),
            asset_progress_fn=lambda *args, **kwargs: None,
        )
        self.assertEqual(results[0].asset, url, "The actual and expected URL are different.")
        self.assertEqual(IsAnError("Uncaught error: Error CheckZipFile."), results[0].issues()[0])
