# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["OmniGraphNodeTypeCatalogModel", "OmniGraphNodeQuickSearchModel"]

import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

import omni.graph.core as og
import omni.graph.tools as ogt
import omni.graph.tools.ogn as ogn
import omni.kit
import omni.ui as ui

from . import graph_config

# These categories will have "(BETA)" appended to their names in the catalog.
BETA_CATEGORIES = ["ui"]


# Pseudo-nodes which are not real OG node types.
@dataclass
class PseudoNode:
    type_name: str
    ui_name: str
    category: str
    icon_path: str
    info: str
    size: Tuple[int, int]
    display_color: Tuple[float, float, float]


# FIXME: Changes to this list of pseudo-node types must be reflected in TelemetryHelpers.h in the omni.graph.telemetry
# extension in order for telemetry data to be collected for pseudo-nodes.
PSEUDO_NODES = [
    PseudoNode(
        "Backdrop",
        "Backdrop",
        "ui",
        f"{graph_config.Paths.ICON_PATH}/Backdrop.svg",
        "Provides a 'group-box' with optional description for node organization.",
        (800, 400),
        (0.3, 0.6, 0.2),
    ),
    PseudoNode(
        "OmniNote",
        "Note",
        "ui",
        f"{graph_config.Paths.ICON_PATH}/Backdrop.svg",  # TODO: Get different svg for this
        "Provides a box with optional description for documenting the graph.",
        (250, 200),
        (0.93, 0.91, 0.78),
    ),
]
# For fast lookup by type name.
PSEUDO_NODES_DICT = {node.type_name: node for node in PSEUDO_NODES}


class ActionNodeItem(ui.AbstractItem):
    """leaf item for OmniGraphNodeTypeCatalogModel"""

    def __init__(
        self,
        item_name: str,
        item_info: str,
        item_type: str,
        item_icon: str = "",
        item_category: str = "",
        item_category_name: str = "",
    ):
        super().__init__()

        self.name_model = ui.SimpleStringModel(item_name)
        self.info_model = ui.SimpleStringModel(item_info)
        self.type_model = ui.SimpleStringModel(item_type)
        self.category_model = ui.SimpleStringModel(item_category)
        self.category_name_model = ui.SimpleStringModel(item_category_name)

        if item_icon is None:
            item_icon = f"{graph_config.Paths.ICON_PATH}/{item_type}.svg"

        self.icon_model = ui.SimpleStringModel(item_icon)
        self.mouse_press_x = None
        self.mouse_press_y = None

        self.visible = True

    def filter(self, text_to_search_for: str):  # noqa: A003
        # When there's no filter text, show everything.
        if not text_to_search_for:
            self.visible = True
            return

        # We want to match all of the words in the filter text, but they can be spread among the various
        # parts of node's catalog entry. For example, "math add" can match "Add" in the Add node's name and
        # "Math" in the name of its category.
        # To do this we combine all of the entry's bits into a single big string.
        category_name = self.category_name_model.as_string
        if not category_name:
            category_name = self.category_model.as_string

        text_to_search_in = category_name.lower() + " " + self.name_model.as_string.lower()
        self.visible = all(word in text_to_search_in for word in text_to_search_for.split())


class ActionGroupItem(ActionNodeItem):
    """group item for OmniGraphNodeTypeCatalogModel"""

    def __init__(self, category: str, action_nodes: List[str]):
        nice_category = graph_config.make_nice_name(category)
        category_info = graph_config.CategoryStyles.STYLE_BY_CATEGORY.get(category, None)
        if category_info:
            _, item_icon, _ = category_info
        else:
            item_icon = graph_config.CategoryStyles.STYLE_BY_CATEGORY["generic"][1]
        if category in BETA_CATEGORIES:
            nice_category += " (BETA)"
        super().__init__(nice_category, "", "", item_icon, category, nice_category)
        self.visible = True
        self.children = []
        for node_type_name in action_nodes:
            if not node_type_name:
                continue
            pseudo_node = PSEUDO_NODES_DICT.get(node_type_name, None)
            if pseudo_node:
                ui_name = pseudo_node.ui_name or node_type_name
                icon_path = pseudo_node.icon_path or graph_config.CategoryStyles.STYLE_BY_CATEGORY["generic"][1]
                info = pseudo_node.info
            else:
                node_type = og.get_node_type(node_type_name)
                ui_name = node_type.get_metadata(ogn.MetadataKeys.UI_NAME)
                if ui_name is None:
                    ui_name = node_type_name.split(".")[-1]
                    ui_name = graph_config.make_nice_name(ui_name)
                _, icon_path, _ = graph_config.CategoryStyles.get_style_for_node_type(node_type_name)
                # allow empty description
                info = node_type.get_metadata(ogn.MetadataKeys.DESCRIPTION) or ""
            info = "\n".join(["\n".join(ogt.shorten_string_lines_to(line.strip(), 80)) for line in info.splitlines()])
            self.children.append(ActionNodeItem(ui_name, info, node_type_name, icon_path, category, nice_category))
        self.children.sort(key=lambda item: item.name_model.as_string.lower())

    def prefilter(self, text: str):
        group_visible = False
        for c in self.children:
            c.filter(text)
            group_visible |= c.visible

        self.visible = group_visible


