# noqa: PLC0302
"""Utilities that handles interactions with the set of OmniGraph graphs and their contents.

The main class is og.Controller, which is an aggregate that implements each of the smaller interfaces that handle
various pieces of the graph manipulation. They are mainly kept separate to avoid a big monolithic implementation
class, while providing a single point of contact for graph manipulation due to the multiple interfaces it inherits.

All of the classes used here follow a pattern that allows the main functions to be called using either an object or a
class, accessing the same underlying functionality but with potentially different arguments.

.. code-block:: python

    class SharedMethodNames:
        def __init__(self, *args, **kwargs):
            # Replace the classmethod in instantiated objects with the internal object-based implementation
            self.dual_method = self.__dual_method_obj

        @staticmethod
        def __dual_method(obj, *args, **kwargs):
            # Implementation of the actual method

        @classmethod
        def dual_method(cls, *args, **kwargs):
            # Any manipulation of the arguments for class-based use is done first, then the implementation is called
            cls.__dual_method(cls, *args, **kwargs)

        def __dual_method_obj(self, *args, **kwargs):
            # Any manipulation of the arguments for object-based use is done first, then the implementation is called
            self.__dual_method(self, *args, **kwargs)

For example, here is an implementation of a class containing a "square()" function that will square the value it owns.
The object will initialized the value as part of its __init__() function, whereas the class method will take the value
as one of its arguments.

.. code-block:: python

    class FlexibleSquare:
        def __init__(self, value: float):
            self.square = self.__square_obj
            self.__value = value

        @staticmethod
        def __square(obj, value: float) -> float:
            return value * value

        @classmethod
        def square(cls, value: float) -> float:
            return cls.__square(cls, value)

        def __square_obj(self) -> float:
            return self.__square(self, self.__value)

    print(f"Square of 3 is {FlexibleSquare.square(3)}")
    five = FlexibleSquare(5)
    print(f"Square of 5 is {five.square()}")

It might also make sense to allow override in the method for the object's method:

    def __square_obj(self, value: float = None) -> float:
        return self.__square(self, self.__value if value is None else value)

    print(f"Square of 3 is {FlexibleSquare.square(3)}")
    five = FlexibleSquare(5)
    print(f"Square of 5 is {five.square()}")
    print(f"Square of 4 is {five.square(4)}")
"""
from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import omni.graph.core as og
import omni.graph.tools.ogn as ogn
from omni.kit import undo
from pxr import Sdf, Usd

from .data_view import DataView
from .errors import OmniGraphError
from .graph_controller import GraphController
from .node_controller import NodeController
from .object_lookup import ObjectLookup
from .type_aliases import (
    AttributeSpec_t,
    AttributeSpecs_t,
    AttributeType_t,
    AttributeTypeSpec_t,
    CompoundSubgraphCmd_t,
    GraphSpec_t,
    GraphSpecs_t,
    NewAttribute_t,
    NewNode_t,
    NodeSpec_t,
    NodeType_t,
    Path_t,
    PrimAttrs_t,
    VariableName_t,
    VariableType_t,
)
from .utils import AttributeValues_t, ValueToSet_t, _flatten_arguments, _Unspecified

# Dictionary type mapping the relative path of a node that was created by the edit() method to the node/prim it created
# TODO: path_to_object_map + graph_path could be broken into a separate class for easier handling
PathToObjectMap_t = Dict[str, Union[og.Node, Usd.Prim]]


# ==============================================================================================================
def _get_as_list(value: Union[Any, List[Any]]) -> List[Any]:
    """Utility to ensure that a passed-in item is returned as a list.
    Args:
        value: Value or list of values to convert
    Returns:
        The value itself if it was already a list, otherwise a single element list containing the value
    """
    return value if isinstance(value, list) else [value]


# ==============================================================================================================
def _find_actual_path(path_id: Path_t, root_path: str, path_to_object_map: Dict[str, Any]) -> str:
    """Finds the actual creation path, applying node mapping and graph path prepending when needed"""
    node_path = str(path_id)
    if node_path.startswith("/"):
        return node_path
    try:
        node_object = path_to_object_map[node_path]
        return node_object.get_prim_path() if isinstance(node_object, og.Node) else node_object
    except KeyError:
        return f"{root_path}/{node_path}"


