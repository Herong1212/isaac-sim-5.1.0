# noqa: PLC0302
"""
Commands that modify the topology of the OmniGraph
"""
import asyncio
from contextlib import suppress
from typing import Any, List, Optional, Tuple, Union

import carb
import omni.graph.core as og
import omni.kit
import omni.kit.commands
import omni.usd
from pxr import Usd

from ..object_lookup import ObjectLookup
from ..type_aliases import Attribute_t, AttributeType_t, ExtendedAttribute_t, Node_t
from .command_type_wrappers import CommandAttributeWrapper, CommandGraphWrapper, CommandVariableWrapper


# ==============================================================================================================
class ConnectPrimCommand(omni.kit.commands.Command):
    """
    Connect Prim **Command**.  Connects a bundle attribute to a prim.  This can be both for
    bundle purposes or for "pure relationship" type connections where we just want a relationship
    that points to a prim, without the connotations associated with bundles.

    Args:
        attr: The relationship attribute. This can be specified in the form
              of an attribute from a node, or a string that denotes the path to the attribute in USD.

        prim_path: The path to the prim that is to be the target of the relationship.
        is_bundle_connection: Whether this connection represents a bundle connection or just a
                              regular relationship

    Returns:
        bool: True if the connect succeded
    """

    def __init__(self, attr: Union[str, og.Attribute], prim_path: str, is_bundle_connection: bool):
        self._attr = CommandAttributeWrapper(attr)
        self._prim_path = prim_path
        self._is_bundle_connection = is_bundle_connection
        self._modify_usd = True
        self._did_doit = False

    def do(self):
        node = self._attr.object.get_node()
        if not node.is_backed_by_usd():
            self._modify_usd = False

        if self._attr.object.connectPrim(self._prim_path, self._modify_usd, self._is_bundle_connection):
            self._did_doit = True
        return self._did_doit

    def undo(self):
        if self._did_doit:
            self._attr.object.disconnectPrim(self._prim_path, self._modify_usd, self._is_bundle_connection)


# ==============================================================================================================
class DisconnectPrimCommand(omni.kit.commands.Command):
    """
    Disconnect Prim **Command**.  Disconnects a bundle attribute from a prim.  This can be both for
    bundle purposes or for "pure relationship" type connections where we just want a relationship
    that points to a prim, without the connotations associated with bundles.

    Args:
        attr: The relationship attribute.  This can be specified in the form
              of an attribute from a node, or a string that denotes the path to the attribute in USD.

        prim_path: The path to the prim that is to be the target of the relationship.
        is_bundle_connection: Whether this connection represents a bundle connection or just a
                              regular relationship

    Returns:
        bool: True if the disconnect succeded
    """

    def __init__(self, attr: Union[str, og.Attribute], prim_path: str, is_bundle_connection: bool):
        self._attr = CommandAttributeWrapper(attr)
        self._prim_path = prim_path
        self._is_bundle_connection = is_bundle_connection
        self._modify_usd = True
        self._did_doit = False

    def do(self):
        node = self._attr.object.get_node()
        if not node.is_backed_by_usd():
            self._modify_usd = False

        if self._attr.object.disconnectPrim(self._prim_path, self._modify_usd, self._is_bundle_connection):
            self._did_doit = True
        return self._did_doit

    def undo(self):
        if self._did_doit:
            self._attr.object.connectPrim(self._prim_path, self._modify_usd, self._is_bundle_connection)


