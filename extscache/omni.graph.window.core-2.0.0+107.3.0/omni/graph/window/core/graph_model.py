# noqa: too-many-lines

# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["OmniGraphModel"]

import asyncio
import collections
import re
from contextlib import contextmanager, suppress
from enum import Enum, IntEnum, auto
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import carb
import carb.events
import carb.input
import omni.graph.core as og
import omni.graph.tools as ogt
import omni.graph.tools.ogn as ogn
import omni.kit

# run_coroutine doesn't exist in Kit 104.2 (only Kit 105 and onwards),
# so to maintain backwards compatibility for this extension the below
# try-except clause has been added.
import omni.kit.app

with suppress(ImportError):
    from omni.kit.async_engine import run_coroutine

import omni.usd
import OmniGraphSchema
from omni.kit.widget.graph import (  # pylint: disable=ungrouped-imports
    GraphModel,
    GraphModelBatchPositionHelper,
    IsolationGraphModel,
    SelectionGetter,
)
from pxr import Sdf, Tf, Usd, UsdUI

from . import graph_config
from .catalog_model import PSEUDO_NODES_DICT
from .compounds import CompoundUtils
from .virtual_node_helper import VirtualNodeHelper

OMNIGRAPH_TYPE = "OmniGraph"

LEGACY_COMPUTEGRAPHSETTINGS_TYPE = "ComputeGraphSettings"
LEGACY_COMPUTEGRAPH_TYPE = "ComputeGraph"
LEGACY_PRIM_TYPE = "omni.graph.core.Prim"
USDUI_NODEGRAPHNODE_ATTR_PREFIX = str(UsdUI.Tokens.uiNodegraphNodePos)[
    : str(UsdUI.Tokens.uiNodegraphNodePos).rfind(":") + 1
]

EMPTY_PORT_NAME = "Add Port"

# List of nodes that cannot be minimized or closed
NOT_EXPANDABLE_NODE_TYPES = ["omni.graph.core.ReadVariable", "omni.graph.instancing.ReadGraphVariable"]

# Change this to True to log UsdNotification Receiving and Processing
_NOTIFY_DEBUG = False


class PrimNodeType(Enum):
    """The prim 'drop' creation options"""

    READ_ATTRIBUTES = auto()
    WRITE_ATTRIBUTES = auto()
    READ_ATTRIBUTE = auto()
    WRITE_ATTRIBUTE = auto()
    READ_BUNDLE = auto()
    LEGACY = auto()


# The (node type, node-instance suffix) for prim drop option
prim_node_types = {
    PrimNodeType.READ_ATTRIBUTES: ("omni.graph.nodes.ReadPrim", "Read"),
    PrimNodeType.WRITE_ATTRIBUTES: ("omni.graph.nodes.WritePrim", "Write"),
    PrimNodeType.READ_ATTRIBUTE: ("omni.graph.nodes.ReadPrimAttribute", "ReadAttrib"),
    PrimNodeType.WRITE_ATTRIBUTE: ("omni.graph.nodes.WritePrimAttribute", "WriteAttrib"),
    PrimNodeType.READ_BUNDLE: ("omni.graph.nodes.ReadPrimBundle", "ReadBundle"),
    PrimNodeType.LEGACY: (LEGACY_PRIM_TYPE, None),
}

_usd_expansion_state_to_og = {
    UsdUI.Tokens.closed: GraphModel.ExpansionState.CLOSED,
    UsdUI.Tokens.open: GraphModel.ExpansionState.OPEN,
    UsdUI.Tokens.minimized: GraphModel.ExpansionState.MINIMIZED,
}

_og_expansion_state_to_usd = {og: usd for usd, og in _usd_expansion_state_to_og.items()}


def _get_path(item: Union[Usd.Prim, Sdf.Path]) -> Optional[Sdf.Path]:
    if isinstance(item, Sdf.Path):
        return item
    if hasattr(item, "GetPath") and callable(item.GetPath):
        return item.GetPath()
    return None


class PathToGraphMap(collections.UserDict):
    """Dict of [Prim Path, Graph Path] which manages node subscriptions for the model"""

    def __init__(self, *args, **kwargs):
        """Expects a kwarg model:OmniGraphModel"""
        self._model: GraphModel = kwargs.pop("model")
        self._subscriptions: Dict[Sdf.Path, Any] = {}
        super().__init__(*args, **kwargs)

    def __del__(self):
        """Validates all subscriptions are removed"""
        if self._model is not None:
            self.destroy()

    def destroy(self):
        """Called to clean up"""
        self._model = None
        for _, sub in self._subscriptions.items():
            sub.unsubscribe()
        self._subscriptions.clear()
        self._subscriptions = None

    def __delitem__(self, key):
        sub = self._subscriptions.pop(key, None)
        if sub:
            sub.unsubscribe()
        self.data.pop(key)

    def __setitem__(self, key, value):
        self.data[key] = value
        if not self._model.is_pseudo_node(key):
            node = og.get_node_by_path(key.pathString)
            if node:
                sub = self._subscriptions.pop(key, None)
                if sub:
                    sub.unsubscribe()
                sub = node.get_event_stream().create_subscription_to_pop(self.__on_node_event)
                self._subscriptions[key] = sub

    def __on_node_event(self, event: og.NodeEvent):
        """Callback from OG on certain node changes"""

        if self._model is None or self._model._graph_root is None:  # noqa: PLW0212
            return

        if (event.type == int(og.NodeEvent.CREATE_ATTRIBUTE)) or (event.type == int(og.NodeEvent.REMOVE_ATTRIBUTE)):
            self._model._on_node_attribute_change()  # noqa: protected-access
        elif event.type == int(og.NodeEvent.ATTRIBUTE_TYPE_RESOLVE):
            node_path = Sdf.Path(event.payload["node"])
            self._model._on_node_attribute_resolve(node_path)  # noqa: protected-access


@contextmanager
def no_undo():
    """Execute commands without leaving any entries in the undo stack.
    For Kit 104 and later use omni.kit.undo.disabled() instead.

    This function is a context manager.

    Example:

    .. code-block:: python

        with no_undo():
            omni.kit.commands.execute("Foo1")
            omni.kit.commands.execute("Foo2")
    """

    stack = omni.kit.undo.get_undo_stack()
    undo_count = len(stack)
    omni.kit.undo.begin_group()
    try:
        yield
    finally:
        omni.kit.undo.end_group()
        while len(stack) > undo_count:
            stack.pop()