class GraphGroupItem(ActionNodeItem):
    """Special group for holding items which are not OG nodes, but are things like subgraphs, backdrops etc"""

    def __init__(self):
        super().__init__("SubGraph", "", "", "")

        self.visible = True
        self.children = []
        self.children.append(
            ActionNodeItem("SubGraph", "Container to encapsulate action subgraph networks.", "SubGraph")
        )
        self.children.append(
            ActionNodeItem("Input Node", "Provides access to the inputs of the current container.", "InputNode")
        )
        self.children.append(
            ActionNodeItem("Output Node", "Provides access to the outputs of the current container.", "OutputNode")
        )

    def prefilter(self, text: str):
        group_visible = False
        for c in self.children:
            c.filter(text)
            group_visible |= c.visible

        self.visible = group_visible


class OmniGraphNodeTypeCatalogModel(ui.AbstractItemModel):
    """Model that has all the OmniGraph nodes it's possible to create."""

    class Column(Enum):
        NAME = 0
        INFO = 1
        ICON = 2
        TYPE = 3
        CATEGORY = 4

    def __init__(self):
        super().__init__()
        self._children = []

        # subscribe to the extension change events
        ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
        self.__rebuild_node_list()

        self.extensions_subscription = None
        self.__registry_subscription = None

        # If we have an execute() method then assume that we are being used for QuickSearch.
        self.__quicksearch_initializing = hasattr(self, "execute")

        # if kit supports events when the graph registry changes (104), use that, otherwise
        # listen for extension changes
        if hasattr(og.GraphRegistry, "get_event_stream") and callable(og.GraphRegistry.get_event_stream):
            self.__registry_subscription = (
                og.GraphRegistry()
                .get_event_stream()
                .create_subscription_to_pop(
                    self.__node_library_changed, name="OmniGraphNodeTypeCatalogModel Registry Changes"
                )
            )
            assert self.__registry_subscription
        else:
            self.extensions_subscription = ext_manager.get_change_event_stream().create_subscription_to_pop(
                lambda _: self.__rebuild_node_list(), name="OmniGraphNodeTypeCatalogModel Extension Changes"
            )

        # Don't build the node list yet because that calls allowed_node_type() and we want to allow derived
        # classes to finish their __init__'s before that happens.
        self.__rebuild_task = asyncio.ensure_future(self.__delayed_rebuild())

    async def __delayed_rebuild(self):
        """Rebuilds the node list after the next update"""
        # If this model is being used by quicksearch we need some extra time to let QS finish
        # its initialization before we change the node list.
        for _ in range(3 if self.__quicksearch_initializing else 1):
            await omni.kit.app.get_app().next_update_async()
        self.__rebuild_node_list()
        self.__quicksearch_initializing = False
        self.__rebuild_task = None

    def __node_library_changed(self, event):
        """Callback invoked when node types are added or removed from the node library"""
        if self.__rebuild_task is None:
            self.__rebuild_task = asyncio.ensure_future(self.__delayed_rebuild())

    def allow_node_type(self, node_type_name: str):
        """Return True if this node type name should be included in the catalog model"""
        if node_type_name in PSEUDO_NODES_DICT:
            return True
        node_type = og.get_node_type(node_type_name)
        if node_type.get_metadata(ogn.MetadataKeys.HIDDEN):
            return False
        return True

    def _checked_get_graph_filter_from_category(self, category_tag: str) -> Optional[str]:
        """Helper to get the graph filter from the given category"""
        return graph_config.CategoryStyles._checked_get_graph_filter_from_category(  # noqa: protected-access
            category_tag
        )

    def __rebuild_node_list(self):
        """rebuild the node list from registered extensions"""
        registered_node_types = og.get_registered_nodes()
        # Create a mapping of category-nice-name -> [node types in that category]
        nodes_by_category = defaultdict(list)

        # Add the pseudo-nodes
        for pseudo_node in PSEUDO_NODES:
            node_type_name = pseudo_node.type_name
            nodes_by_category[pseudo_node.category].append(node_type_name)

        # Add the regular nodes.
        for node_type_name in registered_node_types:
            if not self.allow_node_type(node_type_name):
                continue

            node_type = og.get_node_type(node_type_name)
            category_metadata = node_type.get_metadata(ogn.MetadataKeys.CATEGORIES)
            if not category_metadata:
                categories = ["generic"]
            else:
                categories = category_metadata.split(",")
            # Remove the 'filter' categories since those are not to show up in catalog
            categories = [c for c in categories if self._checked_get_graph_filter_from_category(c) is None]
            # We only use the first category
            if categories:
                category = categories[0].split(":")[0]
                nodes_by_category[category].append(node_type_name)

        # Create a Group for each category
        self._children = []
        for category, node_type_names in nodes_by_category.items():
            self._children.append(ActionGroupItem(category, node_type_names))

        # Add the built-in category which has our 'special' entries that are not actually node types
        # FIXME: Subgraphs/Frames etc are not supported yet
        # self._children.append(GraphGroupItem())
        #
        # Keep the categories sorted by name
        self._children.sort(key=lambda gi: gi.name_model.as_string.lower())
        self._item_changed(None)

    def destroy(self):
        if self.__rebuild_task:
            self.__rebuild_task.cancel()
            self.__rebuild_task = None
        self._children = []
        self.extensions_subscription = None
        self.__registry_subscription = None

    def get_item_children(self, item) -> List[ActionNodeItem]:
        """Returns all the children when the widget asks it."""
        if item is None:
            return [c for c in self._children if c.visible]
        if isinstance(item, (ActionGroupItem, GraphGroupItem)):
            return [c for c in item.children if c.visible]
        return []

    def get_item_value_model_count(self, item):
        """The number of columns"""
        return 1

    def get_item_value_model(self, item, column_id) -> ui.SimpleStringModel:
        """
        Return value model for the given item and column
        """
        if column_id == self.Column.NAME.value:
            return item.name_model
        if column_id == self.Column.INFO.value:
            return ui.SimpleStringModel(" ".join(item.info_model.as_string.split("\n")))
        if column_id == self.Column.ICON.value:
            return item.icon_model
        if column_id == self.Column.TYPE.value:
            return ui.SimpleStringModel(item.info_model.as_string + "\n" + item.type_model.as_string.partition("\n")[0])
        if column_id == self.Column.CATEGORY.value:
            return item.category_model
        return None

    def get_drag_mime_data(self, item):
        """Returns data for be able to drop this item somewhere"""
        data = {
            "node_type": item.type_model.as_string,
            "node_name": self.get_item_value_model(item, self.Column.NAME.value).as_string,
        }
        return json.dumps(data) if data["node_type"] else ""

    def filter_by_text(self, filter_name_text: str):
        """Specify the filter string that is used to reduce the model"""
        for c in self._children:
            c.prefilter(filter_name_text.lower())
        self._item_changed(None)


# This class is not used by omni.graph.window.core as it does not register itself with QuickSearch and
# omni.graph.window.action and omni.graph.window.generic each have their own versions of this class.
# It remains here just in case there are downstream extensions which use it.
class OmniGraphNodeQuickSearchModel(OmniGraphNodeTypeCatalogModel):
    """
    The quick search node model that returns all the children from OmniGraphNodeTypeCatalogModel.
    """

    def execute(self, item):
        """The user pressed enter"""
        # Mime Data has the information about USD types.
        data = self.get_drag_mime_data(item)
        if not data:
            return

        from .extension import OmniGraphWindowCoreExtension

        OmniGraphWindowCoreExtension.add_node(data)
