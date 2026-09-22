# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from omni.graph.window.core import OmniGraphWindow

from .generic_catalog_model import GenericNodeTypeCatalogModel
from .generic_graph_model import GenericGraphModel
from .generic_graph_widget import GenericGraphWidget


class GenericGraphWindow(OmniGraphWindow):
    def on_build_window(self):
        """Override the base widget type"""
        self._main_widget = GenericGraphWidget(  # noqa: attribute-defined-outside-init
            graph_model_class=GenericGraphModel, catalog_model=GenericNodeTypeCatalogModel(), filter_fn=self._filter_fn
        )
