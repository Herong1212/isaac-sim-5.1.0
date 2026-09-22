# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from omni.asset_validator._impl import ExtentsChecker, KindChecker, TypeChecker

from ._engine import registerRule

__all__ = [
    "ExtentsChecker",
    "KindChecker",
    "TypeChecker",
]

registerRule("Omni:Basic")(KindChecker)
registerRule("Omni:Basic")(ExtentsChecker)
registerRule("Omni:Basic")(TypeChecker)
