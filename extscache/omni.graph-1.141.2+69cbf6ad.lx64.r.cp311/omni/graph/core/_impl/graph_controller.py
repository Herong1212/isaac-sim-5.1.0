# noqa: PLC0302
"""Helpers for modifying the contents of a graph"""
from __future__ import annotations

import asyncio
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import omni.graph.core as og
import omni.graph.tools.ogn as ogn
import omni.kit
import omni.usd
from carb import log_info
from pxr import Sdf, Tf, Usd

from .commands import cmds
from .object_lookup import ObjectLookup
from .type_aliases import (
    AttributeSpec_t,
    Graph_t,
    NewNode_t,
    Node_t,
    Nodes_t,
    NodeType_t,
    Path_t,
    Prim_t,
    PrimAttrs_t,
    Variable_t,
    VariableName_t,
    VariableType_t,
)
from .utils import DBG, _flatten_arguments, _Unspecified


# ==============================================================================================================
class GraphController:
    """Helper class that provides a simple interface to modifying the contents of a graph"""

    # --------------------------------------------------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Initializes the class with a particular configuration.
        The arguments are flexible so that classes can initialize only what they need for the calls they
        will be making. Both arguments are optional, and there may be other arguments present that will be ignored.

        Args:
            update_usd (bool): Should any graphs, nodes, and prims referenced in operations be updated immediately to
                               USD? (default True)
            undoable (bool): If True the operations performed with this instance of the class are added to the undo
                             queue, else they are done immediately and forgotten (default True)
            allow_exists_node: If True then succeed creation of a node when matching path, type, and version already exists.
                               It is still a failure if one of those properties on the existing node does not match.
            allow_exists_prim: If True then succeed creation of a prim when matching path and type already exists. It is
                               still a failure if type on the existing prim does not match.
        """
        (self.__update_usd, self.__undoable, self.__allow_exists_node, self.__allow_exists_prim) = _flatten_arguments(
            optional=[
                ("update_usd", True),
                ("undoable", True),
                ("allow_exists_node", False),
                ("allow_exists_prim", False),
            ],
            args=args,
            kwargs=kwargs,
        )

        # Dual function methods that can be called either from an object or directly from the class
        self.create_graph = self.__create_graph_obj
        self.create_node = self.__create_node_obj
        self.create_prim = self.__create_prim_obj
        self.create_variable = self.__create_variable_obj
        self.delete_node = self.__delete_node_obj
        self.expose_prim = self.__expose_prim_obj
        self.connect = self.__connect_obj
        self.disconnect = self.__disconnect_obj
        self.disconnect_all = self.__disconnect_all_obj

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def create_graph(obj, *args, **kwargs) -> og.Graph:  # noqa: N804,PLC0202,PLE0202
        """Create a graph from the description

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. The second argument can be positional or by keyword and is
        mandatory, resulting in an error if omitted. All others are by keyword and optional, defaulting to the value
        set in the constructor in the object context and the function defaults in the class context.

        .. code-block:: python

            new_graph = og.GraphController.create_graph("/TestGraph")
            controller = og.GraphController(undoable=True)
            controller.create_graph({"graph_path": "/UndoableGraph", "evaluator_name": "execution"})

        Args:
            obj: Either cls or self, depending on how the function was called
            graph_id: Parameters describing the graph to be created. If the graph is just a path then a default graph
                      will be created at that location. If the identifier is a dictionary then it will be interpreted
                      as a set of parameters describing the type of graph to create

                      - **graph_path**: Full path to the graph prim to be created to house the OmniGraph
                      - **evaluator_name**: Type of evaluator the graph should use (default **push**)
                      - **fc_backing_type**: og.GraphBackingType that tells you what kind of Fabric to use for graph
                        data (default og.GraphBackingType.GRAPH_BACKING_TYPE_FABRIC_WITHOUT_HISTORY)
                      - **pipeline_stage**: og.GraphPipelineStage that tells you which pipeline stage this graph fits
                        into (default og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_SIMULATION)
                      - **evaluation_mode**: og.GraphEvaluationMode that tells you which evaluation mode this graph uses
                        (default og.GraphEvaluationMode.GRAPH_EVALUATION_MODE_AUTOMATIC)
            update_usd (bool): If specified then override whether to create the graph with a USD backing (default True)
            undoable (bool): If True the operation is added to the undo queue, else it is done immediately and forgotten
                             (default True)

        Returns:
            omni.graph.core.Graph: The created graph

        Raises:
            OmniGraphError: if the graph creation failed for any reason
        """
        return obj.__create_graph(obj, args=args, kwargs=kwargs)

    def __create_graph_obj(self, *args, **kwargs) -> og.Graph:
        """Implements :py:meth:`.GraphController.create_graph` when called as an object method"""
        return self.__create_graph(
            self, update_usd=self.__update_usd, undoable=self.__undoable, args=args, kwargs=kwargs
        )

    @staticmethod
    def __create_graph(
        obj,
        graph_id: Union[Graph_t, Dict[str, Any]] = _Unspecified,
        update_usd: bool = True,
        undoable: bool = True,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> og.Graph:
        """Implements :py:meth:`.GraphController.create_graph`"""
        (graph_id, update_usd, undoable) = _flatten_arguments(
            mandatory=[("graph_id", graph_id)],
            optional=[("update_usd", update_usd), ("undoable", undoable)],
            args=args,
            kwargs=kwargs,
        )

        def __default_create_args(graph_path: str) -> Dict[str, Any]:
            """Returns the default arguments for the CreateGraphAsNode command for the given graph path"""
            return {
                "graph_path": graph_path,
                "node_name": graph_path.rsplit("/", 1)[1],
                "evaluator_name": "push",
                "is_global_graph": True,
                "backed_by_usd": True if update_usd is None else update_usd,
                "fc_backing_type": og.GraphBackingType.GRAPH_BACKING_TYPE_FABRIC_WITHOUT_HISTORY,
                "pipeline_stage": og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_SIMULATION,
                "evaluation_mode": og.GraphEvaluationMode.GRAPH_EVALUATION_MODE_AUTOMATIC,
            }

        def __add_orchestration_graph(graph_cmd_args: Dict[str, Any]):
            """Modify the dictionary to include the appropriate orchestration graph as a parameter"""
            try:
                pipeline_stage = graph_cmd_args["pipeline_stage"]
                orchestration_graphs = og.get_global_orchestration_graphs_in_pipeline_stage(pipeline_stage)
                graph_cmd_args["graph"] = orchestration_graphs[0]
            except (KeyError, IndexError) as error:
                raise og.OmniGraphError(f"Could not find orchestration graph for stage {pipeline_stage}") from error

        success = True
        graph_node = None
        if isinstance(graph_id, str):
            cmd_args = __default_create_args(graph_id)
        elif isinstance(graph_id, dict):
            if "graph_path" not in graph_id:
                raise og.OmniGraphError(f"Tried to create graph without graph path using {graph_id}")
            cmd_args = __default_create_args(graph_id["graph_path"])
            cmd_args.update(graph_id)
        else:
            raise og.OmniGraphError(f"Graph description must be a path or an argument dictionary, not {graph_id}")
        __add_orchestration_graph(cmd_args)
        if undoable:
            (success, graph_node) = cmds.CreateGraphAsNode(**cmd_args)
        else:
            success = True
            graph_node = cmds.imm.CreateGraphAsNode(**cmd_args)

        if graph_node is None or not graph_node.is_valid() or not success:
            raise og.OmniGraphError(f"Failed to wrap graph in node given {graph_id}")
        graph = graph_node.get_wrapped_graph()
        if graph is None:
            raise og.OmniGraphError(f"Failed to construct graph given {graph_id}")

        return graph

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def create_node(obj, *args, **kwargs) -> og.Graph:  # noqa: N804,PLC0202,PLE0202
        """Create an OmniGraph node of the given type and version at the given path.

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. "node_id" and "node_type_id" are mandatory, and can be specified
        either as positional or keyword arguments. All others are by keyword only and optional, defaulting to the value
        set in the constructor in the object context where available, and the function defaults elsewhere.

        .. code-block:: python

            og.GraphController.create_node("/MyGraph/MyNode", "omni.graph.nodes.NodeType")
            og.GraphController(update_usd=True).create_node("/MyGraph/MyNode", "omni.graph.nodes.NodeType")
            og.GraphController.create_node("/MyGraph/MyNode", "omni.graph.nodes.NodeType", update_usd=True)
            og.GraphController.create_node(node_id="/MyGraph/MyNode", node_type="omni.graph.nodes.NodeType")

        Args:
            obj: Either cls or self, depending on how the function was called
            node_id: Absolute path, or (Relative Path, Graph) where the node will be constructed. If an absolute path
                     was passed in it must be part of an existing graph.
            node_type_id: Unique identifier for the type of node to create (name or og.NodeType)
            allow_exists: If True then succeed if a node with matching path, type, and version already exists. It is
                          still a failure if one of those properties on the existing node does not match.
            version: Version of the node type to create. By default it creates the most recent.
            update_usd: If specified then override whether to create the node with a USD backing or not (default True)
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
                      (default True)

        Raises:
            og.OmniGraphError: If one or more of the nodes could not be added to the scene for some reason.

        Returns:
            omni.graph.core.Node | list[omni.graph.core.Node]: Node(s) added to the scene
        """
        return obj.__create_node(obj, args=args, kwargs=kwargs)

    def __create_node_obj(self, *args, **kwargs) -> og.Node:
        """Implements :py:meth:`.GraphController.create_node` when called as an object method"""
        return self.__create_node(
            self,
            update_usd=self.__update_usd,
            undoable=self.__undoable,
            allow_exists=self.__allow_exists_node,
            args=args,
            kwargs=kwargs,
        )

    @staticmethod
    def __create_node(
        obj,
        node_id: NewNode_t = _Unspecified,
        node_type_id: NodeType_t = _Unspecified,
        allow_exists: bool = False,
        version: int = None,
        update_usd: bool = True,
        undoable: bool = True,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> og.Node:
        """Implements :py:meth:`.GraphController.create_node`"""
        (node_id, node_type_id, allow_exists, version, update_usd, undoable) = _flatten_arguments(
            mandatory=[("node_id", node_id), ("node_type_id", node_type_id)],
            optional=[
                ("allow_exists", allow_exists),
                ("version", version),
                ("update_usd", update_usd),
                ("undoable", undoable),
            ],
            args=args,
            kwargs=kwargs,
        )
        _ = DBG and log_info(f"Create '{node_id}' of type '{node_type_id}', allow={allow_exists}, version={version}")

        if version is not None:
            raise og.OmniGraphError("Creating nodes with specific versions not supported")

        graph = None
        if isinstance(node_id, tuple):
            # Handle the (node, graph) pair version of the parameters
            (node_path, graph_id) = node_id
            if not isinstance(node_path, str):
                raise og.OmniGraphError(f"Node identifier '{node_id}' can only be a (str, graph) pair")
            graph = ObjectLookup.graph(graph_id)
            if graph is None:
                raise og.OmniGraphError(f"Tried to create a node with unknown graph spec '{graph_id}'")
            node_path = f"{graph.get_path_to_graph()}/{node_path}"
        else:
            # Infer the graph from the full node path
            (graph, node_path) = ObjectLookup.split_graph_from_node_path(node_id)
            if graph is None:
                raise og.OmniGraphError(f"Tried to create a node in a path without a graph - '{node_id}'")
            if node_path is None:
                raise og.OmniGraphError(f"Tried to create a node from a graph path '{graph.get_path_to_graph()}'")
            node_path = f"{graph.get_path_to_graph()}/{node_path}"

        try:
            node_type = ObjectLookup.node_type(node_type_id)
            node_type_name = node_type.get_node_type()
        except og.OmniGraphError:
            node_type = None
            node_type_name = None

        node = graph.get_node(node_path)
        if node is not None and node.is_valid():
            if allow_exists:
                current_node_type = node.get_type_name()
                if node_type_id is None or node_type_id == current_node_type:
                    return node
                error = f"already exists as type {current_node_type}"
            else:
                error = "already exists"
            raise og.OmniGraphError(f"Creation of {node_path} as type {node_type} failed - {error}")

        if node_type_name is None:
            extension = node_type_id.rsplit(".", 1)[0]
            more = "" if extension == node_type_id else f". Perhaps the extension '{extension}' is not loaded?"
            raise og.OmniGraphError(f"Could not create node using unrecognized type '{node_type_id}'{more}")

        if undoable:
            (_, new_node) = cmds.CreateNode(
                graph=graph, node_path=node_path, node_type=node_type_name, create_usd=update_usd
            )
        else:
            new_node = cmds.imm.CreateNode(graph, node_path, node_type_name, update_usd)
        return new_node

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def create_prim(obj, *args, **kwargs) -> Usd.Prim:  # noqa: N804,PLC0202,PLE0202
        """Create a prim node containing a predefined set of attribute values and a ReadPrim OmniGraph node for it

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. The "prim_path" is mandatory and can appear as either a positional
        or keyword argument. All others are optional, also by position or keyword, defaulting to the value set in the
        constructor in the object context if available, and the function defaults elsewhere.

        .. code-block:: python

            og.GraphController.create_prim("/MyPrim")
            og.GraphController(undoable=False).create_prim("/MyPrim", undoable=True)  # Will be undoable
            og.GraphController().create_prim(prim_path="/MyPrim", prim_type="MyPrimType")
            og.GraphController.create_prim("/MyPrim", )

        Args:
            obj: Either cls or self depending on how the function was called
            prim_path: Location of the prim
            attribute_values: Dictionary of {NAME: (TYPE, VALUE)} for all prim attributes
                The TYPE recognizes OGN format, SDF format, or og.Type values
                The VALUE should be in a format suitable for passing to pxr::UsdAttribute.Set()
            prim_type: The type of prim to create. (default "OmniGraphPrim")
            allow_exists: If True then succeed if a prim with matching path and type already exists. It is
                          still a failure if type on the existing prim does not match.
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
                      (default True)

        Returns:
            Usd.Prim: Prim created

        Raises:
            OmniGraphError: If any of the attribute specifications could not be applied to the prim, or if the
                               prim could not be created.
        """
        return obj.__create_prim(obj, args=args, kwargs=kwargs)

    def __create_prim_obj(self, *args, **kwargs) -> og.Graph:
        """Implements :py:meth:`.GraphController.create_prim` when called as an object method"""
        return self.__create_prim(
            self, undoable=self.__undoable, allow_exists=self.__allow_exists_prim, args=args, kwargs=kwargs
        )

    @staticmethod
    def __create_prim(
        obj,
        prim_path: Path_t = _Unspecified,
        attribute_values: PrimAttrs_t = None,
        prim_type: str = None,
        allow_exists: bool = False,
        undoable: bool = True,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> Usd.Prim:
        """Implements :py:meth:`.GraphController.create_prim`"""
        (prim_path, attribute_values, prim_type, allow_exists, undoable) = _flatten_arguments(
            mandatory=[("prim_path", prim_path)],
            optional=[
                ("attribute_values", attribute_values),
                ("prim_type", prim_type),
                ("allow_exists", allow_exists),
                ("undoable", undoable),
            ],
            args=args,
            kwargs=kwargs,
        )
        # Use the prim path to create the prim
        stage = omni.usd.get_context().get_stage()
        prim_path = str(prim_path)
        prim_type = prim_type if prim_type is not None else "OmniGraphPrim"

        # Make sure the prim won't end up inside an OmniGraph
        (graph, _) = ObjectLookup.split_graph_from_node_path(prim_path)
        if graph is not None:
            raise og.OmniGraphError(
                f"Tried to create a prim inside a graph - '{prim_path}' is in '{graph.get_path_to_graph()}'"
            )

        # Do simple validation on the attribute_values types
        if attribute_values is None:
            attribute_values = {}
        if not isinstance(attribute_values, dict):
            raise og.OmniGraphError(
                f"Attribute values must be a name:(type, value) dictionary - got '{attribute_values}'"
            )

        # Give a better message than GetPrimAtPath would provide if the prim already existed
        prim = stage.GetPrimAtPath(prim_path)
        if prim is not None and prim.IsValid():
            if not allow_exists or prim.GetTypeName() != prim_type:
                raise og.OmniGraphError(f"Cannot create prim at {prim_path} - that path is already occupied")

            # No need to fail if the prim already exists, has the expected type and it is allowed by the caller
            success = True
        else:
            if undoable:
                (success, _) = omni.kit.commands.execute(
                    "CreatePrim", prim_path=prim_path, prim_type=prim_type if prim_type is not None else "OmniGraphPrim"
                )
            else:
                omni.kit.commands.create(
                    "CreatePrim", prim_path=prim_path, prim_type=prim_type if prim_type is not None else "OmniGraphPrim"
                ).do()
                success = True
            prim = stage.GetPrimAtPath(prim_path)

        if not success or not prim.IsValid():
            raise og.OmniGraphError(f"Failed to create prim at {prim_path}")

        # Walk the list of attribute descriptions, creating them on the prim as they go
        for attribute_name, attribute_data in attribute_values.items():
            try:
                (attribute_type_name, attribute_value) = attribute_data
                if not isinstance(attribute_type_name, str) and not isinstance(attribute_type_name, og.Type):
                    raise TypeError
            except (TypeError, ValueError) as error:
                raise og.OmniGraphError(
                    f"Attribute values must be a name:(type, value) dictionary - got '{attribute_values}'"
                ) from error
            if isinstance(attribute_type_name, og.Type):
                attribute_type = attribute_type_name
            else:
                attribute_type = og.AttributeType.type_from_ogn_type_name(attribute_type_name)
                if attribute_type.base_type == og.BaseDataType.UNKNOWN:
                    attribute_type = og.AttributeType.type_from_sdf_type_name(attribute_type_name)
                    if attribute_type.base_type == og.BaseDataType.UNKNOWN:
                        raise og.OmniGraphError(
                            f"Attribute type '{attribute_type_name}' was not a legal type, nor an OGN or Sdf type name"
                        )
            # The attribute type managers already know how to get the SdfValueType so ask the appropriate one
            manager = ogn.get_attribute_manager_type(attribute_type.get_ogn_type_name())
            sdf_type_name = manager.sdf_type_name()
            if sdf_type_name is None:
                raise og.OmniGraphError(
                    f"Attribute type '{attribute_type_name}' could not be translated into a valid Sdf type name"
                )

            sdf_type = getattr(Sdf.ValueTypeNames, sdf_type_name)
            usd_value = og.attribute_value_as_usd(attribute_type, attribute_value)
            attribute = prim.CreateAttribute(attribute_name, sdf_type)
            if not attribute.IsValid():
                raise og.OmniGraphError(
                    f"Attribute type '{attribute_type_name}' could not be created or set to '{usd_value}'"
                )
            attribute.Set(usd_value)

        return prim

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def create_variable(obj, *args, **kwargs) -> og.IVariable:  # noqa: N804,PLC0202,PLE0202
        """Creates a variable with the given name on the graph

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. All others are by keyword and optional, defaulting to the value
        set in the constructor in the object context and the function defaults in the class context.

        Args:
            graph_id: The graph to create a variable on
            name: The name of the variable to create
            var_type: The type of the variable to create, either a string or an OG.Type
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
                      (default True)
            default_value: The default value of the variable to set, or None to not set a default value. (default None)
        Raises:
            OmniGraphError: If the variable can't be created

        Returns:
            omni.graph.core.IVariable: The created variable
        """
        return obj.__create_variable(obj, args=args, kwargs=kwargs)

    def __create_variable_obj(self, *args, **kwargs) -> og.Graph:
        """Implements :py:meth:`.GraphController.create_variable` when called as an object method"""
        return self.__create_variable(self, undoable=self.__undoable, args=args, kwargs=kwargs)

    @staticmethod
    def __create_variable(
        obj,
        graph_id: Graph_t = _Unspecified,
        name: VariableName_t = _Unspecified,
        var_type: VariableType_t = _Unspecified,
        undoable: bool = True,
        default_value: Any = None,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> og.IVariable:
        """Implements :py:meth:`.GraphController.create_variable`"""
        (graph_id, name, var_type, undoable, default_value) = _flatten_arguments(
            mandatory=[("graph_id", graph_id), ("name", name), ("var_type", var_type)],
            optional=[("undoable", undoable), ("default_value", default_value)],
            args=args,
            kwargs=kwargs,
        )
        _ = DBG and log_info(f"Create variable {name} with type {var_type} on {graph_id}")

        graph = ObjectLookup.graph(graph_id)

        if isinstance(var_type, str):
            og_type = og.AttributeType.type_from_ogn_type_name(var_type)
        elif isinstance(var_type, og.Type):
            og_type = var_type
        else:
            raise og.OmniGraphError(f"{type} is not a valid Type object")

        variable = None
        if undoable:
            (_, variable) = cmds.CreateVariable(
                graph=graph, variable_name=name, variable_type=og_type, variable_value=default_value
            )
        else:
            variable = cmds.imm.CreateVariable(
                graph=graph, variable_name=name, variable_type=og_type, variable_value=default_value
            )

        if variable is None:
            raise og.OmniGraphError(f"Could not create variable named {name} with type {og_type} on the graph")

        return variable

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def delete_node(obj, *args, **kwargs) -> bool:  # noqa: N804,PLC0202,PLE0202
        """Deletes one or more OmniGraph nodes.

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. All others are by keyword and optional, defaulting to the value
        set in the constructor in the object context and the function defaults in the class context.

        Args:
            obj: Either cls or self depending on how the function was called
            node_id: Specification of a node or list of nodes to be deleted
            graph_id: Only required if the node_id does not contain enough information to uniquely identify it
            ignore_if_missing: If True then succeed even if no node with a matching path exists
            update_usd: If specified then override whether to delete the node's USD backing (default True)
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
                      (default True)

        Raises:
            OmniGraphError: If the node does not exist

        Returns:
            bool: True if the node was successfully deleted
        """
        return obj.__delete_node(obj, args=args, kwargs=kwargs)

    def __delete_node_obj(self, *args, **kwargs) -> bool:
        """Implements :py:meth:`.GraphController.delete_node` when called as an object method"""
        return self.__delete_node(
            self, update_usd=self.__update_usd, undoable=self.__undoable, args=args, kwargs=kwargs
        )

    @staticmethod
    def __delete_node(
        obj,
        node_id: Nodes_t = _Unspecified,
        graph_id: Optional[Graph_t] = None,
        ignore_if_missing: bool = False,
        update_usd: bool = True,
        undoable: bool = True,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> bool:
        """Implements :py:meth:`.GraphController.delete_node`"""
        (node_id, graph_id, ignore_if_missing, update_usd, undoable) = _flatten_arguments(
            mandatory=[("node_id", node_id)],
            optional=[
                ("graph_id", graph_id),
                ("ignore_if_missing", ignore_if_missing),
                ("update_usd", update_usd),
                ("undoable", undoable),
            ],
            args=args,
            kwargs=kwargs,
        )
        _ = DBG and log_info(f"Delete '{node_id}' on '{graph_id}', ignore_if_missing={ignore_if_missing}")

        graph = ObjectLookup.graph(graph_id)

        def __delete_one_node(node: Node_t) -> bool:
            """Remove a single node from its graph"""
            nodes_graph = graph
            try:
                omnigraph_node = ObjectLookup.node(node, graph)
                nodes_graph = omnigraph_node.get_graph()
            except Exception as error:
                if ignore_if_missing:
                    return True
                raise og.OmniGraphError(f"Could not find node {node} to delete") from error
            node_path = omnigraph_node.get_prim_path()
            if undoable:
                (status, _) = cmds.DeleteNode(graph=nodes_graph, node_path=node_path, modify_usd=update_usd)
            else:
                cmds.imm.DeleteNode(graph=nodes_graph, node_path=node_path, modify_usd=update_usd)
                status = True
            return status

        if isinstance(node_id, list):
            return all(__delete_one_node(node) for node in node_id)
        return __delete_one_node(node_id)

    # --------------------------------------------------------------------------------------------------------------
    ExposePrimNode_t = Tuple[Prim_t, NewNode_t]
    """Typing for information required to expose a prim in a node"""
    ExposePrimNodes_t = Union[ExposePrimNode_t, List[ExposePrimNode_t]]
    """Typing for information required to expose a list of prims in nodes"""

    class PrimExposureType(Enum):
        """Value that specifies the method of exposing USD prims to OmniGraph"""

        AS_ATTRIBUTES = "attributes"
        """Expose the prim via a node that creates outputs for all of the prim's attributes"""
        AS_BUNDLE = "bundle"
        """Expose the prim via a node that creates a single output bundle with all of the prim's attributes"""
        AS_WRITABLE = "writable"
        """Expose the prim to be written to via a node that creates inputs for the prim's attributes"""

    PrimExposureType_t = Union[str, PrimExposureType]
    """Flexible type to specify how to expose the prim"""

    @classmethod
    def node_type_to_expose(cls, exposure_type: PrimExposureType_t) -> str:
        """Returns the type of node that will be used to expose the prim for a given exposure type

        Args:
            exposure_type: Type of exposure desired

        Returns:
            str: Node type of the appropriate omni.graph.core.Node to use to expose the prim
        """
        if exposure_type in [cls.PrimExposureType.AS_ATTRIBUTES, cls.PrimExposureType.AS_ATTRIBUTES.value]:
            return "omni.graph.nodes.ReadPrimAttributes"
        if exposure_type in [cls.PrimExposureType.AS_BUNDLE, cls.PrimExposureType.AS_BUNDLE.value]:
            return "omni.graph.nodes.ExtractPrim"
        assert exposure_type in [cls.PrimExposureType.AS_WRITABLE, cls.PrimExposureType.AS_WRITABLE.value]
        return "omni.graph.nodes.WritePrim"

    @classmethod
    def exposed_attribute_name(cls, exposure_type: PrimExposureType_t) -> str:
        """Returns the name of the attribute that will be used to expose the prim for a given exposure type

        Args:
            exposure_type: Type of exposure desired

        Returns:
            str: Name of the attribute at which a connection should be made to the prim for exposure
        """
        if exposure_type in [cls.PrimExposureType.AS_BUNDLE, cls.PrimExposureType.AS_BUNDLE.value]:
            return "inputs:prims"
        return "inputs:prim"

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def expose_prim(obj, *args, **kwargs) -> og.Node:  # noqa: N804,PLC0202,PLE0202
        """Create a new compute node attached to an ordinary USD prim or list of prims.

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. All others are by keyword and optional, defaulting to the value
        set in the constructor in the object context and the function defaults in the class context.

        Args:
            obj: Either cls or self depending on how the function was called
            exposure_type: Method for exposing the prim to OmniGraph
            prim_id: Identifier of an existing prim in the USD stage
            node_path_id: Identifier of a node path that is valid but does not currently exist
            update_usd: If specified then override whether to delete the node's USD backing (default True)
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
                      (default True)

        Returns:
            omni.graph.core.Node: Node exposing the prim to OmniGraph

        Raises:
            og.OmniGraphError: if the prim does not exist, or the node path already exists
        """
        return obj.__expose_prim(obj, args=args, kwargs=kwargs)

    def __expose_prim_obj(self, *args, **kwargs) -> og.Graph:
        """Implements :py:meth:`.GraphController.expose_prim` when called as an object method"""
        return self.__expose_prim(
            self, update_usd=self.__update_usd, undoable=self.__undoable, args=args, kwargs=kwargs
        )

    @staticmethod
    def __expose_prim(
        obj,
        exposure_type: PrimExposureType_t = _Unspecified,
        prim_id: Prim_t = _Unspecified,
        node_path_id: NewNode_t = _Unspecified,
        update_usd: bool = True,
        undoable: bool = True,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ) -> og.Node:
        """Implements :py:meth:`.GraphController.expose_prim`"""
        (exposure_type, prim_id, node_path_id, update_usd, undoable) = _flatten_arguments(
            mandatory=[("exposure_type", exposure_type), ("prim_id", prim_id), ("node_path_id", node_path_id)],
            optional=[("update_usd", update_usd), ("undoable", undoable)],
            args=args,
            kwargs=kwargs,
        )
        _ = DBG and log_info(
            f"Expose prim using exposure_type={exposure_type}, prim_id={prim_id}, node_path={node_path_id}"
            f", update_usd={update_usd}, undoable={undoable}"
        )

        node_type = obj.node_type_to_expose(exposure_type)
        attribute_name = obj.exposed_attribute_name(exposure_type)

        prim = og.ObjectLookup.prim(prim_id)
        if not prim.IsValid():
            raise og.OmniGraphError(f"Could not expose an invalid prim '{prim_id}'")
        node_path = og.ObjectLookup.node_path(node_path_id)
        new_nodes = [
            obj.create_node(node_path, node_type, allow_exists=False, update_usd=update_usd, undoable=undoable)
        ]
        stage = omni.usd.get_context().get_stage()

        # Create Read Prims for exposure type as bundle
        if exposure_type in [obj.PrimExposureType.AS_BUNDLE, obj.PrimExposureType.AS_BUNDLE.value]:
            next_node_path = omni.usd.get_stage_next_free_path(stage, node_path, False)
            new_node = obj.create_node(
                next_node_path, "omni.graph.nodes.ReadPrims", update_usd=update_usd, undoable=undoable
            )
            new_nodes.insert(0, new_node)

            # Set inputs:primPath attribute
            prim_path_attribute = og.ObjectLookup.attribute("inputs:primPath", new_nodes[1])
            attr = stage.GetAttributeAtPath(str(prim_path_attribute.get_path()))
            attr.Set(str(prim.GetPath()))

        # Give the USD scene time to update
        asyncio.ensure_future(omni.kit.app.get_app().next_update_async())

        # The commented-out lines are what the commands should be, except that at the moment the ConnectPrim command
        # is not working with the new prim configuration. Once that is fixed these lines can be restored and we won't
        # have to go to the USD commands for this function.
        # prim_attribute = og.ObjectLookup.attribute("inputs:prim", new_node)
        # cmds.ConnectPrim(attr=prim_attribute, prim_path=str(prim.GetPrimPath()), is_bundle_connection=True)
        if undoable:
            omni.kit.commands.execute(
                "AddRelationshipTarget",
                relationship=stage.GetPropertyAtPath(f"{new_nodes[0].get_prim_path()}.{attribute_name}"),
                target=prim.GetPath(),
            )
        else:
            omni.kit.commands.create(
                "AddRelationshipTarget",
                relationship=stage.GetPropertyAtPath(f"{new_nodes[0].get_prim_path()}.{attribute_name}"),
                target=prim.GetPath(),
            ).do()

        # Connect output of Read Prim -> Extract Bundle for bundle exposure
        if exposure_type in [obj.PrimExposureType.AS_BUNDLE, obj.PrimExposureType.AS_BUNDLE.value]:
            read_prims_node = new_nodes[0]
            extract_prim_node = new_nodes[1]

            og.Controller.edit(
                read_prims_node.get_graph().get_path_to_graph(),
                {
                    og.Controller.Keys.CONNECT: (
                        f"{read_prims_node.get_prim_path()}.outputs_primsBundle",
                        f"{extract_prim_node.get_prim_path()}.inputs:prims",
                    )
                },
            )

        return new_nodes[-1]

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def __decode_connection_point(cls, port_spec: AttributeSpec_t) -> Union[str, og.Attribute]:  # noqa: PLW0238
        """Decipher the connection point to figure out where the connection/disconnection should happen

        Args:
            port_spec: Location for the connection. It can be an omni.graph.core.Attribute when a real
                       physical connection is to be made in OmniGraph, or a string that references an object when the
                       connection is being made to a path attribute, which can connect to any object in the USD stage
                       by name.

        Returns:
            str | omni.graph.core.Attribute: If an Attribute could be deciphered from the port_spec then returns that,
                else returns a string pointing to the object passed in, if possible.
        """
        try:
            # If the attribute was found then just return it directly
            attribute = ObjectLookup.attribute(port_spec)
            return attribute
        except og.OmniGraphError:
            return ObjectLookup.attribute_path(port_spec)

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def connect(obj, *args, **kwargs):  # noqa: N804,PLC0202,PLE0202
        """Create a connection between two attributes

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. All others are by keyword and optional, defaulting to the value
        set in the constructor in the object context and the function defaults in the class context.

        Args:
            obj: Either cls or self depending on how the function was called
            src_spec: Specification of the attribute to be the source end of the connection
            dst_spec: Specification of the attribute to be the destination end of the connection
            update_usd: If specified then override whether to delete the node's USD backing (default True)
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
                      (default True)

        Raises:
            OmniGraphError: If attributes could not be found or the connection fails
        """
        obj.__connect(obj, args=args, kwargs=kwargs)

    def __connect_obj(self, *args, **kwargs):
        """Implements :py:meth:`.GraphController.connect` when called as an object method"""
        self.__connect(self, update_usd=self.__update_usd, undoable=self.__undoable, args=args, kwargs=kwargs)

    @staticmethod
    def __connect(
        obj,
        src_spec: AttributeSpec_t = _Unspecified,
        dst_spec: AttributeSpec_t = _Unspecified,
        update_usd: bool = True,
        undoable: bool = True,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ):
        """Implement :py:meth:`.GraphController.connect`"""
        (src_spec, dst_spec, update_usd, undoable) = _flatten_arguments(
            mandatory=[("src_spec", src_spec), ("dst_spec", dst_spec)],
            optional=[("update_usd", update_usd), ("undoable", undoable)],
            args=args,
            kwargs=kwargs,
        )
        connection_msg = f"`{src_spec}` -> `{dst_spec}`"
        _ = DBG and log_info(f"Connect {connection_msg}")

        src_location = obj.__decode_connection_point(src_spec)  # noqa: PLW0212
        src_path = src_location if isinstance(src_location, str) else src_location.get_path()
        dst_location = obj.__decode_connection_point(dst_spec)  # noqa: PLW0212
        dst_path = dst_location if isinstance(dst_location, str) else dst_location.get_path()

        if isinstance(src_location, str) and isinstance(dst_location, str):
            raise og.OmniGraphError(f"At least one end of the connection must be an attribute - {connection_msg}")

        _ = DBG and log_info(f"   Connect Attr {src_path} to {dst_path}")
        try:
            if isinstance(src_location, str):
                dst_type = dst_location.get_resolved_type()
                if dst_type.role != og.AttributeRole.PATH:
                    raise og.OmniGraphError(
                        f"Parsed source '{src_location}' as a path attribute, which cannot connect to a"
                        f" destination of type {dst_type}"
                    )
                # TODO: Create callback so that the path attribute gets updated when its target is renamed
                cmds.SetAttr(attr=dst_location, value=src_location)
            elif isinstance(dst_location, str):
                src_type = src_location.get_resolved_type()
                if src_type.role != og.AttributeRole.PATH:
                    raise og.OmniGraphError(
                        f"Parsed destination '{dst_location}' as a path attribute, which cannot connect to a"
                        f" source of type {src_type}"
                    )
                # TODO: Create callback so that the path attribute gets updated when its target is renamed
                cmds.SetAttr(attr=src_location, value=dst_location)
            else:
                if undoable:
                    (success, _) = cmds.ConnectAttrs(
                        src_attr=src_location, dest_attr=dst_location, modify_usd=update_usd
                    )
                else:
                    success = cmds.imm.ConnectAttrs(
                        src_attr=src_location, dest_attr=dst_location, modify_usd=update_usd
                    )
                if not success:
                    raise og.OmniGraphError(f"Failed to connect '{src_location}' to '{dst_location}'")
        except og.OmniGraphError as error:
            raise og.OmniGraphError(f"Failed to connect {src_path} -> {dst_path}") from error

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def disconnect(obj, *args, **kwargs):  # noqa: N804,PLC0202,PLE0202
        """Break a connection between two attributes

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. All others are by keyword and optional, defaulting to the value
        set in the constructor in the object context and the function defaults in the class context.

        Args:
            obj: Either cls or self depending on how the function was called
            src_spec: Specification of the attribute that is the source end of the connection
            dst_spec: Specification of the attribute that is the destination end of the connection
            update_usd: If specified then override whether to delete the node's USD backing (default True)
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
                      (default True)

        Raises:
            OmniGraphError: If attributes could not be found or the disconnection fails
        """
        return obj.__disconnect(obj, args=args, kwargs=kwargs)

    def __disconnect_obj(self, *args, **kwargs):
        """Implements :py:meth:`.GraphController.disconnect` when called as an object method"""
        return self.__disconnect(self, update_usd=self.__update_usd, undoable=self.__undoable, args=args, kwargs=kwargs)

    @staticmethod
    def __disconnect(
        obj,
        src_spec: AttributeSpec_t = _Unspecified,
        dst_spec: AttributeSpec_t = _Unspecified,
        update_usd: bool = True,
        undoable: bool = True,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ):
        """Implement :py:meth:`.GraphController.disconnect`"""
        (src_spec, dst_spec, update_usd, undoable) = _flatten_arguments(
            mandatory=[("src_spec", src_spec), ("dst_spec", dst_spec)],
            optional=[("update_usd", update_usd), ("undoable", undoable)],
            args=args,
            kwargs=kwargs,
        )
        _ = DBG and log_info(f"Disconnect `{src_spec}` -> `{dst_spec}`")
        success = False

        src_location = obj.__decode_connection_point(src_spec)  # noqa: PLW0212
        src_path = src_location if isinstance(src_location, str) else src_location.get_path()
        dst_location = obj.__decode_connection_point(dst_spec)  # noqa: PLW0212
        dst_path = dst_location if isinstance(dst_location, str) else dst_location.get_path()

        if isinstance(src_location, str) and isinstance(dst_location, str):
            raise og.OmniGraphError(
                f"At least one end of the disconnection must be an attribute - '{src_location}' -> '{dst_location}'"
            )

        _ = DBG and log_info(f"   Disconnect Attr {src_path} to {dst_path}")
        try:
            if isinstance(src_location, str):
                dst_type = dst_location.get_resolved_type()
                if dst_type.role != og.AttributeRole.PATH:
                    raise og.OmniGraphError(
                        f"Parsed source '{src_location}' as a path attribute, which cannot disconnect from a"
                        f" destination of type {dst_type}"
                    )
                # TODO: Remove callback on path attributes
            elif isinstance(dst_location, str):
                src_type = src_location.get_resolved_type()
                if src_type.role != og.AttributeRole.PATH:
                    raise og.OmniGraphError(
                        f"Parsed destination '{dst_location}' as a path attribute, which cannot disconnect from a"
                        f" destination of type {src_type}"
                    )
                # TODO: Remove callback on path attributes
            elif undoable:
                if not cmds.DisconnectAttrs(src_attr=src_location, dest_attr=dst_location, modify_usd=update_usd)[0]:
                    raise og.OmniGraphError
            elif not cmds.imm.DisconnectAttrs(src_attr=src_location, dest_attr=dst_location, modify_usd=update_usd):
                raise og.OmniGraphError
        except og.OmniGraphError as error:
            if not success:
                raise og.OmniGraphError(f"Failed to disconnect {src_path} -> {dst_path}") from error

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def disconnect_all(obj, *args, **kwargs):  # noqa: N804,PLC0202,PLE0202
        """Break all connections to and from an attribute

        This function can be called either from the class or using an instantiated object. The first argument is
        positional, being either the class or object. All others are by keyword and optional, defaulting to the value
        set in the constructor in the object context and the function defaults in the class context.

        Args:
            obj: Either cls or self depending on how the function was called
            attribute_spec: Attribute whose connections are to be removed. (attr or (attr, node) pair)
            update_usd: If specified then override whether to delete the node's USD backing (default True)
            undoable: If True the operation is added to the undo queue, else it is done immediately and forgotten
                      (default True)

        Raises:
            OmniGraphError: If attribute could not be found, connection didn't exist, or disconnection fails
        """
        return obj.__disconnect_all(obj, args=args, kwargs=kwargs)

    def __disconnect_all_obj(self, *args, **kwargs):
        """Implements :py:meth:`.GraphController.disconnect_all` when called as an object method"""
        return self.__disconnect_all(
            self, update_usd=self.__update_usd, undoable=self.__undoable, args=args, kwargs=kwargs
        )

    @staticmethod
    def __disconnect_all(
        obj,
        attribute_spec: AttributeSpec_t = _Unspecified,
        update_usd: bool = True,
        undoable: bool = True,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
    ):
        """Implements :py:meth:`.GraphController.disconnect_all`"""
        (attribute_spec, update_usd, undoable) = _flatten_arguments(
            mandatory=[("attribute_spec", attribute_spec)],
            optional=[("update_usd", update_usd), ("undoable", undoable)],
            args=args,
            kwargs=kwargs,
        )
        _ = DBG and (f"Disconnect all from {attribute_spec}")

        if isinstance(attribute_spec, tuple):
            attribute = ObjectLookup.attribute(*attribute_spec)
        else:
            attribute = ObjectLookup.attribute(attribute_spec)

        if undoable:
            (success, _) = cmds.DisconnectAllAttrs(attr=attribute, modify_usd=update_usd)
        else:
            success = cmds.imm.DisconnectAllAttrs(attr=attribute, modify_usd=update_usd)
        # TODO: Also remove the callbacks if the attribute was a path attribute
        if not success:
            raise og.OmniGraphError(f"Failed to break connections on `{attribute_spec}`")

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def set_variable_default_value(cls, variable_id: Variable_t, value):
        """Sets the default value of a variable object.

        Args:
            variable_id: The variable whose value is to be set
            value: The value to set

        Raises:
            OmniGraphError: If the variable is not valid, does not have valid usd backing, or value
            is not a compatible type
        """
        _ = DBG and (f"Set variable {variable_id} to {value}")

        variable = ObjectLookup.variable(variable_id)
        stage = omni.usd.get_context().get_stage()

        if variable.is_backed_by_usd:
            attr = stage.GetAttributeAtPath(variable.source_path)
            if not attr:
                raise og.OmniGraphError(f"Variable {variable.name} does not have a valid backing attribute")

            try:
                attr.Set(value)
            except Tf.ErrorException as error:
                raise og.OmniGraphError(
                    f"Variable {variable.name} type is not compatible with {type(value)}"
                ) from error

            # if FSD is enabled, changes need to be flushed immediately
            og._internal.flush_usd()  # noqa PLW0212

        else:
            # The runtime variables are not backed by USD,
            # hence we must set the value directly on the variable
            prim_path = Sdf.Path(variable.source_path).GetPrimPath()
            try:
                graph = og.Controller.graph(stage.GetPrimAtPath(prim_path))
            except og.OmniGraphError as error:
                raise og.OmniGraphError(
                    f"Variable {variable.name} is not backed by a valid graph at path {prim_path}."
                ) from error
            context = graph.get_default_graph_context()
            variable.set(context, value)

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def get_variable_default_value(cls, variable_id: Variable_t) -> Any:
        """Gets the default value of the given variable

        Args:
            variable_id: The variable whose value is to be set

        Returns:
            Any: The default value of the variable.

        Raises:
            OmniGraphError: If the variable is not valid or does not have valid usd backing.
        """
        _ = DBG and (f"Get variable {variable_id}")

        variable = ObjectLookup.variable(variable_id)
        stage = omni.usd.get_context().get_stage()
        if variable.is_backed_by_usd:
            attr = stage.GetAttributeAtPath(variable.source_path)
            if not attr:
                raise og.OmniGraphError(f"Variable {variable.name} does not have a valid backing attribute")

            return attr.Get()

        # Get the graph owning the variable and get the value from the context
        prim_path = Sdf.Path(variable.source_path).GetPrimPath()
        graph = og.Controller.graph(stage.GetPrimAtPath(prim_path))
        context = graph.get_default_graph_context()
        if variable.type.array_depth > 0:
            return variable.get_array(context)
        return variable.get(context)
