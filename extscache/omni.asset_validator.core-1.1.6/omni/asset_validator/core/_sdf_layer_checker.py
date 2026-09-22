# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from omni.asset_validator._impl import LayerSpecChecker

from ._engine import registerRule

__all__ = ["LayerSpecChecker"]

registerRule("Omni:Basic")(LayerSpecChecker)
