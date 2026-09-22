# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the CallExpressionModel class to represent MDL expressions as string values within the USD ecosystem."""

__all__ = ["CallExpressionModel"]

from typing import List

from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
from pxr import Sdf, Usd, UsdShade


class CallExpressionModel(UsdAttributeModel):
    """A model representing MDL expressions as string values for display purposes.

    This class extends UsdAttributeModel to show the value of expressions used to initialize MDL values in a string field. It is designed to work within the USD ecosystem, leveraging its stages and attribute paths to manage the properties of MDL materials.

    Args:
        stage (:obj:`Usd.Stage`): The USD stage where the attribute paths are located.
        attribute_paths (List[:obj:`Sdf.Path`]): A list of paths to the USD attributes that this model will represent.
        self_refresh (bool): A flag indicating whether the model should refresh itself when the USD stage changes.
        metadata (dict): A dictionary containing metadata for the attribute, which may include keys specific to MDL and SDR.
        change_on_edit_end (bool): A flag that determines if changes should be committed only when an edit operation ends.

    Keyword Args:
        displayGroup (str): Optional. The name of the display group for organizing attributes in the UI.
        displayName (str): Optional. The human-readable name for the attribute.
        options (List[str]): Optional. A list of options for the attribute.
        helpText (str): Optional. A help text associated with the attribute."""

    def __init__(
        self,
        stage: Usd.Stage,
        attribute_paths: List[Sdf.Path],
        self_refresh: bool,
        metadata: dict,
        change_on_edit_end=True,
        **kwargs,
    ):
        """Initializes a new instance of the CallExpressionModel."""
        import omni.UsdMdl as UsdMdl

        super().__init__(stage, attribute_paths, self_refresh, metadata, change_on_edit_end, **kwargs)

        sdr_metadata = metadata.get(UsdShade.Tokens.sdrMetadata, {})
        self._expression_value = sdr_metadata.get(UsdMdl.Metadata.ExpressionValue, "")

    def _get_default_value(self, prop, metadata=None):
        return True, self._expression_value

    def _read_value(self, obj, time_code):
        return self._expression_value