# ==============================================================================================================
class ConnectAttrsCommand(omni.kit.commands.Command):
    """
    Connect Attrs **Command**.  Causes two attributes to be connected together in the omnigraph

    Args:
        src_attr: The source (upstream) attribute.  This can be specified in the form
                   of an attribute from a node, or a string that denotes the path to the attribute
                   in USD.  If specified as a string path, if the node happens to be a prim and
                   the prim doesn't yet have prim node created for it, this command will create
                   one automatically.
        dest_attr: The destination (downstream) attribute.  This can be specified in the form
                   of an attribute from a node, or a string that denotes the path to the attribute
                   in USD.  If specified as a string path, if the node happens to be a prim and
                   the prim doesn't yet have prim node created for it, this command will create
                   one automatically.
        modify_usd: Whether to modify the underlying usd stage with this connection
        connection_type: Whether this is regular connection or something more fancy, like data only
                         and execution only connections

    Returns:
        tuple[omni.graph.core.Attribute, omni.graph.core.Attribute, omni.graph.core.ConnectionType, any, bool]: A
            tuple of the source attribute, destination attribute, type of connection, old destination value, and
            True if the connection succeded in undo mode

    Raises:
        omni.graph.core.OmniGraphError: If the connection failed in immediate mode
    """

    def __init__(
        self,
        src_attr: Union[str, og.Attribute],
        dest_attr: Union[str, og.Attribute],
        modify_usd: bool,
        connection_type: og.ConnectionType = og.ConnectionType.CONNECTION_TYPE_REGULAR,
    ):
        self._src_attr = CommandAttributeWrapper(src_attr)
        self._dst_attr = CommandAttributeWrapper(dest_attr)
        self._modify_usd = modify_usd
        self._connection_type = connection_type
        self._did_doit = False
        self._value = None

    # ---------------------------------------------------------------------------------------------
    class DefaultObject:
        """Object representing a USD value that is not an authored value"""

        def __init__(self):
            pass

    # ---------------------------------------------------------------------------------------------
    @staticmethod
    def do_immediate(
        src_attr: Attribute_t,
        dest_attr: Attribute_t,
        modify_usd: bool,
        connection_type: og.ConnectionType = og.ConnectionType.CONNECTION_TYPE_REGULAR,
        return_old_value: bool = False,
    ):
        _src = src_attr
        _dst = dest_attr
        src_attr = og.Controller.attribute(_src)
        dest_attr = og.Controller.attribute(_dst)
        if not src_attr:
            raise og.OmniGraphError(f"Could not connect to unknown src attribute {_src}")
        if not dest_attr:
            raise og.OmniGraphError(f"Could not connect to unknown destination attribute {_dst}")

        src_node = src_attr.get_node()
        dest_node = dest_attr.get_node()
        nodes_in_usd = src_node.is_backed_by_usd() and dest_node.is_backed_by_usd()

        connected = src_attr.is_connected(dest_attr)
        value = None
        did_doit = False
        if not connected:
            # If there is USD backing for the destination attribute, we prefer to stash the value using the USD
            # mechanism because it is more robust currently.  og.Controller.get() can fail if we haven't loaded the
            # value into Fabric yet when this connection happens.
            if nodes_in_usd:
                with suppress(og.OmniGraphError):
                    usd_attr = og.ObjectLookup.usd_attribute(dest_attr)
                    if isinstance(usd_attr, Usd.Attribute) and usd_attr.HasAuthoredValue():
                        value = usd_attr.Get()
                    elif isinstance(usd_attr, Usd.Relationship):
                        value = None
                    else:
                        value = ConnectAttrsCommand.DefaultObject()
            else:
                value = og.Controller(attribute=dest_attr).get()
            connection_info = og.ConnectionInfo(dest_attr, connection_type)
            if src_attr.connectEx(connection_info, modify_usd):
                did_doit = True

        if return_old_value:
            return (src_attr, dest_attr, connection_type, value, did_doit)

        return True

    # ---------------------------------------------------------------------------------------------
    def do(self):
        try:
            (
                src_attr,
                dst_attr,
                self._connection_type,
                self._value,
                self._did_doit,
            ) = ConnectAttrsCommand.do_immediate(
                self._src_attr.object,
                self._dst_attr.object,
                self._modify_usd,
                self._connection_type,
                return_old_value=True,
            )
            self._src_attr = CommandAttributeWrapper(src_attr)
            self._dst_attr = CommandAttributeWrapper(dst_attr)
            return (self._src_attr.object, self._dst_attr.object, self._connection_type, self._value, self._did_doit)
        except og.OmniGraphError:
            return (self._src_attr.object, self._dst_attr.object, self._connection_type, None, False)

    # ---------------------------------------------------------------------------------------------
    def undo(self):
        if self._did_doit:
            src_attr = self._src_attr.object
            dst_attr = self._dst_attr.object
            if not src_attr or not dst_attr:
                return
            src_attr.disconnect(dst_attr, self._modify_usd)
            if self._value is not None:
                src_node = src_attr.get_node()
                dest_node = dst_attr.get_node()
                nodes_in_usd = src_node.is_backed_by_usd() and dest_node.is_backed_by_usd()
                if nodes_in_usd:
                    with suppress(og.OmniGraphError):
                        usd_attr = og.ObjectLookup.usd_attribute(dst_attr)
                        if not isinstance(self._value, ConnectAttrsCommand.DefaultObject):
                            usd_attr.Set(self._value)
                else:
                    og.Controller(self._dst_attr.object).set(self._value)
            elif dst_attr.get_type_name() != "bundle":
                carb.log_warn("No value to restore after undo of ConnectAttrsCommand")
            self._did_doit = False


