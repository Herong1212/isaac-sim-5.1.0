# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from omni.graph.window.core import OmniGraphWindow

from .action_catalog_model import ActionNodeTypeCatalogModel
from .action_graph_widget import ActionGraphWidget


class ActionGraphWindow(OmniGraphWindow):
    def on_build_window(self):
        """Override the base widget type"""
        self._main_widget = ActionGraphWidget(catalog_model=ActionNodeTypeCatalogModel())  # noqa: PLW0201
