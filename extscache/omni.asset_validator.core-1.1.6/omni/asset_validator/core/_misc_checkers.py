# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from omni.asset_validator._impl import (
    AlmostExtremeExtentChecker,
    PointsPrecisionErrorChecker,
    PointsPrecisionWarningChecker,
    SkelBindingAPIAppliedChecker,
    UsdAsciiPerformanceChecker,
    UsdDanglingMaterialBinding,
    UsdGeomSubsetChecker,
    UsdLuxSchemaChecker,
    UsdMaterialBindingApi,
)

from ._engine import registerRule

__all__ = [
    "AlmostExtremeExtentChecker",
    "PointsPrecisionErrorChecker",
    "PointsPrecisionWarningChecker",
    "SkelBindingAPIAppliedChecker",
    "UsdAsciiPerformanceChecker",
    "UsdDanglingMaterialBinding",
    "UsdGeomSubsetChecker",
    "UsdLuxSchemaChecker",
    "UsdMaterialBindingApi",
]

registerRule("Usd:Performance")(AlmostExtremeExtentChecker)
registerRule("Usd:Performance")(PointsPrecisionErrorChecker)
registerRule("Usd:Performance")(PointsPrecisionWarningChecker)
registerRule("Usd:Performance")(UsdAsciiPerformanceChecker)
registerRule("Usd:Schema")(UsdDanglingMaterialBinding)
registerRule("Usd:Schema")(UsdGeomSubsetChecker)
registerRule("Usd:Schema")(UsdLuxSchemaChecker)
registerRule("Usd:Schema")(UsdMaterialBindingApi)
registerRule("Usd:Schema")(SkelBindingAPIAppliedChecker)