# ==============================================================================================================
class DisconnectAllAttrsCommand(omni.kit.commands.Command):
    """
    Disconnect All Attrs **Command**.  Breaks every connection to and from an OmniGraph attribute

    Args:
        attr: The attribute to be disconnected
        modify_usd: Whether to modify the underlying usd stage with this connection

    Returns:
        bool: True if the disconnection succeeded

    Raises:
        omni.graph.core.OmniGraphError: If the disconnection failed in immediate mode
    """

    def __init__(self, attr: og.Attribute, modify_usd: bool):
        """Remember the command parameters"""
        self._attr = attr
        self._modify_usd = modify_usd
        self._disconnections = []
        self._graph = attr.get_node().get_graph()
        self._undo_cursor = 0  # Current location in the _disconnections of the undo/redo - usually 0 or len()-1

        while self._graph.get_parent_graph():
            self._graph = self._graph.get_parent_graph()

    def __remember_disconnection(self, upstream_attribute: og.Attribute, downstream_attribute: og.Attribute):
        """Add enough information to the disconnection to be able to recreate it in undo. There's no guarantee the
        same og.Attribute object will exist after a series of operations but the paths will be the same."""
        upstream_path = upstream_attribute.get_node().get_prim_path()
        upstream_name = upstream_attribute.get_name()
        downstream_path = downstream_attribute.get_node().get_prim_path()
        downstream_name = downstream_attribute.get_name()
        self._disconnections.append((upstream_path, upstream_name, downstream_path, downstream_name))

    def __get_attributes_from_connection_info(
        self, connection_info: Tuple[str, str, str, str]
    ) -> Tuple[og.Attribute, og.Attribute]:
        """Extract the upstream and downstream attribute from the stored connection information created by
        the __remember_disconnection function"""
        upstream_path, upstream_name, downstream_path, downstream_name = connection_info
        upstream_attribute = self._graph.get_node(upstream_path).get_attribute(upstream_name)
        downstream_attribute = self._graph.get_node(downstream_path).get_attribute(downstream_name)
        return (upstream_attribute, downstream_attribute)

    @staticmethod
    def do_immediate(attr: og.Attribute, modify_usd: bool) -> bool:
        """Do the disconnections without remembering the previous connections
        Args:
            attr: Attribute to be disconnected
            modify_usd: Is the USD to be immediately updated after the disconnections?
        Returns:
            True if all disconnections succeeded
        """
        status = True
        upstream_connections = attr.get_upstream_connections()
        for upstream_attribute in upstream_connections:
            status = upstream_attribute.disconnect(attr, modify_usd) and status
        downstream_connections = attr.get_downstream_connections()
        for downstream_attribute in downstream_connections:
            status = attr.disconnect(downstream_attribute, modify_usd) and status

        if not status:
            downstream = [downstream_connection.get_name() for downstream_connection in downstream_connections]
            raise og.OmniGraphError(
                f"Failed to disconnect {attr.get_name()} from downstream connections {','.join(downstream)}"
            )
        return status

    def do(self):
        """Perform the disconnections, remembering what was disconnected"""
        if self._attr is not None:
            upstream_connections = self._attr.get_upstream_connections()
            for upstream_attribute in upstream_connections:
                if upstream_attribute.disconnect(self._attr, self._modify_usd):
                    self.__remember_disconnection(upstream_attribute, self._attr)
            downstream_connections = self._attr.get_downstream_connections()
            for downstream_attribute in downstream_connections:
                if self._attr.disconnect(downstream_attribute, self._modify_usd):
                    self.__remember_disconnection(self._attr, downstream_attribute)
            self._undo_cursor = len(self._disconnections)
            # Mark the operation as being done once, to avoid accessing potentially stale data
            self._attr = None
            return True

        while self._undo_cursor < len(self._disconnections):
            upstream_attribute, downstream_attribute = self.__get_attributes_from_connection_info(
                self._disconnections[self._undo_cursor]
            )
            if upstream_attribute.disconnect(downstream_attribute, self._modify_usd):
                self._undo_cursor += 1
            else:
                return False
        return True

    def undo(self):
        """Use the remembered disconnections to reestablish the connections"""
        while self._undo_cursor > 0:
            self._undo_cursor -= 1
            upstream_attribute, downstream_attribute = self.__get_attributes_from_connection_info(
                self._disconnections[self._undo_cursor]
            )
            if not upstream_attribute.connect(downstream_attribute, self._modify_usd):
                self._undo_cursor += 1
                return True
        return False


# ==============================================================================================================
class DisconnectAttrsCommand(omni.kit.commands.Command):
    """
    Disconnect Attrs **Command**.  Causes two attrs to be disconnected in OmniGraph

    Args:
        src_attr: The source (upstream) attribute
        dest_attr: The destination (downstream) attribute
        modify_usd: Whether to modify the underlying usd stage with this connection

    Returns:
        bool: False if the disconnection failed in undoable mode

    Raises:
        omni.graph.core.OmniGraphError: If the disconnection failed in immediate mode
    """

    def __init__(self, src_attr: Attribute_t, dest_attr: Attribute_t, modify_usd: bool):
        self._src_attr = CommandAttributeWrapper(src_attr)
        self._dst_attr = CommandAttributeWrapper(dest_attr)
        self._modify_usd = modify_usd
        self._graph = self._src_attr.object.get_node().get_graph()
        self._did_doit = False

        while self._graph.get_parent_graph():
            self._graph = self._graph.get_parent_graph()

    @staticmethod
    def do_immediate(
        src_attr: Attribute_t,
        dest_attr: Attribute_t,
        modify_usd: bool,
    ):
        connected = src_attr.is_connected(dest_attr)
        if connected:
            # since the dest attr is being driven, there is no need to save the state
            # of the driven attribute.  When undo happens, it'll simply be driven again
            return src_attr.disconnect(dest_attr, modify_usd)

        carb.log_warn(f"Could not find connection between {src_attr} and {dest_attr} to remove")
        return False

    def do(self):
        if self._src_attr.object is None:
            carb.log_warn(f"Could not find source attribute {self._src_attr.path} to disconnect from")
            return
        if self._src_attr.object is None:
            carb.log_warn(f"Could not find destination attribute {self._dst_attr.path} to disconnect from")
            return
        self._did_doit = DisconnectAttrsCommand.do_immediate(
            self._src_attr.object, self._dst_attr.object, self._modify_usd
        )

    def undo(self):
        if self._did_doit:
            self._src_attr.object.connect(self._dst_attr.object, self._modify_usd)
            self._did_doit = False


