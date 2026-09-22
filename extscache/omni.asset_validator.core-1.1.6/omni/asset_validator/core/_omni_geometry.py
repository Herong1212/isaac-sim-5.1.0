# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""
All rules in Omni:Geometry category.
"""

from omni.asset_validator._impl import (
    IndexedPrimvarChecker,
    ManifoldChecker,
    SubdivisionSchemeChecker,
    UnusedMeshTopologyChecker,
    UnusedPrimvarChecker,
    ValidateTopologyChecker,
    WeldChecker,
    ZeroAreaFaceChecker,
)

from ._engine import registerRule

__all__ = [
    "IndexedPrimvarChecker",
    "ManifoldChecker",
    "SubdivisionSchemeChecker",
    "UnusedMeshTopologyChecker",
    "UnusedPrimvarChecker",
    "ValidateTopologyChecker",
    "WeldChecker",
    "ZeroAreaFaceChecker",
]

registerRule("Omni:Geometry")(IndexedPrimvarChecker)
registerRule("Omni:Geometry")(ManifoldChecker)
registerRule("Omni:Geometry")(SubdivisionSchemeChecker)
registerRule("Omni:Geometry")(UnusedMeshTopologyChecker)
registerRule("Omni:Geometry")(UnusedPrimvarChecker)
registerRule("Omni:Geometry")(ValidateTopologyChecker)
registerRule("Omni:Geometry")(WeldChecker)
registerRule("Omni:Geometry")(ZeroAreaFaceChecker)
