# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the SelectionGetter class to retrieve the selection from a given GraphModel."""


__all__ = ["SelectionGetter"]

from .abstract_batch_position_getter import AbstractBatchPositionGetter
from typing import Any
from .graph_model import GraphModel


class SelectionGetter(AbstractBatchPositionGetter):
    """A class for retrieving the selection from a GraphModel.

    This helper class is designed to be used in conjunction with GraphModelBatchPosition to obtain the current selection within the GraphModel.

    Args:
        model (GraphModel): The graph model from which the selection is to be retrieved."""

    def __init__(self, model: GraphModel):
        """Initializes a new instance of the SelectionGetter class."""
        super().__init__(model)

    def __call__(self, drive_item: Any):
        model = self.model
        if model:
            return model.selection