# ==============================================================================================================
class _AttributeFactory:
    """Helper class shared by the CreateAttr and RemoveAttr commands since both require the ability to create
    and remove attributes, either in do() or in undo(). It is not assumed that it is safe to hang on to
    PyBind objects after the __init__ call so lookup strings are saved instead.
    """

    def __raise_error(self, msg: str):
        """Raise an OmniGraphError populated with common identifying information"""
        self._failure_pending = True
        raise og.OmniGraphError(f"Failed to {msg} using attribute {self._attr_name} on node {self._node_path}")

    def __init__(self, node: Node_t, *args):
        """Create attribute information either from an actual attribute or from individual create parameters"""
        # If one or the other operation failed then undo will attempt the opposite, which should just be skipped
        self._failure_pending = False
        if len(args) == 1:
            self._created = True
            attribute = ObjectLookup.attribute(args[0])
            self._node_path = attribute.get_node().get_prim_path()
            self._attr_name = attribute.get_name()
            attribute_data = attribute.get_attribute_data()
            self._attr_type = attribute_data.get_type() if attribute_data else og.Type(og.BaseDataType.UNKNOWN)
            self._attr_port = attribute.get_port_type()
            if attribute.get_extended_type() == og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION:
                self._attr_extended_type = (attribute.get_extended_type, ",".join(attribute.get_union_types()))
            else:
                self._attr_extended_type = attribute.get_extended_type()
            # TODO: Really we should be getting the default from og.Attribute.getDefault(), but it doesn't exist
            self._attr_default = None
        elif len(args) == 5:
            self._created = False
            self._node_path = ObjectLookup.node(node).get_prim_path()
            self._attr_name = args[0]
            self._attr_type = args[1]
            self._attr_port = args[2]
            self._attr_default = args[3]
            self._attr_extended_type = args[4]
        else:
            raise og.OmniGraphError(
                "Attribute factory requires either an og.Attribute or tuple of name, type, port, default, extended_type"
            )

    def create(self):
        """Create a new attribute with saved parameters, checking to make sure it hasn't already been created"""
        if self._failure_pending:
            self._failure_pending = False
            return
        if self._created:
            self.__raise_error("create dynamic attribute twice")
        omg_node = ObjectLookup.node(self._node_path)
        args = [self._attr_name, self._attr_type, self._attr_port, self._attr_default]
        if isinstance(self._attr_extended_type, Tuple):
            args.append(self._attr_extended_type[0])
            if isinstance(self._attr_extended_type[1], list):
                args.append(",".join(self._attr_extended_type[1]))

        else:
            args.append(self._attr_extended_type)
        try:
            self._created = omg_node.create_attribute(*args)
        except ValueError as error:
            self._failure_pending = True
            raise og.OmniGraphError() from error

    def remove(self) -> bool:
        """Remove an existing dynamic attribute, raising an exception if it was never created"""
        if self._failure_pending:
            self._failure_pending = False
            return
        omg_node = ObjectLookup.node(self._node_path)
        if not self._created or not omg_node.get_attribute_exists(self._attr_name):
            self.__raise_error("remove unknown dynamic attribute")
        try:
            self._created = not omg_node.remove_attribute(self._attr_name)
        except ValueError as error:
            raise og.OmniGraphError() from error


# ==============================================================================================================
class CreateAttrCommand(omni.kit.commands.Command):
    """
    Create Attribute **Command**.  Adds a new dynamic attribute to a node.

    Args:
        node: Node on which to create the attribute (path or og.Node)
        attr_name: Name of the new attribute, either with or without the port namespace
        attr_type: Type of the new attribute, as an OGN type string or og.Type
        attr_port: Port type of the new attribute, default is og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
        attr_default: The initial value to set on the attribute, default is None, meaning the type's default is used
        attr_extended_type: The extended type of the attribute, default is
                            og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR. If the extended type is
                            og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_UNION then this parameter will be a
                            2-tuple with the second element being a list or comma-separated string of union types

    Returns:
        bool: True if the create succeeded

    Raises:
        omni.graph.core.OmniGraphError: If the create failed in immediate mode
    """

    def __init__(
        self,
        node: Node_t,
        attr_name: str,
        attr_type: AttributeType_t,
        attr_port: Optional[og.AttributePortType] = og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
        attr_default: Optional[Any] = None,
        attr_extended_type: Optional[ExtendedAttribute_t] = og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR,
    ):
        """The information in here is only meant to survive until the do() function is called. After that, the
        do() function will store information necessary to undo and redo the operations."""
        super().__init__()
        self._factory = _AttributeFactory(
            node, attr_name, ObjectLookup.attribute_type(attr_type), attr_port, attr_default, attr_extended_type
        )

    @staticmethod
    def do_immediate(
        node: Node_t,
        attr_name: str,
        attr_type: AttributeType_t,
        attr_port: og.AttributePortType = og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
        attr_default: Any = None,
        attr_extended_type: ExtendedAttribute_t = og.ExtendedAttributeType.EXTENDED_ATTR_TYPE_REGULAR,
    ):
        """Removes the attribute, raising og.OmniGraphError if it fails"""
        attr_type = ObjectLookup.attribute_type(attr_type)
        _AttributeFactory(node, attr_name, attr_type, attr_port, attr_default, attr_extended_type).create()

    def do(self):
        """Create the dynamic attribute with the specified parameters, raising OmniGraphError if the create failed."""
        try:
            self._factory.create()
        except og.OmniGraphError as error:
            carb.log_warn(str(error))
            return False
        return True

    def undo(self):
        """Remove the created attribute, raising OmniGraphError if the removal failed"""
        try:
            self._factory.remove()
        except og.OmniGraphError as error:
            carb.log_warn(str(error))
            return False
        return True


