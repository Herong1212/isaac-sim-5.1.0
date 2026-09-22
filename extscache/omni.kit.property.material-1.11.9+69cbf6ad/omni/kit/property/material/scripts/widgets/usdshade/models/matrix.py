# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""Module provides the MdlMatrixAttributeModel, an extension of MatrixBaseAttributeModel for representing non-uniform matrix attributes in USD stages."""

__all__ = ["MdlMatrixAttributeModel"]

from typing import List

from omni.kit.property.usd.usd_attribute_model import MatrixBaseAttributeModel
from omni.kit.property.usd.usd_model_base import UsdBase
from pxr import Sdf, Usd


class MdlMatrixAttributeModel(MatrixBaseAttributeModel):
    """Extension of MatrixBaseAttributeModel for displaying non-uniform matrices.

    This model is used to represent a matrix attribute where the dimensions of the matrix may not be uniform. It extends the functionality of MatrixBaseAttributeModel by managing the display and update of matrix values in the UI.

    Args:
        stage (:obj:`Usd.Stage`): The USD stage that the attribute belongs to.
        attribute_paths (List[:obj:`Sdf.Path`]): A list of paths to the attributes.
        dimensions (List[int]): The dimensions of the matrix as a list [rows, columns].
        self_refresh (bool): Whether the model should refresh itself automatically.
        metadata (dict): A dictionary containing metadata for the attribute."""

    def __init__(
        self,
        stage: Usd.Stage,
        attribute_paths: List[Sdf.Path],
        dimensions: List[int],
        self_refresh: bool,
        metadata: dict,
    ):
        """Initializes the MdlMatrixAttributeModel with the given parameters."""
        self._rows = dimensions[0]
        self._columns = dimensions[1]

        num_items = self._rows * self._columns

        super().__init__(stage, attribute_paths, num_items, self_refresh, metadata)

    def _update_value(self, force=False):
        # pylint: disable=protected-access
        if UsdBase._update_value(self, force):
            for i, _ in enumerate(self._items):
                self._items[i].model.set_value(self._value[i])

    def _on_value_changed(self, item):
        """Called when the submodel is chaged"""

        if self._edit_mode_counter > 0:
            matrix = [item.model.get_value_as_float() for item in self._items]
            if matrix and self.set_value(matrix):
                self._item_changed(item)
