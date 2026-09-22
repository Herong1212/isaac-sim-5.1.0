# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from omni.asset_validator._impl import ArticulationChecker, ColliderChecker, PhysicsJointChecker, RigidBodyChecker

from ._engine import registerRule

__all__ = [
    "RigidBodyChecker",
    "ColliderChecker",
    "PhysicsJointChecker",
    "ArticulationChecker",
]

registerRule("Usd:Physics")(RigidBodyChecker)
registerRule("Usd:Physics")(ColliderChecker)
registerRule("Usd:Physics")(PhysicsJointChecker)
registerRule("Usd:Physics")(ArticulationChecker)