# ==============================================================================================================
class RemoveAttrCommand(omni.kit.commands.Command):
    """
    Remove Attribute **Command**.  Removes an existing dynamic attribute from a node.

    Args:
        attribute: Name of the attribute to be removed

    Returns:
        bool: True if the removal succeeded

    Raises:
        omni.graph.core.OmniGraphError: If the removal failed in immediate mode
    """

    def __init__(
        self,
        attribute: og.Attribute,
    ):
        """The information in here is only meant to survive until the do() function is called. After that, the
        do() function will store information necessary to undo and redo the operations."""
        super().__init__()
        self._factory = _AttributeFactory(None, attribute)

    @staticmethod
    def do_immediate(attribute: og.Attribute):
        """Removes the dynamic attribute, raising og.OmniGraphError if the removal failed."""
        _AttributeFactory(None, attribute).remove()

    def do(self):
        """Remove the dynamic attribute, returning False if the removal failed."""
        try:
            self._factory.remove()
        except og.OmniGraphError as error:
            carb.log_warn(str(error))
            return False
        return True

    def undo(self):
        """Undo the removal of the dynamic attribute, returning False if the creation failed"""
        try:
            self._factory.create()
        except og.OmniGraphError as error:
            carb.log_warn(str(error))
            return False
        return True


# ==============================================================================================================
class CreateNodeCommand(omni.kit.commands.Command):
    """
    Create Node **Command**.  Creates a new compute node of a particular node type in OmniGraph

    Args:
        graph: The graph in which the new compute node should be created
        node_path: The location in the USD stage to add the new compute node
        node_type: The name of the type of compute node to create
        create_usd: Whether to also create an USD prim on the stage for this node

    Returns:
        omni.graph.core.Node: The created node, or the already existing node at the given path if there was one

    Raises:
        omni.graph.core.OmniGraphError: If the creation failed in immediate mode
    """

    def __init__(self, graph: og.Graph, node_path: str, node_type: str, create_usd: bool):
        self._graph = CommandGraphWrapper(graph)
        self._node_path = node_path
        self._node_type = node_type
        self._modify_usd = create_usd
        self._did_doit = False
        self._node = None

    # Do the operation do_immediately, bypassing the command's interaction with the undo queue
    @staticmethod
    def do_immediate(graph: og.Graph, node_path: str, node_type: str, modify_usd: bool):
        # Don't create a node if one already exists at the specified path.
        node = graph.get_node(node_path)
        if node is not None and node.is_valid():
            raise og.OmniGraphError(f"Node already exists at {node_path}. Cannot create another.")
        return graph.create_node(node_path, node_type, modify_usd)

    def do(self):
        try:
            self._node = CreateNodeCommand.do_immediate(
                self._graph.object, self._node_path, self._node_type, self._modify_usd
            )
        except og.OmniGraphError:
            # This should raise an exception, but for backward compatibility when executed here it will just log a
            # warning and then succeed
            carb.log_warn(f"Node already exists at {self._node_path}. Cannot create another.")
            node = self._node
            self._node = None
            return node

        self._did_doit = True
        return self._node

    def undo(self):
        if self._did_doit and (self._node is not None):
            self._graph.object.destroy_node(self._node_path, self._modify_usd)
            self._node = None
            self._did_doit = False