# ==============================================================================================================
class Controller(GraphController, NodeController, DataView, ObjectLookup):
    r"""Class to provide a simple interface to a variety OmniGraph manipulation functions.

    Provides functions for creating nodes, making and breaking connections, and setting values.
    Graph manipulation functions are undoable, value changes are not.

    Functions are set up to be as flexible as possible, accepting a wide variety of argument variations.

    Here is a summary of the interface methods you can access through this class, grouped by interface class. The ones
    marked with an "!" indicate that they have both a classmethod version and an object method version. In those cases
    the methods use object member values which have corresponding arguments in the classmethod version. (e.g. if the
    method uses the "update_usd" member value then the method will also have a "update_usd:bool" argument)

    Controller
        - ! **edit**           Perform a collection of edits on a graph (the union of all interfaces)
        - **evaluate**         Runs async evaluation on one or more graphs as a waitable (typically called from async tests)
        - **evaluate_sync**    Runs evaluation on one or more graphs immediately

    ObjectLookup
        - **attribute**         Looks up an og.Attribute from a description
        - **attribute_path**    Looks up an attribute string path from a description
        - **attribute_type**    Looks up an og.Type from a description
        - **graph**             Looks up an og.Graph from a description
        - **node**              Looks up an og.Node from a description
        - **node_path**         Looks up a node string path from a description
        - **prim**              Looks up an Usd.Prim from a description
        - **prim_path**         Looks up a Usd.Prim string path from a description
        - **split_graph_from_node_path**  Separate a graph and a relative node path from a full node path

    GraphController
        - ! **connect**          Makes connections between attribute pairs
        - ! **create_graph**     Creates a new og.Graph
        - ! **create_node**      Creates a new og.Node
        - ! **create_prim**      Creates a new Usd.Prim
        - ! **create_variable**  Creates a new og.IVariable
        - ! **delete_node**      Deletes a list of og.Nodes
        - ! **disconnect**       Breaks connections between attribute pairs
        - ! **disconnect_all**   Breaks all connections to and from specific attributes
        - ! **expose_prim**      Expose a USD prim to OmniGraph through an importing node

    NodeController
        - ! **create_attribute**  Create a new dynamic attribute on a node
        - ! **promote_attribute** Promote a node attribute in a compound graph on the parenting compound node
        - ! **remove_attribute**  Remove an existing dynamic attribute from a node
        - **safe_node_name**      Get a node name in a way that's safe for USD

    DataView
        - ! **get**              Get the value of an attribute's data
        - ! **get_array_size**   Get the number of elements in an array attribute's data
        - ! **set**              Set the value of an attribute's data

    Attributes:
        __graph_id: Graph on which the operations are to be performed.
        __path_to_object_map: Dictionary of relative paths mapped on to their full path after creation so that
                              future function calls can use either full paths or short-forms to specify the nodes.
        __update_usd: If True then update the USD after the operations that affect it
        __undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
        __allow_exists_attr: If True then attribute creation operation won't fail when the attribute already exists
                             on the node it was being added to (default False)
        __allow_exists_node: If True then node creation operation won't fail when the node already exists in the
                             scene graph (default False)
        __allow_exists_prim: If True then prim creation operation won't fail when the prim already exists in the
                             scene graph (default False)

    Raises:
        OmniGraphError: If the requested operation could not be performed
    """

    Keys = ogn.GraphSetupKeys

    TYPE_CHECKING = True
    """If True then verbose type checking will happen in various locations so that more legible error messages can
    be emitted. Set it to False to run a little bit faster, with errors just reporting raw Python error messages.
    """

    # --------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        # begin-controller-init
        """Set up state information. You only need to create an instance of the Controller if you are going to
        use the edit() function more than once, when it needs to remember the node mapping used for creation.
        Args are passed on to the parent classes who have inits and interpreted by them as they see fit.

        Args:
            graph_id: If specified then operations are performed on this graph_id unless it is overridden in a
                      particular function call. See GraphController.create_graph() for the data types
                      accepted for the graph description.
            path_to_object_map: Dictionary of relative paths mapped on to their full path after creation so that the
                                edit_commands can use either full paths or short-forms to specify the nodes.
            update_usd: If specified then override whether to update the USD after the operations (default False)
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
                      (default True)
            allow_exists_attr: If True then attribute creation operation won't fail when the attribute already exists
                               on the node it was being added to (default False)
            allow_exists_node: If True then node creation operation won't fail when the node already exists in the
                               scene graph (default False)
            allow_exists_prim: If True then prim creation operation won't fail when the prim already exists in the
                               scene graph (default False)

        Check the help information for GraphController.__init__(), NodeController.__init__(), DataView.__init__(), and
        ObjectLookup.__init__() for details on what other constructor arguments are accepted.
        """
        # end-controller-init
        (
            self.__graph_id,
            self.__path_to_object_map,
            self.__update_usd,
            self.__undoable,
            self.__allow_exists_attr,
            self.__allow_exists_node,
            self.__allow_exists_prim,
        ) = _flatten_arguments(
            optional=[
                ("graph_id", None),
                ("path_to_object_map", None),
                ("update_usd", True),
                ("undoable", True),
                ("allow_exists_attr", False),
                ("allow_exists_node", False),
                ("allow_exists_prim", False),
            ],
            args=args,
            kwargs=kwargs,
        )
        GraphController.__init__(self, *args, **kwargs)
        NodeController.__init__(self, *args, **kwargs)
        DataView.__init__(self, *args, **kwargs)
        ObjectLookup.__init__(self)

        # Dual function methods that can be called either from an object or directly from the class
        self.edit = self.__edit_obj
        self.evaluate = self.__evaluate_obj
        self.evaluate_sync = self.__evaluate_sync_obj

    # --------------------------------------------------------------------------------------------------------------
    @dataclass
    class _EditArgs:
        """Collection of shared arguments that are passed to a bunch of the edit implementation methods

        Attributes:
            path_to_object_map: Dictionary of the mappings of the node names to instantiated node paths
            graph_path: Path location of the graph on which the edits take place
            update_usd: Should editing operations immediately update the USD backing?
            undoable: Should editing operations be undoable?
            allow_exists_attr: Should editing operations fail creation if requested attribute already exists?
            allow_exists_node: Should editing operations fail creation if requested node already exists?
            allow_exists_prim: Should editing operations fail creation if requested prim already exists?
        """

        path_to_object_map: PathToObjectMap_t = None
        graph_path: str = None
        update_usd: bool = None
        undoable: bool = None
        allow_exists_attr: bool = None
        allow_exists_node: bool = None
        allow_exists_prim: bool = None

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    async def evaluate(obj, *args, **kwargs):  # noqa: N804,PLC0202,PLE0202
        """Wait for the next Graph evaluation cycle - await this function to ensure it is finished before returning.

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object.

        .. code-block:: python

            await og.Controller.evaluate()  # Evaluates all graphs
            controller = og.Controller.edit("/TestGraph", {})
            await controller.evaluate()  # Evaluates only "/TestGraph"
            await og.Controller.evaluate("/TestGraph")  # Evaluates only "/TestGraph"
            controller.evaluate(graph_id="/OtherGraph")  # Evaluates only "/OtherGraph" (not its own "/TestGraph")

        Args:
            obj: Either cls or self depending on how the function was called
            graph_id (GraphSpecs_t): Graph or list of graphs to evaluate - None means all existing graphs

        Raises:
            OmniGraphError: If the graph evaluated explicitly does not exist or if it is a pre-render or post-render graph.
        """
        await obj.__evaluate(obj, args=args, kwargs=kwargs)

    async def __evaluate_obj(self, *args, **kwargs) -> Any:
        """Implements Controller.evaluate() when called as an object method"""
        await self.__evaluate(self, graph_id=self.__graph_id, args=args, kwargs=kwargs)

    @staticmethod
    async def __evaluate(
        obj,
        graph_id: Optional[GraphSpecs_t] = None,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ):
        """Implements Controller.evaluate()"""
        (graph_id,) = _flatten_arguments(
            optional=[("graph_id", graph_id)],
            args=args,
            kwargs=kwargs,
        )
        graphs = None
        if graph_id is None:
            graphs = og.get_all_graphs()
        else:
            graphs = obj.graph(graph_id)
            if graphs is None:
                raise OmniGraphError(f"The graph {graph_id} does not exist.")

        if not isinstance(graphs, list):
            graphs = [graphs]

        for graph in graphs:
            match graph.get_pipeline_stage():
                case og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_PRERENDER:
                    if graph_id:
                        raise OmniGraphError(
                            f"The graph {graph_id} is a pre-render graph and cannot be evaluated explicitly."
                        )
                    continue
                case og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_POSTRENDER:
                    if graph_id:
                        raise OmniGraphError(
                            f"The graph {graph_id} is a post-render graph and cannot be evaluated explicitly."
                        )
                    continue
                case _:
                    graph.evaluate()

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def evaluate_sync(obj, *args, **kwargs):  # noqa: N804,PLC0202,PLE0202
        """Run the next Graph evaluation cycle immediately.

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object.

        .. code-block:: python

            og.Controller.evaluate_sync()  # Evaluates all graphs
            controller = og.Controller.edit("/TestGraph", {})
            controller.evaluate_sync()  # Evaluates only "/TestGraph"
            og.Controller.evaluate_sync("/TestGraph")  # Evaluates only "/TestGraph"
            controller.evaluate_sync(graph_id="/OtherGraph")  # Evaluates only "/OtherGraph" (not its own "/TestGraph")

        Args:
            obj: Either cls or self depending on how evaluate_sync() was called
            graph_id (GraphSpecs_t): Graph or list of graphs to evaluate - None means all existing graphs

        Raises:
            OmniGraphError: If the graph evaluated explicitly does not exist or if it is a pre-render or post-render graph.
        """
        return obj.__evaluate_sync(obj, *args, **kwargs)

    def __evaluate_sync_obj(self, *args, **kwargs) -> Any:
        """Implements Controller.evaluate_sync() when called as an object method"""
        return self.__evaluate_sync(self, *args, **kwargs)

    @staticmethod
    def __evaluate_sync(
        obj,
        graph_id: Optional[GraphSpecs_t] = None,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ):
        """Implements Controller.evaluate_sync()"""
        (graph_id,) = _flatten_arguments(
            optional=[("graph_id", graph_id)],
            args=args,
            kwargs=kwargs,
        )
        graphs = None
        if graph_id is None:
            graphs = og.get_all_graphs()
        else:
            graphs = obj.graph(graph_id)
            if graphs is None:
                raise OmniGraphError(f"The graph {graph_id} does not exist.")

        if not isinstance(graphs, list):
            graphs = [graphs]

        for graph in graphs:
            match graph.get_pipeline_stage():
                case og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_PRERENDER:
                    if graph_id:
                        raise OmniGraphError(
                            f"The graph {graph_id} is a pre-render graph and cannot be evaluated explicitly."
                        )
                    continue
                case og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_POSTRENDER:
                    if graph_id:
                        raise OmniGraphError(
                            f"The graph {graph_id} is a post-render graph and cannot be evaluated explicitly."
                        )
                    continue
                case _:
                    graph.evaluate()

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __mapped_node_path(node_path: str, path_to_object_map: PathToObjectMap_t) -> str:
        """Returns the node path after subjecting it to the object path mapping"""
        try:
            node = path_to_object_map[node_path]
            return node.get_prim_path() if isinstance(node, og.Node) else str(node.GetPrimPath())
        except KeyError:
            return node_path

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __mapped_attribute_spec(  # noqa: PLW0238
        attr_spec: AttributeSpec_t, path_to_object_map: PathToObjectMap_t
    ) -> AttributeSpec_t:
        """Returns the attribute spec with any necessary mapping of local path to fully created path made

        Returns:
            og.Attribute: If the attribute spec pointed to an existing attribute
            tuple[str, og.Node]: If the node exists but the attribute does not, so just return the name

        Raises:
            OmniGraphError: If the attribute does not exist and the node could not be found
        """
        # Check for Node.Attr format
        if isinstance(attr_spec, og.Attribute):
            return attr_spec
        if isinstance(attr_spec, str):
            paths = attr_spec.split(".")
            # Attribute without node has no mapping
            if len(paths) == 1:
                return attr_spec
            # Remap node path and rejoin with attribute
            if len(paths) == 2:
                return ".".join([Controller.__mapped_node_path(paths[0], path_to_object_map), paths[1]])
            raise OmniGraphError(f"Attribute spec can only have one '.' separator - saw '{attr_spec}'")
        if isinstance(attr_spec, (tuple, list)):
            if len(attr_spec) not in [2, 3]:
                raise OmniGraphError(
                    f"Attribute spec should be either (name, node) or (name, node, graph) - saw '{attr_spec}'"
                )
            # Make it reversible when it can be inferred
            if isinstance(attr_spec[0], og.Node):
                return (attr_spec[1], attr_spec[0])
            if isinstance(attr_spec[1], og.Node):
                return attr_spec
            node_path = Controller.__mapped_node_path(attr_spec[1], path_to_object_map)
            node = Controller.node(node_path, None if len(attr_spec) == 2 else attr_spec[2])
            return (attr_spec[0], node)

        # Nothing else has a mapping
        return attr_spec

    # --------------------------------------------------------------------------------------------------------------

    @staticmethod
    def _process_create_nodes(
        obj,
        nodes_to_create: List[Tuple[NewNode_t, Union[NodeType_t, CompoundSubgraphCmd_t]]],
        edit_args: Controller._EditArgs,
    ):
        """Creates a list of nodes, updating the path_to_object_map to include the new mappings

        Args:
            nodes_to_create: List of nodes that are to be created
            edit_args: The common arguments used to configure editing operations Controller._EditArgs

        Raises:
            OmniGraphError: If any of the nodes could not be created
        """
        if obj.TYPE_CHECKING:
            for element in nodes_to_create:
                type_wrong = (not isinstance(element, (tuple, list))) or len(element) != 2
                type_wrong |= type(element[0]) not in [str, og.Node, Sdf.Path, Usd.Prim]
                type_wrong |= type(element[1]) not in [str, og.NodeType, og.Node, Usd.Prim, dict]
                if type_wrong:
                    raise OmniGraphError(f"Node creation spec must be (node_path, node_type) pairs - got '{element}'")

        def _actual_node_type(node_type: Union[NodeType_t, CompoundSubgraphCmd_t]):
            if isinstance(node_type, dict):
                return "omni.graph.nodes.CompoundSubgraph"
            return node_type

        # Before creation make sure the graph path is prepended or the mapped location is found to the node
        # path if the path is not absolute
        nodes_constructed = [
            obj.create_node(
                _find_actual_path(node_path, edit_args.graph_path, edit_args.path_to_object_map),
                _actual_node_type(node_type),
                update_usd=edit_args.update_usd,
                undoable=edit_args.undoable,
                allow_exists=edit_args.allow_exists_node,
            )
            for node_path, node_type in nodes_to_create
        ]
        just_names = [name for (name, _node_type) in nodes_to_create]
        edit_args.path_to_object_map.update(dict(zip(just_names, nodes_constructed)))

        def _create_subgraphs(node, cmds):
            # don't reuse the instance to do the recursive call
            caller = obj if isinstance(obj, type) else type(obj)

            # recursively call the edit on the subgraph of the node
            caller.__edit(  # noqa: PLW0212
                caller,
                graph_id=node.get_compound_graph_instance(),
                edit_commands=cmds,
                path_to_object_map=edit_args.path_to_object_map,
                update_usd=edit_args.update_usd,
                undoable=edit_args.undoable,
                allow_exists_node=edit_args.allow_exists_node,
                allow_exists_prim=edit_args.allow_exists_prim,
            )

        # second pass to create the subgraphs
        for node, (_node_path, cmds) in zip(nodes_constructed, nodes_to_create):
            if isinstance(cmds, dict) and node:
                _create_subgraphs(node, cmds)

        return nodes_constructed

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _process_delete_nodes(
        obj,
        nodes_to_delete: List[NodeSpec_t],
        edit_args: Controller._EditArgs,
    ):
        """Deletes a list of nodes, updating the path_to_object_map to remove any that are no longer in it

        Args:
            nodes_to_delete: List of nodes that are to be deleted
            edit_args: The common arguments used to configure editing operations Controller._EditArgs

        Raises:
            OmniGraphError: If the nodes could not be found or could not be deleted
        """
        if obj.TYPE_CHECKING:
            for element in nodes_to_delete:
                if isinstance(element, og.Node) and not element.is_valid():
                    raise OmniGraphError(f"Node deletion spec points to an invalid node - '{element}'")
                if (
                    not isinstance(element, str)
                    and not isinstance(element, Usd.Prim)
                    and not isinstance(element, og.Node)
                ):
                    raise OmniGraphError(f"Node deletion spec must be a string, node, or prim - got '{element}'")

        for element in set(nodes_to_delete):
            # Make sure the path to object map no longer has the reference to the deleted node
            if isinstance(element, og.Node):
                for node_path, node in edit_args.path_to_object_map.items():
                    if node == element:
                        del edit_args.path_to_object_map[node_path]
                        break
                obj.delete_node(element, update_usd=edit_args.update_usd, undoable=edit_args.undoable)
            elif isinstance(element, Usd.Prim):
                omnigraph_node = og.get_node_by_path(element.GetPrimPath())
                if omnigraph_node is not None and omnigraph_node.is_valid():
                    for node_path, node in edit_args.path_to_object_map.items():
                        if node == omnigraph_node:
                            del edit_args.path_to_object_map[node_path]
                            break
                obj.delete_node(element, update_usd=edit_args.update_usd, undoable=edit_args.undoable)
            else:
                if element in edit_args.path_to_object_map:
                    node_path = og.ObjectLookup.node_path(edit_args.path_to_object_map[element])
                    del edit_args.path_to_object_map[element]
                    obj.delete_node(node_path, update_usd=edit_args.update_usd, undoable=edit_args.undoable)
                else:
                    obj.delete_node(
                        f"{edit_args.graph_path}/{element}",
                        update_usd=edit_args.update_usd,
                        undoable=edit_args.undoable,
                    )

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _process_create_attributes(
        obj,
        attributes_to_create: List[Tuple[NewAttribute_t, AttributeTypeSpec_t]],
        edit_args: Controller._EditArgs,
    ):
        """Creates a list of nodes, updating the path_to_object_map to include the new mappings

        Args:
            attributes_to_create: List of specs for attributes to be created
            edit_args: The common arguments used to configure editing operations Controller._EditArgs

        Raises:
            OmniGraphError: If any of the nodes could not be created
        """
        if obj.TYPE_CHECKING:
            for element in attributes_to_create:
                type_wrong = (not isinstance(element, (tuple, list))) or len(element) != 2
                if isinstance(element[0], (tuple, list)):
                    if len(element[0]) == 2:
                        type_wrong |= not isinstance(element[0][0], (str, tuple))
                        type_wrong |= not isinstance(element[0][1], (str, og.Node, Sdf.Path, Usd.Prim, Usd.Typed))
                    elif len(element[0]) == 3:
                        type_wrong |= not isinstance(element[0][0], (str, tuple))
                        type_wrong |= not isinstance(element[0][1], (str, og.Node, Sdf.Path, Usd.Prim, Usd.Typed))
                        type_wrong |= not isinstance(element[0][2], (str, og.Graph, Sdf.Path, Usd.Prim, Usd.Typed))
                    else:
                        type_wrong |= not isinstance(element[0], (str, Sdf.Path))
                if type_wrong:
                    raise OmniGraphError(
                        f"Attribute creation spec must be (attribute_path, attribute_type) pairs - got '{attributes_to_create}'"
                    )

        # Before creation make sure the graph path is prepended or the mapped location is found to the node
        # path if the path is not absolute
        attributes_constructed = []
        for attribute_spec, attribute_type_spec in attributes_to_create:
            full_path = obj.__mapped_attribute_spec(attribute_spec, edit_args.path_to_object_map)  # noqa: PLW0212
            if isinstance(full_path, tuple):
                (decoded_name, node) = full_path
            else:
                (node, decoded_name) = str(full_path).split(".")
            extended_type = og.ExtendedAttributeType.REGULAR
            if isinstance(attribute_type_spec, list):
                extended_type = (og.ExtendedAttributeType.UNION, attribute_type_spec)
                attribute_type = og.Type(og.BaseDataType.TOKEN)
            elif attribute_type_spec == "any":
                extended_type = og.ExtendedAttributeType.ANY
                attribute_type = og.Type(og.BaseDataType.TOKEN)
            else:
                attribute_type = obj.attribute_type(attribute_type_spec)
            if isinstance(decoded_name, tuple):
                name = og.Attribute.ensure_port_type_in_name(
                    decoded_name[0], decoded_name[1], attribute_type.role == og.AttributeRole.BUNDLE
                )
                port = decoded_name[1]
            else:
                name = decoded_name
                port = og.Attribute.get_port_type_from_name(name)
            if port == og.AttributePortType.UNKNOWN:
                port = og.AttributePortType.INPUT
            attributes_constructed.append(obj.create_attribute(node, name, attribute_type, port, None, extended_type))

        return attributes_constructed

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _process_connections(
        obj,
        connection_definitions: List[Tuple[AttributeSpec_t, AttributeSpec_t]],
        breaking_connections: bool,
        edit_args: Controller._EditArgs,
    ):
        """Process the edit section connections to be made or broken

        Args:
            connection_definitions: List of (src, dst) attribute pairs of the connections to be processed
            breaking_connections: If True then disconnect the pairs, otherwise connect the pairs
            edit_args: The common arguments used to configure editing operations Controller._EditArgs

        Raises:
            OmniGraphError: If any of the attributes could not be found or the connections failed
        """
        for src_spec, dst_spec in connection_definitions:
            src_attr = obj.__mapped_attribute_spec(src_spec, edit_args.path_to_object_map)  # noqa: PLW0212
            dst_attr = obj.__mapped_attribute_spec(dst_spec, edit_args.path_to_object_map)  # noqa: PLW0212
            if breaking_connections:
                obj.disconnect(src_attr, dst_attr, update_usd=edit_args.update_usd, edit_args=edit_args.undoable)
            else:
                obj.connect(src_attr, dst_attr, update_usd=edit_args.update_usd, edit_args=edit_args.undoable)

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _process_disconnect_all(obj, attribute_specs: AttributeSpecs_t, edit_args: Controller._EditArgs):
        """Process the edit section connections to be made or broken

        Args:
            path_to_object_map: The map in use with local path names to created objects
            attribute_specs: List of attribute from which all connections are to be broken
            edit_args: The common arguments used to configure editing operations Controller._EditArgs

        Raises:
            OmniGraphError: If the attribute could not be found or the disconnect failed
        """
        attribute_specs = attribute_specs if isinstance(attribute_specs, list) else [attribute_specs]
        for attribute_spec in attribute_specs:
            attribute = (obj.__mapped_attribute_spec(attribute_spec, edit_args.path_to_object_map),)  # noqa: PLW0212
            obj.disconnect_all(attribute, update_usd=edit_args.update_usd, undoable=edit_args.undoable)

    # --------------------------------------------------------------------------------------------------------------
    PrimCreationData_t = Union[Tuple[Path_t, PrimAttrs_t], Tuple[Path_t, str], Tuple[Path_t, PrimAttrs_t, str]]

    @staticmethod
    def _process_create_prims(
        obj,
        prim_definitions: List[PrimCreationData_t],
        edit_args: Controller._EditArgs,
    ) -> List[Usd.Prim]:
        """Process the edit section specifying prim creation

        Args:
            prim_definitions: List of prim paths with optional attribute values and prim type to create on the prim
            edit_args: The common arguments used to configure editing operations Controller._EditArgs

        Returns:
            List of prims that were created that correspond to the definitions

        Raises:
            OmniGraphError if there was a problem with the prim path or attribute definition
        """

        def __create_one_prim(prim_definition: obj.PrimCreationData_t) -> Usd.Prim:
            """Normalize the inputs to turn them all into types suitable for calling create_prim with"""
            prim_path = None
            prim_attributes = {}
            prim_type = None
            if isinstance(prim_definition, (str, Sdf.Path)):
                prim_path = prim_definition
            elif isinstance(prim_definition, (tuple, list)) and isinstance(prim_definition[0], (str, Sdf.Path)):
                if len(prim_definition) == 2:
                    if isinstance(prim_definition[1], str):
                        (prim_path, prim_type) = prim_definition
                    elif isinstance(prim_definition[1], dict):
                        (prim_path, prim_attributes) = prim_definition
                elif (
                    len(prim_definition) == 3
                    and isinstance(prim_definition[1], dict)
                    and isinstance(prim_definition[2], str)
                ):
                    (prim_path, prim_attributes, prim_type) = prim_definition
            if prim_path is None:
                raise OmniGraphError(
                    f"Prim definitions must be name, (name,values), (name,type) or (name,values,type) -"
                    f" '{prim_definition}' is not recognized"
                )

            return obj.create_prim(
                _find_actual_path(str(prim_path), "", {}),
                prim_attributes,
                prim_type,
                undoable=edit_args.undoable,
                allow_exists=edit_args.allow_exists_prim,
            )

        # Loop through all prim definitions, creating them as we go
        return [__create_one_prim(prim_definition) for prim_definition in prim_definitions]

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _process_expose_prims(
        obj,
        exposure_definitions: List[GraphController.ExposePrimNode_t],
        edit_args: Controller._EditArgs,
    ) -> List[og.Node]:
        """Process the edit section specifying prim creation

        Args:
            exposure_definitions: List of (exposure_type, prim, node_path) mappings giving the type of exposure,
                                  prim to expose, and new node path at which it will be exposed
            edit_args: The common arguments used to configure editing operations Controller._EditArgs

        Returns:
            List of nodes that were created to expose the specified prims

        Raises:
            OmniGraphError if there was a problem with the prim or node path
        """
        nodes_constructed = [
            obj.expose_prim(
                exposure_type,
                _find_actual_path(prim_id, "", edit_args.path_to_object_map) if isinstance(prim_id, str) else prim_id,
                _find_actual_path(node_path, edit_args.graph_path, edit_args.path_to_object_map),
                update_usd=edit_args.update_usd,
                undoable=edit_args.undoable,
            )
            for (exposure_type, prim_id, node_path) in exposure_definitions
        ]
        just_names = [node_path for (_, _, node_path) in exposure_definitions]
        edit_args.path_to_object_map.update(dict(zip(just_names, nodes_constructed)))

        return nodes_constructed

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _process_set_values(obj, value_definitions: AttributeValues_t, edit_args: Controller._EditArgs):
        """Process the edit section specifying value setting

        Args:
            value_definitions: List of (AttributeSpec_t, value) tuples indicating the attributes and the values to set
                               on them. The attribute spec will have the path_to_object_map applied to them if they
                               contain a relative node path. Optionally it will be a 3-tuple where the third member
                               is an AttributeType_t that specifies a resolve type for the attribute. This is only
                               valid for extended attribute types.
            edit_args: The common arguments used to configure editing operations Controller._EditArgs

        Raises:
            OmniGraphError: If the attributes could not be found, the values were invalid, or setting failed
        """

        def _process_set_value(attribute_id: AttributeSpec_t, value: ValueToSet_t, type_info: AttributeType_t = None):
            """Sets a single value on an attribute"""
            attribute_spec = obj.__mapped_attribute_spec(attribute_id, edit_args.path_to_object_map)  # noqa: PLW0212
            if type_info is not None:
                value = og.TypedValue(value, type_info)
            obj.set(
                og.ObjectLookup.attribute(attribute_spec),
                value,
                update_usd=edit_args.update_usd,
                undoable=edit_args.undoable,
            )

        if isinstance(value_definitions, list):
            _ = [_process_set_value(*value_definition) for value_definition in value_definitions]
        else:
            _process_set_value(*value_definitions)

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _process_create_variable(
        obj,
        variable_definitions: List[Tuple[VariableName_t, VariableType_t, Optional[Any]]],
        edit_args: Controller._EditArgs,
    ) -> List[og.IVariable]:
        """Process the edit section that creates new variables

        Args:
            variable_definition: List of descriptions for variables to be created
            edit_args: The common arguments used to configure editing operations Controller._EditArgs

        Returns:
            List of variables created
        """
        return [
            obj.create_variable(
                edit_args.graph_path,
                name,
                var_type,
                undoable=edit_args.undoable,
                default_value=def_value[0] if len(def_value) > 0 else None,
            )
            for (name, var_type, *def_value) in variable_definitions
        ]

    # --------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _process_promote_attributes(
        obj, promote_attributes: List[Tuple[AttributeSpec_t, str]], edit_args: Controller._EditArgs
    ) -> List[og.Attribute]:
        """Process the promote attributes section that promotes new attributes on compounds

        Args:
            promote_attributes: List of attribute, name pairs describing the attributes to promote
            edit_args: The common arguments used to configure editing operations Controller._EditArgs

        Returns:
            List of attributes created
        """
        return [
            obj.promote_attribute(
                attribute=obj.__mapped_attribute_spec(attribute_spec, edit_args.path_to_object_map),  # noqa: PLW0212
                name=name,
                undoable=edit_args.undoable,
            )
            for (attribute_spec, name) in promote_attributes
        ]

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def edit(  # noqa: PLC0202,PLE0202
        obj, *args, **kwargs  # noqa: N804
    ) -> Tuple[og.Graph, List[og.Node], List[Usd.Prim], PathToObjectMap_t]:
        """Edit and/or create an OmniGraph from the given description.

        This function provides a single call that will make a set of modifications to an OmniGraph. It can be used to
        create a new graph from scratch or to make changes to an existing graph.

        If the "undoable" mode is not set to False then a single undo will revert everything done via this call.

        The description below contains different sections that perform different operations on the graph. They are
        always done in the order listed to minimize conflicts. If you need to execute them in a different order then use
        multiple calls to edit().

        This function can be called either from the class or using an instantiated object. When calling from an object
        context the arguments passed in will take precedence over the arguments provided to the constructor. Here are
        some of the legal ways to call the edit function:

        .. code-block:: python

            # For example purposes "cmds()" is a function that returns a dictionary of editing commands

            (graph, _, _, _) = og.Controller.edit("/TestGraph", cmds())

            new_controller = og.Controller(graph)
            new_controller.edit(cmds())

            og.Controller.edit(graph, cmds())
            new_controller.edit(graph, cmds())
            new_controller.edit(graph, cmds(), undoable=False)  # Overrides the normal undoable state of new_controller

        Below is the list of the allowed operations, in the order in which they will be performed.

        The parameters are described as lists, though if you have only one parameter for a given operation you can pass
        it without it being in a list.

        .. code-block:: python

            { OPERATION: [List, Of, Arguments] }
            { OPERATION: SingleArgument }

        For brevity the shortcut "keys = og.Controller.Keys" is assumed to exist.

            - keys.DELETE_NODES: NodeSpecs_t

                Deletes a node or list of nodes. If the node specification is a relative path then it must be in the
                list of full paths that the controller created in a previous call to edit().

                .. code-block:: python

                    { keys.DELETE_NODES: ["NodeInGraph", "/Some/Other/Graph/Node", my_omnigraph_node] }

            - keys.CREATE_VARIABLES: [(VariableName_t, VariableType_t)] or [(VariableName_t, VariableType_t, Any)]

                Constructs a variable on the graph with the given name and type and an optional default value.
                The type can be specified as either a ogn type string (e.g. "float4"), or as an og.Type
                (e.g. og.Type(og.BaseDataType.FLOAT))

                .. code-block:: python

                    { keys.CREATE_VARIABLES: [("velocity", "float3"), ("count", og.Type(og.BaseDataType.FLOAT), 4)] }

            - keys.CREATE_NODES: [(Path_t, Union[NodeType_t, dict])]

                Constructs a node of the given type at the given path. If the path is a relative one then it is
                added directly under the graph being edited. A map is remembered between the given path, relative or
                absolute, and the node created at it so that further editing functions can refer to the node by that
                name directly rather than trying to infer the final full name.

                .. code-block:: python

                    { keys.CREATE_NODES: [("NodeInGraph", "omni.graph.tutorial.SimpleData"),
                                          ("Inner/Node/Path", og.NodeType(node_type_name))] }

                The node type can also be a dictionary of editing commands. In that scenario, the created node
                becomes a compound node which uses the commands to construct a subgraph that defines its execution.

                .. code-block:: python

                    { keys.CREATE_NODES: [("CompoundNode", {
                                            keys.CREATE_NODES: ("NodesInCompound", "omni.graph.tutorial.SimpleData")
                                         })
                    ]}


            - keys.CREATE_PRIMS: [(Path_t, {ATTR_NAME: (AttributeType_t, ATTR_VALUE)}, Optional(PRIM_TYPE))]

                Constructs a prim at path "PRIM_PATH" containing a set of attributes with specified types and values.
                Only those attribute types supported by USD can be used here, though the type specification can be in
                OGN form - invalid types result in an error. Whereas relative paths on nodes are treated as being
                relative to the graph, for prims a relative path is relative to the stage root. Prims are not allowed
                inside an OmniGraph and attempts to create one there will result in an error.

                Note that the PRIM_TYPE can appear with or without an attribute definition. (Many prim types are part
                of a schema and do not require explicit attributes to be added.)

                .. code-block:: python

                    { keys.CREATE_PRIMS: [("/World/Prim", {"speed": ("double", 1.0)}),
                                          ("/World/Cube", "Cube"),
                                          ("RootPrim", {
                                              "mass": (Type(BaseDataType.DOUBLE), 3.0),
                                              "force:gravity": ("double", 32.0)
                    })]}

            - keys.EXPOSE_PRIMS: [(cls.PrimExposureType, Prim_t, NewNode_t)]

                Exposes a prim to OmniGraph through creation of one of the node types designed to do that.
                The first member of the tuple is the method used to expose the prim. The prim path is
                the second member of the tuple and it must already exist in the USD stage. The third member
                of the tuple is a node name with the same restrictions as the name in the CREATE_NODES edit.

                .. code-block:: python

                    { keys.EXPOSE_PRIMS: [(cls.PrimExposureType.AS_BUNDLE, "/World/Cube", "BundledCube")] }

            - keys.CREATE_ATTRIBUTES: [(AttributeSpec_t, AttributeTypeSpec_t)]

                Constructs one or more new dynamic attributes on nodes. The first argument of the tuple defines the
                location of the new attribute by path and/or node. The second argument of the tuple defines the type
                and port of the attribute in a flexible way (see the type definition for more details). Any combination
                of specifications can be used to define new attributes. Unspecified ports default the attribute to
                being an input.

                .. code-block:: python

                    { keys.CREATE_ATTRIBUTES: [
                        ("NewNode.inputs:new_float_attribute", "float"),
                        (
                            ("new_attribute", new_node),
                            (og.Type(og.BaseDataType.INT), og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT),
                        ),
                        (
                            "/World/Graph/Node.new_union_output",
                            (["float", "double"], og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT),
                        ),
                        ("/World/Graph/Node.new_any_input", "any"),
                    }

            - keys.CONNECT: [(AttributeSpec_t, AttributeSpec_t)]

                Makes a connection between the given source and destination attributes. The local name of a newly
                created node may be made as part of the node in the spec, or the node portion of the attribute path:

                .. code-block:: python

                    { keys.CONNECT: [("NodeInGraph.outputs:value", ("inputs:value", "NodeInGraph"))]}

            - keys.DISCONNECT: [(AttributeSpec_t, AttributeSpec_t)]

                Breaks a connection between the given source and destination attributes. The local name of a newly
                created node may be made as part of the node in the spec, or the node portion of the attribute path:

                .. code-block:: python

                    { keys.DISCONNECT: [("NodeInGraph.outputs:value", ("inputs:value", "NodeInGraph"))]}

            - keys.DISCONNECT_ALL: [AttributeSpec_t]

                Breaks all connections to and from the given attributes. The local name of a newly
                created node may be made as part of the node in the spec, or the node portion of the attribute path:

                .. code-block:: python

                    { keys.DISCONNECT_ALL: ["NodeInGraph.outputs:value", ("inputs:value", "NodeInGraph")]}

            - keys.PROMOTE_ATTRIBUTES: [(AttributeSpec_t, str)]

                Promotes attributes on a node in a compound graph instance as attributes on the parent compound node
                with the given name. Only input and output attributes on a node in a compound graph can be promoted.
                The prefix of the promoted name is optional; the 'inputs' prefix will be prepended for input attributes,
                and the 'outputs' prefix will be prepended for output attributes if necessary.

                .. code-block:: python

                    {keys.PROMOTE_ATTRIBUTES :[("NodeInGraph.inputs:value", "inputs:new_name"),
                                              ("OtherNodeInGraph.outputs:value", "result")

                    ]}

            - keys.SET_VALUES: [AttributeSpec_t, Any] or [AttributeSpec_t, Any, AttributeType_t]

                Sets the value of the given list of attributes.

                .. code-block:: python

                    { keys.SET_VALUES: [("/World/Graph/Node.inputs:attr1", 1.0), (("inputs:attr2", node), 2.0)] }

                In the case of extended attribute types you may also need to supply a data type, which is the type the
                attribute will resolve to when the value is set. To supply a type, add it as a third parameter to the
                attribute value:

                .. code-block:: python

                    { keys.SET_VALUES: [("inputs:ext1", node), 2.0, "float"] }

        Here's a simple call that first deletes an existing node "/World/PushGraph/OldNode", then creates two nodes of
        type "omni.graph.tutorials.SimpleData", connects their "a_int" attributes, disconnects their "a_float"
        attributes and sets the input "a_int" of the source node to the value 5. It also creates two unused USD Prim
        nodes, one with a float attribute named "attrFloat" with value 2.0, and the other with a boolean attribute
        named "attrBool" with the value true.

        .. code-block:: python

            controller = og.Controller()
            keys = og.Controller.Keys
            (graph, nodes_constructed, prims_constructed, path_to_object_map) = controller.edit("/World/PushGraph", {
                keys.DELETIONS: [
                    "OldNode"
                ],
                keys.CREATE_NODES: [
                    ("src", "omni.graph.tutorials.SimpleData"),
                    ("dst", "omni.graph.tutorials.SimpleData")
                    ],
                keys.CREATE_PRIMS: [
                    ("Prim1", {"attrFloat": ("float", 2.0)}),
                    ("Prim2", {"attrBool": ("bool", True)}),
                    ],
                keys.CONNECT: [
                    ("src.outputs:a_int", "dst.inputs:a_int")
                    ],
                keys.DISCONNECT: [
                    ("src.outputs:a_float", "dst.inputs:a_float")
                    ],
                keys.SET_VALUES: [
                    ("src.inputs:a_int", 5)
                    ]
                keys.CREATE_VARIABLES: [
                    ("a_float_var", og.Type(og.BaseDataType.FLOAT)),
                    ("a_bool_var", "bool", True)
                ]
                }
            )

        .. note::

            The controller object remembers where nodes are created so that you can use short forms for the node paths
            for convenience. That's why in the above graph the node paths for creation and the node specifications in
            the connections just says "src" and "dst". As they have no leading "/" they are treated as being relative
            to the graph path and will actually end up in "/World/PushGraph/src" and "/World/PushGraph/dst".

            Node specifications with a leading "/" are assumed to be absolute paths and must be inside the path of an
            existing or created graph. e.g. the NODES reference could have been "/World/PushGraph/src", however using
            "/src" would have been an error.

            This node path mapping is remembered across multiple calls to edit() so you can always use the shortform
            so long as you use the same Controller object.

        Args:
            obj: Either cls or self depending on how edit() was called
            graph_id: Identifier that says which graph is being edited. See GraphController.create_graph()
                      for the data types accepted for the graph description.
            edit_commands: Dictionary of commands and parameters indicating what modifications are to be made
                           to the specified graph. A strict set of keys is accepted. Each of the values in the
                           dictionary can be either a single value or a list of values of the proscribed type.
            path_to_object_map: Dictionary of relative paths mapped on to their full path after creation so that the
                                edit_commands can use either full paths or short-forms to specify the nodes.
            update_usd: If specified then override whether to update the USD after the operations (default False)
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
                      (default True)
            allow_exists_attr: If True then attribute creation operation won't fail when the attribute already exists
                               on the node it was being added to (default False)
            allow_exists_node: If True then node creation operation won't fail when the node already exists in the
                               scene graph (default False)
            allow_exists_prim: If True then prim creation operation won't fail when the prim already exists in the
                               scene graph (default False)

        Returns:
            (Graph, list[Node], list[Usd.Prim], dict[str, str]):
                - the og.Graph being used for the operation
                - the list of og.Nodes created by the operation
                - the list of Usd.Prims created by the operation
                - the map of node/prim path name to the created og.Node/Usd.Prim objects. Can usually be ignored; it
                  will be used internally to manage the shortform names of the paths used in multiple commands.

        Raises:
            OmniGraphError: if any of the graph creation instructions could not be fulfilled
                The graph will be left in the partially constructed state it reached at the time of the error
        """
        return obj.__edit(obj, args=args, kwargs=kwargs)

    def __edit_obj(self, *args, **kwargs):
        """Implements Controller.edit() as an object method"""
        results = self.__edit(
            self,
            graph_id=self.__graph_id,
            path_to_object_map=self.__path_to_object_map,
            update_usd=self.__update_usd,
            undoable=self.__undoable,
            allow_exists_node=self.__allow_exists_node,
            allow_exists_prim=self.__allow_exists_prim,
            allow_exists_attr=self.__allow_exists_attr,
            args=args,
            kwargs=kwargs,
        )
        self.__graph_id = results[0]
        self.__path_to_object_map = results[3]
        return results

    @staticmethod
    def __edit(
        obj,
        graph_id: Union[GraphSpec_t, Dict[str, Any]] = _Unspecified,
        edit_commands: Optional[Dict[str, Any]] = None,
        path_to_object_map: PathToObjectMap_t = None,
        update_usd: bool = True,
        undoable: bool = True,
        allow_exists_node: bool = False,
        allow_exists_prim: bool = False,
        allow_exists_attr: bool = False,
        args: List[str] = None,
        kwargs: Dict[str, Any] = None,
    ) -> Tuple[og.Graph, List[og.Node], List[Usd.Prim]]:
        """Implements Controller.edit()"""
        (
            graph_id,
            edit_commands,
            path_to_object_map,
            update_usd,
            undoable,
            allow_exists_node,
            allow_exists_prim,
            allow_exists_attr,
        ) = _flatten_arguments(
            mandatory=[("graph_id", graph_id)],
            optional=[
                ("edit_commands", edit_commands),
                ("path_to_object_map", path_to_object_map),
                ("update_usd", update_usd),
                ("undoable", undoable),
                ("allow_exists_node", allow_exists_node),
                ("allow_exists_prim", allow_exists_prim),
                ("allow_exists_attr", allow_exists_attr),
            ],
            args=args,
            kwargs=kwargs,
        )
        if edit_commands is None:
            edit_commands = {}
        if path_to_object_map is None:
            path_to_object_map = {}

        # If the undo or usd update states were specified then add them to the arguments everywhere
        shared_kwargs = Controller._EditArgs(
            update_usd=update_usd,
            undoable=undoable,
            path_to_object_map=path_to_object_map,
            allow_exists_node=allow_exists_node,
            allow_exists_prim=allow_exists_prim,
            allow_exists_attr=allow_exists_attr,
        )

        # Separate the actual work so that it can be configured before being called
        def __do_the_edits():
            # A dictionary ID always indicates the graph should be created, otherwise check if it already exists
            graph = obj.graph(graph_id) if not isinstance(graph_id, dict) else None
            nodes_constructed = []
            prims_constructed = []

            # If the graph couldn't be found then infer that it should be created with the given specification.
            if graph is None:
                graph = obj.create_graph(graph_id)

            # The graph could be in an illegal state when halfway through editing operations. This will disable it
            # until all operations are completed. It's up to the caller to ensure that the state is legal after all
            # operations are completed.
            graph_was_disabled = graph.is_disabled()
            graph.set_disabled(True)
            graph_path = graph.get_path_to_graph()
            shared_kwargs.graph_path = graph_path

            try:
                # Syntax check first
                for instruction, _data in edit_commands.items():
                    if instruction not in obj.Keys.ALL:
                        raise OmniGraphError(f"Unknown graph edit operation - `{instruction}` not in {obj.Keys.ALL}")

                # Delete first because we may be creating nodes with the same names
                with suppress(KeyError):
                    obj._process_delete_nodes(  # noqa: PLW0212
                        obj,
                        _get_as_list(edit_commands[obj.Keys.DELETE_NODES]),
                        edit_args=shared_kwargs,
                    )

                # Variables next, so they exist when nodes are created
                with suppress(KeyError):
                    obj._process_create_variable(  # noqa: PLW0212
                        obj,
                        _get_as_list(edit_commands[obj.Keys.CREATE_VARIABLES]),
                        edit_args=shared_kwargs,
                    )

                # Create nodes next since connect and set may need them
                nodes_constructed = []
                with suppress(KeyError):
                    nodes_constructed = obj._process_create_nodes(  # noqa: PLW0212
                        obj,
                        _get_as_list(edit_commands[obj.Keys.CREATE_NODES]),
                        edit_args=shared_kwargs,
                    )

                # Prims next as they may be used in connections
                with suppress(KeyError):
                    prims_constructed = obj._process_create_prims(  # noqa: PLW0212
                        obj,
                        _get_as_list(edit_commands[obj.Keys.CREATE_PRIMS]),
                        edit_args=shared_kwargs,
                    )

                # Exposure of a raw prim to OmniGraph through one of the prim interface nodes
                with suppress(KeyError):
                    nodes_constructed += obj._process_expose_prims(  # noqa: PLW0212
                        obj,
                        _get_as_list(edit_commands[obj.Keys.EXPOSE_PRIMS]),
                        edit_args=shared_kwargs,
                    )

                # Create attributes next since connect and set may need them
                with suppress(KeyError):
                    obj._process_create_attributes(  # noqa: PLW0212
                        obj,
                        _get_as_list(edit_commands[obj.Keys.CREATE_ATTRIBUTES]),
                        edit_args=shared_kwargs,
                    )

                # Connections next as setting values may override their data
                with suppress(KeyError):
                    obj._process_connections(  # noqa: PLW0212
                        obj,
                        _get_as_list(edit_commands[obj.Keys.CONNECT]),
                        breaking_connections=False,
                        edit_args=shared_kwargs,
                    )

                # Disconnections may have been created by the connections list so they're next, though that's unlikely
                with suppress(KeyError):
                    obj._process_connections(  # noqa: PLW0212
                        obj,
                        _get_as_list(edit_commands[obj.Keys.DISCONNECT]),
                        breaking_connections=True,
                        edit_args=shared_kwargs,
                    )

                # Disconnections of all attributes is last for connection changes as it will read existing connections
                with suppress(KeyError):
                    obj._process_disconnect_all(  # noqa: PLW0212
                        obj,
                        _get_as_list(edit_commands[obj.Keys.DISCONNECT_ALL]),
                        edit_args=shared_kwargs,
                    )

                # For compound nodes, promote an inputs and outputs on the parent graph
                with suppress(KeyError):
                    obj._process_promote_attributes(  # noqa: PLW0212
                        obj,
                        _get_as_list(edit_commands[obj.Keys.PROMOTE_ATTRIBUTES]),
                        edit_args=shared_kwargs,
                    )

                # Now that everything is in place it is safe to set the values
                # TODO: Setting values has two parameters (on_gpu, and update_usd) that are not accounted for here.
                #       Extra information should be provided to allow for them. Until then the defaults will be used.
                with suppress(KeyError):
                    obj._process_set_values(  # noqa: PLW0212
                        obj, _get_as_list(edit_commands[obj.Keys.SET_VALUES]), edit_args=shared_kwargs
                    )
            finally:
                # Really important that this always gets reset
                graph.set_disabled(graph_was_disabled)

            # process any pending usd changes caused by this edit
            if update_usd:
                og._internal.flush_usd()  # noqa PLW0212

            return (graph, nodes_constructed, prims_constructed, path_to_object_map)

        # Put every operation into a single undo umbrella. They will handle queueing undoable operations internally.
        if undoable:
            with undo.group():
                return __do_the_edits()

        return __do_the_edits()
