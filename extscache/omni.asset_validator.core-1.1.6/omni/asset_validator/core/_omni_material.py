# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from omni.asset_validator._impl import (
    MaterialOldMdlSchemaChecker,
    MaterialOutOfScopeChecker,
    MaterialPathChecker,
    ShaderImplementationSourceChecker,
)

from ._engine import registerRule

__all__ = [
    "MaterialPathChecker",
    "MaterialOutOfScopeChecker",
    "MaterialOldMdlSchemaChecker",
    "ShaderImplementationSourceChecker",
]


registerRule("Omni:Material")(MaterialPathChecker)
registerRule("Omni:Material")(MaterialOutOfScopeChecker)
registerRule("Omni:Material")(MaterialOldMdlSchemaChecker)
registerRule("Omni:Material")(ShaderImplementationSourceChecker)
