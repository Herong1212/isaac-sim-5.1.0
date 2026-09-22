# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

from typing import Iterable

import omni.graph.core as og
import omni.graph.tools.ogn as ogn
from omni.graph.window.core import OmniGraphNodeTypeCatalogModel


class ActionNodeTypeCatalogModel(OmniGraphNodeTypeCatalogModel):
    """
    Model used by the node catalog to select nodes for dragging into the graph.
    """

    def allow_node_type(self, node_type_name: str):
        """Override of the base to filter out non-action-graph types"""
        if not super().allow_node_type(node_type_name):
            return False

        node_type = og.get_node_type(node_type_name)
        category_metadata = node_type.get_metadata(ogn.MetadataKeys.CATEGORIES)
        if category_metadata:
            categories = category_metadata.split(",")
            for category in categories:
                graph_filter = self._checked_get_graph_filter_from_category(category)
                if graph_filter and (graph_filter != "action"):
                    return False
        return True


# We don't want to have to change the golden images for tests every time
# a new category or node type is added (the number of node types in each
# category is displayed on the catalog widget).
#
# This class allows tests to build a catalog containing only a specified
# set of nodes.
#
# This class should be in the tests folder and used to be there, but there is a bizarre
# interaction with ETM which causes OmniGraphNodeTypeCatalogModel's call to super().__init__()
# to fail with an invalid 'self'. It only happens when the test is run through ETM, on Linux.
# Moving this class here fixes the problem. I have no idea why.
class OgActionTestCatalogModel(ActionNodeTypeCatalogModel):
    def __init__(self, allowed_node_types: Iterable[str] = None):
        self._allowed_node_types: Iterable[str] = allowed_node_types
        super().__init__()

    def allow_node_type(self, node_type_name: str):
        # Let the base class have its say.
        if not super().allow_node_type(node_type_name):
            return False

        if hasattr(self, "_allowed_node_types") and self._allowed_node_types:
            return node_type_name in self._allowed_node_types
        return True


class OmniGraphNodeQuickSearchModel(ActionNodeTypeCatalogModel):
    """
    Model used by the QuickSearch window to select nodes for adding to the graph.
    """

    # Workaround for OM-99274. See note below.
    _node_created = False

    def execute(self, item):
        """The user pressed enter or clicked on an item"""
        # Mime Data has the information about USD types.
        data = self.get_drag_mime_data(item)
        if not data:
            return

        # Workaround for OM-99274. See note in omni.graph.window.core's catalog_model.py for details.
        # This check is to prevent the node being added twice once OM-99274 is fixed. It should be removed
        # at the same time as the corresponding code in omni.graph.window.core.
        if not __class__._node_created:  # noqa: PLW0212
            __class__._node_created = True  # noqa: PLW0212
            from .action_graph_extension import ActionGraphExtension

            ActionGraphExtension.add_node(data, False)