class OmniGraphModel(GraphModel, GraphModelBatchPositionHelper):
    """The model to watch the OmniGraph action network"""

    class EventType(IntEnum):
        """Types of events dispatched by OmniGraphModel to its event stream."""

        # Payload: path_str: string - Path to the added node.
        NODE_ADDED = carb.events.type_from_string("omni.graph.window.core@node_added")

        # Payload: path_str: string - Path to the removed node.
        NODE_REMOVED = carb.events.type_from_string("omni.graph.window.core@node_removed")

    def __init__(self, prim: Usd.Prim):
        super().__init__()

        # -------------------------------------------------------------
        # Public Members (anyone can access)

        # None

        # -------------------------------------------------------------
        # Protected Members (derived classes can access)
        self._usd_context = omni.usd.get_context()
        self._stage = self._usd_context.get_stage()
        self._graph_root = prim.GetPath()
        self._input = carb.input.acquire_input_interface()

        # find the current editing graph
        self._graph: og.Graph = None
        all_graphs = og.get_all_graphs()
        for graph in all_graphs:
            if graph.get_path_to_graph() == self._graph_root.pathString:
                self._graph = graph
                break

        # connections
        # {key: dest_port_path, value: source_port_paths}. Execution connections allow multiple inputs (fan-in)
        self._connections: Dict[Sdf.Path, Set(Sdf.Path)] = {}
        # {key: source_port_path, value: dest_port_paths}
        self._reversed_connections: Dict[Sdf.Path, Set(Sdf.Path)] = {}
        # this is for delegate to show only connected ports
        # {key: node_path, value: connected_ports}
        self._node_connected_ports: Dict[Sdf.Path, Set(Sdf.Path)] = {}

        # -------------------------------------------------------------
        # Private Members (no-one except this class can access)

        (self.__kit_version_major, _) = og.get_kit_version()
        self.__is_pre_schema_graph = not bool(OmniGraphSchema.OmniGraph(prim))

        # nodes
        # This is the key attribute, used to define the existence of the nodes
        # all nodes paths in the graph are keyed, include subgraph
        # {key: prim_path, value: subgraph_path}
        self.__primpath_to_subgraph = PathToGraphMap(model=self)
        # {key: subgraph_path, value: Set[prim_path_in_subgraph]}
        self.__subgraph_to_primpaths: Dict[Sdf.Path, Set(Sdf.Path)] = {}

        # Duplicated prims.
        # {key: duplicate_path, value: original_path}
        self.__duplicated_prims: List[Dict[Sdf.Path, Sdf.Path]] = [{}, {}]

        # node position
        self.__positions: Dict[Sdf.Path, Tuple[float]] = {}
        # Position before the user drags the node
        self.__positions_on_begin: Dict[Sdf.Path, Tuple[float]] = {}
        # True when omni.kit.undo.begin_group() is called and
        # omni.kit.undo.end_group() is not called
        self.__set_position_group = False

        # node size
        self.__sizes: Dict[Sdf.Path, Tuple[float]] = {}
        # Size before the user resizes the node.
        self.__sizes_on_begin: Dict[Sdf.Path, Tuple[float]] = {}

        # node expansion states
        self.__node_states: Dict[Union[Usd.Prim, Sdf.Path], self.ExpansionState] = {}

        # list of nodes that cannot be minimized or closed
        self.__non_expansion_node_types = set(NOT_EXPANDABLE_NODE_TYPES)

        # subgraph
        self.__subgraph_paths: Set(Sdf.Path) = set()

        # ports
        # {key: node_path, value: {node_path: {"inputs": List(Sdf.Path), "outputs": List(Sdf.Path),
        # "outputOnly_inputs": List(Sdf.Path), "execution_inputs": List(Sdf.Path), "execution_outputs": set(Sdf.Path)}}}
        self.__ports_categories: Dict[Sdf.Path, Dict[str, List[Sdf.Path]]] = {}
        # this is created to cache the subgraph port type which does not exist in og
        # {key: port_path, value: port_type}
        self.__subgraph_port_map: Dict[Sdf.Path, str] = {}

        # selection
        self.__selection = self._usd_context.get_selection()
        __events = self._usd_context.get_stage_event_stream()
        self.__stage_selection_subscription = __events.create_subscription_to_pop(
            self.__on_stage_event, name="OmniGraphModel stage Watch"
        )
        assert self.__stage_selection_subscription  # This is mostly to avoid lint complaints.

        self.add_get_moving_items_fn(SelectionGetter(self))

        # sync
        # Collection of prims that have been resynced since the last update
        self.__dirty_prim_paths: List[List[Sdf.Path]] = [[], []]
        # Collection of properties that have been resynced since the last update
        self.__dirty_prop_paths: List[List[Sdf.Path]] = [[], []]
        # Collection of properties which have changed value (or connections) only since the last update
        self.__info_changed_prop_paths: List[List[Sdf.Path]] = [[], []]
        # Double buffered index - the dirty frame index is the index currently being written to.
        # self.__update_frame_index is the index used to update the graph model
        self.__dirty_frame_index = 0
        self.__update_frame_index = 1

        # The async task for processing pending graph changes
        self.__prim_changed_task: List[asyncio.Task] = [None, None]
        # Callback from graph for node error/warning status changes.
        self.__node_status_change_cb = None
        # List of nodes which need to be redrawn due to changes that Kit's graph widget doesn't recognize.
        self.__nodes_requiring_redraw: List[Set[og.Node]] = [set(), set()]
        # We use _rebuild_node() to redraw a single node. However it currently can only handle a subset of
        # potential changes in the way a node is drawn (e.g. it cannot redraw ports).
        # For those cases we have to redraw the entire graph.
        self.__full_redraw_required = [False, False]
        # subscription to graph events
        self.__on_graph_event_sub = None
        # registered callbacks
        self.__on_graph_event_callback = None

        self.__event_stream = carb.events.get_events_interface().create_event_stream("OmniGraphModel")

        if self._stage:
            self.__stage_listener = Tf.Notice.Register(
                Usd.Notice.ObjectsChanged, self.__on_objects_changed, self._stage
            )
            assert self.__stage_listener  # This is mostly to avoid lint complaints.
        else:
            carb.log_error("Failed to get the current stage for omni graph model")

        # USD notifications are insufficient to sort out node/prim duplication
        # so we watch specifically for those.
        self.__pre_dupe_cb = omni.kit.commands.register_callback(
            "CopyPrim", omni.kit.commands.PRE_DO_CALLBACK, self.__on_begin_duplicate
        )

        # cache all the graph nodes and connection
        if self._graph:
            self.__on_graph_event_sub = self._graph.get_event_stream().create_subscription_to_pop(self._on_graph_event)
            assert self.__on_graph_event_sub  # This is mostly to avoid lint complaints.

            # We don't want listeners acting on changes until we're done.
            with Sdf.ChangeBlock():
                self.__node_status_change_cb = self._graph.register_error_status_change_callback(
                    self.__on_node_status_changed
                )
                self.cache_graph()
        else:
            carb.log_error(f"Unable to set current editor graph to {self._graph_root}: No such graph found")

    def destroy(self):
        """Called when window is destroyed to clean up"""
        # nodes

        # sync
        if self.__stage_listener:
            self.__stage_listener.Revoke()
            self.__stage_listener = None

        if self.__prim_changed_task[0]:
            self.__prim_changed_task[0].cancel()
            self.__prim_changed_task[0] = None

        if self.__prim_changed_task[1]:
            self.__prim_changed_task[1].cancel()
            self.__prim_changed_task[1] = None

        if self.__primpath_to_subgraph:
            self.__primpath_to_subgraph.destroy()
        self.__primpath_to_subgraph = None

        self.__subgraph_to_primpaths = {}
        self.__positions = {}
        self.__positions_on_begin = {}
        self.__sizes = {}
        self.__sizes_on_begin = {}
        self.__node_states = {}

        # connections
        self._connections = {}
        self._reversed_connections = {}
        self._node_connected_ports = {}
        # ports
        self.__ports_categories = {}
        self.__subgraph_port_map = {}
        # subgraph
        self.__subgraph_paths = set()
        # selection
        self.__selection = None
        self.__stage_selection_subscription = None

        self.__event_stream = None
        self.__dirty_prim_paths.clear()
        self.__dirty_prop_paths.clear()
        self.__info_changed_prop_paths.clear()

        if self._graph:
            self._graph.deregister_error_status_change_callback(self.__node_status_change_cb)
        self.__node_status_change_cb = None
        self.__on_graph_event_sub = None
        self.__on_graph_event_callback = None

        if self.__pre_dupe_cb:
            omni.kit.commands.unregister_callback(self.__pre_dupe_cb)
        self.__pre_dupe_cb = None

        self._graph = None
        self._graph_root = None

    # Returns the name of the node/prim/attribute passed to it.
    # If a prim is passed and the 'showNameAsType' setting is true then the node's "nice" type name will
    # be returned. A bit hacky, but we're trying to stay within the constraints of modern delegate as much
    # as possible.
    @property
    def name(self, item: Union[og.Node, Usd.Prim, Sdf.Path] = None):  # noqa: property-with-parameters
        # If this is a compound subgraph, use the compound name rather than the graph name
        if isinstance(item, Usd.Prim) and graph_config.Supports.compound_subgraphs():
            compound = CompoundUtils.owning_compound_node(item)
            if compound is not None:
                return compound.GetPath().name

        def is_legacy_or_compound(node):
            return (node.get_node_type() and node.get_type_name() == LEGACY_PRIM_TYPE) or (
                graph_config.Supports.compound_subgraphs() and node.is_compound_node()
            )

        # nodes
        if isinstance(item, og.Node):
            return Sdf.Path(item.get_prim_path()).name
        if isinstance(item, Usd.Prim):
            name = item.GetPath().name
            if graph_config.Settings.get_show_name_as_type():
                node = self._graph.get_node(item.GetPath().pathString)
                # Two exceptions to the show_name_as_type setting:
                # 1. Users who have legacy prims enabled aren't going to want to see them all labelled as 'Prim'
                # 2. Compounds should show their name, which will (hopefully) be more descriptive than "Compound
                #    Subgraph"
                if node and not is_legacy_or_compound(node):
                    ui_name = node.get_node_type().get_metadata(ogn.MetadataKeys.UI_NAME)
                    if ui_name:
                        name = ui_name
                    else:
                        type_name_without_namespace = node.get_type_name().split(".")[-1]
                        name = graph_config.make_nice_name(type_name_without_namespace)
            return name
        # ports
        if isinstance(item, Sdf.Path):
            return item.name
        # The base view and delegate may rely on this returning None, so don't add a fallback
        # result here.
        return None

    @name.setter
    def name(self, value, item: Union[og.Node, Usd.Prim, Sdf.Path]):
        if isinstance(item, Usd.Prim):
            # We assume we are renaming the og.Node or Pseudo-node
            old_path: Sdf.Path = item.GetPath()
            new_path = old_path.GetParentPath().AppendChild(value)
            if old_path != new_path:
                try:
                    node = og.Controller.node(old_path)
                except og.OmniGraphValueError:
                    carb.log_error(f"Cannot rename {old_path}, only nodes can be renamed")
                    return
                omni.kit.commands.execute(
                    "RenameNodeCommand", graph=node.get_graph(), path=str(old_path), new_path=str(new_path)
                )

        # ports
        elif isinstance(item, Sdf.Path):
            attr = og.Controller.attribute(str(VirtualNodeHelper.convert_from(item)))
            port_type = attr.get_port_type()
            is_bundle = attr.get_resolved_type().role == og.AttributeRole.BUNDLE
            name_without_namespace = og.Attribute.remove_port_type_from_name(value, is_bundle)
            name = CompoundUtils.sanitize_attribute_name(
                name_without_namespace, attr.get_node(), port_type, is_bundle, attr.get_name()
            )
            if not name:
                carb.log_error(f"{value} is not an valid attribute name")
            # only rename if new name is different
            elif name != og.Attribute.remove_port_type_from_name(
                attr.get_name(), attr.get_resolved_type().role == og.AttributeRole.BUNDLE
            ):
                og._unstable.cmds.RenameCompoundSubgraphAttribute(  # noqa: protected-access
                    attribute=attr, new_name=name
                )

    @property
    def nice_name(self, item=None) -> Optional[str]:  # noqa: property-with-parameters
        # nodes
        if isinstance(item, Usd.Prim):
            if graph_config.Settings.get_show_name_as_type():
                node = self._graph.get_node(item.GetPath().pathString)
                if node and node.get_node_type():
                    ui_name = node.get_node_type().get_metadata(ogn.MetadataKeys.UI_NAME)
                    if ui_name:
                        return ui_name
            name = item.GetPath().name
            return graph_config.make_nice_name(name, False)
        # ports
        if isinstance(item, Sdf.Path):
            attr = self.get_attribute_from_path(item)
            custom_name = attr and attr.get_metadata(ogn.MetadataKeys.UI_NAME)
            if custom_name:
                return graph_config.make_nice_name(custom_name, True)

            # For attributes, remove namespaces and bundle prefixes
            if attr:
                name = og.Attribute.remove_port_type_from_name(
                    item.name, attr.get_resolved_type().role == og.AttributeRole.BUNDLE
                )
                return graph_config.make_nice_name(name, False)
            return graph_config.make_nice_name(item.name, False)

        # IsolationGraphModel doesn't currently support the 'nice_name' property, so we need to deal
        # with its EmptyPort ourselves.
        if isinstance(item, IsolationGraphModel.EmptyPort):
            return EMPTY_PORT_NAME
        # We replicate the fall-through behavior of the 'name' property above in the expectation that 'nice_name'
        # support will be added to the omni.kit.widget.graph in the future.
        return None

    def __allow_multi_inputs(self, attr: og.Attribute) -> bool:
        # This is a hack to make the repo tests succeed until kit-graphs can refer to it version 104
        metadata_key = "allowMultiInputs"
        if "ALLOW_MULTI_INPUTS" in ogn.MetadataKeys.__dict__:
            metadata_key = ogn.MetadataKeys.ALLOW_MULTI_INPUTS
        if attr.get_metadata(metadata_key) == "1":
            return True
        return False

    def __node_type_name(self, prim: Usd.Prim) -> Optional[str]:
        if prim and isinstance(prim, Usd.Prim):
            if self.is_pseudo_node(prim):
                return prim.GetTypeName()
            node = self._graph.get_node(prim.GetPath().pathString)
            if node and node.get_node_type():
                return node.get_type_name()
        return None

    @property
    def type(self, item=None) -> Optional[str]:  # noqa: property-with-parameters, A003
        """For OG Nodes this is the OG node type, for ports it is a description of the OG type,
        including the resolution state"""
        if isinstance(item, Usd.Prim):
            return self.__node_type_name(item)
        if isinstance(item, Sdf.Path):
            return self.get_port_type(item)
        return None

    @property
    def node_type_name(self, item) -> Optional[str]:  # noqa: property-with-parameters
        """return node type name"""
        return self.__node_type_name(item)

    @property
    def description(self, item):  # noqa: property-with-parameters
        if self[item].type in ["Backdrop", "OmniNote"]:
            if self[item].type == "Backdrop":
                prim = UsdUI.Backdrop(item)
                description_attr = prim.GetDescriptionAttr()
            elif self[item].type == "OmniNote":
                description_attr = item.GetAttribute(UsdUI.Tokens.uiDescription)
            if description_attr:
                return description_attr.Get()
        return None

    @description.setter
    def description(self, value, item=None):
        if self[item].type in ["Backdrop", "OmniNote"]:
            prop_path = item.GetPath().AppendProperty(UsdUI.Tokens.uiDescription)
            omni.kit.commands.execute(
                "ChangePropertyCommand",
                prop_path=prop_path,
                value=value,
                prev=None,
                type_to_create_if_not_exist=Sdf.ValueTypeNames.Token,
            )

    def is_output(self, item=None) -> bool:
        attr = None
        if isinstance(item, Sdf.Path):
            prim_path = item.GetPrimPath()
            if self.is_graph(prim_path) and prim_path in self.__ports_categories:
                is_output = item in self.__ports_categories[prim_path]["outputs"]
                is_input = item in self.__ports_categories[prim_path]["inputs"]
                if is_output or is_input:
                    return is_output
            attr = self.get_attribute_from_path(item)
        elif isinstance(item, og.Attribute):
            attr = item
        else:
            return False

        if attr and attr.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT:
            return True
        return False

    def is_execution(self, item=None) -> bool:
        attr = None
        if isinstance(item, Sdf.Path):
            prim_path = item.GetPrimPath()
            if (
                self.is_graph(prim_path)
                and prim_path in self.__ports_categories
                and (
                    item in self.__ports_categories[prim_path]["execution_inputs"]
                    or item in self.__ports_categories[prim_path]["execution_outputs"]
                )
            ):
                return True
            attr = self.get_attribute_from_path(item)
        elif isinstance(item, og.Attribute):
            attr = item
        else:
            return False

        if attr and attr.get_resolved_type().role == og.AttributeRole.EXECUTION:
            return True
        return False

    @property
    def is_execution_pin(self, item=None):  # noqa: property-with-parameters
        return self.is_execution(item)

    def port_tooltip_text(self, item: Sdf.Path) -> str:
        """Return the text content of a tooltip for the given port"""
        indent = "   "
        indent_newline = "\n" + indent
        attrib = self.get_attribute_from_path(item)
        if attrib:
            tip = f"{item.name} ({self.get_port_type(item)})"
            description = attrib.get_metadata(ogn.MetadataKeys.DESCRIPTION)
            if description:
                # line endings indicate pre-formatted text
                if "\n" in description:
                    description_lines = description.splitlines()
                else:
                    description_lines = ogt.shorten_string_lines_to(description, 80)
                tip = f"{tip}\n{indent}{indent_newline.join(description_lines)}"
            if self.__allow_multi_inputs(attrib):
                tip = f"{tip}\n\nSupports multiple inputs."
            if hasattr(attrib, "target_mapping") and attrib.target_mapping:
                tip = f"{tip}\n\nGraph Target Mapping: {attrib.target_mapping}"
            return tip
        return ""

    def cull_legacy_prims(self):
        """Return True if the OgnPrim nodes should not be created in the graph"""
        return graph_config.Settings.cull_legacy_prims()

    def cache_graph(self):
        """Cache the nodes and connections, including subgraphs/compounds"""
        if self._graph:

            # Reset the cached connections. Otherwise as we are walking the compound hierarchy,
            # we can get stale values for the connections
            if self.__primpath_to_subgraph:
                self.__primpath_to_subgraph.destroy()
            self.__primpath_to_subgraph = PathToGraphMap(model=self)
            self.__subgraph_to_primpaths: Dict[Sdf.Path, Set(Sdf.Path)] = {}
            self._connections: Dict[Sdf.Path, Set(Sdf.Path)] = {}
            self._reversed_connections: Dict[Sdf.Path, Set(Sdf.Path)] = {}
            self._node_connected_ports: Dict[Sdf.Path, Set(Sdf.Path)] = {}
            self.__ports_categories: Dict[Sdf.Path, Dict[str, List[Sdf.Path]]] = {}

            # cache the node first
            self.cache_nodes(self._graph)
            # then connections. we can't cache connections while caching nodes, since the nodes might not exist,
            # so we won't be able to create port in that case
            for path in self.__primpath_to_subgraph.keys():
                self.cache_connections(path.pathString)

    # only called when importing nodes
    def cache_nodes(self, graph):
        results = set()
        graph_path = Sdf.Path(graph.get_path_to_graph())

        if graph_config.Settings.are_compounds_enabled():
            for sub_graph in CompoundUtils.get_compound_graphs(graph):
                sub_graph_path = Sdf.Path(sub_graph.get_path_to_graph())
                self.__subgraph_paths.add(sub_graph_path)
                results.add(sub_graph_path)
                self.__primpath_to_subgraph[sub_graph_path] = graph_path
                self.cache_nodes(sub_graph)

        # Get any pseudo-nodes parented under this graph.
        graph_prim = self._stage.GetPrimAtPath(graph_path)
        if graph_prim:
            for child in graph_prim.GetChildren():
                if self.is_pseudo_node(child):
                    child_path = child.GetPath()
                    results.add(child_path)
                    self.__primpath_to_subgraph[child_path] = graph_path

        for node in graph.get_nodes():
            # Don't auto populate legacy prims
            if self.cull_legacy_prims() and (node.get_type_name() == LEGACY_PRIM_TYPE):
                continue

            # cache the subgraph port map here instead of in cache connections
            # as they may be unconnected, but they should still have a port
            if graph_config.Settings.are_compounds_enabled() and node.is_compound_node():
                for src_attr in node.get_attributes():
                    if (
                        src_attr.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
                        or src_attr.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
                    ):
                        new_attr_path = VirtualNodeHelper.convert_to(Sdf.Path(src_attr.get_path()))
                        self.__subgraph_port_map[new_attr_path] = str(
                            self.get_usd_port_type(Sdf.Path(src_attr.get_path()))
                        )
                        self._create_port_ui(
                            new_attr_path,
                            self.is_execution(src_attr),
                            self.is_output(src_attr),
                            src_attr.get_metadata(ogt.ogn.MetadataKeys.OUTPUT_ONLY) == "1",
                        )

            # TODO: Workaround for OM-44798, which leaves invalid legacy prim nodes in the graph
            #       after their underlying USD prims have been deleted.
            try:
                prim = og.Controller.prim(node)
            except og.OmniGraphError:
                continue
            if not prim.IsValid():
                continue

            prim_path = Sdf.Path(node.get_prim_path())
            results.add(prim_path)
            self.__primpath_to_subgraph[prim_path] = graph_path

        self.__subgraph_to_primpaths[graph_path] = results

    @property
    def nodes(self, item: Optional[Usd.Prim] = None):  # noqa: property-with-parameters
        """
        Get the nodes from the current graph/subgraph and cache the nodes/ports

        Args:
            item(Usd.Prim): The primitive representing the root of the sub-graph, or None to access all
            nodes in the model.

        Returns:
            A set of USD.Prims that represent nodes in the graph
        """
        # invalid expired prim
        if (item is not None) and (not item.IsValid()):
            return None

        return [self._stage.GetPrimAtPath(path) for path in self.__non_hidden_nodes(item)]

    def __all_nodes(self, item: Optional[Usd.Prim] = None):
        """
        Get the list of all nodes, as Sdf.Paths, in the current graph

        Args:
            item(Usd.Prim): The primitive representing the root of the sub-graph to retrieve, or None to access all
            nodes in the model.

        Returns:
            A set of Sdf.Paths that represent nodes in the graph
        """
        if not self._stage:
            return set()
        if not item and self._graph_root:
            item = self._stage.GetPrimAtPath(self._graph_root)
        if not isinstance(item, Usd.Prim):
            return set()

        graph_path = item.GetPath()
        if not self._graph or not self._graph.is_valid():
            return set()
        subgraph = self._graph.get_subgraph(graph_path.pathString)
        if not subgraph or not subgraph.is_valid():
            graph_path = self._graph_root

        return self.__subgraph_to_primpaths.get(graph_path, set())

    def __non_hidden_nodes(self, item: Optional[Usd.Prim] = None):
        """
        Get the list of nodes, as Sdf.Paths, that are not marked as hidden in the current graph.

        Args:
            item(Usd.Prim): The primitive representing the root of the sub-graph to retrieve, or None to access all
            nodes in the model.

        Returns:
            An iterable of Sdf.Paths that represent nodes in the graph
        """

        def is_node_hidden(path):
            node = self._graph.get_node(path.pathString)
            return not node.is_valid()  # This could also check if the prim itself has hidden metadata.

        return filter(lambda path: self.is_pseudo_node(path) or not is_node_hidden(path), self.__all_nodes(item))

    def allow_multiple_inputs(self, item: Optional[Union[og.Attribute, Sdf.Path, Usd.Prim]] = None) -> bool:
        """
        Args:
            item(Optional[Union[og.Attribute, Sdf.Path, Usd.Prim]]): The item whose attribute to check if it allows multiple inputs.

        Returns:
            (bool): True if the item supports multiple inputs.
        """
        if self.is_execution(item):
            return True

        attr = None
        if isinstance(item, Sdf.Path):
            attr = self.get_attribute_from_path(item)
        elif isinstance(item, og.Attribute):
            attr = item

        if attr:
            if self.__allow_multi_inputs(attr):
                return True

            if len(attr.get_upstream_connections()) > 1:
                carb.log_warn(
                    f"Attribute {item} has more than one upstream connection without 'allowMultiInputs' metadata. "
                    "Add metadata to allow multiple connections in the graph editor."
                )

        return False

    def cache_connections(self, node_string: str):
        """
        Cache all the connections for each node. Compounds are dealt with explicitly by checking the ingoing and outgoing
        connections of the nodes
        """
        if self.is_pseudo_node(Sdf.Path(node_string)):
            return
        node = self._graph.get_node(node_string)
        if not node.is_valid():
            return

        attributes = node.get_attributes()

        for attr in attributes:
            if not attr.is_valid():
                continue

            # Check upstream connections.
            attr_node = attr.get_node()
            attr_graph = attr_node.get_graph()
            attr_path = self.get_path_from_attribute(attr)

            for conn in attr.get_upstream_connections():

                src_attr_path = self.get_path_from_attribute(conn)

                src_node = conn.get_node()
                src_graph = src_node.get_graph()

                # connection in the same graph
                if attr_graph == src_graph:
                    self.connect_attribute_ui(src_attr_path, attr_path)
                    continue

                # compounds not enabled, skip
                if not graph_config.Settings.are_compounds_enabled():
                    continue

                # Connection is to a compound node. Treat it as a connection to the compound graph.
                # The resulting virtual nodes will 'represent' the compound graph
                if src_node.is_compound_node() and src_node.get_compound_graph_instance() == attr_graph:
                    new_port_path = attr_graph.get_path_to_graph()
                    new_attr_path = Sdf.Path(new_port_path).AppendProperty(Sdf.Path(src_attr_path).name)
                    self.connect_attribute_ui(new_attr_path, attr_path)

            # only check downstream connections for compounds, as other downstream connections are handled by being
            # upstream connections on the other node
            if not graph_config.Settings.are_compounds_enabled():
                continue

            for dest in attr.get_downstream_connections():
                dest_node = dest.get_node()

                # the connection is the destination port on a compound node
                if dest_node.is_compound_node():
                    if dest_node.get_compound_graph_instance() == attr_graph:
                        new_port_path = attr_graph.get_path_to_graph()
                        new_attr_path = Sdf.Path(new_port_path).AppendProperty(Sdf.Path(dest.get_path()).name)
                        self.connect_attribute_ui(attr_path, new_attr_path)

                    # this is a self connection, which is valid for a compound node between input and outputs
                    if dest_node == attr_node and dest.get_port_type() != attr.get_port_type():
                        self.connect_attribute_ui(attr_path, self.get_path_from_attribute(dest))

    @property
    def connected_ports(self, item=None):  # noqa: property-with-parameters
        """Get the connected ports for the input node"""
        if not isinstance(item, Usd.Prim):
            return set()

        return self._node_connected_ports.get(item.GetPath(), set())

    @property
    def ports(self, item=None):  # noqa: property-with-parameters
        if not isinstance(item, Usd.Prim) or not self._graph or not self._graph.is_valid():
            return []

        node_path = item.GetPath()
        if not self.is_graph(node_path):
            node = self._graph.get_node(node_path.pathString)
            if not node or not node.is_valid() or not node.is_backed_by_usd():
                return []
            # process attributes
            is_legacy_prim = node.get_type_name() == LEGACY_PRIM_TYPE
            for a in node.get_attributes():
                if self.__kit_version_major >= 105:
                    # ignore literalOnly ports because they are not connectable
                    literal_only = a.get_metadata(ogn.MetadataKeys.LITERAL_ONLY)
                    if literal_only is not None:
                        continue

                attr_name = a.get_name()
                # ignore node or state ports
                if (
                    attr_name.startswith("node:")
                    or attr_name.startswith("state:")
                    or attr_name.startswith(USDUI_NODEGRAPHNODE_ATTR_PREFIX)
                ):
                    continue

                # ignore the hidden port
                hidden = a.get_metadata(ogn.MetadataKeys.HIDDEN)
                if hidden is not None:
                    continue

                # ignore the node-as-bundle output for non-Prim nodes
                if (
                    (not is_legacy_prim)
                    and (attr_name == node_path.name)
                    and (a.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)
                ):
                    continue

                # Give input attr an output port?
                output_only = a.get_metadata(ogn.MetadataKeys.OUTPUT_ONLY) == "1"

                port_path = node_path.AppendProperty(attr_name)
                self._create_port_ui(port_path, self.is_execution(a), self.is_output(a), output_only)

        if node_path in self.__ports_categories:
            ports = self.__ports_categories[node_path]
            return (
                ports["execution_inputs"]
                + ports["execution_outputs"]
                + ports["inputs"]
                + ports["outputOnly_inputs"]
                + ports["outputs"]
            )
        return []

    @property
    def inputs(self, item):  # noqa: property-with-parameters
        if not isinstance(item, Sdf.Path):
            return None

        # check if the port is an input
        node_path = item.GetPrimPath()
        if node_path not in self.__ports_categories:
            return None

        ports = self.__ports_categories[node_path]
        if item not in ports["inputs"] + ports["execution_inputs"]:
            return None

        result = self._connections.get(item, None)
        if result:
            return list(result)
        return []

    def _can_disconnect(self, values: List[Sdf.Path], item: Union[og.Attribute, Sdf.Path, Usd.Prim]):
        """
        Returns true if the existing connections should be disconnected when adding a new one to item.

        Args:
            values(List[Sdf.Path]): The new connections to the item.
            item(Union[og.Attribute, Sdf.Path, Usd.Prim]): The item that the new connections are being dragged to.

        Returns:
            True if the existing connections to item should be disconnected.
        """
        # Don't perform a disconnection if we're creating a new execution connection
        is_execution_creation = bool(values) and self.is_execution(item)
        if is_execution_creation:
            return False

        # Don't disconnect if item is connected to multi-input and ctrl is down
        is_ctrl_down = self._input.get_keyboard_value(None, carb.input.KeyboardInput.LEFT_CONTROL) > 0
        if is_ctrl_down:
            if self.allow_multiple_inputs(item):
                return False
            for path in values:
                if self.allow_multiple_inputs(path):
                    return False

        return True

    def _create_subgraph_port_ui(
        self, new_attr_path: Sdf.Path, src_attr: og.Attribute, is_attr_output: bool, is_attr_output_only: bool
    ):
        """
        Helper function to update the UI for a new subgraph port.
        Args:
            new_attr_path:          The promoted attr on the compound subgraph
            src_attr:               The source attr inside the compound
            is_attr_output:         Is port an output?
            is_attr_output_only:    Output only inputs should be published as outputs
        """
        is_execution = self.is_execution(src_attr)
        self.__subgraph_port_map[new_attr_path] = str(self.get_usd_port_type(Sdf.Path(src_attr.get_path())))
        self._create_port_ui(new_attr_path, is_execution, is_attr_output, is_attr_output_only)

        if is_attr_output or is_attr_output_only:
            self.connect_attribute_ui(Sdf.Path(src_attr.get_path()), new_attr_path)
        else:
            self.connect_attribute_ui(new_attr_path, Sdf.Path(src_attr.get_path()))

    def _create_port_ui(self, port_path: Sdf.Path, is_execution: bool, is_output: bool, is_output_only: bool):
        node_path = port_path.GetPrimPath()
        if node_path not in self.__ports_categories:
            self.__ports_categories.update(
                {
                    node_path: {
                        "inputs": [],
                        "outputs": [],
                        "outputOnly_inputs": [],
                        "execution_inputs": [],
                        "execution_outputs": [],
                    }
                }
            )

        if is_execution:
            if is_output:
                if port_path not in self.__ports_categories[node_path]["execution_outputs"]:
                    self.__ports_categories[node_path]["execution_outputs"].append(port_path)
            else:
                if port_path not in self.__ports_categories[node_path]["execution_inputs"]:
                    self.__ports_categories[node_path]["execution_inputs"].append(port_path)
        elif is_output:
            if port_path not in self.__ports_categories[node_path]["outputs"]:
                self.__ports_categories[node_path]["outputs"].append(port_path)
        elif is_output_only:
            if port_path not in self.__ports_categories[node_path]["outputOnly_inputs"]:
                self.__ports_categories[node_path]["outputOnly_inputs"].append(port_path)
        else:
            if port_path not in self.__ports_categories[node_path]["inputs"]:
                self.__ports_categories[node_path]["inputs"].append(port_path)

    def remove_port_ui(self, port_path: Sdf.Path):
        node_path = port_path.GetPrimPath()

        try:
            # For compound subgraphs, the port is actually on the compound node, but it gets registered as if it was on
            # the subgraph itself, so need to re-map paths to the subgraph
            node = og.Controller.node(node_path)
            if node.is_valid() and graph_config.Supports.compound_subgraphs() and node.is_compound_node():
                port_path = VirtualNodeHelper.convert_to(port_path)
                node_path = port_path.GetPrimPath()
        except og.OmniGraphError:
            pass

        if node_path not in self.__ports_categories:
            return

        ports = self.__ports_categories[node_path]
        if port_path in ports["execution_inputs"]:
            ports["execution_inputs"].remove(port_path)
        if port_path in ports["execution_outputs"]:
            ports["execution_outputs"].remove(port_path)
        if port_path in ports["inputs"]:
            ports["inputs"].remove(port_path)
        if port_path in ports["outputOnly_inputs"]:
            ports["outputOnly_inputs"].remove(port_path)
        if port_path in ports["outputs"]:
            ports["outputs"].remove(port_path)

        if self.is_graph(node_path) and port_path in self.__subgraph_port_map:
            self.__subgraph_port_map.pop(port_path)

    def connect_attribute_ui(
        self, src_attr_path: Sdf.Path, dest_attr_path: Sdf.Path, connectable_check=False, compatibility_check=False
    ) -> bool:
        """connection for the ui purpose"""

        # if this is a self connection, convert it to the 'virtual' node form (i.e. subgraph form)
        if src_attr_path.GetPrimPath() == dest_attr_path.GetPrimPath():
            src_attr_path = VirtualNodeHelper.convert_to(src_attr_path)
            dest_attr_path = VirtualNodeHelper.convert_to(dest_attr_path)

        # cache the connection for the ui
        # if the connection already exist, no need to add again
        if src_attr_path in self._connections.get(dest_attr_path, set()):
            return False

        # Validate that the connections exists between nodes that are in this graph. This ignores
        # connections to nodes in compound graphs.
        if (
            src_attr_path.GetPrimPath() not in self.__primpath_to_subgraph
            or dest_attr_path.GetPrimPath() not in self.__primpath_to_subgraph
        ):
            return False

        # compatibility check
        if compatibility_check:
            src_attribute = self.get_attribute_from_path(src_attr_path)
            dest_attribute = self.get_attribute_from_path(dest_attr_path)
            if (not src_attribute) or (not dest_attribute):
                return False
            if not src_attribute.is_compatible(dest_attribute):
                carb.log_error(
                    f"Connection {src_attr_path} -> {dest_attr_path} rejected due to mismatched types. "
                    f"Source type is '{self.__get_attribute_type_description(src_attribute)}', destination type is"
                    f" '{self.__get_attribute_type_description(dest_attribute)}'"
                )
                return False

        # ---
        # Two cases to check for with compound inputs and output nodes for remapping
        # Compound Node Input to Compound Graph Input
        # Compound Graph Output to Compound Node Output
        if src_attr_path.GetPrimPath().GetParentPath() != dest_attr_path.GetPrimPath().GetParentPath():
            # convert to the appropriate virtual node paths
            src_attr_path, dest_attr_path = VirtualNodeHelper.convert_connection(src_attr_path, dest_attr_path)

        # Some attributes allow multiple inputs (fan-in connections)
        if self.allow_multiple_inputs(dest_attr_path):
            self._connections[dest_attr_path] = self._connections.get(dest_attr_path, set()) | {src_attr_path}
        else:
            self._connections[dest_attr_path] = {src_attr_path}
        self._reversed_connections[src_attr_path] = self._reversed_connections.get(src_attr_path, set()) | {
            dest_attr_path
        }

        # cache the connected ports for nodes
        src_node_path = src_attr_path.GetPrimPath()
        self._node_connected_ports[src_node_path] = self._node_connected_ports.get(src_node_path, set()) | {
            src_attr_path
        }
        dest_node_path = dest_attr_path.GetPrimPath()
        self._node_connected_ports[dest_node_path] = self._node_connected_ports.get(dest_node_path, set()) | {
            dest_attr_path
        }
        return True

    def disconnect_attribute_ui(self, dest_attr_path: Sdf.Path):
        # for compounds this will return the appropriate representation for destination ports
        dest_attr_path = VirtualNodeHelper.convert_to_destination(dest_attr_path)
        if dest_attr_path not in self._connections:
            return

        src_attr_paths = self._connections[dest_attr_path]
        if not src_attr_paths:
            return

        # remove cached connections
        self._connections.pop(dest_attr_path)

        for src_attr_path in src_attr_paths:
            self._reversed_connections[src_attr_path].remove(dest_attr_path)
            if len(self._reversed_connections[src_attr_path]) == 0:
                self._reversed_connections.pop(src_attr_path)
            # remove cached connected ports
            src_node_path = src_attr_path.GetPrimPath()
            dest_node_path = dest_attr_path.GetPrimPath()
            if src_attr_path in self._node_connected_ports.get(src_node_path, []):
                self._node_connected_ports[src_node_path].remove(src_attr_path)
                if len(self._node_connected_ports[src_node_path]) == 0:
                    self._node_connected_ports.pop(src_node_path)
            if dest_attr_path in self._node_connected_ports.get(dest_node_path, []):
                self._node_connected_ports[dest_node_path].remove(dest_attr_path)
                if len(self._node_connected_ports[dest_node_path]) == 0:
                    self._node_connected_ports.pop(dest_node_path)

    # Due to the issue adapting multi-connections for execution attribute of a node in action graph, the deletion of
    # inputs is hard to implement in a natural way. Unlike the name suggests, the input property is only used to add
    # new connections
    #
    # To add connections:
    #   For normal nodes: inputs = [src_port] will clear all the old connections and connect the src_port with the
    #   ports inside the list
    #
    #   For execution port which allows multiple connection: inputs = [src_port] will simply add the connection to the
    #   src_port without touching old connections
    #
    # To remove connections:
    #   inputs = [] will clear all connections.
    #
    # To remove part of the connections requires a model reference and call it's remove_connections method.
    # We did not change the usage of inputs because it is already in use and we are not sure if we can change all the
    # existing usages accordingly.
    @inputs.setter
    def inputs(self, values, item=None):
        self._set_inputs(values, item)

    def _set_inputs(self, values: List[Sdf.Path], item: Union[og.Attribute, Sdf.Path, Usd.Prim]):
        """
        This adds connections between item and all the values.

        Args:
            values(List[Sdf.Path]): New connections to the item.
            item(Union[og.Attribute, Sdf.Path, Usd.Prim]): The item that a new connection is being dragged to.
        """
        if item is None:
            return

        # If there are no new values, we simply disconnect the old connections from the input
        if not values:
            self.remove_connections(item, self._connections.get(item, None))

        for src in values:
            # new output port, new connection
            dest_attr_path = None
            if isinstance(item, Usd.Prim):
                # create a new output port on the output node
                attr = self.get_attribute_from_path(src)
                if attr:
                    dest_attr_path = self.create_new_subgraph_port(attr, item, True, True)
            elif isinstance(item, Sdf.Path):
                dest_attr_path = VirtualNodeHelper.convert_from(item)

            if not dest_attr_path:
                continue

            # new input port, new connection
            src_attr_path = None
            if isinstance(src, Usd.Prim):
                # create a new input port on the input node
                attr = self.get_attribute_from_path(item)
                if attr:
                    src_attr_path = self.create_new_subgraph_port(attr, src, False, True)
            elif isinstance(src, Sdf.Path):
                src_attr_path = VirtualNodeHelper.convert_from(src)

            if not src_attr_path:
                continue

            self.create_connections(dest_attr_path, src_attr_path)

        # Trigger refresh
        self._item_changed(None)

    def __resolve_attributes_from_paths(
        self, dest_attr_path: Sdf.Path, src_attr_path: Sdf.Path
    ) -> List[Tuple[og.Attribute, og.Attribute]]:
        """
        Resolves all the pairs of (source, destination) attributes from their respective item paths.

        Args:
              dest_attr_path(Sdf.Path): The path of the destination item.
              src_attr_path(Sdf.Path): The path of the source item.
        """
        # find the actual source ports
        pairs = []

        # check if the attributes exist in og
        actual_src_attr = self.get_attribute_from_path(src_attr_path)
        if actual_src_attr:
            actual_dest_attr = self.get_attribute_from_path(dest_attr_path)
            if actual_dest_attr:
                pairs.append((actual_src_attr, actual_dest_attr))

        return pairs

    def create_connections(self, dest_attr_path: Sdf.Path, src_attr_path: Sdf.Path):
        """
        Creates connections between the source attributes and the destination attributes.

        Note: before a connection is made, the incoming connections into the destination attribute are removed,
              unless the destination attribute supports multiple connections.

        Args:
              dest_attr_path(Sdf.Path): The paths to the destination item.
              src_attr_path(Sdf.Path): The paths to the source item.
        """
        with omni.kit.undo.group():
            pairs = self.__resolve_attributes_from_paths(dest_attr_path, src_attr_path)
            for src_attribute, dst_attribute in pairs:
                actual_src_attr_type = src_attribute.get_type_name()

                # If the destination attribute has incoming connections, remove them.
                # If the attributes are compatible, remove previous connections into the destination attribute.
                if (
                    dst_attribute.get_upstream_connection_count() > 0
                    and src_attribute.is_compatible(dst_attribute)
                    and not self.allow_multiple_inputs(dst_attribute)
                ):
                    item = VirtualNodeHelper.convert_to(self.get_path_from_attribute(dst_attribute))

                    # fetch the connections directly, instead of querying self[item].inputs to support virtual nodes
                    self.remove_connections(item, self._connections.get(item, None))

                # Connect a Prim to an OG node
                if (actual_src_attr_type == "bundle") and (
                    src_attribute.get_node().get_type_name() == LEGACY_PRIM_TYPE
                ):
                    og.cmds.ConnectPrim(
                        attr=dst_attribute,
                        prim_path=src_attribute.get_path().pathString,
                        is_bundle_connection=False,
                    )
                else:
                    # Connect an OG node to an OG node
                    og.Controller.connect(src_attribute, dst_attribute)

    def remove_connections(self, dest_attr_path: Sdf.Path, disconnected_values: List[Sdf.Path]):
        """
        Removes connections between the source attributes and the destination attributes.

        Args:
            dest_attr_path: The destination port of the connections to be removed
            disconnected_values: The list containing source ports of the connections to be removed

            If there is a connection from a port in disconnected_values to dest_attr_path, the connection will be removed
        """
        # there is nothing to remove
        if not disconnected_values:
            return

        # make sure it is an existing connection
        src_attr_paths = self._connections.get(dest_attr_path, None)
        if not src_attr_paths:
            return

        actual_dest_attr = self.get_attribute_from_path(dest_attr_path)
        if not actual_dest_attr:
            return

        # do scope
        omni.kit.undo.begin_group()
        for src_attr_path in disconnected_values:
            actual_src_attr = self.get_attribute_from_path(src_attr_path)
            if actual_src_attr:
                actual_src_attr_type = actual_src_attr.get_type_name()
                if (actual_src_attr_type == "bundle") and (
                    actual_src_attr.get_node().get_type_name() == LEGACY_PRIM_TYPE
                ):
                    _success, _error = og.cmds.DisconnectPrim(
                        attr=actual_dest_attr,
                        prim_path=str(src_attr_path),
                        is_bundle_connection=False,
                    )
                else:
                    # Disconnect OG node from OG node
                    og.Controller.disconnect(actual_src_attr, actual_dest_attr)
        omni.kit.undo.end_group()

    def create_new_subgraph_port(
        self, src_attr: og.Attribute, dest_prim: Usd.Prim, is_output: bool, force_new_port: bool
    ) -> Sdf.Path:
        """
        Create port on subgraph:

        Args:
            src_attr: the attribute on the source node
            dest_prim: the destination prim to apply the attribute to. This is the prim of a compound subgraph
            is_output: whether the attribute is an output or input
            force_new_port: whether to force create a new port or reuse existing port. This is a deprecated attribute, only a value of True is supported

        Returns:
            Sdf.Path: The path of the new port
        """

        if not force_new_port:
            raise DeprecationWarning(
                "Calling create_new_graph_port with force_new_port not enabled is deprecated code path"
            )

        if not graph_config.Settings.are_compounds_enabled():
            return None

        subgraph = og.Controller.graph(dest_prim.GetPath())
        if not subgraph:
            return None

        compound_node = subgraph.get_owning_compound_node()
        if not compound_node:
            return None

        # special fixup for the name in the case we are promoting an output_only input to a compound output.
        is_attr_output = self.is_output(src_attr)
        is_attr_output_only = src_attr.get_metadata(ogt.ogn.MetadataKeys.OUTPUT_ONLY) == "1"
        is_output = is_attr_output or is_attr_output_only
        is_bundle = src_attr.get_resolved_type().role == og.AttributeRole.BUNDLE

        # special case when creating pass-through ports from the compound input to the compound output
        if src_attr.get_node() == compound_node:
            # only supported from input nodes
            if src_attr.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
                return None

            is_attr_output = True
            is_attr_output_only = False
            is_output = True

            proposed_name = og.Attribute.remove_port_type_from_name(src_attr.get_name(), is_bundle)
            proposed_name = og.Attribute.ensure_port_type_in_name(
                proposed_name,
                og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
                src_attr.get_resolved_type().role == og.AttributeRole.BUNDLE,
            )
            proposed_name, _ = self.get_next_free_name(proposed_name, dest_prim.GetPath())
            attr_type = (
                src_attr.get_resolved_type()
                if src_attr.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR
                else src_attr.get_type_name()
            )
            ext_type = src_attr.get_extended_type()
            if src_attr.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION:
                ext_type = (og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION, src_attr.get_union_types())
            elif src_attr.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY:
                ext_type = og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY

            with omni.kit.undo.group():
                attr = og.Controller.create_attribute(
                    node=compound_node,
                    attr_name=proposed_name,
                    attr_extended_type=ext_type,
                    attr_port=og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
                    attr_type=attr_type,
                    update_usd=True,
                    undoable=True,
                )
                if attr:
                    og.Controller.connect(src_attr, attr, update_usd=True, undoable=True)

        else:
            # clean the name
            proposed_name = og.Attribute.remove_port_type_from_name(src_attr.get_name(), is_bundle)
            proposed_name = og.Attribute.ensure_port_type_in_name(
                proposed_name,
                (
                    og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
                    if is_output
                    else og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
                ),
                is_bundle,
            )

            proposed_name, _ = self.get_next_free_name(proposed_name, dest_prim.GetPath())
            attr = og.NodeController.promote_attribute(src_attr, proposed_name, undoable=True)

        if not attr:
            return None

        # The actual node is created on the compound node, but it gets registered as an if it's an attribute
        # on the compound subgraph
        new_attr_path = Sdf.Path(f"{compound_node.get_compound_graph_instance().get_path_to_graph()}.{attr.get_name()}")
        self._create_subgraph_port_ui(new_attr_path, src_attr, is_attr_output, is_attr_output_only)
        return new_attr_path

    @property
    def outputs(self, item):  # noqa: property-with-parameters
        if not isinstance(item, Sdf.Path):
            return None

        # Check if this is an output port.
        prim_path = item.GetPrimPath()
        if prim_path in self.__ports_categories:
            ports = self.__ports_categories[prim_path]
            if item in ports["outputOnly_inputs"] + ports["outputs"] + ports["execution_outputs"]:
                # We only need the actual connections if this is a subgraph node. For regular
                # nodes the connections will be handled from the input side.
                if self.is_graph(prim_path):
                    result = self._connections.get(item, None)
                    if result:
                        return list(result)
                # Even though we're not returning any connections, returning an empty list lets
                # the caller know that this is an output port.
                return []
        # Return None to let the caller know that this isn't an output port.
        return None

    @outputs.setter
    def outputs(self, value, item=None):
        pass

    def get_output_connections(self, item) -> Optional[List[Sdf.Path]]:
        """
        Query the list of output connections. Similar to the outputs property, but works for all nodes
        Returns:
            None if not an output port
            A list, possible empty, of the connections as Sdf.Paths
        """
        if not isinstance(item, Sdf.Path):
            return None

        prim_path = item.GetPrimPath()
        if prim_path in self.__ports_categories:
            ports = self.__ports_categories[prim_path]
            if item in ports["outputOnly_inputs"] + ports["outputs"] + ports["execution_outputs"]:
                return list(self._reversed_connections.get(item, []))

        # Return None to let the caller know that this isn't an output port.
        return None

    @property
    def display_color(self, item):  # noqa: property-with-parameters
        color = None
        if item.HasAPI(UsdUI.NodeGraphNodeAPI):
            node_graph_node = UsdUI.NodeGraphNodeAPI(item)
            color_attr = node_graph_node.GetDisplayColorAttr()
            if color_attr:
                color = color_attr.Get()
        if not color and self.is_pseudo_node(item):
            color = PSEUDO_NODES_DICT[item.GetTypeName()].display_color
        return color

    @display_color.setter
    def display_color(self, value, item=None):
        omni.kit.commands.execute(
            "UsdUINodeGraphNodeSetCommand",
            attribute=UsdUI.Tokens.uiNodegraphNodeDisplayColor,
            prim_path=item.GetPath(),
            value=value,
            prev=None,
        )

    @property
    def position(self, item=None):  # noqa: property-with-parameters
        path = _get_path(item)
        if not path:
            return None

        result = self.__positions.get(path, None)
        if result:
            return result

        # for compound virtual nodes the first property path is passed as the item
        if isinstance(item, Sdf.Path) and item.IsPropertyPath():
            pos = VirtualNodeHelper.get_virtual_node_position(item, None)
            if pos is None:  # position is not set yet
                return VirtualNodeHelper.compute_initial_position(item)
            return pos

        # For compounds this will be called with both the graph prim and
        # the input and output properties. Ignore the graph prim calls
        if isinstance(item, Usd.Prim) and item.IsA(OmniGraphSchema.OmniGraph):
            return None

        if item.HasAPI(UsdUI.NodeGraphNodeAPI):
            if isinstance(item, Usd.Prim):
                node_graph_node = UsdUI.NodeGraphNodeAPI(item)
            else:
                # TODO: Is this case for a Backdrop?
                node_graph_node = UsdUI.NodeGraphNodeAPI(self._stage.GetPrimAtPath(path))

            pos_attr = node_graph_node.GetPosAttr()
            if pos_attr:
                result = pos_attr.Get()
                self.__positions[item.GetPath()] = result
                return result
        return None

    @position.setter
    def position(self, new_position, item=None):
        path = _get_path(item)
        if not path:
            return

        self.batch_set_position(new_position, item)

        prev_position = self.__positions.get(path, None)
        if prev_position != new_position:
            if new_position is None:
                omni.kit.commands.execute("UsdUIRemovePositionCommand", prim_path=path)
            else:
                self.__positions[path] = new_position
            self._item_changed(item)

    def position_begin_edit(self, item):
        path = _get_path(item)
        if not path:
            return

        self.batch_position_begin_edit(item)
        position = self[item].position
        self.__positions_on_begin[path] = position

    def position_end_edit(self, item):
        path = _get_path(item)
        if not path:
            return

        position = self.__positions.get(path, None)
        position_on_begin = self.__positions_on_begin.pop(path, None)
        if not position or not position_on_begin:
            # Can't do anything
            self.batch_position_end_edit(item)
            return

        # Begin undo group
        if not self.__set_position_group and self.__positions_on_begin:
            need_end_group = True
            self.__set_position_group = True
            omni.kit.undo.begin_group()
        else:
            need_end_group = False

        # For Input and Output nodes, a property path is passed in.
        # The path is an attribute on the graph prim
        if isinstance(item, Sdf.Path) and item.IsPropertyPath():
            VirtualNodeHelper.set_virtual_node_position(item, position)
        # For compounds this will be called with both the graph prim and
        # The input and output properties. Ignore the graph prim calls
        elif isinstance(item, Usd.Prim) and item.IsA(OmniGraphSchema.OmniGraph):
            pass
        else:
            omni.kit.commands.execute(
                "UsdUINodeGraphNodeSetCommand",
                attribute=UsdUI.Tokens.uiNodegraphNodePos,
                prim_path=path,
                value=position,
                prev=position_on_begin,
            )

        # This will call position_end_edit for all the other nodes in the selection.
        self.batch_position_end_edit(item)

        # End undo group
        if need_end_group:
            self.__set_position_group = False
            omni.kit.undo.end_group()

    @property
    def size(self, item):  # noqa: property-with-parameters
        result = self.__sizes.get(item.GetPath(), None)
        if result:
            return result

        # Caching size for fastest access
        if item.HasAPI(UsdUI.NodeGraphNodeAPI):
            node_graph_node = UsdUI.NodeGraphNodeAPI(item)
            size_attr = node_graph_node.GetSizeAttr()
            if size_attr:
                result = size_attr.Get()
                self.__sizes[item.GetPath()] = result
        if not result and self.is_pseudo_node(item):
            result = PSEUDO_NODES_DICT[item.GetTypeName()].size
        return result

    @size.setter
    def size(self, value, item=None):
        path = item.GetPath()
        if path in self.__sizes_on_begin:
            self.__sizes[path] = value

    def size_begin_edit(self, item):
        self.__sizes_on_begin[item.GetPath()] = self[item].size

    def size_end_edit(self, item):
        path = item.GetPath()
        omni.kit.commands.execute(
            "UsdUINodeGraphNodeSetCommand",
            attribute=UsdUI.Tokens.uiNodegraphNodeSize,
            prim_path=item.GetPath(),
            value=self.__sizes[path],
            prev=self.__sizes_on_begin[path],
        )
        self.__sizes_on_begin.pop(path)

    # We make these two method instance methods instead of class methods to allow derived classes to
    # override them to create their own custom expansion states.
    def og_expansion_state_to_usd(self, og_state: GraphModel.ExpansionState) -> str:
        return _og_expansion_state_to_usd.get(og_state, None)

    def usd_expansion_state_to_og(self, usd_state: str) -> GraphModel.ExpansionState:
        return _usd_expansion_state_to_og.get(usd_state, None)

    def get_default_node_expansion_state(self, node_type_name: str) -> GraphModel.ExpansionState:
        """Returns the default expansion state for the given node type.

        Args:
            node_type_name: Type of node to return expansion state for.

        Returns:
            Expansion state.
        """
        # In the core we always default to open.
        return self.ExpansionState.OPEN

    @property
    def expansion_state(  # noqa: property-with-parameters
        self, item: Union[Usd.Prim, Sdf.Path] = None
    ) -> GraphModel.ExpansionState:
        result = self.__node_states.get(item, None)
        if result:
            return self.__filter_expansion_state(item, result)

        # Handle new prims.
        if isinstance(item, Usd.Prim):
            result = self.__filter_expansion_state(
                item, self.get_default_node_expansion_state(self.__node_type_name(item))
            )

            # If the prim has a USD expansion state set, use that.
            if item.HasAPI(UsdUI.NodeGraphNodeAPI):
                node_graph_node = UsdUI.NodeGraphNodeAPI(item)
                state_attr = node_graph_node.GetExpansionStateAttr()
                if state_attr:
                    saved_state = self.__filter_expansion_state(item, self.usd_expansion_state_to_og(state_attr.Get()))
                    if saved_state:
                        self.__node_states[item] = saved_state
                        result = saved_state

            return result

        # Expansion state for ports and anything else we didn't recognize above.
        return self.ExpansionState.OPEN

    @expansion_state.setter
    def expansion_state(self, new_value: GraphModel.ExpansionState, item: Union[Usd.Prim, Sdf.Path] = None):
        new_value = self.__filter_expansion_state(item, new_value)
        old_value = self.__node_states.get(item, None)

        if new_value != old_value:
            self.__node_states[item] = new_value

            if isinstance(item, Usd.Prim):
                path = _get_path(item)
                if path:
                    omni.kit.commands.execute(
                        "UsdUINodeGraphNodeSetCommand",
                        attribute=UsdUI.Tokens.uiNodegraphNodeExpansionState,
                        prim_path=path,
                        value=self.og_expansion_state_to_usd(new_value),
                        prev=self.og_expansion_state_to_usd(old_value),
                    )

            # TODO: self._item_changed(item) # update only 1 item is broken
            self._item_changed(None)

    def __filter_expansion_state(
        self, item: Union[Usd.Prim, Sdf.Path], state: GraphModel.ExpansionState
    ) -> GraphModel.ExpansionState:
        """Filters the desired expansion state to account for nodes that do not allow minimized or closed states"""
        if isinstance(item, Sdf.Path):
            item = self._stage.GetPrimAtPath(item)

        if self.__node_type_name(item) in self.__non_expansion_node_types:
            return GraphModel.ExpansionState.OPEN
        return state

    @property
    def selection(self) -> List[Usd.Prim]:
        """Returns the selected primitives"""
        if self.__selection is None:
            return None
        selected_nodes = set(self.__selection.get_selected_prim_paths() or [])
        result = []
        for path_name in selected_nodes:
            prim = self._stage.GetPrimAtPath(path_name)
            if prim is not None:
                result.append(prim)
        return result

    @selection.setter
    def selection(self, value: List[Usd.Prim]):
        old_selection = set()
        if self.__selection:
            old_selection = set(self.__selection.get_selected_prim_paths() or [])
        new_selection = set({prim.GetPath().pathString for prim in (value or [])})

        if old_selection != new_selection:
            omni.kit.commands.execute(
                "SelectPrimsCommand",
                old_selected_paths=list(old_selection),
                new_selected_paths=list(new_selection),
                expand_in_stage=True,
            )
            self._selection_changed()

    @property
    def stacking_order(self, item):  # noqa: property-with-parameters
        if self[item].type == "Backdrop":
            return -1

        return 1

    # --------------------------------------------------------------------------------------------------------------
    def __ensure_delayed_prim_change(self):
        """Cause an async full dirty callback if one is not already queued"""
        index = self.__dirty_frame_index
        if self.__prim_changed_task[index] is None or self.__prim_changed_task[index].done():
            try:
                self.__prim_changed_task[index] = run_coroutine(self.__delayed_prim_changed())
            except BaseException:  # noqa: broad-except
                self.__prim_changed_task[index] = asyncio.ensure_future(self.__delayed_prim_changed())
            _ = _NOTIFY_DEBUG and print(f"Trigger {index} {omni.kit.app.get_app().get_update_number()}")

    def __on_stage_event(self, event):
        """Called with omni.usd.context when stage event"""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self._selection_changed()
        elif event.type == int(omni.usd.StageEventType.CLOSING):
            self._item_changed(None)

    def __on_objects_changed(self, notice, sender):
        """Called by Usd.Notice.ObjectsChanged"""

        # We have two issues that we need to deal with here:
        #
        # 1) We may get several calls to this method for one logical operation and would prefer to handle all
        #    the related changes together.
        #
        # 2) We are in a race with graph (i.e. the actual C++ Graph object) to process some of these changes. We
        #    want to let the Graph win so that the OG Nodes corresponding to any new prims will have already been
        #    created by the time we get to them.
        #
        # The solution to both of these issues is to record the changes here but delay acting on them until
        # the next UI tick.
        #

        root_path = self._graph_root

        def should_handle_changeinfo(path: Sdf.Path) -> bool:
            return path.HasPrefix(root_path)

        def should_handle_resync(path: Sdf.Path) -> bool:
            if p.IsAbsoluteRootPath():
                return True
            return path.GetPrimPath().HasPrefix(root_path) or root_path.HasPrefix(path.GetPrimPath())

        need_update = False
        for p in notice.GetResyncedPaths():
            if should_handle_resync(p):
                if p.IsAbsoluteRootOrPrimPath():
                    self.__dirty_prim_paths[self.__dirty_frame_index].append(p)
                    need_update = True
                if p.IsPropertyPath():
                    self.__dirty_prop_paths[self.__dirty_frame_index].append(p)
                    need_update = True

        for p in notice.GetChangedInfoOnlyPaths():
            if p.IsAbsoluteRootOrPrimPath() and should_handle_changeinfo(p):
                self.__dirty_prim_paths[self.__dirty_frame_index].append(p)
                need_update = True
            if p.IsPropertyPath() and should_handle_changeinfo(p):
                self.__info_changed_prop_paths[self.__dirty_frame_index].append(p)
                need_update = True

        _ = _NOTIFY_DEBUG and print(
            f"UsdNotify: {self.__dirty_frame_index} {omni.kit.app.get_app().get_update_number()} - NeedUpdate: {need_update}"
        )

        if not need_update:
            return

        # Update on the next UI tick.
        self.__ensure_delayed_prim_change()

    def __on_node_status_changed(self, nodes: List[og.Node], graph: og.Graph):
        """Callback from the graph when nodes change their error/warning status during compute."""
        if graph != self._graph:
            carb.log_error("graph mismatch in callback.")
            return
        self.__nodes_requiring_redraw[self.__dirty_frame_index].update(set(nodes))

        # Delay until the next tick so that other changes arising from the same evaluation get
        # merged into the same UI update.
        _ = _NOTIFY_DEBUG and print(f"NodeStatusChanged {omni.kit.app.get_app().get_update_number()}")
        self.__ensure_delayed_prim_change()

    def _on_node_attribute_change(self):
        """Called when one of our nodes has an attribute added or removed"""
        # Visual changes to a port cannot be handled be handled by rebuilding the
        # node's UI. We must instead rebuild the entire graph.
        self.__full_redraw_required[self.__dirty_frame_index] = True

        # Delay until the next tick so that other changes arising from the same evaluation get
        # merged into the same UI update.
        _ = _NOTIFY_DEBUG and print(f"NodeAttributeChanged {omni.kit.app.get_app().get_update_number()}")
        self.__ensure_delayed_prim_change()

    def _on_graph_event(self, event: og.GraphEvent):
        """Invoked when a graph related event occurs. Forwards the event to an external callback"""
        if self.__on_graph_event_callback:
            self.__on_graph_event_callback(event)

    def register_graph_event_callback(self, callback: Callable[[og.GraphEvent], None]):
        """
        Registers a callback method that is invoke when an OmniGraph graph event occurs.

        Note, only a single callback can be registered at a time
        """
        self.__on_graph_event_callback = callback

    def _on_node_attribute_resolve(self, node_path: Sdf.Path):
        """Called when one of our nodes has an attribute resolution change"""
        if node_path not in self.__ports_categories:
            return

        # Note: once we are fully on kit 105 we shouldn't need this try/except check.
        try:
            self._rebuild_node(self._stage.GetPrimAtPath(node_path), full=True)
        except TypeError:
            self._rebuild_node(self._stage.GetPrimAtPath(node_path))

        # Delay until the next tick so that other changes arising from the same evaluation get
        # merged into the same UI update.
        self.__full_redraw_required[self.__dirty_frame_index] = True
        _ = _NOTIFY_DEBUG and print(f"NodeAttributeResolved {omni.kit.app.get_app().get_update_number()}")
        self.__ensure_delayed_prim_change()

    def __on_begin_duplicate(self, info):
        path_from = info.get("path_from", None)
        path_to = info.get("path_to", None)
        if path_from and path_to:
            self.__duplicated_prims[self.__dirty_frame_index][Sdf.Path(path_to)] = Sdf.Path(path_from)

    def _update_dirty(self):
        """
        Create/remove dirty items that was collected from TfNotice. Can be
        called any time to pump changes.
        """
        # Swap dirty state in to local variables
        dirty_prim_paths = set(self.__dirty_prim_paths[self.__update_frame_index])
        dirty_prop_paths = set(self.__dirty_prop_paths[self.__update_frame_index])
        info_changed_prop_paths = set(self.__info_changed_prop_paths[self.__update_frame_index])
        nodes_requiring_redraw = set(self.__nodes_requiring_redraw[self.__update_frame_index])
        self.__dirty_prim_paths[self.__update_frame_index].clear()
        self.__dirty_prop_paths[self.__update_frame_index].clear()
        self.__info_changed_prop_paths[self.__update_frame_index].clear()
        self.__nodes_requiring_redraw[self.__update_frame_index].clear()

        # Filter out invalid duplications.
        duplicates: Dict[Sdf.Path, Sdf.Path] = {}

        for dupe_path, orig_path in self.__duplicated_prims[self.__update_frame_index].items():
            # The original should be a non-graph prim that we already know about.
            if orig_path == self._graph_root or orig_path not in self.__primpath_to_subgraph:
                continue
            # The duplicate should be a non-graph prim that we don't yet know about.
            if dupe_path == self._graph_root or dupe_path in self.__primpath_to_subgraph:
                continue
            # And the duplicate should actually be in a graph.
            if self.is_graph(dupe_path.GetParentPath()):
                duplicates[orig_path] = dupe_path

        self.__duplicated_prims[self.__update_frame_index] = {}

        reload_graph = False
        recache = False
        regenerate = self.__full_redraw_required[self.__update_frame_index]
        self.__full_redraw_required[self.__update_frame_index] = False

        changed_prim_paths = set()
        new_prim_paths = set()
        removed_prim_paths = set()

        # Handle duplications.
        if duplicates:
            self.__process_duplicates(duplicates)

        # Handle new and deleted prims.
        for path in dirty_prim_paths:
            prim = self._stage.GetPrimAtPath(path)
            if path not in self.__primpath_to_subgraph:
                # removed the graph's parent or the graph itself
                if not prim and self._graph_root.HasPrefix(path):
                    self._item_changed(None)
                    return
                if path != self._graph_root:
                    parent_path = path.GetParentPath()
                    # new prim created
                    if self.is_graph(parent_path):
                        self.create_node_ui(path, parent_path)
                        new_prim_paths.add(path)
                        regenerate = True
                    continue

            if not prim:
                # prim is removed
                if path in self.__primpath_to_subgraph:
                    graph_path = self.__primpath_to_subgraph[path]
                    if graph_path in self.__subgraph_to_primpaths:
                        removed_prim_paths.add(path)

                        self.__subgraph_to_primpaths[graph_path].remove(path)
                        self.__primpath_to_subgraph.pop(path, None)

                        # Remove cached positions and sizes
                        self.__positions.pop(path, None)
                        self.__positions_on_begin.pop(path, None)
                        self.__sizes.pop(path, None)
                        self.__sizes_on_begin.pop(path, None)

                        # Remove cached expansion state
                        self.__node_states.pop(prim, None)

                        # if a compound node or graph is reloaded, the rename will affect the entire hierarchy
                        reload_graph = True
                        recache = True
                        regenerate = True
            else:
                # Prim is changed
                changed_prim_paths.add(path)

        # Cache connections for new nodes.
        #
        # We can't do this in the loop above because the nodes at both ends of
        # the connection must be cached before a connection between them will be
        # accepted.
        for path in new_prim_paths:
            self.cache_connections(path.pathString)

        # Handle UsdUI attributes changes
        for prop_path in list(dirty_prop_paths):
            prim_path = prop_path.GetParentPath()
            prop_name = prop_path.name
            if prop_name == UsdUI.Tokens.uiNodegraphNodePos:
                self.__positions.pop(prim_path, None)
                self.__positions_on_begin.pop(prim_path, None)
                changed_prim_paths.add(prim_path)
                dirty_prop_paths.discard(prop_path)
            elif prop_name == UsdUI.Tokens.uiNodegraphNodeSize:
                self.__sizes.pop(prim_path, None)
                self.__sizes_on_begin.pop(prim_path, None)
                changed_prim_paths.add(prim_path)
                dirty_prop_paths.discard(prop_path)
            elif prop_name == UsdUI.Tokens.uiNodegraphNodeExpansionState:
                prim = self._stage.GetPrimAtPath(prim_path)
                self.__node_states.pop(prim, None)
                changed_prim_paths.add(prim_path)
                dirty_prop_paths.discard(prop_path)
                regenerate = True
            elif prop_name == UsdUI.Tokens.uiNodegraphNodeDisplayColor:
                self._item_changed(None)
                return

        # Handle UsdUI attribute value changes
        for prop_path in list(info_changed_prop_paths):
            prim_path = prop_path.GetParentPath()
            prop_name = prop_path.name
            prop = self._stage.GetPropertyAtPath(prop_path)
            if prop_name == UsdUI.Tokens.uiNodegraphNodePos:
                cached_pos = self.__positions.get(prim_path)
                new_pos = prop.Get()
                if cached_pos != new_pos:
                    self.__positions.pop(prim_path, None)
                    self.__positions_on_begin.pop(prim_path, None)
                    changed_prim_paths.add(prim_path)
                info_changed_prop_paths.discard(prop_path)
            elif prop_name == UsdUI.Tokens.uiNodegraphNodeExpansionState:
                prim = self._stage.GetPrimAtPath(prim_path)
                cached_state = self.__node_states.get(prim)
                new_state = self.usd_expansion_state_to_og(prop.Get())
                if cached_state != new_state:
                    self.__node_states.pop(prim, None)
                    changed_prim_paths.add(prim_path)
                    regenerate = True
                info_changed_prop_paths.discard(prop_path)
            elif prop_name in (UsdUI.Tokens.uiNodegraphNodeDisplayColor, UsdUI.Tokens.uiDescription):
                changed_prim_paths.add(prim_path)
                regenerate = True

        dirty_prop_paths = {p for p in dirty_prop_paths if p.GetParentPath() not in removed_prim_paths}
        info_changed_prop_paths = {p for p in info_changed_prop_paths if p.GetParentPath() not in removed_prim_paths}

        regenerate |= self._process_prop_changes(dirty_prop_paths, True)
        regenerate |= self._process_prop_changes(info_changed_prop_paths, False)

        # When a prim is removed USD will notify the destinations of its connections and the calls
        # above will have cleaned up any cached data for those connections.
        # However, there may still be cached data for connections where the removed prim was the
        # destination. We must clean those up as well.
        for path in removed_prim_paths:
            connected_attr_paths = self._node_connected_ports.get(path, set()).copy()
            for attr_path in connected_attr_paths:
                self.disconnect_attribute_ui(attr_path)
            self.__ports_categories.pop(path, None)

        # If we have specific nodes which need to be redrawn but there is no _rebuild_node() function
        # available, then we will have to redraw the entire graph.
        have_rebuild_node = hasattr(self, "_rebuild_node") and callable(self._rebuild_node)
        regenerate |= len(nodes_requiring_redraw) > 0 and not have_rebuild_node

        # if a compound port has changed, the input and output ports may need refreshing
        recache |= any(CompoundUtils.is_compound_node(p.GetPrimPath()) for p in dirty_prop_paths)
        regenerate |= recache

        # A rename or move of a compound graph will impact the entire hierarchy
        # this is a workaround for the graph not properly updating the prim paths
        # of the subgraphs and their nodes.
        if reload_graph and self._graph:
            self._graph.reload_from_stage()

        if recache:
            self.cache_graph()

        if regenerate:
            # Regenerate everything. Not necessary to continue.
            self._item_changed(None)
        else:
            for path in changed_prim_paths:
                prim = self._stage.GetPrimAtPath(path)
                self._item_changed(prim)
            for node in nodes_requiring_redraw:
                prim = og.Controller.prim(node)
                self._rebuild_node(prim)

        # Send out events.
        if self.__event_stream:
            for path in removed_prim_paths:
                self.__event_stream.dispatch(
                    OmniGraphModel.EventType.NODE_REMOVED, payload={"path_str": path.pathString}
                )
            for path in new_prim_paths:
                self.__event_stream.dispatch(OmniGraphModel.EventType.NODE_ADDED, payload={"path_str": path.pathString})

    def __get_corresponding_attr(self, template_attr: og.Attribute, target_node: og.Node) -> og.Attribute:
        """
        Returns the attribute of *target_node* which corresponds to *template_attr*.
        Usually this will be the attribute of *target_node* with the same name, but if *template_attr*
        is the node's output prim bundle the attribute of *target_node* will have the same name as the node.
        """
        attr_name = template_attr.get_name()
        if template_attr.get_type_name() == "bundle":
            template_prim_path = Sdf.Path(template_attr.get_node().get_prim_path())
            template_prim_name = template_prim_path.name
            if attr_name == template_prim_name:
                target_prim_path = Sdf.Path(target_node.get_prim_path())
                attr_name = target_prim_path.name
        return target_node.get_attribute(attr_name)

    def __process_duplicates(self, duplicates: Dict[Sdf.Path, Sdf.Path]):
        # Undoing the duplication will also undo everything we do below, so let's not clutter the undo
        # queue with entries which will have no meaning for the user.
        disable_available = hasattr(omni.kit.undo, "disable") and callable(omni.kit.undo.disabled)
        with omni.kit.undo.disabled() if disable_available else no_undo():
            for orig_path, dupe_path in duplicates.items():
                # Visually the duplicate will be sitting right on top of its original. Offset it a bit.
                x, y = self.__positions[orig_path]
                omni.kit.commands.execute(
                    "UsdUINodeGraphNodeSetCommand",
                    attribute=UsdUI.Tokens.uiNodegraphNodePos,
                    prim_path=dupe_path,
                    value=(x + 40, y + 40),
                    prev=(x, y),
                )

                # We don't need to process pseudo-nodes any further
                if self.is_pseudo_node(orig_path):
                    continue

                # If two of the original nodes had a connection between them (A1 -> B1) then we want
                # to replicate that connection between their duplicates (A2 -> B2).
                try:
                    orig_node = og.Controller.node(orig_path)
                    dupe_node = og.Controller.node(dupe_path)
                except og.OmniGraphError:
                    # in the case of compounds, which may copy prims, the duplicated prim may be removed prior to processing
                    continue

                copy_conns = []
                for orig_dest_attr in orig_node.get_attributes():
                    for orig_src_attr in orig_dest_attr.get_upstream_connections():
                        orig_src_prim_path = Sdf.Path(orig_src_attr.get_node().get_prim_path())
                        dupe_src_prim_path = duplicates.get(orig_src_prim_path, None)
                        if not dupe_src_prim_path:
                            continue
                        dupe_src_node = og.Controller.node(dupe_src_prim_path)
                        if not dupe_src_node:
                            continue
                        dupe_dest_attr = self.__get_corresponding_attr(orig_dest_attr, dupe_node)
                        dupe_src_attr = self.__get_corresponding_attr(orig_src_attr, dupe_src_node)
                        if dupe_dest_attr and dupe_src_attr:
                            # We don't want to change connections while iterating over them so just record
                            # it for now.
                            copy_conns.append((orig_src_attr, orig_dest_attr, dupe_src_attr, dupe_dest_attr))

                for orig_src_attr, _, dupe_src_attr, dupe_dest_attr in copy_conns:
                    # At the time this was written the USD copy would have created a connection from the
                    # original source to the duplicate destination (A1 -> B2). We need to get rid of that.
                    if orig_src_attr in dupe_dest_attr.get_upstream_connections():
                        orig_src_attr.disconnect(dupe_dest_attr, True)
                    # Create the connection between the duplicates (A2 -> B2).
                    dupe_src_attr.connect(dupe_dest_attr, True)

    def _process_prop_changes(self, dirty_prop_paths: Set[Sdf.Path], is_resync: bool) -> bool:
        """Process property changes
        Args:
            dirty_prop_paths: The property paths that are dirty
            is_resync: True if the given paths have been resync, otherwise they are info-only changes
        Returns:
            True if the graph should be completely regenerated
        """
        regenerate = False
        for prop_path in dirty_prop_paths:
            # connections
            prop = self._stage.GetPropertyAtPath(prop_path)
            # If the USD Property does not exist, it must have been just removed
            if not prop or not prop.IsValid():
                if is_resync:
                    self.remove_port_ui(prop_path)
                regenerate = True
            elif isinstance(prop, Usd.Relationship):
                graph_attr = self.get_attribute_from_path(prop_path)
                if graph_attr and graph_attr.get_type_name() in ["bundle", "target"]:
                    regenerate = self._process_relationship(prop_path)
            elif prop.HasAuthoredConnections():
                connections = prop.GetConnections()
                self.disconnect_attribute_ui(prop_path)
                if not connections:
                    # Next time it will not have AuthoredConnections
                    prop.ClearConnections()
                    regenerate = True
                for connection in connections:
                    if self.connect_attribute_ui(connection, prop_path, True):
                        regenerate = True
            elif is_resync:
                # A variable property has structurally changed (e.g. the type has changed), which triggers
                # a rebuild
                if prop.GetName().startswith("graph:variable:") and prop.GetPrimPath() == self._graph_root:
                    regenerate = True
                    continue
                # The property is an attribute with no connections, if this is a resync then it could
                # be a new dynamic attribute.
                graph_attr = self.get_attribute_from_path(prop_path)
                # There is no corresponding OG attribute, so this must be a non-OG property which
                # we decline to display on the node
                if not graph_attr:
                    continue
                attr_port_type = graph_attr.get_port_type()
                # We only care about non-hidden inputs and outputs
                if (
                    attr_port_type
                    in (
                        og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
                        og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
                    )
                    and graph_attr.get_metadata(ogn.MetadataKeys.HIDDEN) is None
                ):
                    regenerate = True
            else:
                # regenerate if the variableName attribute of Read/WriteVariable has changed
                graph_attr = self.get_attribute_from_path(prop_path)
                if graph_attr:
                    attr_name = graph_attr.get_name()
                    node_name = graph_attr.get_node().get_type_name()
                    if attr_name == "inputs:variableName" and (
                        node_name in ("omni.graph.core.ReadVariable", "omni.graph.core.WriteVariable")
                    ):
                        regenerate = True

        return regenerate

    # _process_bundle left for backwards compatibility
    def _process_bundle(self, prop_path) -> bool:
        """Processes a bundle during _process_prop_changes
        Args:
            prop_path: The property path
        Returns:
            True if the graph should be completely regenerated
        """
        graph_attr = self.get_attribute_from_path(prop_path)
        regenerate = False
        targets = self._stage.GetPropertyAtPath(prop_path).GetTargets()
        upstream_attrs = graph_attr.get_upstream_connections()
        self.disconnect_attribute_ui(prop_path)
        if not targets:
            # This is a disconnection of a relationship
            regenerate = True
        else:
            # This is a connection to a relationship
            if upstream_attrs and len(targets) == 1:
                for conn in upstream_attrs:
                    src_attr_path = self.get_path_from_attribute(conn)
                    if self.connect_attribute_ui(src_attr_path, prop_path, True):
                        regenerate = True
            else:
                for target in targets:
                    # assume the target is a path to a port; get the node (parent) path
                    node_path = target.GetParentPath()
                    target_ui = None
                    if self._graph.get_node(node_path.pathString):
                        # construct the path to the port with AppendProperty so the delimiters are correct
                        target_ui = node_path.AppendProperty(target.name)
                    else:
                        # here target is a prim path, while in the ui, to show the attribute we appended the name at the end
                        target_ui = target.AppendProperty(target.name)
                    regenerate |= self.connect_attribute_ui(target_ui, prop_path, True)
        return regenerate

    def _process_relationship(self, prop_path: Sdf.Path) -> bool:
        """Processes a relationship during _process_prop_changes
        Args:
            prop_path: The property path
        Returns:
            True if the graph should be completely regenerated
        """
        # Disconnect all upstream connections then re-add to properly support fan-in
        self.disconnect_attribute_ui(prop_path)
        graph_attr = self.get_attribute_from_path(prop_path)
        upstream_attrs = graph_attr.get_upstream_connections()
        if len(upstream_attrs) == 0:
            return True
        regenerate = False
        for upstream_attr in upstream_attrs:
            src_attr_path = self.get_path_from_attribute(upstream_attr)
            src_attr_role = upstream_attr.get_resolved_type().role
            if src_attr_role == og.AttributeRole.BUNDLE:
                node_path = src_attr_path.GetParentPath()
                src_attr_path = node_path.AppendProperty(src_attr_path.name)
            regenerate |= self.connect_attribute_ui(src_attr_path, prop_path, True)
        return regenerate

    async def __delayed_prim_changed(self):
        """Called to pump changes at the next frame to the model after the changes received"""
        # Double buffer the updates, so any received notifications this frame, will be applied after a full
        # ui update tick.

        # An example of the double buffering in action, showing the order of operations relative to each frame
        # separated by each ui_tick, first when notifications (possibly multiple) are received each frame
        # and secondly when sparse notifications are received.
        # TriggerUpdate indicates the initiation of the coroutine, WaitUpdate indicates the await until next frame and
        # Process is the actual processing of the USD notifications. Set _NOTIFY_DEBUG = TRUE to display these calls to
        # the console

        #
        # UI_TICK ------------------------------------------------------------------------------------------------------
        #
        #         UsdNotification(DIRTY_INDEX = 0) -> TriggerUpdate(DIRTY_INDEX = 0)
        #         UsdNotification(DIRTY_INDEX = 0)
        # UI_TICK ------------------------------------------------------------------------------------------------------
        #                                             WaitUpdate(DIRTY_INDEX = 0)
        #         UsdNotification(DIRTY_INDEX = 1)                                    -> TriggerUpdate(DIRTY_INDEX = 1)
        #         UsdNotification(DIRTY_INDEX = 1)
        # UI_TICK ------------------------------------------------------------------------------------------------------
        #                                             ProcessUpdates(DIRTY_INDEX = 0)    WaitUpdate(DIRTY_INDEX = 1)
        #         UsdNotification(DIRTY_INDEX = 0) -> TriggerUpdate(DIRTY_INDEX = 0)
        #         UsdNotification(DIRTY_INDEX = 0)
        # UI_TICK ------------------------------------------------------------------------------------------------------
        #                                             WaitUpdate(DIRTY_INDEX = 0)        ProcessUpdates(DIRTY_INDEX = 1)
        #         UsdNotification(DIRTY_INDEX = 1)                                    -> TriggerUpdate(DIRTY_INDEX = 1)
        #         UsdNotification(DIRTY_INDEX = 1)
        # UI_TICK ------------------------------------------------------------------------------------------------------
        #                                             ProcessUpdates(DIRTY_INDEX = 0)    WaitUpdate(DIRTY_INDEX = 1)
        # UI_TICK ------------------------------------------------------------------------------------------------------
        #                                                                                ProcessUpdates(DIRTY_INDEX = 1)
        # UI_TICK ------------------------------------------------------------------------------------------------------
        # UI_TICK ------------------------------------------------------------------------------------------------------
        #         UsdNotification(DIRTY_INDEX = 0) -> TriggerUpdate(DIRTY_INDEX = 0)
        #                                             ...

        # Flip the frame index prior to the wait. The coroutine isn't started until the ui_tick
        # so if multiple USD notifications have occurred, they have been batched together.

        update_frame_index = self.__dirty_frame_index
        _ = _NOTIFY_DEBUG and print(f"WaitUpdate {update_frame_index} {omni.kit.app.get_app().get_update_number()}")
        self.__dirty_frame_index = 1 - self.__dirty_frame_index

        await omni.kit.app.get_app().next_update_async()

        # release the current task so a new one can be created for the next frame
        self.__prim_changed_task[update_frame_index] = None

        # Pump the changes to the model.
        self.__update_frame_index = update_frame_index
        _ = _NOTIFY_DEBUG and print(f"ProcessUpdate {update_frame_index} {omni.kit.app.get_app().get_update_number()}")
        self._update_dirty()

    def create_node_ui(self, node_path: Sdf.Path, graph_path: Sdf.Path):
        prim = self._stage.GetPrimAtPath(node_path)
        if not prim:
            return
        node_type = prim.GetTypeName()
        if self.__is_pre_schema_graph:
            #  ignore settings node
            if node_type == LEGACY_COMPUTEGRAPHSETTINGS_TYPE:
                return
            if node_type == LEGACY_COMPUTEGRAPH_TYPE:
                self.__subgraph_paths.add(node_path)
        elif node_type == OMNIGRAPH_TYPE:
            self.__subgraph_paths.add(node_path)

        self.__subgraph_to_primpaths[graph_path] = self.__subgraph_to_primpaths.get(graph_path, set()) | {node_path}
        self.__primpath_to_subgraph[node_path] = graph_path

    def import_node(
        self, prim_path: Sdf.Path, graph_path_str: str, node_type: PrimNodeType, window, position: Tuple[float]
    ):
        """This is to import prim from the current stage to the graph, e.g. mesh prim

        Args:
            prim_path: The full path of the prim to import
            graph_path_str: full path of the og.Graph to import the node into
            node_type: The sort of prim node to add
            window: The ui.Window modal dialog that invokes this function
            position: canvas position for the new node
        """
        graph = self.get_graph(graph_path_str)
        if not graph:
            carb.log_error(f"Could find graph {graph_path_str} for Prim import")
            return

        with omni.kit.undo.group():
            new_path = self._add_prim_import_export(prim_path, graph, node_type, window)

            if not self.cull_legacy_prims():  # noqa: SIM102
                # We dropped the Prim, but OG may have declined to create a legacy Prim for it
                if og.get_node_by_path(prim_path.pathString):  # noqa: SIM102
                    self.create_node_ui(prim_path, Sdf.Path(graph_path_str))

            # Position
            self.__positions[new_path] = position
            if position:
                omni.kit.commands.execute(
                    "UsdUINodeGraphNodeSetCommand",
                    attribute=UsdUI.Tokens.uiNodegraphNodePos,
                    prim_path=new_path,
                    value=position,
                    prev=None,
                    stage=self._stage,
                )
                expansion = self.get_default_node_expansion_state(prim_node_types[node_type][0])
                omni.kit.commands.execute(
                    "UsdUINodeGraphNodeSetCommand",
                    attribute=UsdUI.Tokens.uiNodegraphNodeExpansionState,
                    prim_path=new_path,
                    value=self.og_expansion_state_to_usd(expansion),
                    prev=None,
                    stage=self._stage,
                )

            self._item_changed(None)
            carb.log_info(f'Added "{new_path}" to "{graph_path_str}"')

    def create_read_prim_node(self, prim_paths: List[Sdf.Path], graph_path_str: str, window, position: Tuple[float]):
        """This imports prims to a single read prim node from the current stage to the graph

        Args:
            prim_paths: The full paths of the prims to set on the read prim node
            graph_path_str: full path of the og.Graph to import the node into
            window: The ui.Window modal dialog that invokes this function
            position: canvas position for the new node
        """
        graph = self.get_graph(graph_path_str)
        if not graph:
            carb.log_error(f"Could find graph {graph_path_str} for Prim import")
            return

        if window:
            window.visible = False

        if len(prim_paths) <= 0:
            return

        with omni.kit.undo.group():
            stage = self._usd_context.get_stage()
            graph_path = Sdf.Path(graph.get_path_to_graph())

            # Special case for the global implicit graph. We want to prepend the default prim instead of putting the node
            # at the graph root (which is "/").
            if graph_path == Sdf.Path.absoluteRootPath and stage.HasDefaultPrim():
                default_prim = stage.GetDefaultPrim()
                if default_prim:
                    graph_path = default_prim.GetPath()

            new_node_path = graph_path.AppendChild("Read")
            new_node_path_str = omni.usd.get_stage_next_free_path(stage, new_node_path, False)
            # Create the new OG read/write node
            new_node_type = "omni.graph.nodes.ReadPrim"
            if self.__kit_version_major >= 105:
                new_node_type = "omni.graph.nodes.ReadPrims"
            og.cmds.CreateNode(graph=graph, node_path=new_node_path_str, node_type=new_node_type, create_usd=True)

            # Hook up the source prim `rel`
            new_node_input_prop = "inputs:prim"
            if self.__kit_version_major >= 105:
                new_node_input_prop = "inputs:prims"
            src_attr = stage.GetPropertyAtPath(f"{new_node_path_str}.{new_node_input_prop}")
            for prim_path in prim_paths:
                omni.kit.commands.execute("AddRelationshipTarget", relationship=src_attr, target=prim_path)

            new_path = Sdf.Path(new_node_path_str)

            if not self.cull_legacy_prims():  # noqa: SIM102
                # We dropped the Prim, but OG may have declined to create a legacy Prim for it
                if og.get_node_by_path(new_path.pathString):  # noqa: SIM102
                    self.create_node_ui(new_path, Sdf.Path(graph_path_str))

            # Position
            self.__positions[new_path] = position
            if position:
                omni.kit.commands.execute(
                    "UsdUINodeGraphNodeSetCommand",
                    attribute=UsdUI.Tokens.uiNodegraphNodePos,
                    prim_path=new_path,
                    value=position,
                    prev=None,
                    stage=self._stage,
                )
                expansion = self.get_default_node_expansion_state(new_node_type)
                omni.kit.commands.execute(
                    "UsdUINodeGraphNodeSetCommand",
                    attribute=UsdUI.Tokens.uiNodegraphNodeExpansionState,
                    prim_path=new_path,
                    value=self.og_expansion_state_to_usd(expansion),
                    prev=None,
                    stage=self._stage,
                )

            self._item_changed(None)
            carb.log_info(f'Added "{new_path}" to "{graph_path_str}"')

    def _add_prim_import_export(
        self, prim_path: Sdf.Path, graph: og.Graph, node_type: PrimNodeType, window
    ) -> Sdf.Path:
        """Adds a OG Prim Import or Export node for the given prim

        Args:
            prim_path: The full path to the existing prim
            graph: The graph to import the prim into
            node_type: The sort of prim node to add
            window: The ui.Window modal dialog that invokes this function
        Returns:
            Path to the newly created OG node
        """
        if window:
            window.visible = False

        node_type_name, suffix = prim_node_types[node_type]

        if node_type is PrimNodeType.LEGACY:
            og.cmds.CreateNode(graph=graph, node_path=prim_path.pathString, node_type=node_type_name, create_usd=False)
            return prim_path

        stage = self._usd_context.get_stage()
        graph_path = Sdf.Path(graph.get_path_to_graph())
        prim = stage.GetPrimAtPath(prim_path)
        prim_name = prim.GetName()

        # Special case for the global implicit graph. We want to prepend the default prim instead of putting the node
        # at the graph root (which is "/").
        if graph_path == Sdf.Path.absoluteRootPath and stage.HasDefaultPrim():
            default_prim = stage.GetDefaultPrim()
            if default_prim:
                graph_path = default_prim.GetPath()

        new_node_path = graph_path.AppendChild(f"{prim_name}{suffix}")
        new_node_path_str = omni.usd.get_stage_next_free_path(stage, new_node_path, False)
        # Create the new OG read/write node
        og.cmds.CreateNode(graph=graph, node_path=new_node_path_str, node_type=node_type_name, create_usd=True)
        # Hook up the source prim `rel`
        src_attr = stage.GetPropertyAtPath(f"{new_node_path_str}.inputs:prim")
        omni.kit.commands.execute("AddRelationshipTarget", relationship=src_attr, target=prim.GetPath())
        return Sdf.Path(new_node_path_str)

    def create_backdrop(self, graph_path: Sdf.Path, position: Tuple[float]):
        pseudo_node = PSEUDO_NODES_DICT["Backdrop"]
        omni.kit.commands.execute(
            "CreateUsdUIBackdropCommand",
            parent_path=graph_path,
            identifier="OGBackdrop",
            position=position,
            size=pseudo_node.size,
            display_color=pseudo_node.display_color,
        )

    def create_note(self, graph_path: Sdf.Path, position: Tuple[float]):
        pseudo_node = PSEUDO_NODES_DICT["OmniNote"]
        omni.kit.commands.execute(
            "CreateUsdUINoteCommand",
            parent_path=graph_path,
            identifier="OGNote",
            position=position,
            size=pseudo_node.size,
            display_color=pseudo_node.display_color,
        )

    def create_node(self, node_type_name: str, graph_path: str, position: Tuple[float], node_name: str = None):
        graph = self.get_graph(graph_path)
        if not graph:
            return None

        if not node_name:
            node_type = og.get_node_type(node_type_name)
            ui_name = None
            metadata = node_type.get_all_metadata()
            if metadata:
                ui_name = metadata.get(ogn.MetadataKeys.UI_NAME)
                if ui_name:
                    ui_name = ui_name.replace("(BETA)", "").strip()

            if not ui_name:
                type_name_without_namespace = node_type_name.split(".")[-1]
                ui_name = graph_config.make_nice_name(type_name_without_namespace)

            node_name = re.sub("[^0-9a-zA-Z]+", "_", ui_name).lower()  # replace non alphanumeric characters

        node_path_str = omni.usd.get_stage_next_free_path(
            self._stage, graph_path + "/" + og.Controller.safe_node_name(node_name), False
        )

        prim_path = Sdf.Path(node_path_str)
        self.__positions[prim_path] = position
        with omni.kit.undo.group():
            success, node = og.cmds.CreateNode(
                graph=graph, node_path=node_path_str, node_type=node_type_name, create_usd=True
            )
            omni.kit.commands.execute(
                "UsdUINodeGraphNodeSetCommand",
                attribute=UsdUI.Tokens.uiNodegraphNodePos,
                prim_path=prim_path,
                value=position,
                prev=None,
                stage=self._stage,
            )
            expansion = self.get_default_node_expansion_state(node_type_name)
            omni.kit.commands.execute(
                "UsdUINodeGraphNodeSetCommand",
                attribute=UsdUI.Tokens.uiNodegraphNodeExpansionState,
                prim_path=prim_path,
                value=self.og_expansion_state_to_usd(expansion),
                prev=None,
                stage=self._stage,
            )

        return success, node

    def create_subgraph_node(self, graph_path: str, position: Tuple[float]):
        graph = self.get_graph(graph_path)
        if not graph:
            return

        node_path_str = omni.usd.get_stage_next_free_path(self._stage, graph_path + "/subgraph", False)
        prim_path = Sdf.Path(node_path_str)
        self.__positions[prim_path] = position
        with omni.kit.undo.group():
            og.cmds.CreateSubgraph(graph=graph, subgraph_path=node_path_str, evaluator=None, create_usd=True)
            omni.kit.commands.execute(
                "UsdUINodeGraphNodeSetCommand",
                attribute=UsdUI.Tokens.uiNodegraphNodePos,
                prim_path=prim_path,
                value=position,
                prev=None,
                stage=self._stage,
            )
            omni.kit.commands.execute(
                "UsdUINodeGraphNodeSetCommand",
                attribute=UsdUI.Tokens.uiNodegraphNodeExpansionState,
                prim_path=prim_path,
                value=UsdUI.Tokens.open,
                prev=None,
                stage=self._stage,
            )

    def create_compound(self, compound_name: str, compound_namespace: str, selected_nodes: List[Usd.Prim]):
        """Creates a compound from the given list of node prims"""
        if not graph_config.Settings.are_compounds_enabled():
            return

        if not selected_nodes:
            return

        pos = CompoundUtils.compute_compound_node_position(selected_nodes)
        node_paths = [x.GetPath() for x in selected_nodes]
        self.selection = []

        (compound_name, compound_namespace) = CompoundUtils.sanitize_compound_name_and_namespace(
            compound_name, compound_namespace
        )

        with omni.kit.undo.group():
            (_, compound_node_path) = og.cmds.ReplaceWithCompound(
                nodes=node_paths, compound_name=compound_name, namespace=compound_namespace
            )
            if compound_node_path != Sdf.Path():
                omni.kit.commands.execute(
                    "UsdUINodeGraphNodeSetCommand",
                    attribute=UsdUI.Tokens.uiNodegraphNodePos,
                    prim_path=compound_node_path,
                    value=pos,
                    prev=None,
                )
                self.selection = [self._stage.GetPrimAtPath(compound_node_path)]
                self._item_changed(None)

    def create_subgraph_compound(self, selected_nodes: List[Usd.Prim]):
        """
        Transforms a selection of nodes into a subgraph-style compound
        """
        if not graph_config.Settings.are_compounds_enabled():
            return

        if not selected_nodes:
            return

        pos = CompoundUtils.compute_compound_node_position(selected_nodes)
        node_paths = [x.GetPath() for x in selected_nodes]
        self.selection = []

        with omni.kit.undo.group():
            (_, compound_node) = og._unstable.cmds.ReplaceWithCompoundSubgraph(  # noqa: protected-access
                nodes=node_paths
            )
            if compound_node:
                omni.kit.commands.execute(
                    "UsdUINodeGraphNodeSetCommand",
                    attribute=UsdUI.Tokens.uiNodegraphNodePos,
                    prim_path=compound_node.get_prim_path(),
                    value=pos,
                    prev=None,
                )
                self.selection = [self._stage.GetPrimAtPath(compound_node.get_prim_path())]
                self._item_changed(None)

    def get_graph(self, graph_path: str):
        """get the subgraph/root graph"""
        if not self._graph or not self._graph.is_valid():
            return None

        if graph_path is None or graph_path == self._graph_root.pathString:
            return self._graph

        # can't get any valid graph
        graph = self._graph.get_subgraph(graph_path)
        if not graph or not graph.is_valid():
            return None

        return graph

    def is_graph(self, item: Sdf.Path):
        """Check if item is a graph"""
        if item == self._graph_root:
            return True
        return item in self.__subgraph_paths

    def get_attribute_from_path(self, attr_path: Sdf.Path) -> Optional[og.Attribute]:
        """get the attribute from the graph with an input usd attribute path"""
        if not attr_path or not isinstance(attr_path, Sdf.Path):
            return None

        # If the attribute path specifies a path on a compound (e.g. /../Compound/Subgraph.inputs:foo)
        # this will return the attribute on the owning compound node (e.g. /Compound.inputs:foo)
        attr_path = VirtualNodeHelper.convert_from(attr_path)
        with suppress(og.OmniGraphError):
            return og.Controller.attribute(str(attr_path))
        return None

    def get_path_from_attribute(self, attr: og.Attribute) -> Sdf.Path:
        """get the attribute path from an input Attribute"""
        if not attr.is_valid():
            return Sdf.Path()
        attr_name = attr.get_name()
        node = attr.get_node()
        attr_path = Sdf.Path(node.get_prim_path()).AppendProperty(attr_name)
        return attr_path

    def traverse_actual_dests(self, ports: List[Sdf.Path], results: List[List[Sdf.Path]]):
        """Traverse the actual dests of the given port and append the result to the results list

        Note: this is no longer used internally, but kept for backwards compatibility"""
        dests = self._reversed_connections.get(ports[-1], set())
        if dests:
            for dest in dests:
                result = ports.copy()
                result.append(dest)
                if self.is_graph(dest.GetPrimPath()):
                    self.traverse_actual_dests(result, results)
                else:
                    results.append(result)
        else:
            results.append(ports)

    def get_actual_dests(self, port: Sdf.Path) -> List[List[Sdf.Path]]:
        """
        Return a list contains each route from the actual dest port with all connected dests port

        Note: this is no longer used internally, but kept for backwards compatibility
        """
        results = []
        self.traverse_actual_dests([port], results)
        return results

    def get_actual_source(self, port_path: Sdf.Path) -> List[Sdf.Path]:
        """
        Return a list contains from the input source port with all connected actual source port

        Note: this is no longer used internally, but kept for backwards compatibility
        """
        if self.is_graph(port_path.GetPrimPath()) and port_path in self._connections:
            sources = self._connections[port_path]
            if sources:
                return [port_path] + [path for source in sources for path in self.get_actual_source(source)]
        return [port_path]

    def get_event_stream(self) -> carb.events.IEventStream:
        return self.__event_stream

    def __get_attribute_type_description(self, attr: og.Attribute) -> str:
        """Returns the text description of the given attribute's type"""
        attr_type = attr.get_resolved_type()
        if attr_type.base_type == og.BaseDataType.UNKNOWN:
            extended_type = attr.get_extended_type()
            if extended_type == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_ANY:
                return "unresolved {any}"
            if extended_type == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION:
                return "unresolved {union}"
        if attr_type.base_type == og.BaseDataType.PRIM:
            return "bundle"
        return attr_type.get_ogn_type_name()

    def get_port_type(self, path: Sdf.Path) -> Optional[str]:
        """Returns the description of the port's attribute type, or None if there is a problem"""
        if path in self.__subgraph_port_map:
            return self.__subgraph_port_map[path]
        attr = self.get_attribute_from_path(path)
        return self.__get_attribute_type_description(attr) if attr else None

    def get_usd_port_type(self, attr_path: Sdf.Path) -> Sdf.ValueTypeName:
        if attr_path in self.__subgraph_port_map:
            return self.__subgraph_port_map[attr_path]
        attr = self._stage.GetPrimAtPath(attr_path.GetPrimPath()).GetAttribute(attr_path.name)
        return attr.GetTypeName() if attr else None

    def get_next_free_name(self, base_name, node_path: Sdf.Path):
        """create a unique attribute name on the input prim"""
        proposed_name = base_name
        proposed_id = 0
        attr_path = node_path.AppendProperty(proposed_name)
        # can't use usd prim GetAttribute to check since imported graph doesn't not have ports for subgraph in backend
        while attr_path in self.__subgraph_port_map:
            proposed_id += 1
            proposed_name = f"{base_name}{proposed_id}"
            attr_path = node_path.AppendProperty(proposed_name)
        return proposed_name, attr_path

    def get_node_from_prim(self, prim: Union[Usd.Prim, Sdf.Path]) -> Optional[og.Node]:
        if self.is_pseudo_node(prim):
            return None
        if self._graph:
            return og.Controller.node(prim, self._graph)
        return None

    def is_pseudo_node(self, prim_or_path: Union[Usd.Prim, Sdf.Path]):
        if isinstance(prim_or_path, Sdf.Path):
            prim_or_path = self._stage.GetPrimAtPath(prim_or_path)
        elif not isinstance(prim_or_path, Usd.Prim):
            return False
        return prim_or_path and prim_or_path.GetTypeName() in PSEUDO_NODES_DICT

    def find_next_position_descending(self, pos: Tuple[float]) -> Tuple[float]:
        """
        Attempts to find a position that doesn't conflict by moving downwards from the given
        position to resolve potential conflicts
        """
        # TODO -- use the actual node sizes
        use_node_width = 200
        use_node_height = 100

        def collides(pos):
            def overlap(posa, posb):
                return (abs(posb[0] - posa[0]) <= use_node_width) and (abs(posb[1] - posa[1]) <= use_node_height)

            return next(filter(partial(overlap, pos), self.__positions.values()), None)

        while collides(pos):
            pos = (pos[0], pos[1] + use_node_height / 4)

        return pos

    def special_select_widget(self, node, node_widget):
        """This is for specifying a part of a node that should be selectable,
        when you don't want the whole node to be selectable.  For example,
        just the header bar for a Backdrop.
        """
        if self[node].type == "Backdrop":
            return node_widget.header_frame

        # Returning None means node_widget will get used
        return None

    # Kept for backward compatibility
    @staticmethod
    def make_nice_name(ugly_name: str, preserve_final_part: bool = False):
        """
        Takes a raw name and formats it for use as the corresponding nice name in the UI.

        o  (For attribute names) Standard namespaces ('inputs', 'outputs', 'state') are stripped off the front.
        o  (For attribute names) Any remaining namespaces are converted to words within the name.
        o  Underscores are converted to spaces.
        o  Mixed-case words are broken into separate words (e.g. 'primaryRGBColor' -> 'primary RGB Color').
        o  Words which are all lower-case are capitalized (e.g. 'primary' -> 'Primary').

        If 'preserve_final_part' is True then the portion of 'ugly_name' after the last namespace is left as-is.
        """
        return graph_config.make_nice_name(ugly_name, preserve_final_part)

    # ------------------------------------------------------------------------------------------------------------
    # Deprecated functions

    # Deprecated due to the models concept of selection, which may not take into account
    # the compound that is currently active

    @ogt.deprecated_function("Use create_compound instead")
    def create_compound_from_selection(self, compound_name: str, compound_namespace: str):
        """Creates a compound node from the current set of selected nodes"""
        return self.create_compound(compound_name, compound_namespace, self.selected_nodes)

    @ogt.deprecated_function("Use the selection from graph view")
    @property
    def selected_nodes(self) -> List[Usd.Prim]:
        """Returns only those selected prims which represent graph nodes."""
        return list(set(self.selection or []).intersection(self.nodes or []))
