# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
__all__ = ["UnicodeNameChecker"]

from omni.asset_validator._impl import UnicodeNameChecker
from pxr import Usd

from ._engine import registerRule

if Usd.GetVersion() >= (0, 24, 3):
    registerRule("Omni:Basic")(UnicodeNameChecker)
