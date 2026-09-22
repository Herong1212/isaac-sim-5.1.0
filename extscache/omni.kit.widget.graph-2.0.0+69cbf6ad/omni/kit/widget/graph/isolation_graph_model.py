# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides a class to isolate and manage a sub-graph within a larger graph model, including functionality for adding, editing, and connecting nodes and ports in the isolated section."""


__all__ = ["IsolationGraphModel"]

from .graph_model import GraphModel
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
from .graph_model_batch_position_helper import GraphModelBatchPositionHelper


def _get_ports_recursive(model, root):
    """Recursively get all the ports"""
    ports = model[root].ports
    if ports:
        recursive = []
        for port in ports:
            recursive.append(port)
            subports = _get_ports_recursive(model, port)
            if subports:
                recursive += subports
        return recursive
    return ports


class IsolationGraphModel:
    """A model class to isolate and manage a sub-graph within a larger graph model.

    This class provides functionality to create and manage a sub-graph within a larger graph model. It allows for the isolation of a section of a graph model, enabling operations such as adding, editing, and connecting nodes and ports within this isolated section, without affecting the rest of the graph model.

    Args:
        model (GraphModel): The graph model from which the sub-graph is isolated.
        root: The root node of the sub-graph to be isolated."""

    class MagicWrapperMeta(type):
        """
        Python always looks in the class (and parent classes) __dict__ for
        magic methods and __getattr__ doesn't work, but since we want to
        override them, we need to use this trick with proxy property.

        It makes the class looking like the source object.

        See https://stackoverflow.com/questions/9057669 for details.
        """

        def __init__(cls, name, bases, dct):
            ignore = "class mro new init setattr getattribute dict"

            def make_proxy(name):
                def proxy(self, *args):
                    return getattr(self.source, name)

                return proxy

            type.__init__(cls, name, bases, dct)
            ignore = set("__%s__" % n for n in ignore.split())
            for name in dir(cls):
                if name.startswith("__"):
                    if name not in ignore and name not in dct:
                        setattr(cls, name, property(make_proxy(name)))

    class EmptyPort:
        """Is used by the model for an empty port"""

        def __init__(self, parent: Union["IsolationGraphModel.InputNode", "IsolationGraphModel.OutputNode"]):
            self.parent = parent

        @staticmethod
        def get_type_name() -> str:
            """The string type that goes the source model abd view"""
            return "EmptyPort"

    class InputNode(metaclass=MagicWrapperMeta):
        """
        Is used by the model for the input node. This node represents input
        ports of the compound node and it's placed to the subnetwork of the
        compound.
        """

        def __init__(self, model: GraphModel, source):
            self._model = model
            self._inputs = []
            self.source = source

            # TODO: circular reference
            self.empty_port = IsolationGraphModel.EmptyPort(self) if self._model[self.source].add_empty_input_port else None

        def __getattr__(self, attr):
            return getattr(self.source, attr)

        def __hash__(self):
            # Hash should be different from source and from OutputNode
            return hash((self.source, "InputNode"))

        @staticmethod
        def get_type_name() -> str:
            """The string type that goes the source model and view"""
            return "InputNode"

        @property
        def ports(self) -> Optional[List[Any]]:
            """The list of ports of this node. It only has input ports from the compound node."""
            ports = _get_ports_recursive(self._model, self.source)
            if ports is not None:
                inputs = [(port, self._model[port].inputs) for port in ports]
                self._inputs = [(p, i) for p, i in inputs if i is not None]
                res = [p for p, _ in self._inputs]
                if self.empty_port:
                    res += [self.empty_port]
                return res

    class OutputNode(metaclass=MagicWrapperMeta):
        """
        Is used by the model for the ouput node. This node represents output
        ports of the comound node and it's placed to the subnetwork of the
        compound.
        """

        def __init__(self, model: GraphModel, source):
            self.source = source
            self._model = model
            self._outputs = []

            # TODO: circular reference
            self.empty_port = IsolationGraphModel.EmptyPort(self) if self._model[self.source].add_empty_output_port else None

        def __getattr__(self, attr):
            return getattr(self.source, attr)

        def __hash__(self):
            # Hash should be different from source and from InputNode
            return hash((self.source, "OutputNode"))

        @staticmethod
        def get_type_name() -> str:
            """The string type that goes the source model and view"""
            return "OutputNode"

        @property
        def ports(self) -> Optional[List[Any]]:
            """The list of ports of this node. It only has output ports from the compound node."""
            ports = self._model[self.source].ports
            if ports is not None:
                outputs = [(port, self._model[port].outputs) for port in ports]
                self._outputs = [(p, o) for p, o in outputs if o is not None]
                res = [p for p, _ in self._outputs]
                if self.empty_port:
                    res += [self.empty_port]
                return res

    class _IsolationItemProxy(GraphModel._ItemProxy):
        """
        The proxy class that redirects the model calls from view to the
        source model or to the isolation model.
        """

        def __init__(self, model: GraphModel, item: Any, isolation_model: "IsolationGraphModel"):
            super().__init__(model, item)
            object.__setattr__(self, "_isolation_model", isolation_model)

        def __setattr__(self, attr, value):
            """
            Called when an attribute assignment is attempted. This is called
            instead of the normal mechanism (i.e. store the value in the
            instance dictionary).
            """
            if hasattr(type(self), attr):
                proxy_property = getattr(type(self), attr)
                proxy_property.fset(self, value)
            else:
                super().__setattr__(attr, value)

        def is_input_node(
            self, item: Union["IsolationGraphModel.InputNode", "IsolationGraphModel.OutputNode"] = None
        ) -> bool:
            """True if the current redirection is related to the input node"""
            if item is None:
                item = self._item
            return isinstance(item, IsolationGraphModel.InputNode)

        def is_output_node(
            self, item: Union["IsolationGraphModel.InputNode", "IsolationGraphModel.OutputNode"] = None
        ) -> bool:
            """True if the current redirection is related to the output node"""
            if item is None:
                item = self._item
            return isinstance(item, IsolationGraphModel.OutputNode)

        def is_empty_port(self, item: "IsolationGraphModel.EmptyPort" = None) -> bool:
            """True if the current redirection is related to the empty port"""
            if item is None:
                item = self._item
            return isinstance(item, IsolationGraphModel.EmptyPort)

        # The methods of the model

        @property
        def name(self) -> str:
            """Redirects call to the source model if it's the model of the source model"""
            if self.is_input_node():
                return self._model[self._item.source].name + " (input)"
            elif self.is_output_node():
                return self._model[self._item.source].name + " (output)"
            elif self.is_empty_port():
                return type(self._item).get_type_name()
            else:
                return self._model[self._item].name

        @name.setter
        def name(self, value: str):
            # Usually it's redirected automatically, but since we overrided property getter, we need to override setter
            if self.is_input_node() or self.is_output_node():
                self._model[self._item.source].name = value
            else:
                self._model[self._item].name = value

        @property
        def type(self) -> str:
            """Redirects call to the source model if it's the model of the source model"""
            if self.is_input_node() or self.is_output_node() or self.is_empty_port():
                return type(self._item).get_type_name()
            else:
                return self._model[self._item].type

        @property
        def ports(self) -> Optional[List[Any]]:
            """Redirects call to the source model if it's the model of the source model"""
            if self.is_input_node() or self.is_output_node():
                ports = self._item.ports
            elif self.is_empty_port():
                # TODO: Sub-ports
                return
            else:
                ports = self._model[self._item].ports

            # Save it for the future, so we know which ports belong to the current sub-network.
            # TODO: read from cache when second call
            for port in ports or []:
                self._isolation_model._ports[port] = self._item
            self._isolation_model._nodes[self._item] = ports

            return ports

        @ports.setter
        def ports(self, value: List[Any]):
            if self.is_input_node():
                # Pretend like we set the ports of the compound node of the source model.
                filtered = list(self._isolation_model._root_outputs.keys())
                for port in value:
                    if self.is_empty_port(port):
                        continue
                    filtered.append(port)
                self._model[self._item.source].ports = filtered
            elif self.is_output_node():
                # Pretend like we set the ports of the compound node of the source model.
                filtered = []
                for port in value:
                    if self.is_empty_port(port):
                        continue
                    filtered.append(port)
                filtered += list(self._isolation_model._root_inputs.keys())
                self._model[self._item.source].ports = filtered
            else:
                # Just redirect the call
                self._model[self._item].ports = value

        @property
        def inputs(self) -> Optional[List[Any]]:
            if self.is_empty_port():
                if self.is_output_node(self._item.parent):
                    # Show dot on the left side
                    return []
                else:
                    return
            elif self._item in self._isolation_model._root_ports:
                # This is the port of the root compound node
                inputs = self._isolation_model._root_outputs.get(self._item, None)
                if inputs is None:
                    return
            else:
                inputs = self._model[self._item].inputs
            if not inputs:
                return inputs
            # Filter out the connections that go outside of this isolated model
            return [
                i
                for i in inputs
                if i in self._isolation_model._ports
                or i in self._isolation_model._root_inputs
                or i in self._isolation_model._root_outputs
            ]

        @inputs.setter
        def inputs(self, value: List[Any]):
            if self.is_empty_port():
                # The request to connect something to the Empty port of InputNode or OutputNode
                target = self._item.parent.source
            elif self.is_input_node() or self.is_output_node():
                # The request to connect something to the InputNode or OutputNode itself
                target = self._item.source
            else:
                target = self._item

            if value is not None:
                filtered = []
                for p in value:
                    if isinstance(p, IsolationGraphModel.EmptyPort):
                        # If it's an EmptyPort, we need to connect it to the
                        # source directly. When the model receives the request
                        # to connect to the node itself, it will create a port
                        # for it.
                        source = p.parent.source
                        filtered.append(source)
                    else:
                        filtered.append(p)
                value = filtered

            self._model[target].inputs = value

        @property
        def outputs(self) -> Optional[List[Any]]:
            if self.is_empty_port():
                if self.is_input_node(self._item.parent):
                    # Show dot on the right side
                    return []
                else:
                    return
            elif self._item in self._isolation_model._root_ports:
                outputs = self._isolation_model._root_inputs.get(self._item)
                if outputs is None:
                    return
            else:
                outputs = self._model[self._item].outputs
            if not outputs:
                return outputs
            # Filter out the connections that go outside of this isolated model
            return [
                o
                for o in outputs
                if o in self._isolation_model._ports
                or o in self._isolation_model._root_inputs
                or o in self._isolation_model._root_outputs
            ]

        @property
        def position(self) -> Optional[Tuple[float]]:
            if self.is_input_node():
                if self._isolation_model._root_inputs:
                    # TODO: It's not good to keep the position on the first available port. We need to group them.
                    port_to_keep_position = list(self._isolation_model._root_inputs.keys())[0]
                    position = self._model[port_to_keep_position].position
                    if position is not None:
                        return position
                    elif self._isolation_model._input_position:
                        return self._isolation_model._input_position
                else:
                    return self._isolation_model._input_position
            elif self.is_output_node():
                if self._isolation_model._root_outputs:
                    # TODO: It's not good to keep the position on the first available port. We need to group them.
                    port_to_keep_position = list(self._isolation_model._root_outputs.keys())[0]
                    position = self._model[port_to_keep_position].position
                    if position is not None:
                        return position
                    elif self._isolation_model._output_position:
                        return self._isolation_model._output_position
                else:
                    return self._isolation_model._output_position
            else:
                return self._model[self._item].position

        @position.setter
        def position(self, value: Optional[Tuple[float]]):
            if self.is_input_node():
                if self._isolation_model._root_inputs:
                    # TODO: get the proper port_to_keep_position
                    port_to_keep_position = list(self._isolation_model._root_inputs.keys())[0]
                    self._model[port_to_keep_position].position = value
                else:
                    self._isolation_model._input_position = value
            elif self.is_output_node():
                if self._isolation_model._root_outputs:
                    # TODO: get the proper port_to_keep_position
                    port_to_keep_position = list(self._isolation_model._root_outputs.keys())[0]
                    self._model[port_to_keep_position].position = value
                else:
                    self._isolation_model._output_position = value
            else:
                self._model[self._item].position = value

        @property
        def size(self) -> Optional[Tuple[float]]:
            if self.is_input_node() or self.is_output_node():
                # Can't set/get size of input/output node
                return
            else:
                return self._model[self._item].size

        @size.setter
        def size(self, value: Optional[Tuple[float]]):
            if self.is_input_node() or self.is_output_node():
                # Can't set/get size of input/output node
                pass
            else:
                self._model[self._item].size = value

        @property
        def display_color(self) -> Optional[Tuple[float]]:
            if self.is_input_node() or self.is_output_node():
                # Can't set/get display_color of input/output node
                return
            else:
                return self._model[self._item].display_color

        @display_color.setter
        def display_color(self, value: Optional[Tuple[float]]):
            if self.is_input_node() or self.is_output_node():
                # Can't set display color of input/output
                pass
            else:
                self._model[self._item].display_color = value

        @property
        def stacking_order(self) -> int:
            if self.is_input_node() or self.is_output_node():
                return 1
            else:
                return self._model[self._item].stacking_order

        @property
        def preview(self) -> Any:
            """Redirects call to the source model if it's the model of the source model"""
            if self.is_input_node() or self.is_output_node():
                return self._model[self._item.source].preview
            else:
                return self._model[self._item].preview

        @property
        def icon(self) -> Any:
            """Redirects call to the source model if it's the model of the source model"""
            if self.is_input_node() or self.is_output_node():
                return self._model[self._item.source].icon
            else:
                return self._model[self._item].icon

        @property
        def preview_state(self) -> GraphModel.PreviewState:
            """Redirects call to the source model if it's the model of the source model"""
            if self.is_input_node() or self.is_output_node():
                return self._model[self._item.source].preview_state
            else:
                return self._model[self._item].preview_state

        @preview_state.setter
        def preview_state(self, value: GraphModel.PreviewState):
            if self.is_input_node() or self.is_output_node():
                self._model[self._item.source].preview_state = value
            else:
                self._model[self._item].preview_state = value

    ############################################################################

    def __getattr__(self, attr):
        """Pretend it's self._model"""
        return getattr(self._model, attr)

    def __getitem__(self, item):
        """Called to implement evaluation of self[key]"""
        # Return a proxy that redirects its properties back to the model.
        # return self._model[item]
        return self._IsolationItemProxy(self._model, item, self)

    def __init__(self, model: GraphModel, root):
        """Initializes the IsolationGraphModel."""
        self._model: Optional[GraphModel] = model
        # It's important to set the proxy to set the position through this model
        if self._model and isinstance(self._model, GraphModelBatchPositionHelper):
            self._model.batch_proxy = self

        self._root = root

        self.clear_caches()

        # Redirect events from the original model to here
        self.__on_item_changed = GraphModel._Event()
        self.__on_selection_changed = GraphModel._Event()
        self.__on_node_changed = GraphModel._Event()
        self.__item_changed_subscription = self._model.subscribe_item_changed(self._item_changed)
        self.__selection_changed_subscription = self._model.subscribe_selection_changed(self._selection_changed)
        self.__node_changed_subscription = self._model.subscribe_node_changed(self._rebuild_node)

        # We create input and output nodes for the attributes of the parent compound
        # node. When the parent doesn't have attributes, we need to keep the
        # position locally.
        self._input_position = None
        self._output_position = None

        # Virtual nodes
        if self._root is not None and self._root_inputs:
            self._input_nodes = [IsolationGraphModel.InputNode(self._model, self._root)]
        else:
            self._input_nodes = []

        if self._root is not None and self._root_outputs:
            self._output_nodes = [IsolationGraphModel.OutputNode(self._model, self._root)]
        else:
            self._output_nodes = []

    def destroy(self):
        """Destroys the model, clearing all internal data and subscriptions."""
        self._model = None
        self._root = None
        self._ports = {}
        self._nodes = {}
        self._root_inputs = {}
        self._root_outputs = {}
        self.__on_item_changed = GraphModel._Event()
        self.__on_selection_changed = GraphModel._Event()
        self.__on_node_changed = GraphModel._Event()
        self.__item_changed_subscription = None
        self.__selection_changed_subscription = None
        self._input_nodes = []
        self._output_nodes = []

    def clear_caches(self):
        """Clears the internal caches of the model."""
        # Port to node
        # TODO: WeakKeyDictionary
        self._ports: Dict[Any, Any] = {}
        # Nodes to ports
        # TODO: WeakKeyDictionary
        self._nodes: Dict[Any, Any] = {}

        # Cache ports and inputs
        self._root_ports: List[Any] = _get_ports_recursive(self._model, self._root) if (self._root is not None) else []
        # Port to input/output
        self._root_inputs: Dict[Any, Any] = {}
        self._root_outputs: Dict[Any, Any] = {}

        for p in self._root_ports or []:
            inputs = self._model[p].inputs
            if inputs is not None:
                self._root_inputs[p] = inputs

            outputs = self._model[p].outputs
            if outputs is not None:
                self._root_outputs[p] = outputs

    def add_input_or_output(self, position: Tuple[float], is_input: bool = True):
        """Adds an input or output node to the isolation graph.

        Args:
            position (Tuple[float]): The position where the node should be added.
            is_input (bool, optional): Whether the node is an input node. Defaults to True."""
        if is_input:
            if self._input_nodes:  # pragma: no cover
                # TODO: Remove when we can handle many nodes
                if self._root_inputs:
                    # Set the position of the input node if the position is not set
                    port_position = list(self._root_inputs.keys())[0]
                    if not self[port_position].position:
                        self[port_position].position = position
                return
            node = IsolationGraphModel.InputNode(self._model, self._root)
            self._input_nodes.append(node)
        else:
            if self._output_nodes:  # pragma: no cover
                # TODO: Remove when we can handle many nodes
                if self._root_outputs:
                    # Set the position of the output node if the position is not set
                    port_position = list(self._root_outputs.keys())[0]
                    if not self[port_position].position:
                        self[port_position].position = position
                return
            node = IsolationGraphModel.OutputNode(self._model, self._root)
            self._output_nodes.append(node)
        self[node].position = position
        # TODO: Root is changed
        self._item_changed(None)

    def _item_changed(self, item=None):
        """Call the event object that has the list of functions"""
        if item is None:
            self.clear_caches()

        if item == self._root:
            # Root item is changed. Rebuild all.
            self.clear_caches()
            item = None

        if item in self._root_inputs.keys():
            self.__on_item_changed(self._input_nodes[0])
        elif item in self._root_outputs.keys():
            self.__on_item_changed(self._output_nodes[0])
        else:
            # TODO: Filter unnecessary calls
            self.__on_item_changed(item)

    def subscribe_item_changed(self, fn):
        """Subscribes to item changed events.

        Args:
            fn (Callable): The function to be called when an item changes.

        Returns:
            _EventSubscription: An object that will automatically unsubscribe when destroyed."""
        return self._EventSubscription(self.__on_item_changed, fn)

    def _selection_changed(self):
        """Call the event object that has the list of functions"""
        # TODO: Filter unnecessary calls
        self.__on_selection_changed()

    def _rebuild_node(self, item=None, full=False):
        """Call the event object that has the list of functions"""
        self.__on_node_changed(item, full=full)

    def subscribe_selection_changed(self, fn):
        """Subscribes to selection changed events.

        Args:
            fn (Callable): The function to be called when the selection changes.

        Returns:
            _EventSubscription: An object that will automatically unsubscribe when destroyed."""
        return self._EventSubscription(self.__on_selection_changed, fn)

    def subscribe_node_changed(self, fn):
        """Subscribes to node changed events.

        Args:
            fn (Callable): The function to be called when a node changes.

        Returns:
            _EventSubscription: An object that will automatically unsubscribe when destroyed."""
        return self._EventSubscription(self.__on_node_changed, fn)

    @property
    def nodes(self, item: Any = None):
        """It's only called to get the nodes from the top level

        Returns:
            Optional[List[Any]]: A list of nodes at the top level, if any."""
        nodes = self._model[self._root].nodes
        if nodes is not None:
            # Inject the input and the output nodes
            nodes += self._input_nodes + self._output_nodes
        return nodes

    def can_connect(self, source: Any, target: Any):
        """Checks if a connection between the source and target can be made.

        Args:
            source (Any): The source of the connection.
            target (Any): The target of the connection.

        Returns:
            bool: True if the connection is possible, False otherwise."""
        if isinstance(source, IsolationGraphModel.EmptyPort) or isinstance(target, IsolationGraphModel.EmptyPort):
            return True

        return self._model.can_connect(source, target)

    def position_begin_edit(self, item: Any):
        """Begins the edit operation for the position of an item.

        Args:
            item (Any): The item whose position is being edited."""
        if isinstance(item, IsolationGraphModel.InputNode):
            if self._root_inputs:
                # The position of the input node
                port_to_keep_position = list(self._root_inputs.keys())[0]
                self._model.position_begin_edit(port_to_keep_position)
        elif isinstance(item, IsolationGraphModel.OutputNode):
            if self._root_outputs:
                # The position of the output node
                port_to_keep_position = list(self._root_outputs.keys())[0]
                self._model.position_begin_edit(port_to_keep_position)
        else:
            # Position of the regular node
            self._model.position_begin_edit(item)

    def position_end_edit(self, item: Any):
        """Ends the edit operation for the position of an item.

        Args:
            item (Any): The item whose position edit operation is being ended."""
        if isinstance(item, IsolationGraphModel.InputNode):
            if self._root_inputs:
                # The position of the input node
                port_to_keep_position = list(self._root_inputs.keys())[0]
                self._model.position_end_edit(port_to_keep_position)
        elif isinstance(item, IsolationGraphModel.OutputNode):
            if self._root_outputs:
                # The position of the output node
                port_to_keep_position = list(self._root_outputs.keys())[0]
                self._model.position_end_edit(port_to_keep_position)
        else:
            # Position of the regular node
            self._model.position_end_edit(item)

    @property
    def selection(self) -> Optional[List[Any]]:
        """Gets the current selection.

        Returns:
            Optional[List[Any]]: The currently selected items."""
        # Redirect to the model. We need it to override the setter
        if self._model:
            return self._model.selection

    @selection.setter
    def selection(self, value: Optional[List[Any]]):
        """Sets the selection, filtering out input and output nodes.

        Args:
            value (Optional[List[Any]]): The items to be selected."""
        if not self._model:
            return

        # Remove InputNode and OutputNode from selection
        filtered = []
        for v in value:
            if not isinstance(v, IsolationGraphModel.EmptyPort):
                filtered.append(v)

        self._model.selection = filtered