# ==============================================================================================================
class CreateGraphAsNodeCommand(omni.kit.commands.Command):
    """
    Create Graph As Node **Command**.  Creates a new graph wrapped by a node.

    Args:
        graph: The graph in which the new wrapper node should be created
        node_name: The name of the node
        graph_path: The path to the graph
        evaluator_name: The name of the evaluator to use for the graph
        is_global_graph: Whether this is a global graph (global level graphs have their own FC)
        backed_by_usd: Whether the constructs are to be backed by USD
        fc_backing_type: What kind of Fabric backs this graph
        pipeline_stage: What pipeline stage does this graph occupy: simulation, prerender, or postrender
        evaluation_mode: What evaluation mode to use with this graph: Automatic, Standalone or Instanced

    Returns:
        omni.graph.core.Node: The newly created node

    Raises:
        omni.graph.core.OmniGraphError: If the creation failed in immediate mode
    """

    def __init__(
        self,
        graph,
        node_name,
        graph_path,
        evaluator_name,
        is_global_graph,
        backed_by_usd,
        fc_backing_type,
        pipeline_stage,
        evaluation_mode=og.GraphEvaluationMode.GRAPH_EVALUATION_MODE_AUTOMATIC,
    ):
        self._graph = graph
        self._node_name = node_name
        self._graph_path = graph_path
        self._evaluator_name = evaluator_name
        self._is_global_graph = is_global_graph
        self._backed_by_usd = backed_by_usd
        self._fc_backing_type = fc_backing_type
        self._pipeline_stage = pipeline_stage
        self._evaluation_mode = evaluation_mode
        self._did_doit = False
        self._created_node = None

    # Do the operation do_immediately, bypassing the command's interaction with the undo queue
    @staticmethod
    def do_immediate(
        graph,
        node_name,
        graph_path,
        evaluator_name,
        is_global_graph,
        backed_by_usd,
        fc_backing_type,
        pipeline_stage,
        evaluation_mode,
    ) -> og.Node:
        return graph.create_graph_as_node(
            node_name,
            graph_path,
            evaluator_name,
            is_global_graph,
            backed_by_usd,
            fc_backing_type,
            pipeline_stage,
            evaluation_mode,
        )

    # Returns the created node wrapping the graph
    def do(self) -> og.Node:

        try:
            node = CreateGraphAsNodeCommand.do_immediate(
                self._graph,
                self._node_name,
                self._graph_path,
                self._evaluator_name,
                self._is_global_graph,
                self._backed_by_usd,
                self._fc_backing_type,
                self._pipeline_stage,
                self._evaluation_mode,
            )
            if node is not None and node.is_valid():
                self._did_doit = True
                self._created_node = node
        except og.OmniGraphError as error:
            carb.log_warning(f"Creating graph at {self._graph_path} as node {self._node_name} failed with '{error}'")
        return node

    def undo(self):
        if self._did_doit and (self._created_node is not None):
            self._graph.destroy_node(self._created_node.get_prim_path(), self._backed_by_usd)
            self._created_node = None
            self._did_doit = False


# ==============================================================================================================
class CreateSubgraphCommand(omni.kit.commands.Command):
    """
    Create Subgraph **Command**.  Creates a new subgraph node in OmniGraph

    Args:
        graph: The graph in which the new compute node should be created
        subgraph_path: The location in the USD stage to add the new compute node

    Returns:
        omni.graph.core.Graph: The newly created subgraph

    Raises:
        omni.graph.core.OmniGraphError: If the create failed
    """

    def __init__(self, graph, subgraph_path, evaluator=None, create_usd=True):
        self._graph = CommandGraphWrapper(graph)
        self._subgraph_path = subgraph_path
        self._evaluator = evaluator
        self._create_usd = create_usd
        self._did_doit = False
        self._subgraph = None

    def do(self):
        # Don't create a subgraph if one already exists at the specified path.
        subgraph = self._graph.object.get_node(self._subgraph_path)
        if subgraph is None or not subgraph.is_valid():
            self._subgraph = self._graph.object.create_subgraph(self._subgraph_path, self._evaluator, self._create_usd)
            self._did_doit = True
            return self._subgraph
        return subgraph

    def undo(self):
        if self._did_doit and (self._subgraph is not None):
            self._graph.object.destroy_node(self._subgraph_path, True)
            if self._create_usd:
                delete_cmd = omni.usd.commands.DeletePrimsCommand([self._subgraph_path])
                delete_cmd.do()
            self._subgraph = None
            self._did_doit = False


# ==============================================================================================================
class DeleteNodeCommand(omni.kit.commands.Command):
    """
    Delete Node **Command**.  Delete the specified node in the graph

    Args:
        graph: The graph from which the node should be removed
        node_path: The location in the USD stage to find the node
        modify_usd: Whether to also delete the USD prim on the stage for this node

    Returns:
        tuple[str, list[omni.graph.core.Attribute], list[omni.graph.core.Attribute], bool]: A tuple consisting of the
            node type name of the deleted node, a list of the upstream attributes that were disconnected as a result
            of the deletion, a list of the downstream attributes that were disconnected as a result of the deletion,
            and a boolean indicating if the deletion was successful

    Raises:
        omni.graph.core.OmniGraphError: If the deletion failed in immediate mode
    """

    def __init__(self, graph: og.Graph, node_path: str, modify_usd: bool):
        self._graph = CommandGraphWrapper(graph)
        self._node_path = node_path
        self._node_type = None
        self._modify_usd = modify_usd
        self._did_doit = False
        self._upstream_connections = {}
        self._downstream_connections = {}

    # Do the operation do_immediately, bypassing the command's interaction with the undo queue
    @staticmethod
    def do_immediate(graph: og.Graph, node_path: str, modify_usd: bool):
        upstream_connections = {}
        downstream_connections = {}
        did_doit = False
        node = graph.get_node(node_path)
        if node is not None and node.is_valid():
            attributes = node.get_attributes()
            for attribute in attributes:
                _upstream_connections = attribute.get_upstream_connections()
                upstream_connections[attribute.get_name()] = [
                    (src_attr.get_node().get_prim_path(), src_attr.get_name()) for src_attr in _upstream_connections
                ]
                for src_attr in _upstream_connections:
                    src_attr.disconnect(attribute, modify_usd)

                _downstream_connections = attribute.get_downstream_connections()
                downstream_connections[attribute.get_name()] = [
                    (dst_attr.get_node().get_prim_path(), dst_attr.get_name()) for dst_attr in _downstream_connections
                ]
                for dst_attr in _downstream_connections:
                    attribute.disconnect(dst_attr, modify_usd)

            node_type = node.get_type_name()
            if not node_type:
                node_type = node.get_type_name()
            graph.destroy_node(node_path, modify_usd)
            did_doit = True

            return (node_type, upstream_connections, downstream_connections, did_doit)
        raise og.OmniGraphError(f"Deleting node {node_path} from graph {graph} ")

    def do(self):
        try:
            (
                self._node_type,
                self._upstream_connections,
                self._downstream_connections,
                self._did_doit,
            ) = DeleteNodeCommand.do_immediate(self._graph.object, self._node_path, self._modify_usd)
            return (self._node_type, self._upstream_connections, self._downstream_connections, self._did_doit)
        except og.OmniGraphError as error:
            carb.log_warn(f"Delete of {self._node_path} failed with {error}")
            return (None, [], [], False)

    def undo(self):
        if self._did_doit and (self._node_type is not None):
            node = self._graph.object.create_node(self._node_path, self._node_type, self._modify_usd)
            for attribute_name, src_connections in self._upstream_connections.items():
                attribute = node.get_attribute(attribute_name)
                for src_node_path, src_attr_name in src_connections:
                    src_node = self._graph.object.get_node(src_node_path)
                    src_attr = src_node.get_attribute(src_attr_name)
                    src_attr.connect(attribute, self._modify_usd)

            for attribute_name, dest_connections in self._downstream_connections.items():
                attribute = node.get_attribute(attribute_name)
                for dest_node_path, dest_attr_name in dest_connections:
                    dest_node = self._graph.object.get_node(dest_node_path)
                    dest_attr = dest_node.get_attribute(dest_attr_name)
                    attribute.connect(dest_attr, self._modify_usd)

            self._node_type = None
            self._did_doit = False


