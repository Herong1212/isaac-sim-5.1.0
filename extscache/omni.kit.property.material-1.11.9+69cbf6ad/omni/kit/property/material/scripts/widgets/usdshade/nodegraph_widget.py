# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""Provides a widget for displaying and interacting with USD Shade Node Graphs within the USD material property extension."""

__all__ = ["UsdShadeNodeGraphWidget"]

from pxr import UsdShade

from .base_widget import UsdShadeBaseWidget


class UsdShadeNodeGraphWidget(UsdShadeBaseWidget):
    """A widget for displaying and interacting with a USD Shade Node Graph.

    This widget extends the UsdShadeBaseWidget to provide a graphical interface for
    managing USD Shade Node Graphs, which are used to define complex shading networks
    for digital assets. It offers a default title but can be customized upon
    initialization.

    Args:
        title (str): The title of the widget. Defaults to 'Node Graph'."""

    def __init__(self, title: str = "Node Graph"):
        """Initializes the UsdShadeNodeGraphWidget with a default or provided title."""
        super().__init__(UsdShade.NodeGraph, title, schema_ignore=[UsdShade.Material])

    def _identical_selection(self) -> bool:
        return False
