# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from omni.asset_validator._impl import (
    ByteAlignmentChecker,
    CompressionChecker,
    MissingReferenceChecker,
    NormalMapTextureChecker,
    PrimEncapsulationChecker,
    StageMetadataChecker,
    TextureChecker,
)

from ._engine import registerRule

__all__ = [
    "ByteAlignmentChecker",
    "CompressionChecker",
    "MissingReferenceChecker",
    "NormalMapTextureChecker",
    "PrimEncapsulationChecker",
    "StageMetadataChecker",
    "TextureChecker",
]

registerRule("Basic")(ByteAlignmentChecker)
registerRule("Basic")(CompressionChecker)
registerRule("Basic")(MissingReferenceChecker)
registerRule("Basic")(StageMetadataChecker)
registerRule("Basic")(TextureChecker)
registerRule("Basic")(PrimEncapsulationChecker)
registerRule("Basic")(NormalMapTextureChecker)
