import omni.anim.graph.core as ag
import omni.kit.undo
from omni.kit.widget.graph.graph_model import GraphModel
from pxr import Usd
from .animation_graph_manager import AnimationGraphManager
from .node import Port, Node
from .node_graph import NodeGraph, NodeGraphRoot
from typing import List, Tuple, Optional, Dict


class AnimationGraphModel(GraphModel):
    def __init__(self, node_graph: NodeGraphRoot, graph_manager: AnimationGraphManager):
        super().__init__()

        self._root_graph = node_graph
        self._graph_manager = graph_manager
        self._stage: Usd.Stage = node_graph.prim.GetStage()
        self._current_graph: NodeGraph = self._root_graph

        def graph_changed(node: Node):
            if not node or (node.has_sub_graph() and node.sub_graph == self._current_graph):
                self._item_changed(None)
            else:
                self._item_changed(node)

        self._root_graph_changed_callback_id: Optional[int] = self._root_graph.add_graph_changed_callback(graph_changed)
        self._expansion_states: Dict[Node, GraphModel.ExpansionState] = {}
        self._selected_nodes: List[Node] = []
        self._node_positions: Dict[Node, Tuple[float, float]] = {}
        self._current_active_node: Optional[Node] = None
        self._current_selected_nodes: Dict[Node, Tuple[float, float]] = {}

    def destroy(self):
        self._stage = None
        self._graph_manager = None
        self._root_graph.remove_graph_changed_callback(self._root_graph_changed_callback_id)
        self._root_graph = None
        self._root_graph_changed_callback_id = None
        self._current_graph = None
        self._selected_nodes = None
        self._node_positions = None
        self._current_active_node = None
        self._current_selected_nodes = None

    @property
    def stage(self):
        return self._stage

    @property
    def root_graph(self):
        return self._root_graph

    @property
    def current_graph(self):
        return self._current_graph

    @current_graph.setter
    def current_graph(self, graph: NodeGraph):
        if not self._root_graph or \
                graph == self._current_graph or \
                not graph.prim.GetPath().HasPrefix(self._root_graph.prim.GetPath()):
            return
        self._current_graph = graph
        self._item_changed(None)

    def refresh(self):
        self._item_changed(None)

    @property
    def nodes(self, item=None):
        if item is None:
            if self._current_graph is None:
                return []
            return self._current_graph.nodes
        if isinstance(item, Node) and item.has_sub_graph():
            return item.sub_graph.nodes
        return None

    @property
    def name(self, item):
        return item.name

    @name.setter
    def name(self, value, item):
        item.name = value

    @property
    def type(self, item):
        return item.type

    @property
    def description(self, item):
        return item.description

    @property
    def inputs(self, item):
        if isinstance(item, Node):
            return None
        if item.kind == Port.Kind.Input:
            return item.connected_ports
        return None

    @inputs.setter
    def inputs(self, value, item):
        if isinstance(item, Node):
            return
        graph = item.node_graph
        graph_path = graph.prim.GetPath()
        if not graph_path.HasPrefix(self._root_graph.prim.GetPath()):
            return
        if len(value) > 0:
            with omni.kit.undo.group():
                for port in value:
                    port_graph = port.node_graph
                    if port_graph.prim.GetPath().HasPrefix(graph_path):
                        # Special case for state machine UI, the actual port passed in doesn't matter.
                        # Only the node that the port belongs to matters, so just force the correct
                        # port from that node
                        if port.kind != Port.Kind.Output and port.type == Port.Type.Flow and item.type == Port.Type.Flow:
                            port_node = port_graph.get_node(port_graph.get_node_path(port))
                            if port_node:
                                port = port_node.output
                        graph.create_connection(port, item)
        else:
            with omni.kit.undo.group():
                for port in item.connected_ports.copy():
                    graph.delete_connection(port, item)

    @property
    def outputs(self, item):
        if isinstance(item, Node):
            return None
        if item.kind == Port.Kind.Output:
            return []
        return None

    @property
    def connected_ports(self, item=None):
        if item is None:
            return None
        if isinstance(item, Port):
            return item.connected_ports
        if isinstance(item, Node):
            return [port for port in item.ports if len(port.connected_ports) > 0]

    @property
    def ports(self, item=None):
        if item is None:
            return None
        if isinstance(item, Port):
            return None
        return item.ports

    def can_connect(self, source, target):
        """Return if it's possible to connect source to target"""
        if source and target and source != target and source.type == target.type:
            if source.type == Port.Type.Flow:
                # Special case for state machine UI, the actual port passed in doesn't matter.
                # Only the node that the port belongs to matters, so just force the correct
                # port from that node
                if source.kind != Port.Kind.Output:
                    source_graph = source.node_graph
                    source_node = source_graph.get_node(source_graph.get_node_path(source))
                    if source_node:
                        source = source_node.output
                return source not in target.connected_ports and target not in source.connected_ports
            return source.kind != target.kind
        return False

    @property
    def expansion_state(self, item=None):
        return self._expansion_states.get(item, GraphModel.ExpansionState.OPEN)

    @expansion_state.setter
    def expansion_state(self, value, item=None):
        if value == GraphModel.ExpansionState.OPEN and item in self._expansion_states:
            del self._expansion_states[item]
        else:
            self._expansion_states[item] = value
        self._item_changed(None)

    @property
    def selection(self):
        return self._selected_nodes

    @selection.setter
    def selection(self, value: List[Node]):
        self._selected_nodes = value
        self._selection_changed()

    @property
    def position(self, item):
        if self._current_active_node:
            return self._node_positions.get(item, item.position)

        return item.position

    @position.setter
    def position(self, value, item=None):
        if not value:
            return

        self._node_positions[item] = value
        if self._current_active_node == item:
            for node, node_position in self._current_selected_nodes.items():
                self._node_positions[node] = (value[0] + node_position[0], value[1] + node_position[1])
                self._item_changed(node)
        elif not self._current_active_node:
            item.set_position(value, True)

    def position_begin_edit(self, item):
        position = self[item].position
        self._current_active_node = item
        if len(self.selection) > 1:
            self._current_selected_nodes = {}
            for node in self.selection:
                if not node == item:
                    node_position = self[node].position
                    self._current_selected_nodes[node] = (
                        node_position[0] - position[0],
                        node_position[1] - position[1],
                    )

    def position_end_edit(self, item):
        if self._current_active_node:
            with omni.kit.undo.group():
                self._current_active_node.position = self[self._current_active_node].position
                for node in self._current_selected_nodes.keys():
                    node.position = self[node].position

                self._current_active_node = None
                self._current_selected_nodes = {}

    @property
    def errors(self, item):
        errors = item.errors
        if errors:
            return errors

        node_compile_errors = self._graph_manager.get_compile_errors(item.node_graph.root_graph)
        if node_compile_errors:
            item_path_string = item.prim.GetPath().pathString
            if item_path_string in node_compile_errors:
                return node_compile_errors[item_path_string]

        return None
