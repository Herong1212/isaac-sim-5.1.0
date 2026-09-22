# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "LayerExtension",
    "ContextMenu",
    "LayerItem",
    "PrimSpecItem",
    "LayerModel",
    "LayerUtils",
    "get_instance",
    "get_current_focused_layer_item",
    "set_current_focused_layer_item",
    "remove_layer_selection_changed_fn",
    "add_layer_selection_changed_fn",
    "get_layer_model",
    "get_selected_items"
    ]

from .extension import *
from .context_menu import ContextMenu
from .layer_item import LayerItem
from .prim_spec_item import PrimSpecItem
from .layer_model import LayerModel
from omni.kit.usd.layers import LayerUtils
import omni.kit.app


@omni.kit.app.deprecated("omni.kit.widget.layers.get_instance is deprecated, please use the public API for specific functionality instead of accessing the extension instance.")
def get_instance():
    """
    Returns the instance of the LayerExtension.

    Returns:
        :obj:'omni.ext.IExt': The instance of the LayerExtension.

    """
    return LayerExtension.get_instance()
