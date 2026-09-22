# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from omni.asset_validator._impl import AnchoredAssetPathsChecker, SupportedFileTypesChecker, UsdzUdimLimitationChecker

from ._engine import registerRule

__all__ = [
    "AnchoredAssetPathsChecker",
    "SupportedFileTypesChecker",
    "UsdzUdimLimitationChecker",
]


registerRule("AtomicAsset")(AnchoredAssetPathsChecker)
registerRule("AtomicAsset")(SupportedFileTypesChecker)
registerRule("AtomicAsset")(UsdzUdimLimitationChecker)
