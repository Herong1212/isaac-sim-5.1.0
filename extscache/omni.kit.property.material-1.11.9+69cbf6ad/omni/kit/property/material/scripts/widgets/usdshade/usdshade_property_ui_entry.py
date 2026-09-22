# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module defines UsdShadePropertyUiEntry, a subclass of UsdPropertyUiEntry, which overrides the metadata comparison function."""

__all__ = ["UsdShadePropertyUiEntry"]

from omni.kit.property.usd.usd_property_widget import UsdPropertyUiEntry
from pxr import Sdf, Sdr


class UsdShadePropertyUiEntry(UsdPropertyUiEntry):
    """Subclass of :obj:`UsdPropertyUiEntry` that overrides the metadata comparison function."""

    def _compare_metadata(self, meta1: dict, meta2: dict) -> bool:
        keys_to_check = [
            Sdr.PropertyMetadata.RenderType,
            Sdf.AttributeSpec.CustomDataKey,
            Sdf.AttributeSpec.DisplayGroupKey,
            Sdf.AttributeSpec.DisplayNameKey,
            Sdf.PrimSpec.TypeNameKey,
        ]

        return all(meta1.get(key, None) == meta2.get(key, None) for key in keys_to_check)
