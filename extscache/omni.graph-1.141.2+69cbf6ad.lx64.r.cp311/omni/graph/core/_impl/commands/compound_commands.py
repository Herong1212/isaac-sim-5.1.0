"""Commands related to the creation and modification of Node Types for  Compound Graphs"""

from typing import Dict, List, Optional, Set, Tuple

import carb
import omni.graph.core as og
import omni.graph.core._unstable as ogu
import omni.graph.tools.ogn as ogn
import omni.kit
import omni.kit.commands
import omni.usd
import OmniGraphSchema
from pxr import Sdf

# ==============================================================================================================
# helper routines for the commands

INPUT_PREFIX = "omni:graph:input:"
OUTPUT_PREFIX = "omni:graph:output:"
ATTRIBUTE_INPUT_PREFIX = "inputs:"
ATTRIBUTE_OUTPUT_PREFIX = "outputs:"

TYPE_METADATA_KEY = "omni:graph:type"


# --------------------------------------------------------------------------------------------------------------
def _get_compound_graph(compound_prim: OmniGraphSchema.CompoundNodeType_1) -> og.Graph:
    """Gets the graph object associated with a compound prim"""
    targets = compound_prim.GetOmniGraphAssetRel().GetTargets()
    if not targets or len(targets) == 0:
        raise og.OmniGraphError(f"NodeType does {compound_prim.GetPath()} not have an associated graph prim")
    graph = og.get_graph_by_path(str(targets[0]))
    if graph is None or not graph.is_valid():
        raise og.OmniGraphError(f"Node Type Graph at {targets[0]} not found")
    return graph


# -------------------------------------------------------------------------------------------------------------
def _make_unique(name: str, names: Set[str]) -> str:
    """Given a name, returns a unique name, using the provided set to find duplicates"""
    orig_name = name
    count = 0
    while name in names:
        count = count + 1
        name = f"{orig_name}_{count:02d}"
    names.add(name)
    return name