# ==============================================================================================================
class CreateVariableCommand(omni.kit.commands.Command):
    """
    Create Variable **Command**.  Creates a new variable of a particular type in OmniGraph

    Args:
        graph: The graph in which the new variable should be created
        variable_name: The name of the new variable
        variable_type: The OmniGraph type of the new variable
        graph_context: The OmniGraph context to use when setting the initial variable value
        variable_value: The initial variable value
        is_backed_by_usd: Specifies if the variable will be backed by Usd.
                          If False, the variable will be a non-persistent, runtime variable.
                          Default value is True.

    Returns:
        omni.graph.core.Variable: The newly created variable, None if it could not be created

    Raises:
        omni.graph.core.OmniGraphError: If the variable could not be created, in immediate mode
    """

    def __init__(
        self,
        graph: og.Graph,
        variable_name: str,
        variable_type: og.Type,
        graph_context: og.GraphContext = None,
        variable_value=None,
        is_backed_by_usd: bool = True,
    ):
        self._graph = CommandGraphWrapper(graph)
        self._variable_name = variable_name
        self._variable_type = variable_type
        self._graph_context = graph_context
        self._variable_value = variable_value
        self._is_backed_by_usd = is_backed_by_usd
        self._created_variable = None

    @staticmethod
    def do_immediate(
        graph: og.Graph,
        variable_name: str,
        variable_type: og.Type,
        graph_context: og.GraphContext = None,
        variable_value=None,
        is_backed_by_usd=True,
    ):
        if not graph or not graph.is_valid() or not variable_name or not variable_type:
            raise og.OmniGraphError("Cannot create variable")

        if is_backed_by_usd:
            created_variable = graph.create_variable(variable_name, variable_type)
        else:
            created_variable = graph.create_runtime_variable(variable_name, variable_type)
        if created_variable and variable_value is not None:
            og.Controller.set_variable_default_value(created_variable, variable_value)
        return created_variable

    def do(self):
        try:
            self._created_variable = CommandVariableWrapper(
                CreateVariableCommand.do_immediate(
                    self._graph.object,
                    self._variable_name,
                    self._variable_type,
                    self._graph_context,
                    self._variable_value,
                    self._is_backed_by_usd,
                )
            )
            return self._created_variable.object
        except og.OmniGraphError as error:
            carb.log_warn(f"Failed to create variable {self._variable_name} - {error}")
            return None

    def undo(self):
        if self._created_variable is None:
            return

        self._graph.object.remove_variable(self._created_variable.object)
        self._created_variable = None


# ==============================================================================================================
class RemoveVariableCommand(omni.kit.commands.Command):
    """
    Remove Variable **Command**.  Remove the specified variable in the graph

    Args:
        graph: The graph to remove the variable from
        variable: The OmniGraph IVariable to be removed
        graph_context: The OmniGraph context to use when restoring the variable value on undo

    Returns:
        omni.graph.core.Variable: The newly removed variable, None if it could not be removed

    Raises:
        omni.graph.core.OmniGraphError: If the variable could not be removed, in immediate mode
    """

    def __init__(
        self,
        graph: og.Graph,
        variable: og.IVariable,
        graph_context: og.GraphContext = None,
    ):
        self._graph = CommandGraphWrapper(graph)
        self._variable = CommandVariableWrapper(variable)
        self._variable_name = None
        self._variable_type = None
        self._variable_backed_by_usd: bool = True
        self._graph_context = graph_context
        self._variable_value = None
        self._removed = False

    def do(self):
        self._variable_name = self._variable.object.name
        self._variable_type = self._variable.object.type
        self._variable_backed_by_usd = self._variable.object.is_backed_by_usd
        try:
            self._variable_value = og.Controller.get_variable_default_value(self._variable.object)
            self._removed = self._graph.object.remove_variable(self._variable.object)
            return True
        except og.OmniGraphError as error:
            carb.log_warn(f"Variable {self._variable_name} could not be removed - {error}")
            return False

    def undo(self):
        if not self._removed:
            return True

        try:
            var = None
            if self._variable_backed_by_usd:
                var = self._graph.object.create_variable(self._variable_name, self._variable_type)
            else:
                var = self._graph.object.create_runtime_variable(self._variable_name, self._variable_type)
            self._variable = CommandVariableWrapper(var)
            if self._variable_value is not None:
                og.Controller.set_variable_default_value(self._variable.object, self._variable_value)
            return True
        except og.OmniGraphError as error:
            carb.log_warn(f"Variable {self._variable_name} removal could not be undone - {error}")
            return False


