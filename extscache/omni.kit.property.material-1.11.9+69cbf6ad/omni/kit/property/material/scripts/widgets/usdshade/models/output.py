# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module provides the UsdShadeOutputModel class to represent USD Shade Outputs in a property view, with functionality to get a string representation of the output's value."""

__all__ = ["UsdShadeOutputModel"]

from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
from pxr import Sdr, UsdShade


class UsdShadeOutputModel(UsdAttributeModel):
    """A class to represent a USD Shade Output in a property view.

    This class overrides the widget representation for a UsdShade.Output to display a simple string that indicates the output type.
    """

    def get_value_as_string(self, elide_big_array=True) -> str:
        """Returns a string representation of the UsdShade.Output's value.

        Args:
            elide_big_array (bool): If True, elide arrays larger than a threshold.

        Returns:
            str: Render type as a string."""
        import omni.UsdMdl as UsdMdl

        self._update_value()
        render_type = self.metadata.get(Sdr.PropertyMetadata.RenderType, "")

        if render_type == UsdMdl.Types.Array:
            sdr_metadata = self.metadata.get(UsdShade.Tokens.sdrMetadata, {})

            element_render_type = sdr_metadata.get(UsdMdl.Metadata.ArrayElementType, None)
            if element_render_type:
                render_type = f"{element_render_type}[]"

        return render_type