# ================================================================================================================
class ReplaceWithCompound(omni.kit.commands.Command):
    """Command that replaces a set of nodes in a graph with a new compound graph and compound node"""

    # -------------------------------------------------------------------------
    def __init__(
        self,
        nodes: List[Sdf.Path],
        compound_name: str = "compound",
        graph_name: str = "Graph",
        namespace: Optional[str] = None,
    ):
        self._nodes = nodes
        self._node_type = None
        self._compound_name = compound_name
        self._graph_name = graph_name
        self._applied = False
        self._old_graph_path = Sdf.Path()
        self._new_graph_path = Sdf.Path()
        self._namespace = namespace

    # -------------------------------------------------------------------------
    def do(self):
        """
        Applies the command.

        Returns the path to the new compound node, or an empty path if an error occurs
        """
        if self._applied:
            return Sdf.Path()

        og_nodes = [og.get_node_by_path(str(path)) for path in self._nodes]
        if not self._validate_nodes(og_nodes):
            return Sdf.Path()

        with omni.kit.undo.group():
            # create the node type
            (_, self._node_type) = omni.kit.commands.execute(
                "CreateCompoundNodeType",
                compound_name=self._compound_name,
                graph_name=self._graph_name,
                namespace=self._namespace,
            )
            if not self._node_type:
                return Sdf.Path()

            src_graph = og_nodes[0].get_graph()
            compound_graph = _get_compound_graph(self._node_type)
            self._new_graph_path = Sdf.Path(compound_graph.get_path_to_graph())
            self._old_graph_path = Sdf.Path(og_nodes[0].get_graph().get_path_to_graph())

            # store the existing connections to the nodes on the graph
            (input_connections, output_connections) = self._find_connections(og_nodes)

            # copy the nodes to the new graph
            self._copy_nodes_to_graph(og_nodes, compound_graph)

            node_type_sdf_path = self._node_type.GetPrim().GetPrimPath()

            # create inputs and outputs on the node type
            input_connections = self._calculate_input_names(input_connections)
            for _, dst, in_name in input_connections:
                # remap the old node input to the node
                remap_dst = self._remap_path(dst)
                ogu.cmds.CreateCompoundNodeTypeInput(
                    node_type=node_type_sdf_path, input_name=in_name, attribute_path=remap_dst
                )

            output_connections = self._calculate_output_names(output_connections)
            for src, (name, _) in output_connections.items():
                remap_src = self._remap_path(src)
                ogu.cmds.CreateCompoundNodeTypeOutput(
                    node_type=node_type_sdf_path, output_name=name, attribute_path=remap_src
                )

            # delete the original nodes
            for node_path in self._nodes:
                og.cmds.DeleteNode(graph=src_graph, node_path=str(node_path), modify_usd=True)

            # compute a unique path for the compound node
            stage = omni.usd.get_context().get_stage()
            proposed_path = self._old_graph_path.AppendChild(self._compound_name)
            compound_node_path = Sdf.Path(omni.usd.get_stage_next_free_path(stage, proposed_path, False))

            # create the new compound node
            og.cmds.CreateNode(
                graph=src_graph,
                node_path=str(compound_node_path),
                node_type=str(node_type_sdf_path),
                create_usd=True,
            )

            if not stage.GetPrimAtPath(compound_node_path):
                raise og.OmniGraphError(f"Expected compound prim at {compound_node_path}")

            # reconnect the inputs and outputs
            # TODO -- cache the connection type?
            for src, _dst, in_name in input_connections:
                dest_path = compound_node_path.AppendProperty(ATTRIBUTE_INPUT_PREFIX + in_name)
                og.cmds.ConnectAttrs(
                    src_attr=str(src),
                    dest_attr=str(dest_path),
                    modify_usd=True,
                )

            for _src, (name, dst_list) in output_connections.items():
                for dst in dst_list:
                    src_path = Sdf.Path(compound_node_path).AppendProperty(ATTRIBUTE_OUTPUT_PREFIX + name)
                    og.cmds.ConnectAttrs(
                        src_attr=str(src_path),
                        dest_attr=str(dst),
                        modify_usd=True,
                    )

        self._applied = True

        return compound_node_path

    # -------------------------------------------------------------------------
    def undo(self):
        self._applied = False

    # -------------------------------------------------------------------------
    def _remap_path(self, path: Sdf.Path):
        if self._new_graph_path == Sdf.Path():
            raise og.OmniGraphError("Graph paths have not been set yet")

        return path.MakeRelativePath(self._old_graph_path).MakeAbsolutePath(self._new_graph_path)

    # -------------------------------------------------------------------------
    def _copy_nodes_to_graph(self, nodes: List[og.Node], graph: og.Graph):
        """
        Copies nodes from one graph to another, including links between nodes

        """
        stage = omni.usd.get_context().get_stage()
        graph_path = graph.get_path_to_graph()
        new_node_paths = set()

        with Sdf.ChangeBlock():
            for node in nodes:
                old_graph_path = Sdf.Path(node.get_graph().get_path_to_graph())
                old_node_path = Sdf.Path(node.get_prim_path())
                new_node_path = old_node_path.MakeRelativePath(old_graph_path).MakeAbsolutePath(graph_path)
                omni.kit.commands.execute(
                    "CopyPrim", path_from=old_node_path, path_to=new_node_path, exclusive_select=False
                )
                new_node_paths.add(new_node_path)

        # remove existing connections and replace with new connections, if they exist
        with Sdf.ChangeBlock():
            for node_path in new_node_paths:
                prim = stage.GetPrimAtPath(node_path)
                for attr in prim.GetAttributes():
                    name = str(attr.GetName())
                    if name.startswith(ATTRIBUTE_INPUT_PREFIX) or name.startswith(ATTRIBUTE_OUTPUT_PREFIX):
                        attr.ClearConnections()

        # reload the compound graph so the nodes get created
        graph.reload_from_stage()

        # reattach the connections
        with Sdf.ChangeBlock():
            # walk the old node list, and create inter connections where needed
            for node in nodes:
                old_graph_path = Sdf.Path(node.get_graph().get_path_to_graph())
                old_node_path = Sdf.Path(node.get_prim_path())
                new_node_path = old_node_path.MakeRelativePath(old_graph_path).MakeAbsolutePath(graph_path)

                for attr in node.get_attributes():
                    port_type = attr.get_port_type()
                    if port_type in [
                        og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
                        og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT,
                    ]:
                        for con_info in attr.get_upstream_connections_info():
                            (up, con_type) = (con_info.attr, con_info.connection_type)
                            up_path = (
                                Sdf.Path(up.get_path()).MakeRelativePath(old_graph_path).MakeAbsolutePath(graph_path)
                            )
                            up_node = up_path.GetPrimPath()

                            # Either it's connected to the new node, or connected to something in the nodes subgraph
                            if up_node in new_node_paths or up_node.HasPrefix(new_node_path):
                                output_path = up_path
                                input_path = (
                                    Sdf.Path(attr.get_path())
                                    .MakeRelativePath(old_graph_path)
                                    .MakeAbsolutePath(graph_path)
                                )
                                og.cmds.ConnectAttrs(
                                    src_attr=str(output_path),
                                    dest_attr=str(input_path),
                                    modify_usd=True,
                                    connection_type=con_type,
                                )

        return new_node_paths

    # -------------------------------------------------------------------------
    def _validate_nodes(self, nodes: List[og.Node]) -> bool:
        """Validates the nodes all belong to the same graph"""
        if len(nodes) == 0:
            return False

        graph = nodes[0].get_graph()
        for node in nodes[1:]:
            if node.get_graph() != graph:
                carb.log_error("Could not create a compound, not all nodes belong to the same graph")
                return False
        return True

    # -------------------------------------------------------------------------
    def _calculate_input_names(self, inputs: List[Tuple[Sdf.Path, Sdf.Path]]) -> List[Tuple[Sdf.Path, Sdf.Path, str]]:
        """Given the set of input connections calculate and append the name of the compound input"""
        names = set()
        result = []
        for out_path, in_path in inputs:
            name = str(in_path.name)
            if name.startswith(ATTRIBUTE_INPUT_PREFIX):
                name = name[len(ATTRIBUTE_INPUT_PREFIX) :]
            name = _make_unique(name, names)
            result.append((out_path, in_path, name))

        return result

    # -------------------------------------------------------------------------
    def _calculate_output_names(
        self, outputs: List[Tuple[Sdf.Path, Sdf.Path]]
    ) -> Dict[Sdf.Path, Tuple[str, List[Sdf.Path]]]:
        """Given the set of output connections calculate the names. Since outputs can have multiple input connections
        Reorders the data struct map an output -> name, input
        """

        names = set()
        result = {}
        for src, dest in outputs:
            if src in result:
                (name, result_list) = result[src]
                result_list.append(dest)
                result[src] = (name, result_list)
            else:
                name = str(src.name)
                if name.startswith(ATTRIBUTE_OUTPUT_PREFIX):
                    name = name[len(ATTRIBUTE_OUTPUT_PREFIX) :]
                if name.startswith(ATTRIBUTE_INPUT_PREFIX):
                    name = name[len(ATTRIBUTE_INPUT_PREFIX) :]
                name = _make_unique(name, names)
                result[src] = (name, [dest])

        return result

    # -------------------------------------------------------------------------
    def _find_connections(
        self, nodes: List[og.Node]
    ) -> Tuple[List[Tuple[Sdf.Path, Sdf.Path]], List[Tuple[Sdf.Path, Sdf.Path]]]:
        """Finds the input and output connections from a subset of nodes that are connected externally to the list"""

        node_path_set = {Sdf.Path(node.get_prim_path()) for node in nodes}
        inputs = []
        outputs = []

        for node in nodes:  # noqa: PLR1702
            for attr in node.get_attributes():
                port_type = attr.get_port_type()

                if port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
                    for up in attr.get_upstream_connections():
                        src_path = Sdf.Path(up.get_path())
                        dest_path = Sdf.Path(attr.get_path())
                        if src_path.GetPrimPath() not in node_path_set:
                            inputs.append((src_path, dest_path))

                    # special case for constant nodes, which are technically inputs
                    for down in attr.get_downstream_connections():
                        if down.get_metadata(ogn.MetadataKeys.OUTPUT_ONLY) == "1":
                            src_path = Sdf.Path(attr.get_path())
                            dest_path = Sdf.Path(down.get_path())
                            if dest_path.GetPrimPath() not in node_path_set:
                                outputs.append((src_path, dest_path))

                elif port_type == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT:
                    for down in attr.get_downstream_connections():
                        src_path = Sdf.Path(attr.get_path())
                        dest_path = Sdf.Path(down.get_path())
                        if dest_path.GetPrimPath() not in node_path_set:
                            outputs.append((src_path, dest_path))

        return (inputs, outputs)