# ==============================================================================================================
class ChangeVariableTypeCommand(omni.kit.commands.Command):
    """
    Change Variable Type **Command** that changes the type of a variable.

    Use this instead of removing and recreating a variable, as removing the underlying attribute in USD requires
    the attribute to be defined on the authoring layer. Where as changing the type can add an opinion about the
    type.

    Args:
        variable: The variable to change the type of
        variable_type: The new type for the variable

    Returns:
        bool: True if the variable was successfully changed
    """

    def __init__(self, variable: og.IVariable, variable_type: og.Type):
        super().__init__()
        self._variable = CommandVariableWrapper(variable)
        self._type = variable_type
        self._prev_type = None
        self._prev_default = None

    def do(self):
        prev_type = self._variable.object.type
        prev_default = og.Controller.get_variable_default_value(self._variable.object)
        if self._variable.object.set_type(self._type):
            self._prev_type = prev_type
            self._prev_default = prev_default
            return True

        carb.log_warn(
            f"Could not change variable {self._variable.object.name} to type {self._type}. "
            "This may be due to the current authoring layer having a weaker opinion."
        )
        return False

    def undo(self):
        if self._prev_type is not None:
            if self._variable.object.set_type(self._prev_type) and self._prev_default is not None:
                og.Controller.set_variable_default_value(self._variable.object, self._prev_default)
            self._prev_type = None
        return True


class _OGRestoreConnectionsOnUndo(omni.kit.commands.Command):  # pragma: no cover
    """
    Restore connections between OG nodes on undo. (Does nothing on do or redo.)

    This command is for internal use only. It may be changed or removed
    without notice.

    Args:
        connections (List[(str, str)])
            The connections to be restored. Each element of the list is a tuple
            containing the path strings for the source and destination attributes.
    """

    # When the source prim for a connection is deleted OG removes all traces of the
    # connection. If the deletion is undone OG has no way of knowing that the restored
    # prim had a connection which should also be restored. This command is used to
    # restore those connections on undo.
    def __init__(self, connections: List[Tuple[str, str]]):
        self._path_strings: List[Tuple[str, str]] = connections.copy()
        self.__reconnect_task = None

    def destroy(self):
        if self.__reconnect_task:
            if not self.__reconnect_task.done():
                self.__reconnect_task.cancel()
            self.__reconnect_task = None

    def do(self):
        pass

    def undo(self):
        # We cannot do the reconnection yet because OG won't have created the prim's
        # Node yet.
        if self.__reconnect_task is None or self.__reconnect_task.done():
            self.__reconnect_task = asyncio.ensure_future(self.__do_reconnections())

    async def __do_reconnections(self):
        # Give OG a chance to create the prim's Node.
        await omni.kit.app.get_app().next_update_async()

        for src_attr_str, dest_attr_str in self._path_strings:
            src_attr: og.Attribute = og.Controller.attribute(src_attr_str)
            dest_attr: og.Attribute = og.Controller.attribute(dest_attr_str)
            if src_attr and dest_attr and src_attr not in dest_attr.get_upstream_connections():
                src_attr.connect(dest_attr, modify_usd=True)
        self.__reconnect_task = None


# ==============================================================================================================
class ResolveAttrTypeCommand(omni.kit.commands.Command):
    """
    Resolve Attribute Type **Command**. (Re)resolves an extended attribute to a particular type

    Args:
        attr: The attribute to be (re)resolved
        type_id: The data type to resolve the attribute to

    Returns:
        bool: True if the attribute was resolved
    """

    def __init__(
        self,
        attr: og.Attribute,
        type_id: AttributeType_t,
    ):
        self._attr = CommandAttributeWrapper(attr)
        self._type_id = type_id
        self._previous_type_id: AttributeType_t = "unknown"

    def do(self):
        try:
            self._previous_type_id = self._attr.helper.type
            self._attr.helper.resolve_type(self._type_id)
            return True
        except og.OmniGraphError as error:
            carb.log_warn(f"Attribute {self._attr.path} could not be resolved - {error}")
            return False

    def undo(self):
        try:
            self._attr.helper.resolve_type(self._previous_type_id)
            return True
        except og.OmniGraphError as error:
            carb.log_warn(f"Attribute {self._attr.path} resolution could not be undone - {error}")
            return False
