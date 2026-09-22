# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import json
import posixpath
import re
from contextlib import contextmanager
from functools import namedtuple, update_wrapper, wraps
from math import gcd
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple, Union

import carb
import numpy as np
import omni.graph.core as og
import omni.kit.async_engine
import omni.usd
import pxr
import usdrt
from omni.syntheticdata.scripts.SyntheticData import SyntheticData
from pxr import Gf, Sdf, Semantics, Tf, Usd, UsdGeom, UsdSemantics, UsdShade

from . import viewport_manager as vp_manager

AttrMap = namedtuple("AttrMap", ["upstream", "downstream"])

# SDG_GRAPH = "/Render/PostProcess/SDGPipeline"
REPLICATOR_SCOPE = "/Replicator"
GRAPH_PATH = f"{REPLICATOR_SCOPE}/SDGPipeline"
ATTRIBUTE_MAPPINGS = {
    AttrMap("outputs:execOut", "inputs:execIn"),
    AttrMap("outputs:exec", "inputs:execIn"),
    AttrMap("outputs:execOut", "inputs:exec"),
    AttrMap("outputs_prims", "inputs:prims"),
    AttrMap("outputs_prim", "inputs:prims"),
    AttrMap("outputs:prim", "inputs:prims"),
    AttrMap("outputs:pressed", "inputs:execIn"),  # HACK to re-use keyboardinput node
    AttrMap("outputs_samples", "inputs:values"),
    AttrMap("outputs:samples", "inputs:values"),
    AttrMap("outputs_primsBundle", "inputs:prims"),
}


def _remove_prim_spec(layer: Sdf.Layer, prim_spec_path: str):
    """Removes prim spec from layer."""
    prim_spec = layer.GetPrimAtPath(prim_spec_path)
    if not prim_spec:
        return False

    if prim_spec.nameParent:
        name_parent = prim_spec.nameParent
    else:
        name_parent = layer.pseudoRoot

    if not name_parent:
        return False

    name = prim_spec.name
    if name in name_parent.nameChildren:
        del name_parent.nameChildren[name]
    return True


@contextmanager
def new_layer(name: str = None):
    """Create a new authoring layer context.
    Use ``new_layer`` to keep replicator changes into a contained layer. If a layer of the same name already exists,
    the layer will be cleared before new changes are applied.

    Args:
        name: Name of the layer to be created. If ommitted, the name "Replicator" is used.

    Example:
        >>> import omni.replicator.core as rep
        >>> with rep.new_layer():
        >>>     rep.create.cone(count=100, position=rep.distribution.uniform((-100,-100,-100),(100,100,100)))
    """
    stage = omni.usd.get_context().get_stage()
    cur_authoring_layer = stage.GetEditTarget()
    try:
        if name is None:
            name = "Replicator"
        vp_manager.destroy_hydra_textures(name)
        vp_manager._set_context(name)
        replicator_layer = None
        for layer in stage.GetLayerStack():
            if layer.GetDisplayName() == name:
                replicator_layer = layer
                break

        if replicator_layer is None:
            root = stage.GetRootLayer()
            replicator_layer = Sdf.Layer.CreateAnonymous(tag=name)
            root.subLayerPaths.append(replicator_layer.identifier)
        else:
            syntheticdata_instance = SyntheticData.Get()
            if syntheticdata_instance is None:
                SyntheticData.Initialize()
                syntheticdata_instance = SyntheticData.Get()
            # WAR to delete session layer deltas (ie. camera)
            _remove_prim_spec(stage.GetSessionLayer(), "/Replicator")
            # Remove synthetic data graphs
            # Reset SyntheticData
            SyntheticData.Get().reset()
            _remove_prim_spec(stage.GetSessionLayer(), "/Render/PostProcess")
            _remove_prim_spec(stage.GetRootLayer(), "/Render/PostProcess")
            # WAR to delete deltas added to root layer
            _remove_prim_spec(stage.GetRootLayer(), "/Replicator")
            replicator_layer.Clear()

        omni.usd.set_edit_target_by_identifier(stage, replicator_layer.identifier)
        yield replicator_layer
    except Exception as e:
        carb.log_warn(e)

    finally:
        stage.SetEditTarget(cur_authoring_layer)
        vp_manager._clear_context()


def singleton(class_):
    """
    A singleton decorator.
    """
    instances = {}

    @wraps(class_)
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


def get_replicator_graph_exists() -> bool:
    controller = og.Controller()
    if bool(controller.graph(GRAPH_PATH)):
        return True

    stage = omni.usd.get_context().get_stage()
    if not stage:
        return False
    render_prim = stage.GetPrimAtPath("/Render")
    if not render_prim.IsValid():
        return False
    for p in Usd.PrimRange(render_prim):
        if p.GetName() == "SDGPipeline":
            return True
    return False


def get_graph(graph_path: str = None, is_hidden: bool = False):
    """Get or create the replicator graph

    Retrieve a graph at specified path. If no graph exists, an execution (aka action) graph
    in the ``SIMULATION`` stage is created. If no ``graph_path`` is specified, use ``/Replicator/SDGPipeline``.

    Args:
        graph_path: Path to which graph is created.
        is_hidden: If ``True``, hide created graph in Stage panel. Ignored if graph already exists.
    """
    stage = omni.usd.get_context().get_stage()
    if stage is None:
        return None

    if graph_path is None:
        graph_path = GRAPH_PATH
        if not stage.GetPrimAtPath(REPLICATOR_SCOPE):
            stage.DefinePrim(REPLICATOR_SCOPE, "Scope")

    controller = og.Controller()

    if not controller.graph(graph_path):
        stage.RemovePrim(graph_path)  # If layer is cleared, graph somehow remains
        graph = controller.create_graph(
            {
                "graph_path": graph_path,
                "evaluator_name": "execution",
                "pipeline_stage": og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_SIMULATION,
            }
        )
        if is_hidden:
            stage.GetPrimAtPath(graph_path).SetMetadata("hide_in_stage_window", 1)
        return graph
    else:
        return controller.graph(graph_path)


def create_node(node_type_id: str, graph: omni.graph.core.Graph = None, node_name=None, input_prims=None, **kwargs):
    """Helper function to create a replicator node of type `node_type_id`

    Args:
        node_type_id: Node type ID
        graph: Optionally specify the graph onto which to create node
        kwargs: Node attributes can optionally be set by specifying them as kwargs
    """
    stage = omni.usd.get_context().get_stage()
    controller = og.Controller()
    if graph is None:
        graph = get_graph()
    graph_path = graph.get_path_to_graph()
    if node_name is not None:
        node_name = Tf.MakeValidIdentifier(node_name)
    else:
        node_name = node_type_id.split(".")[-1]

    node_path = omni.usd.get_stage_next_free_path(stage, f"{graph_path}/{node_name}", False)

    try:
        controller.node(node_path).get_graph().destroy_node(
            node_path, True
        )  # If layer is cleared, node somehow remains
    except og.OmniGraphError:
        pass
    node = controller.create_node((node_path.split("/")[-1], graph), node_type_id)

    for attribute, value in kwargs.items():
        if value is None:
            continue
        if isinstance(value, ReplicatorItem):
            _setup_random_attribute(write_node=node, input_name=attribute, attribute_value=value, do_count=False)
        else:
            if not isinstance(value, list) and "[]" in node.get_attribute(f"inputs:{attribute}").get_type_name():
                value = list([value])
            attr = node.get_attribute(f"inputs:{attribute}")
            if attr.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
                # TODO HANDLE ALL CASES
                if isinstance(value, list):
                    for i in range(len(value)):
                        if isinstance(value[i], Sdf.Path):
                            value[i] = str(value[i])
                elif isinstance(value, Sdf.Path):
                    value = str(value)
                # Resolve type based on value
                attr.set_resolved_type(get_graph_type(value))
            og.AttributeValueHelper(attr).set(value, update_usd=True)
            # node.get_attribute(f"inputs:{attribute}").set(value)

    return node


def _disconnect(attribute):
    upstream_conns = attribute.get_upstream_connections()
    if upstream_conns:
        for conn in upstream_conns:
            conn.disconnect(attribute, True)


def auto_connect(upstream_node, downstream_node, mapping=None, no_exec=False):
    """Connect downsteam node attributes to matching upstream node attributes

    Args:
        upstream_node: Upstream node
        downstream_node: Downstream node
    """
    # Get input names for matching with upstream node
    if upstream_node is None or downstream_node is None:
        return

    downstream_inputs = []
    for attr in downstream_node.get_attributes():
        if attr.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT or attr.get_name()[:7] != "inputs:":
            continue
        if no_exec and attr.get_resolved_type().get_role_name() == "execution":
            continue
        downstream_inputs.append(attr.get_name()[7:])

    # Connect based on same attribute name
    for downstream_input in downstream_inputs:
        if upstream_node.get_attribute_exists(f"outputs:{downstream_input}"):
            _disconnect(downstream_node.get_attribute(f"inputs:{downstream_input}"))
            downstream_attr = downstream_node.get_attribute(f"inputs:{downstream_input}")
            upstream_node.get_attribute(f"outputs:{downstream_input}").connect(downstream_attr, True)

    # Connect based on default mappings
    for m in ATTRIBUTE_MAPPINGS:
        if upstream_node.get_attribute_exists(m.upstream) and downstream_node.get_attribute_exists(m.downstream):
            if no_exec and upstream_node.get_attribute(m.upstream).get_resolved_type().get_role_name() == "execution":
                continue
            _disconnect(downstream_node.get_attribute(m.downstream))
            upstream_node.get_attribute(m.upstream).connect(downstream_node.get_attribute(m.downstream), True)

    # Connect based on mappings
    if mapping is not None:
        for m in mapping:
            if upstream_node.get_attribute_exists(m.upstream) and downstream_node.get_attribute_exists(m.downstream):
                if (
                    no_exec
                    and upstream_node.get_attribute(m.upstream).get_resolved_type().get_role_name() == "execution"
                ):
                    continue
                _disconnect(downstream_node.get_attribute(m.downstream))
                upstream_node.get_attribute(m.upstream).connect(downstream_node.get_attribute(m.downstream), True)
    # Special case: ReadPrim
    if upstream_node.get_type_name() == "omni.graph.nodes.ReadPrim" and downstream_node.get_attribute_exists(
        "inputs:prims"
    ):
        targets = upstream_node.get_attribute("inputs:prims").get()
        set_target_prims(downstream_node, "inputs:prims", targets)


def is_execution_node(node, on_input_only=False):
    """Returns True if node is an execution node.

    Execution status is determined by traversing through the node's attributes and verifying each attribute's role.

    Args:
        node: Node to investigate
        on_input_only: If ``True``, only look at the node's input attributes
    """
    if node is None:
        return False
    for attribute in node.get_attributes():
        if on_input_only and attribute.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
            continue
        if attribute.get_resolved_type().get_role_name() == "execution":
            return True
    return False


def get_exec_attr(node, on_input: bool):
    if node is None:
        return None
    port_type = (
        og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT if on_input else og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT
    )
    for attribute in node.get_attributes():
        if attribute.get_port_type() != port_type:
            continue
        if attribute.get_resolved_type().get_role_name() == "execution":
            return attribute
    return None


def _get_first_upstream_exec_nodes(node):
    """Return the first exec nodes in a subgraph traveling upstream from `node`"""
    first_execs = []
    subgraph = [node]
    while subgraph:
        cur_node = subgraph.pop(0)
        output_exec = get_exec_attr(cur_node, on_input=False)
        if output_exec:
            first_execs.append(cur_node)
        else:
            for attribute in cur_node.get_attributes():
                is_input = attribute.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
                if is_input and attribute.get_upstream_connection_count():
                    subgraph += [a.get_node() for a in attribute.get_upstream_connections()]

    return first_execs


def _get_first_exec_attr(node):
    """Return the first exec attribute in a subgraph traveling upstream from `node`

    Note: Assumes a single execution attribute exists on each node's inputs
    """
    if node is None:
        return
    first_exec = None
    subgraph = [node]
    while subgraph:
        cur_node = subgraph.pop(0)
        node_exec_inputs = []
        for attribute in cur_node.get_attributes():
            is_input = attribute.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT
            is_exec = attribute.get_resolved_type().get_role_name() == "execution"
            if is_input and is_exec:
                node_exec_inputs.append(attribute)

        if not node_exec_inputs:
            # No upstream exec node, set node's output exec as first exec
            first_exec = get_exec_attr(cur_node, on_input=False)

        for node_exec_input in node_exec_inputs:
            conns = node_exec_input.get_upstream_connections()
            for conn in conns:
                conn_node = conn.get_node()
                # avoid infinite loop if node connects to itself
                if conn_node == cur_node:
                    continue
                # avoid adding node already in subgraph - can cause runtimes to explode
                if conn_node in subgraph:
                    continue
                subgraph.append(conn_node)

    if first_exec is None:
        return get_exec_attr(cur_node, on_input=False)
    return first_exec


def _get_last_exec_attr(node, consider_targets=True):
    """Return the last exec attribute in a subgraph traveling downstream from ``node``"""
    last_exec = get_exec_attr(node, on_input=True)
    subgraph = [node]
    while subgraph:
        cur_node = subgraph.pop(0)
        for attribute in cur_node.get_attributes():
            if attribute.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
                continue
            if attribute.get_resolved_type().get_role_name() == "execution":
                last_exec = attribute
                conns = last_exec.get_downstream_connections()
                for conn in conns:
                    if conn.get_node() != cur_node:  # avoid infinite loop if node connects to itself
                        subgraph.append(conn.get_node())
            elif consider_targets and attribute.get_type_name() == "target":
                conns = attribute.get_downstream_connections()
                for conn in conns:
                    if conn.get_node() != cur_node:  # avoid infinite loop if node connects to itself
                        subgraph.append(conn.get_node())
    return last_exec


def _get_last_exec_attrs(node):
    """Return the last exec attributes in a subgraph traveling downstream from ``node``"""
    last_execs = [get_exec_attr(node, on_input=True)]
    subgraph = [(node, 0)]

    while subgraph:
        cur_node, subgraph_idx = subgraph.pop(0)
        for attribute in cur_node.get_attributes():
            if attribute.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
                continue
            if attribute.get_resolved_type().get_role_name() == "execution" or attribute.get_type_name() == "target":
                if attribute.get_resolved_type().get_role_name() == "execution":
                    last_execs[subgraph_idx] = attribute
                    conns = last_execs[subgraph_idx].get_downstream_connections()
                else:
                    conns = attribute.get_downstream_connections()

                for i, conn in enumerate(conns):
                    if conn.get_node() != cur_node:  # avoid infinite loop if node connects to itself
                        subgraph.append((conn.get_node(), len(last_execs)))
                        last_execs.append(None)
    last_execs = [le for le in last_execs if le]
    return last_execs


def _get_node_attributes(node, on_input: bool, on_output: bool) -> List[str]:
    node_attributes = []
    if node is None:
        return []
    valid_port_types = []
    if on_input:
        valid_port_types.append(og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT)
    if on_output:
        valid_port_types.append(og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT)

    for attribute in node.get_attributes():
        if attribute.get_port_type() not in valid_port_types:
            continue
        node_attributes.append(attribute.get_name().split(":")[-1])
    return node_attributes


def _get_and_increment_seed_count(graph):
    """Get seed count from graph and increment by one.
    Seed count provides an additional entropy term that enables two identical samplers
    to nevertheless draw from different distributions given the same global seed. Note that this
    is not applied to specifically seeded samplers.
    """
    context = graph.get_default_graph_context()
    if not graph.find_variable("seedCount"):
        graph.create_variable("seedCount", og.Type(og.BaseDataType.INT))
        variable = graph.find_variable("seedCount")
        seed_count = 0
    else:
        variable = graph.find_variable("seedCount")
        seed_count = variable.get(context)
    variable.set(context, seed_count + 1)

    return seed_count


def add_node_id_attribute(node):
    """Add node ID attribute and set to current graph seed count

    A node ID attribute is used to save a node's identifier to USD to enable repeatable results when sampling from a
    global seed.

    Args: node: Node to which to add and set a nodeId attribute
    """
    graph = node.get_graph()
    if not node.get_attribute_exists("inputs:nodeId"):
        node.create_attribute("inputs:nodeId", og.Type(og.BaseDataType.INT, 1))
        node.get_attribute("inputs:nodeId").set_metadata("hidden", "true")
    og.AttributeValueHelper(node.get_attribute("inputs:nodeId")).set(
        _get_and_increment_seed_count(graph), update_usd=True
    )


def _get_prim_dependencies(node):
    """Get all upstream prim dependencies

    Recursively add upstream nodes every time a target input is encountered.
    Then for each prim path obtained, search the scene for graphs that refer to the same prim
    and return all nodes in the scene that make reference to the same prim.
    """
    # For each node starting with current:
    #   For each input of type "target":
    #       - If prims defined: add to dependent prims
    #       - Else If upstream connections: Add connection nodes to search and to list of upstream nodes
    # For each dependent prim found:
    #   Traverse through stage and identify all OG nodes with prim in attribute (input or output)
    #       - Add to dependent nodes

    # Make list of prims that the node depends on
    dependent_prims = set()
    dependent_nodes = []
    upstream_nodes = [node]
    while upstream_nodes:
        cur_node = upstream_nodes.pop()
        # Find inputs with prims
        for attr in cur_node.get_attributes():
            if attr.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
                continue
            if attr.get_type_name() == "target":
                cur_connections = attr.get_upstream_connections()
                if cur_connections:
                    conn_nodes = [c.get_node() for c in cur_connections]
                    upstream_nodes.extend(conn_nodes)
                    dependent_nodes.extend(conn_nodes)
                elif attr.get():
                    dependent_prims.update({str(e) for e in attr.get()})

    # Find all prims that use one or more of the dependent prims
    usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
    for cur_prim_path in usdrt_stage.GetPrimsWithTypeName("OmniGraphNode"):
        # Skip self
        if str(node.get_prim_path()) == str(cur_prim_path):
            continue

        try:
            cur_node = og.Controller().node(str(cur_prim_path))
        except og.OmniGraphValueError as e:
            carb.log_warn(e)
            continue

        # Find all nodes that include one or more dependent prim
        for attr in cur_node.get_attributes():
            if attr.get_type_name() == "target":
                node_attr_prims = {str(e) for e in attr.get()}
                if dependent_prims.intersection(node_attr_prims):
                    dependent_nodes.append(cur_node)
                    break

    return dependent_nodes


def _attach_scheduled_exec(node, exec_context):
    """Attached scheduled execution input
    Attached the node's execution input such that it is scheduled after
    all other upstream nodes.

    Args:
        node: The node to be connected to the existing graph
        exec_context: The current execution context

    """
    # Disconnect current exec
    if get_exec_attr(node, on_input=True).get_upstream_connections():
        _disconnect(get_exec_attr(node, on_input=True))

    triggers_ignored = ["omni.graph.action.OnImpulseEvent"]
    upstream_exec_nodes = []

    # Get all upstream execution nodes
    for attr in node.get_attributes():
        if attr.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT:
            continue

        if attr.get_resolved_type().get_role_name() == "execution":
            continue

    dependency_nodes = _get_prim_dependencies(node)

    for dn in dependency_nodes:
        if dn:
            upstream_exec_nodes.extend(_get_first_upstream_exec_nodes(dn))
    dependency_downstream_execs = []
    for dn in dependency_nodes + upstream_exec_nodes:
        deps = _get_last_exec_attrs(dn)
        # Filter out current node
        deps = [d for d in deps if d.get_node() != node]
        dependency_downstream_execs.extend(deps)
    dependency_downstream_execs = list(set(dependency_downstream_execs))

    if len(upstream_exec_nodes) == 0:
        auto_connect(exec_context, node)
    else:
        # Multiple upstream execution nodes: retrieve upstream triggers
        downstream_execs = []
        upstream_triggers = []
        if exec_context and get_exec_attr(exec_context, on_input=False):
            downstream_execs.append(get_exec_attr(exec_context, on_input=False))
        first_exec_attr = _get_first_exec_attr(exec_context)
        if exec_context and first_exec_attr:
            upstream_triggers.append(first_exec_attr.get_node())

        for dependency_downstream_exec in dependency_downstream_execs:
            upstream_trigger = _get_first_exec_attr(dependency_downstream_exec.get_node()).get_node()
            if upstream_trigger and upstream_trigger.get_type_name() not in triggers_ignored:
                upstream_triggers.append(upstream_trigger)
                downstream_execs.append(dependency_downstream_exec)

        # TODO If exec context is upstream of another exec, ignore it
        # If multiple execs and exec_context is impulse, ignore exec context
        if len(upstream_triggers) > 1 and (upstream_triggers[0].get_type_name() in triggers_ignored):
            upstream_triggers.pop(0)
            downstream_execs.pop(0)

        # Determine the distinct triggers that trigger this and input nodes
        distinct_triggers = set(upstream_triggers)
        distinct_trigger_execs = []
        stage = omni.usd.get_context().get_stage()

        # TODO support multi-trigger connections
        if len(distinct_triggers) > 1:
            if len(distinct_triggers) > 2 and all(
                [trigger.get_type_name() != "omni.graph.action.OnImpulseEvent" for trigger in distinct_triggers]
            ):
                carb.log_warn(
                    f"Parameterizing of node {node} used in multiple triggers ({distinct_triggers}) not currently supported."
                    " This may result in unexpected node scheduling."
                )
                distinct_triggers = upstream_triggers[:1]

        # For each trigger, identify the downstream execution nodes and connect them through a sync gate
        for distinct_trigger in distinct_triggers:
            matches = [i for i, t in enumerate(upstream_triggers) if t == distinct_trigger]
            if len(matches) == 1:
                # No sync gate needed
                distinct_trigger_execs.append(downstream_execs[matches[0]])
            else:
                # Add a node to read fabric time if one doesn't arleady exist
                read_time_path = node.get_graph().get_path_to_graph() + "/ReadTime"
                if not stage.GetPrimAtPath(read_time_path):
                    og.Controller().create_node(read_time_path, "omni.replicator.core.ReadFabricTime")
                read_time_node = og.Controller().node(read_time_path)

                # add sync gate
                gate_path = omni.usd.get_stage_next_free_path(
                    stage, node.get_graph().get_path_to_graph() + "/SyncGate", False
                )
                gate = og.Controller().create_node(gate_path, "omni.graph.action.RationalTimeSyncGate")
                read_time_node.get_attribute("outputs:fabricFrameTimeNumerator").connect(
                    gate.get_attribute("inputs:rationalTimeNumerator"), True
                )
                read_time_node.get_attribute("outputs:fabricFrameTimeDenominator").connect(
                    gate.get_attribute("inputs:rationalTimeDenominator"), True
                )
                for match in matches:
                    downstream_execs[match].connect(gate.get_attribute("inputs:execIn"), True)
                distinct_trigger_execs.append(gate.get_attribute("outputs:execOut"))

        # Connect sync gates to node
        if len(distinct_trigger_execs) == 1:
            distinct_trigger_execs[0].connect(get_exec_attr(node, on_input=True), True)
        else:
            # For multi-trigger configurations, connect sync gates through a trigger sync gate
            # This gate will only fire if both the sync gate and its upstream trigger have been fired
            # TODO support multi-trigger connections
            if len(distinct_trigger_execs) > 1:
                distinct_trigger_execs[0].connect(get_exec_attr(node, on_input=True), True)


class ReplicatorWrapper:
    """Replicator component decorator
    Wraps replicator functions to enable ``with`` syntax and automate node graph creation.

    Args:
        fn: Function to be wrapped as a ``ReplicatorItem``
    """

    def __init__(self, fn: Callable):
        update_wrapper(self, fn)
        self.__fn = fn

    def __call__(self, *args, **kwargs):
        return ReplicatorItem(self.__fn, *args, **kwargs)


class ReplicatorItem:
    """Replicator Item

    ReplicatorItems wrap Omnigraph nodes to add convenient functionality for constructing Replicator scenarios.
    For instance, ReplicatorItems can use the ``with`` syntax to automatically connect nodes together. Nodes contain input
    attributes, or parameters, and output values that are filled when a node is computed. These attributes can be
    accessed through ``get_inputs`` and ``get_outputs`` methods.

    attributes:
        node: the wrapped og.Node object
        inputs: name of the node's input attributes
        outputs: name of the node's output attributes
    """

    _exec_stack = [None]
    _stack = [None]
    _sequential = False
    _prim_stack = {}
    _prim_groups = {}

    def __init__(self, fn, *args, **kwargs):
        self._inputs = []
        self._outputs = []
        self.__fn = fn
        update_wrapper(self, fn)

        self.node = self.__fn(*args, **kwargs)
        if isinstance(self.node, ReplicatorItem):
            self.node = self.node.node

        self._inputs = _get_node_attributes(self.node, on_input=True, on_output=False)
        self._outputs = _get_node_attributes(self.node, on_input=False, on_output=True)

        auto_connect(self._get_context(), self.node)

        # For execution nodes, setup exec connections
        if is_execution_node(self.node, on_input_only=True):
            _attach_scheduled_exec(self.node, self._get_exec_context())

        if self.node and is_execution_node(self.node, on_input_only=True):
            if self._get_exec_context() is None:
                # Enable impulse on next frame
                omni.kit.async_engine.run_coroutine(og.Controller().evaluate(graph_id=get_graph()))

                # carb.settings.get_settings().set("/omni/replicator/impulse", True)
                # Find next active impulse
                suffix = 1
                impulse_path = f"{GRAPH_PATH}/OnImpulseEvent"
                impulse = self.node.get_graph().get_node(impulse_path)
                next_impulse = impulse
                next_impulse_path = impulse_path
                # Get last impulse
                while next_impulse:
                    next_impulse_path = f"{GRAPH_PATH}/OnImpulseEvent_{suffix:02}"
                    next_impulse = self.node.get_graph().get_node(next_impulse_path)
                    suffix += 1
                if not impulse or not impulse.get_attribute("state:enableImpulse").get():
                    impulse = og.Controller().create_node(
                        (next_impulse_path.split("/")[-1], self.node.get_graph()),
                        "omni.graph.action.OnImpulseEvent",
                    )
                    og.AttributeValueHelper(impulse.get_attribute("state:enableImpulse")).set(True, update_usd=True)
                    og.AttributeValueHelper(impulse.get_attribute("inputs:onlyPlayback")).set(False, update_usd=True)

                # Connect to last node of impulse graph
                # this ensures that the operation order matches user expectations
                exec_out = _get_last_exec_attr(impulse, consider_targets=False)
                if exec_out.get_node() != self.node:  # Avoid connecting nodes to themselves
                    exec_out.connect(get_exec_attr(self.node, on_input=True), True)

            if self._sequential:
                self._exec_stack.append(self.node)

        # Generate node ID for nodes with seed input
        if self.node and self.node.get_attribute_exists("inputs:seed"):
            add_node_id_attribute(self.node)

        self._set_prim_context(self.node)

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    def get_inputs(self):
        """Get input parameters

        Returns a dictionary containing input data.
        """
        if not self.node:
            raise ValueError("ReplicatorItem contains no valid node.")
        if not self.node:
            raise ValueError("ReplicatorItem contains no valid node.")
        inputs = {}
        for i in self.inputs:
            # Catch Unresolved data type
            if self.node.get_attribute(f"inputs:{i}").get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
                input_value = None
            else:
                input_value = self.node.get_attribute(f"inputs:{i}").get()
            inputs[i] = input_value
        return inputs

    def get_outputs(self):
        """Get output parameters

        Returns a dictionary containing output data
        """
        if not self.node:
            raise ValueError(f"ReplicatorItem `{self}` contains no valid node.")
        outputs = {}
        for o in self.outputs:
            # Catch Unresolved data type
            if self.node.get_attribute(f"outputs:{o}").get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
                output_value = None
            else:
                output_value = self.node.get_attribute(f"outputs:{o}").get()
            outputs[o] = output_value
        return outputs

    def get_input(self, name: str) -> Any:
        """Get input attribute value

        Args:
            name: Name of input attribute value to return.

        Returns:
            Attribute value corresponding to `name`
        """
        if not self.node:
            raise ValueError("ReplicatorItem contains no valid node.")
        if not self.node.get_attribute_exists(f"inputs:{name}"):
            raise ValueError(f"No attribute found corresponding to `{name}`. Valid attribtues are: {self.inputs}")
        return self.node.get_attribute(f"inputs:{name}").get()

    def set_input(self, name: str, value: Any) -> None:
        """Modify input attribute value

        Args:
            name: Name of input attribute value to modify.
            value: New value to set input attribute to.
        """
        if not self.node:
            # TODO needs dedicated error?
            raise ValueError("ReplicatorItem contains no valid node.")
        if not self.node.get_attribute_exists(f"inputs:{name}"):
            raise ValueError(f"No attribute found corresponding to `{name}`. Valid attribtues are: {self.inputs}")
        if isinstance(value, ReplicatorItem):
            raise NotImplementedError("Setting input attributes with ReplicatorItem objects is not yet supported")
        self.node.get_attribute(f"inputs:{name}").set(value)

    def get_output(self, name: str) -> Any:
        """Get output attribute value

        Args:
            name: Name of output attribute value to retrieve.

        Returns:
            Output attribute value.
        """
        if not self.node:
            # TODO needs dedicated error?
            raise ValueError("ReplicatorItem contains no valid node.")
        if not self.node.get_attribute_exists(f"outputs:{name}"):
            raise ValueError(f"No attribute found corresponding to `{name}`. Valid attributes are: {self.outputs}")
        return self.node.get_attribute(f"outputs:{name}").get()

    def _get_prims(self, from_output: bool = False) -> Dict[str, List[Usd.Prim]]:
        """Get a dictionary of attributes to attached USD prim objects

        Retrieve USD Prim objects from the ReplicatorItem node for all valid inputs or outputs.

        Args:
            from_output: If ``True``, output prims are returned. Defaults to ``False``.
        """
        if not self.node:
            raise ValueError("ReplicatorItem contains no valid node.")
        port = "outputs" if from_output else "inputs"
        attribute_names = self.outputs if from_output else self.inputs
        stage = omni.usd.get_context().get_stage()
        found_prims = {}
        for attribute_name in attribute_names:
            attr = self.node.get_attribute(f"{port}:{attribute_name}")
            if attr.get_resolved_type().role.name != "TARGET":
                continue
            prim_attribute_data = self.node.get_attribute(f"{port}:{attribute_name}").get()
            found_prims[attribute_name] = [stage.GetPrimAtPath(str(path)) for path in prim_attribute_data]
        return found_prims

    def get_input_prims(self) -> Dict[str, List[Usd.Prim]]:
        """Get all attached input prims

        Retrieve USD Prim objects from the ReplicatorItem node for all valid inputs.

        Returns
            Dictionary mapping attribute name to a list of attached prims
        """
        return self._get_prims()

    def get_output_prims(self) -> Dict[str, List[Usd.Prim]]:
        """Get all attached output prims

        Retrieve USD Prim objects from the ReplicatorItem node for all valid outputs.

        Returns
            Dictionary mapping attribute name to a list of attached prims
        """
        return self._get_prims(from_output=True)

    @classmethod
    def _reset(cls):
        cls._exec_stack = [None]
        cls._stack = [None]
        cls._sequential = False
        cls._prim_stack = {}
        cls._prim_groups = {}

    def __enter__(self):
        # If node has an input exec that is already connected, duplicate node
        # This allows nodes to be re-used under new triggers without affecting the original behaviour
        # Uses first exec. This is an assumption that normally holds true
        in_exec = get_exec_attr(self.node, on_input=True)
        if (
            in_exec
            and in_exec.get_upstream_connections()
            and self._get_exec_context() is not None
            and in_exec.get_upstream_connections()[0].get_node() != self._get_exec_context()
        ):
            stage = omni.usd.get_context().get_stage()
            node_path_new = omni.usd.get_stage_next_free_path(stage, self.node.get_prim_path(), False)
            node_new = og.Controller().create_node(node_path_new, self.node.get_node_type())
            # Connect attributes
            for attr_src, attr_dst in zip(self.node.get_attributes()[1:], node_new.get_attributes()[1:]):
                if attr_src.get_port_type() == og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT:
                    continue
                if attr_src.get_resolved_type().get_base_type_name() not in [
                    "unknown",
                    "prim",
                ] and not attr_dst.get_name().startswith("node:"):
                    attr_dst.set(attr_src.get())
                elif attr_src.get_resolved_type().get_base_type_name() == "prim":
                    set_target_prims(node_new, attr_dst, self.node.get_attribute(attr_src.get_name()).get())
                for src_conn in attr_src.get_upstream_connections():
                    src_conn.connect(attr_dst, False)
            self.node = node_new

        auto_connect(self._get_exec_context(), self.node)
        auto_connect(self._get_context(), self.node)
        self._add_context(self.node)

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if is_execution_node(self.node):
            popped_node = None
            while popped_node != self.node:
                popped_node = self._pop_exec_context()
        self._pop_context()

    @classmethod
    def _add_context(cls, node):
        is_prim_source_nodes = node.get_attribute_exists("outputs:prims")
        if is_execution_node(node):
            cls._exec_stack.append(node)

        # we need to make sure a prim isn't used in multiple groups
        if node and is_prim_source_nodes:  # node.get_type_name() in prim_source_nodes:
            # identify if should use input or output side
            attribute = "inputs:prims" if node.get_attribute_exists("inputs:prims") else "outputs:prims"
            for prim_path in node.get_attribute(attribute).get():
                if str(prim_path) in cls._prim_groups and cls._prim_groups.get(str(prim_path)) != node:
                    carb.log_warn(
                        f"Attempting to use prim `{str(prim_path)}` in group `{node.get_prim_path()}` "
                        f"which is also used in group `{cls._prim_groups[str(prim_path)].get_prim_path()}` "
                        "which may lead to non-deterministic results."
                    )
                cls._prim_groups[str(prim_path)] = node

            # If initializing a group node, set as current prim context
            cls._prim_stack["cur_context"] = node.get_prim_path()
        else:
            cls._prim_stack["cur_context"] = None
        cls._stack.append(node)

    @classmethod
    def _clear_prim_stacks(cls):
        cls._prim_stack = {}
        cls._prim_groups = {}

    @classmethod
    def _pop_context(cls):
        ctx = cls._stack.pop(-1)
        if cls._stack[-1] is None:
            # Clear _prim_stack and prim groups if we're out context
            cls._clear_prim_stacks()

    @classmethod
    def _pop_exec_context(cls):
        exec_cxt = cls._exec_stack.pop(-1)
        if cls._exec_stack[-1] is None:
            # Clear _prim_stack and prim groups if we're out of the current trigger
            cls._clear_prim_stacks()
        return exec_cxt

    @classmethod
    def _get_context(cls):
        return cls._stack[-1]

    @classmethod
    def _get_exec_context(cls):
        # Find any prim dependencies
        return cls._exec_stack[-1]

    @classmethod
    def _set_prim_context(cls, node):
        # need to track, per group, per exec node type, the last exec node
        # If an exec node of the same type with the same trigger has already been applied to the same prim, we want
        # to chain those nodes together to ensure deterministic outcome.
        if is_execution_node(node):
            prim_context = cls._prim_stack.get("cur_context")
            if prim_context:
                cls._prim_stack.setdefault(prim_context, {})["last_exec"] = node
                cls._prim_stack.setdefault(prim_context, {})[node.get_type_name()] = node

    @classmethod
    def _get_prim_context(cls, node):
        if node is None:
            return None
        prim_context = cls._prim_stack.get("cur_context")
        return cls._prim_stack.get(prim_context, {}).get(node.get_type_name(), None)

    @classmethod
    def _set_sequential(cls, value: bool):
        cls._sequential = bool(value)

    def __repr__(self):
        return f"{self.__fn.__module__.replace('omni.replicator.core.scripts', 'omni.replicator.core')}.{self.__fn.__name__}"

    def __str__(self):
        return f"{self.__fn.__module__.replace('omni.replicator.core.scripts', 'omni.replicator.core')}.{self.__fn.__name__}"


@contextmanager
def sequential():
    is_first_sequential = False
    exec_ctx = None
    try:
        exec_ctx = ReplicatorItem._get_exec_context()
        is_first_sequential = not ReplicatorItem._sequential
        ReplicatorItem._set_sequential(True)
        yield None
    finally:
        if is_first_sequential:
            ReplicatorItem._set_sequential(False)
            while ReplicatorItem._get_exec_context() != exec_ctx:
                ReplicatorItem._pop_exec_context()


def _set_semantics_legacy(
    input_prims: Union[str, List[str], List[Usd.Prim], ReplicatorItem], semantics: List[Tuple[str, str]]
):
    if isinstance(input_prims, ReplicatorItem) and input_prims.node.get_attribute_exists("outputs:prims"):
        input_prims = input_prims.node.get_attribute("outputs:prims").get()
    elif isinstance(input_prims, og.Node):
        input_prims = input_prims.get_attribute("outputs:prims").get()
    elif not isinstance(input_prims, List):
        input_prims = [input_prims]
    for item in input_prims:
        if isinstance(item, Usd.Prim):
            prim = item
        elif isinstance(item, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.Path.IsValidPathString(str(item)):
            stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath(str(item))
        else:
            raise ValueError(f"Unable to find prim {item}")

        for semantic_type, semantic_value in semantics:
            instance_name = Tf.MakeValidIdentifier(f"{semantic_type}_{semantic_value}")
            sem = Semantics.SemanticsAPI.Apply(prim, instance_name)
            sem.CreateSemanticTypeAttr()
            sem.CreateSemanticDataAttr()
            sem.GetSemanticTypeAttr().Set(semantic_type)
            sem.GetSemanticDataAttr().Set(semantic_value)


def _setup_random_attribute(
    write_node, attribute_value, prim_path=None, mode="prims", input_name=None, mapping=None, do_count=True
):
    stage = omni.usd.get_context().get_stage()

    if input_name and not input_name.startswith("inputs:"):
        input_name = f"inputs:{input_name}"

    if isinstance(attribute_value, ReplicatorItem):
        attribute_value = attribute_value.node

    if isinstance(attribute_value, og.Node):
        if is_execution_node(attribute_value):
            ReplicatorItem._exec_stack.append(attribute_value)
        if input_name is None:
            auto_connect(attribute_value, write_node, mapping)
        else:
            attribute_value.get_attribute("outputs:samples").connect(write_node.get_attribute(input_name), True)
        if prim_path is None or isinstance(prim_path, ReplicatorItem):
            if attribute_value.get_attribute_exists("inputs:numSamples") and do_count:
                counter = ReplicatorItem(
                    create_node, "omni.replicator.core.OgnCount", mode=mode
                )  # FIXME: avoid create a new node for each attribute

                num_samples_attr = attribute_value.get_attribute("inputs:numSamples")
                # setup all its upstream attribute's numSamples if any exists
                # TODO: TEMP solution
                all_connections = num_samples_attr.get_upstream_connections()
                for connected_attr in all_connections:
                    node = connected_attr.get_node()

                    if node.get_attribute_exists("inputs:numSamples"):
                        num_samples_input_attr = node.get_attribute("inputs:numSamples")
                        og.Controller.disconnect_all(num_samples_input_attr)
                        counter.node.get_attribute("outputs:count").connect(
                            num_samples_input_attr, True
                        )  # TODO handle all cases

                counter.node.get_attribute("outputs:count").connect(
                    attribute_value.get_attribute("inputs:numSamples"), True
                )  # TODO handle all cases
                if prim_path:
                    set_target_prims(counter.node, "inputs:prims", prim_path)
                    if write_node.get_attribute_exists("inputs:prims"):
                        set_target_prims(write_node, "inputs:prims", prim_path)
        elif isinstance(prim_path, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.Path.IsValidPathString(str(prim_path)):
            write_attribute_node_prim = stage.GetPrimAtPath(write_node.get_prim_path())
            write_attribute_node_prim.GetRelationship("inputs:prims").SetTargets([prim_path])
    elif write_node.get_attribute_exists(input_name):
        write_node.get_attribute(input_name).set(attribute_value)


def set_target_prims(node: og.Node, attribute: og.Attribute, target_prims: List[Union[ReplicatorItem, og.Node, str]]):
    """Set node targets to attribute

    This function provides a convenient way to set targets to a node attribute, and will be deprecated once
    multi-prim node attributes are supported.

    Args:
        node: Node to which to set targets
        attribute: Attribute name
        target_prims: Targets to attach to attribute
    """
    stage = omni.usd.get_context().get_stage()
    if isinstance(node, ReplicatorItem):
        node = node.node
    if not hasattr(target_prims, "__iter__") or type(target_prims) == str:
        target_prims = [target_prims]
    node_prim = stage.GetPrimAtPath(node.get_prim_path())

    target_prim_paths = []
    target_nodes = []
    for tp in target_prims:
        if isinstance(tp, ReplicatorItem):
            tp = tp.node
        if isinstance(tp, og.Node) and tp.get_attribute_exists("outputs:prims"):
            target_nodes.append(tp)
        elif isinstance(tp, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.Path.IsValidPathString(str(tp)):
            # Only append valid prims
            str_tp = str(tp)  # Cast to string, because USD doesn't always take Sdf.Path or usdrt.Sdf.Path
            if Sdf.Path.IsValidPathString(str_tp) and stage.GetPrimAtPath(str_tp).IsValid():
                target_prim_paths.append(str_tp)
        elif isinstance(tp, Usd.Prim) and tp.IsValid():
            target_prim_paths.append(tp.GetPath())
        else:
            raise ValueError(f"Unable to set target prim of type {type(tp)}")

    # If prim paths and target nodes, create new group node
    if target_prim_paths and target_nodes:
        new_group_node = create_node("omni.replicator.core.OgnGroup")
        new_group_node.get_attribute("inputs:primsIn").set(target_prim_paths)
        for i, target_node in enumerate(target_nodes):
            suffix = i + 1
            target_node.get_attribute("outputs:prims").connect(
                new_group_node.get_attribute(f"inputs:primsIn{suffix}"), True
            )
        new_group_node.get_attribute("outputs:prims").connect(node.get_attribute(attribute), True)
    # If multiple target nodes create new group node
    elif target_nodes and len(target_nodes) > 1:
        new_group_node = create_node("omni.replicator.core.OgnGroup")
        for i, target_node in enumerate(target_nodes):
            suffix = "" if i == 0 else i
            target_node.get_attribute("outputs:prims").connect(
                new_group_node.get_attribute(f"inputs:primsIn{suffix}"), True
            )
        new_group_node.get_attribute("outputs:prims").connect(node.get_attribute(attribute), True)
    # If a single target node, connect it directly to node attribute
    elif target_nodes and len(target_nodes) == 1:
        target_nodes[0].get_attribute("outputs:prims").connect(node.get_attribute(attribute), True)
    # If only prim paths provided, set node attribute directly
    elif target_prim_paths:
        node_prim.GetRelationship(attribute).SetTargets(target_prim_paths)


def _connect_prims(node: og.Node, attribute: og.Attribute, upstream_node: og.Node):
    if upstream_node.node.get_attribute_exists("outputs_primsBundle"):
        upstream_node.node.get_attribute("outputs_primsBundle").connect(node.get_attribute(attribute), True)
    elif upstream_node.node.get_attribute_exists("outputs:prims"):
        upstream_node.node.get_attribute("outputs:prims").connect(node.get_attribute(attribute), True)
    else:
        upstream_node.node.get_attribute("outputs_prims").connect(node.get_attribute(attribute), True)


def get_prims_from_paths(prim_paths: Union[Sdf.Path, str]) -> List[Usd.Prim]:
    """Convert prim paths to prim objects

    Args:
        prim_paths: list of prim paths
    """
    stage = omni.usd.get_context().get_stage()

    prims = []
    for prim_path in prim_paths:
        if not Sdf.Path.IsValidPathString(str(prim_path)):
            carb.log_warn(f"Encountered invalid prim path {str(prim_path)}, skipping.")
            continue
        prim = stage.GetPrimAtPath(str(prim_path))
        if not prim:
            carb.log_warn(f"Encountered invalid prim path {str(prim_path)}, skipping.")
            continue
        prims.append(prim)
    return prims


def get_non_xform_prims(prim_paths: List[Union[Sdf.Path, str]], usd_usdrt: bool = False) -> List[str]:
    """Return non-xform prim paths

    For each prim_path specified, return its child prim if it has the ``replicatorXform`` attribute.

    Args:
        prim_paths: list of prim paths
        usd_usdrt: If True, use UsdRT functions, otherwise use PXR functions.
    """
    if usd_usdrt:
        stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
    else:
        stage = omni.usd.get_context().get_stage()

    leaf_prim_paths = []
    while prim_paths:
        prim_path = prim_paths.pop(0)
        prim = stage.GetPrimAtPath(str(prim_path))
        if not prim:
            carb.log_warn(f"Encountered invalid prim path {str(prim_path)}")
        elif prim.HasAttribute("replicatorXform"):
            for child in prim.GetChildren():
                prim_paths.append(str(child.GetPath()))
        else:
            leaf_prim_paths.append(prim_path)
    return leaf_prim_paths


def get_node_targets(node: og.Node, attribute: str, replicatorXform: bool = True) -> List[str]:
    """Get node targets from prims bundle - DEPRECATED

    This function provided a convenient way to retrieve targets from a node attribute and is now deprecated. Use
    ``get_non_xform_prims`` for similar functionality.

    Args:
        node: Node from which to get targets
        attribute: Attribute name
        replicatorXform: If ``False`` and a target has the attribute `replicatorXform`, return its leaf children.
    """
    stage = omni.usd.get_context().get_stage()
    if (
        attribute == "outputs_prims"
        and not node.get_attribute_exists("outputs_prims")
        and node.get_attribute_exists("outputs_primsBundle")
    ):
        attribute = "outputs_primsBundle"
    if attribute == "inputs:prims" and not node.get_attribute_exists("inputs:prims"):
        if node.get_attribute_exists("outputs_prims"):
            attribute = "outputs_prims"
        elif node.get_attribute_exists("outputs_primsBundle"):
            attribute = "outputs_primsBundle"
        elif node.get_attribute_exists("outputs:prims"):
            attribute = "outputs:prims"

    if node.get_attribute(attribute).get_resolved_type().base_type == og.BaseDataType.RELATIONSHIP:
        prim_paths = stage.GetPrimAtPath(node.get_prim_path()).GetRelationship(attribute).GetTargets()
    else:
        prim_paths = [
            bundle.get_attribute_by_name("sourcePrimPath").get()
            for bundle in node.get_attribute(attribute).get().get_child_bundles()
        ]

    prim_paths2 = []
    for prim_path in prim_paths:
        if "outputs_primsBundle" in str(prim_paths[0]):
            # FIXME - this approach is preferable but non-deterministic. Prims order can change from run to run
            # bundle_paths = [bundle.get_attribute_by_name("sourcePrimPath").get() for bundle in og.Controller().attribute(str(prim_path)).get().get_child_bundles()]

            # WAR - This produces deterministic order
            bundle_paths = (
                stage.GetPrimAtPath(og.Controller().attribute(str(prim_path)).get_node().get_prim_path())
                .GetRelationship("inputs:prims")
                .GetTargets()
            )
            prim_paths2.extend(bundle_paths)
        else:
            prim_paths2.append(prim_path)
    prim_paths = prim_paths2

    if (
        len(prim_paths) == 1
        and stage.GetPrimAtPath(prim_paths[0])
        and stage.GetPrimAtPath(prim_paths[0]).GetTypeName() == "Output"
    ):
        output_prim = stage.GetPrimAtPath(prim_paths[0])
        paths = output_prim.GetRelationship("prims").GetTargets()
        if len(paths) == 0:
            upstream_node_prim = stage.GetPrimAtPath(prim_paths[0].GetParentPath())
            attr_name = prim_paths[0].name
            paths = upstream_node_prim.GetRelationship(attr_name).GetTargets()
            if len(paths) == 0:
                attr_name = attr_name.replace("outputs_", "outputs:")
                paths = upstream_node_prim.GetRelationship(attr_name).GetTargets()
            # HACK outputs will sometimes be unpopulated in recent Kit versions, so check inputs
            if len(paths) == 0 and "ReadPrimsBundle" in prim_paths[0].pathString:
                paths = upstream_node_prim.GetRelationship(attr_name.replace("outputs", "inputs")).GetTargets()

        prim_paths = paths

    # we should be able to have multiple meshes in our inclusion (surfacePrims, volumePrims) and exclusion (noCollPrims) lists
    elif len(prim_paths) > 1 and attribute in [
        "inputs:surfacePrims",
        "inputs:volumePrims",
        "inputs:noCollPrims",
        "inputs:volumeExclPrims",
    ]:
        new_prim_paths = []
        all_nametypes_output = True
        for prim_path in prim_paths:
            if stage.GetPrimAtPath(prim_path).GetTypeName() == "Output":
                output_prim = stage.GetPrimAtPath(prim_path)
                paths = output_prim.GetRelationship("prims").GetTargets()
                if len(paths) == 0:
                    upstream_node_prim = stage.GetPrimAtPath(prim_path.GetParentPath())
                    attr_name = prim_path.name
                    paths = upstream_node_prim.GetRelationship(attr_name).GetTargets()
                    if len(paths) == 0:
                        attr_name = attr_name.replace("outputs_", "outputs:")
                        paths = upstream_node_prim.GetRelationship(attr_name).GetTargets()
                    # HACK outputs will sometimes be unpopulated in recent Kit versions, so check inputs
                    if len(paths) == 0 and "ReadPrimsBundle" in prim_paths[0].pathString:
                        paths = upstream_node_prim.GetRelationship(attr_name.replace("outputs", "inputs")).GetTargets()

                new_prim_paths.append(paths[0])
            else:
                all_nametypes_output = False

        if all_nametypes_output == True:
            prim_paths = new_prim_paths

    if not replicatorXform:
        prim_paths = _get_attribute_prims(prim_paths)
    return prim_paths


# TODO
# def get_input_prims(input_prims):
#     stage = omni.usd.get_context().get_stage()
#     input_prims = []
#     if isinstance(tp, og.Node):
#         node_prim = stage.GetPrimAtPath(node.get_prim_path())
#         for tp in target_prims:
#             if isinstance(tp, ReplicatorItem):
#                 tp = tp.node
#             if isinstance(tp, og.Node) and tp.get_type_name() == "omni.graph.nodes.ReadPrim":
#                 tp_prim = stage.GetPrimAtPath(tp.get_prim_path())
#                 targets = tp_prim.GetRelationship('inputs:prim').GetTargets()
#                 target_prim_paths.extend(targets)
#             elif isinstance(tp, str) or isinstance(tp, Sdf.Path):
#                 target_prim_paths.append(tp)
#             else:
#                 raise ValueError(f"Unable to set target prim of type {type(tp)}")

#     node_prim.GetRelationship(attribute).SetTargets(target_prim_paths)


def _set_position(prim_paths: Union[ReplicatorItem, List[str]], position: Tuple[float, float, float]):
    """Set the position of the prims defined by ``prim_paths``.

    Args:
        prim_paths: Paths of prims to modify
        position: Position in world frame for XYZ axes.
    """
    stage = omni.usd.get_context().get_stage()
    if isinstance(prim_paths, ReplicatorItem) and prim_paths.node.get_attribute_exists("outputs:prims"):
        prim_paths = prim_paths.node.get_attribute("outputs:prims").get()
    elif isinstance(prim_paths, og.Node) and prim_paths.get_attribute_exists("outputs:prims"):
        prim_paths = prim_paths.get_attribute("outputs:prims").get()
    elif isinstance(prim_paths, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.Path.IsValidPathString(str(prim_paths)):
        prim_paths = [prim_paths]
    else:
        raise ValueError(
            f"Got invalid value for `prim_paths`: {type(prim_paths)}. `prim_paths` must be a list of strings or a ReplicatorItem with a `outputs:prims` attribute"
        )
    with Sdf.ChangeBlock():
        for prim_path in prim_paths:
            if isinstance(position, int) or isinstance(position, float):
                position = (position, position, position)
            prim = stage.GetPrimAtPath(str(prim_path))
            if not prim.GetAttribute("xformOp:translate"):
                UsdGeom.Xformable(prim).AddTranslateOp()
            prim.GetAttribute("xformOp:translate").Set(position)


def _set_scale(prim_paths: Union[ReplicatorItem, List[str]], scale: Tuple[float, float, float]):
    """Set the scale of the prims defined by ``prim_paths``.

    Args:
        prim_paths: Paths of prims to modify
        scale: Scale factor for each axis
    """
    stage = omni.usd.get_context().get_stage()
    if isinstance(prim_paths, ReplicatorItem) and prim_paths.node.get_attribute_exists("outputs:prims"):
        prim_paths = prim_paths.node.get_attribute("outputs:prims").get()
    elif isinstance(prim_paths, og.Node) and prim_paths.get_attribute_exists("outputs:prims"):
        prim_paths = prim_paths.get_attribute("outputs:prims").get()
    elif isinstance(prim_paths, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.Path.IsValidPathString(str(prim_paths)):
        prim_paths = [prim_paths]
    else:
        raise ValueError(
            f"Got invalid value for `prim_paths`: {type(prim_paths)}. `prim_paths` must be a list of strings or a ReplicatorItem with a `outputs:prims` attribute"
        )
    with Sdf.ChangeBlock():
        for prim_path in prim_paths:
            if isinstance(scale, int) or isinstance(scale, float):
                scale = (scale, scale, scale)
            prim = stage.GetPrimAtPath(str(prim_path))
            if not prim.GetAttribute("xformOp:scale"):
                UsdGeom.Xformable(prim).AddScaleOp()
            prim.GetAttribute("xformOp:scale").Set(scale)


def _set_rotation(
    prim_paths: Union[ReplicatorItem, List[str]], rotate: Tuple[float, float, float], rotation_order: str
):
    """Set the rotation of the prims defined by ``prim_paths``.

    Args:
        prim_paths: Paths of prims to modify
        rotate: Rotation, in degrees, for each axis
        rotation_order: Rotation axes. Must be a permutation of axes `X`, `Y`, ``Z``.
    """
    stage = omni.usd.get_context().get_stage()
    if isinstance(prim_paths, ReplicatorItem) and prim_paths.node.get_attribute_exists("outputs:prims"):
        prim_paths = prim_paths.node.get_attribute("outputs:prims").get()
    elif isinstance(prim_paths, og.Node) and prim_paths.get_attribute_exists("outputs:prims"):
        prim_paths = prim_paths.get_attribute("outputs:prims").get()
    elif isinstance(prim_paths, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.Path.IsValidPathString(str(prim_paths)):
        prim_paths = [prim_paths]
    else:
        raise ValueError(
            f"Got invalid value for `prim_paths`: {type(prim_paths)}. `prim_paths` must be a list of strings or a ReplicatorItem with a `outputs:prims` attribute"
        )
    with Sdf.ChangeBlock():
        for prim_path in prim_paths:
            if isinstance(rotate, int) or isinstance(rotate, float):
                rotate = (rotate, rotate, rotate)
            prim = stage.GetPrimAtPath(str(prim_path))
            if not prim.GetAttribute(f"xformOp:rotate{rotation_order}"):
                UsdGeom.Xformable(prim).AddRotateXYZOp()
            prim.GetAttribute(f"xformOp:rotate{rotation_order}").Set(rotate)


def _set_visibility(prim_paths: Union[ReplicatorItem, List[str]], visibility: bool):
    """Set the visibility of the prims defined by ``prim_paths``.

    Args:
        prim_paths: Paths of prims to modify
        visibility: If ``True``, set visibility to ``inherited`` otherwise set to ``invisible``.
    """
    stage = omni.usd.get_context().get_stage()
    if isinstance(prim_paths, ReplicatorItem) and prim_paths.node.get_attribute_exists("outputs:prims"):
        prim_paths = prim_paths.node.get_attribute("outputs:prims").get()
    elif isinstance(prim_paths, og.Node) and prim_paths.get_attribute_exists("outputs:prims"):
        prim_paths = prim_paths.get_attribute("outputs:prims").get()
    elif isinstance(prim_paths, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.Path.IsValidPathString(str(prim_paths)):
        prim_paths = [prim_paths]
    else:
        raise ValueError(
            f"Got invalid value for `prim_paths`: {type(prim_paths)}. `prim_paths` must be a list of strings or a ReplicatorItem with a `outputs:prims` attribute"
        )
    with Sdf.ChangeBlock():
        for prim_path in prim_paths:
            vis = "inherited" if visibility else "invisible"
            prim = stage.GetPrimAtPath(str(prim_path))
            prim.GetAttribute("visibility").Set(vis)


def get_files_group(
    folder_path: str, file_suffixes: List[str] = None, ignore_case: bool = True, file_type: str = "png"
) -> List[dict]:
    """Retrieve all the files in a folder and group them based on the suffixes.

    Args:
        folder_path: The folder where to search.
        file_prefix: The prefix to filter the files by.
        file_type: The texture file type.

    Returns:
        A list of tuples with each tuple of the format (<prefix>, {<suffix>: <filepath>,}).
    """

    async def list_files(path):
        lists = await asyncio.gather(*[omni.client.list_async(path)])
        return lists

    def filter_file_types(paths):
        filtered_files = []
        img_filter = rf"^.*\.({file_type})$"
        for path in paths:
            if re.fullmatch(img_filter, path):
                filtered_files.append(path)
        return filtered_files

    if not Path(folder_path).is_dir():
        carb.log_error(f"{folder_path} is not a valid folder path!")
        return

    if not file_suffixes:
        carb.log_error("No texture prefix provided!")
        return

    loop = asyncio.get_event_loop()
    if loop.is_running():
        # sequential
        lists = [omni.client.list(folder_path)]
    else:
        # async
        lists = loop.run_until_complete(list_files(folder_path))

    (result, entries) = lists[0]
    files = [e.relative_path for e in entries]

    if not result == omni.client.Result.OK:
        carb.log_warn("There was an error retrieving texture files!")
        return

    all_files = {}
    filtered_files = filter_file_types(files)

    re_flags = 0
    if ignore_case:
        re_flags = re.IGNORECASE

    # Further filter texture files
    for suffix in file_suffixes:
        file_filter = f"^(\w*)({suffix})$"
        path_pattern_regex = re.compile(file_filter, flags=re_flags)

        for filtered_file in filtered_files:
            filename, _ = filtered_file.split(".")

            # Check to see if the filename matches the suffix filter
            filter_match = re.fullmatch(path_pattern_regex, filename)
            if filter_match:
                if filter_match.group(1) not in all_files:
                    all_files[filter_match.group(1)] = {}
                all_files[filter_match.group(1)][suffix] = Path(folder_path).joinpath(filtered_file).as_posix()

    all_files_list = [json.dumps({ob: all_files[ob]}) for ob in all_files]
    all_files_list.sort()
    return all_files_list


def get_usd_files(path: str, recursive: bool = False, path_filter: str = None) -> List[str]:
    """Retrieve a list of USD files at the provided path

    Args:
        path: Path or URL to search from.
        recursive: If ``True``, recusively search through sub-directories.
        path_filter: Optional regex filter to refine the search.
    """

    async def list_paths(paths):
        lists = await asyncio.gather(*[omni.client.list_async(p) for p in paths])
        return lists

    def filter_usd_files(paths):
        usd_files, others = [], []
        usd_filter = "^.*\.(usd|usda|usdc|USD|USDA|USDC)$"
        img_filter = "^.*\.(jpg|png|hdri|jpeg|dds|thumbs|JPG|PNG|HDRI|JPEG)$"
        for path in paths:
            if re.fullmatch(usd_filter, path):
                usd_files.append(path)
            elif re.fullmatch(img_filter, path):
                pass
            else:
                others.append(path)
        return usd_files, others

    path_list = [path]
    all_files = []
    is_first_level = True
    while path_list:
        usd_files, other_paths = filter_usd_files(path_list)

        # Further filter usd files (if needed)
        for usd_file in usd_files:
            is_path_match = True if path_filter is None else re.search(path_filter, usd_file)
            if is_path_match:
                all_files.append(usd_file)

        path_list = []
        # If recursion is True or in first level, find children of other paths
        if recursive or is_first_level:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # sequential
                lists = [omni.client.list(path) for path in other_paths]
            else:
                # async
                lists = loop.run_until_complete(list_paths(other_paths))
            for path, (result, entries) in zip(other_paths, lists):
                if result == omni.client.Result.OK:
                    path_list += [posixpath.join(path, e.relative_path) for e in entries]
                    is_first_level = False

    return sorted(all_files)


def get_prim_variant_values(prim_path: Union[str, Sdf.Path], variant_name: str) -> List[str]:
    stage = omni.usd.get_context().get_stage()

    if prim_path and Sdf.Path.IsValidPathString(str(prim_path)):
        prim = stage.GetPrimAtPath(prim_path)
    else:
        carb.log_error(f"Invalid prim path: {prim_path}")

    if not isinstance(variant_name, str):
        carb.log_error("Variant name must be of type str!")

    if variant_name in prim.GetVariantSets().GetNames():
        return prim.GetVariantSet(variant_name).GetVariantNames()
    else:
        carb.log_error(f"{variant_name} isn't a variant set on prim {prim_path}!")
        return []


def _get_attribute_prims(prim_paths: List[Union[str, Sdf.Path]]):
    stage = omni.usd.get_context().get_stage()
    if isinstance(prim_paths, (str, Sdf.Path)):
        prim_paths = [prim_paths]
    attribute_prim_paths = []
    while prim_paths:
        prim_path = prim_paths.pop(0)
        prim = stage.GetPrimAtPath(prim_path)
        if prim.GetAttribute("replicatorXform").Get():
            children_prim_paths = [p.GetPath().pathString for p in prim.GetChildren()]
            prim_paths.extend(children_prim_paths)
        else:
            attribute_prim_paths.append(prim_path)
    return attribute_prim_paths


def find_prims(prim_paths: List[Union[Sdf.Path, str]], mode: str = "instances") -> List[Usd.Prim]:
    """
    Find prims based on specified mode

    :param prim_paths: List of paths to prims in the current stage
    :param mode: Choose from one of the following modes:['prims', 'prototypes', 'materials', 'meshes', 'instances'], defaults to "instances".

        * ``prims`` - Returns the prims corresponding to the paths in prim_paths.
        * ``prototypes`` - Returns the prims corresponding to the paths in prim_paths and parses point instancers to retreive its prototypes.
        * ``meshes`` - Traverse through the prims in prim_paths and return all meshes and geomsubsets.
        * ``materials`` - Traverse through the prims in prim_paths and return all bound materials.
    :raises ValueError: Invalid mode choice
    :return: List of Usd prim objects
    """

    stage = omni.usd.get_context().get_stage()
    found_prims = [stage.GetPrimAtPath(str(path)) for path in prim_paths]

    if mode == "prims":
        return found_prims

    prims_and_protos = []
    for prim in found_prims:
        if prim.GetTypeName() == "PointInstancer":
            protos = prim.GetRelationship("prototypes").GetTargets()
            prims_and_protos.extend([stage.GetPrimAtPath(proto) for proto in protos])
        else:
            prims_and_protos.append(prim)

    if mode == "instances":
        return prims_and_protos
    elif mode == "meshes":
        output = []
        queue = list(prims_and_protos)
        while queue:
            prim = queue.pop()
            if prim.GetTypeName() in ["Mesh", "GeomSubset"]:
                output.append(prim)
            queue.extend(prim.GetChildren())
        return output
    elif mode == "materials":
        output = []
        queue = list(prims_and_protos)
        while queue:
            prim = queue.pop()
            material = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]
            if material:
                output.append(material)
            queue.extend(prim.GetChildren())
        return output
    else:
        raise ValueError(f"Invalid `mode` {mode} provided.")


def _validate_paths(paths):
    invalid_paths = []
    for path in paths:
        result, _ = omni.client.stat(path)

        if result != omni.client.Result.OK:
            invalid_paths.append(path)

    if invalid_paths:
        raise ValueError(f"One or more invalid paths were found: {invalid_paths}")


def parse_semantics(prim):
    """Return the prim semantics"""

    if not isinstance(prim, Usd.Prim):
        raise ValueError(f"Invalid prim: {prim}")

    def parse_semantic_schema_legacy(prim):
        schemas = [s.split(":")[1] for s in prim.GetAppliedSchemas() if "SemanticsAPI" in s]
        semantics = []
        for schema in schemas:
            sem = Semantics.SemanticsAPI.Get(prim, schema)
            sem_type = sem.GetSemanticTypeAttr().Get()
            sem_data = sem.GetSemanticDataAttr().Get()
            semantics.append((sem_type, sem_data))
        return semantics

    def parse_semantic_schema(prim):
        schemas = [s.split(":")[1] for s in prim.GetAppliedSchemas() if "SemanticsLabelsAPI" in s]
        semantics = []
        for schema in schemas:
            sem = UsdSemantics.LabelsAPI(prim, schema)
            sem_data = sem.GetLabelsAttr().Get()
            semantics.extend([(schema, label) for label in sem_data])
        return semantics

    has_prim_semantics_legacy = prim.HasAPI(Semantics.SemanticsAPI)
    has_prim_semantics = prim.HasAPI(UsdSemantics.LabelsAPI)
    material = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0].GetPrim()
    has_material_semantics_legacy = material and material.HasAPI(Semantics.SemanticsAPI)
    has_material_semantics = material and material.HasAPI(UsdSemantics.LabelsAPI)

    semantics = []
    if has_prim_semantics_legacy:
        semantics.extend(parse_semantic_schema_legacy(prim))
    if has_material_semantics_legacy:
        semantics.extend(parse_semantic_schema_legacy(material))
    if has_prim_semantics:
        semantics.extend(parse_semantic_schema(prim))
    if has_material_semantics:
        semantics.extend(parse_semantic_schema(material))

    return semantics


def legacy_semantics_arg_to_new(legacy_semantics_arg):
    """Convert legacy semantics argument to new format

    The legacy format consisted of a list of tuples, where each tuple contained a semantic type and a semantic value.
    The new format consists of a dictionary, where each key is a semantic type and the value is a list of semantic values.
    """
    new = {}
    if isinstance(legacy_semantics_arg, list):
        if len(legacy_semantics_arg) == 0:
            return new
        if isinstance(legacy_semantics_arg[0], tuple):
            for t in legacy_semantics_arg:
                new.setdefault(t[0], []).append(t[1])
            return new
        if isinstance(legacy_semantics_arg[0], str):
            for s in legacy_semantics_arg:
                k, v = s.split(":")
                new.setdefault(k, []).append(v)
            return new
    return legacy_semantics_arg


def _add_ftheta_params(prim):
    # Setup missing ftheta params
    prim.CreateAttribute("cameraProjectionType", Sdf.ValueTypeNames.Token)
    prim.CreateAttribute("fthetaPolyA", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("fthetaPolyB", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("fthetaPolyC", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("fthetaPolyD", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("fthetaPolyE", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("fthetaPolyF", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("fthetaCx", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("fthetaCy", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("fthetaWidth", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("fthetaHeight", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("fthetaMaxFov", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("p0", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("p1", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("s0", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("s1", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("s2", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("s3", Sdf.ValueTypeNames.Float)
    prim.CreateAttribute("crossCameraReferenceName", Sdf.ValueTypeNames.String)


def compute_aabb(bbox_cache: UsdGeom.BBoxCache, prim: str, include_children: bool = True) -> np.array:
    """Compute an AABB for a given prim_path, a combined AABB is computed if include_children is True

    Args:
        bbox_cache (UsdGeom.BboxCache): Existing Bounding box cache to use for computation
        prim_path (UsdPrim): prim to compute AABB for
        include_children (bool, optional): include children of specified prim in calculation. Defaults to True.

    Returns:
        np.array: Bounding box for this prim, [min x, min y, min z, max x, max y, max z]
    """
    total_bounds = Gf.BBox3d()
    if include_children:
        for p in Usd.PrimRange(prim):
            total_bounds = Gf.BBox3d.Combine(
                total_bounds, Gf.BBox3d(bbox_cache.ComputeWorldBound(p).ComputeAlignedRange())
            )
    else:
        total_bounds = Gf.BBox3d(bbox_cache.ComputeWorldBound(prim).ComputeAlignedRange())

    return np.array([*total_bounds.ComputeAlignedBox().GetMin(), *total_bounds.ComputeAlignedBox().GetMax()])


def _get_data_type(data):
    if isinstance(data, (list, tuple)):
        el_len = len(data)
        el = data[0]
        el_type = type(el)
    else:
        el_len = ""
        el = data
        el_type = type(el)

    if el_type == int:
        base_type = f"int{el_len}"
    elif el_type == float:
        base_type = f"double{el_len}"
    elif el_type == bool:
        base_type = "bool"
    elif el_type == str and el_len == 0:
        base_type = "string"
    elif isinstance(el, (Sdf.Path, usdrt.Sdf.Path)):
        base_type = "target"
    elif el_type and el_len != "":
        base_type = "token"
    else:
        raise ValueError(
            f"Base type {el_type} is not supported. Only elements of type str, bool, int and float are supported."
        )
    return base_type


def get_graph_type(data):
    if data is None:
        return og.Type(og.BaseDataType.UNKNOWN, 1, 0)
    name = ""
    if isinstance(data, np.ndarray):
        pass
        # TODO
    if isinstance(data, (list, tuple)):
        data_len = len(data)
        el = data[0]
        if isinstance(el, (list, tuple)):
            el_len = len(el)
            el_type = type(el[0])
        else:
            el_type = type(el)
            el_len = 1
    else:
        data_len = 0
        el_len = 1
        el_type = type(data)

    if "matrix" not in name:
        if el_type == float:
            return og.Type(og.BaseDataType.DOUBLE, el_len, data_len)
        elif el_type == int:
            return og.Type(og.BaseDataType.INT, el_len, data_len)
        elif el_type == str or el_type == Sdf.Path:
            return og.Type(og.BaseDataType.TOKEN, 1, data_len)
        elif el_type == bool:
            return og.Type(og.BaseDataType.BOOL, el_len, data_len)
        elif isinstance(el, (Sdf.Path, usdrt.Sdf.Path)):
            return "target"
    else:
        if name == "matrix4d":
            return og.Type(og.BaseDataType.DOUBLE, 16, data_len)
        elif name == "matrix4f":
            return og.Type(og.BaseDataType.FLOAT, 16, data_len)
        elif name == "matrix3d":
            return og.Type(og.BaseDataType.DOUBLE, 9, data_len)
        elif name == "matrix3f":
            return og.Type(og.BaseDataType.FLOAT, 9, data_len)
        elif name == "matrix2d":
            return og.Type(og.BaseDataType.DOUBLE, 4, data_len)
        elif name == "matrix2f":
            return og.Type(og.BaseDataType.FLOAT, 4, data_len)
    return None


def read_prim_transform(prim_ref: Usd.Prim):
    """Return the prim's local to world transform for current time

    Args:
        prim_ref: Prim to compute transform for
    """
    timeline = omni.timeline.get_timeline_interface()
    t = timeline.get_current_time() * timeline.get_time_codes_per_seconds()

    prim = UsdGeom.Xformable(prim_ref)
    return prim.ComputeLocalToWorldTransform(t)


def send_og_event(event_name: str) -> None:
    """Send an OmniGraph event that can be received by the `omni.graph.action.OnCustomEvent` node.

    Sends an empty payload to signal the `omni.graph.action.OnCustomEvent` node to activate

    Args:
        event_name: Name of the omnigraph event to send. The event name sent is always in the format
            `omni.graph.action.{event_name}`.
    """
    # TODO: This is a workaround to send an event to the `omni.graph.action.OnCustomEvent` node.
    # which still uses the old event system.
    reg_event_name = carb.events.type_from_string(f"omni.graph.action.{event_name}")
    message_bus = omni.kit.app.get_app().get_message_bus_event_stream()
    message_bus.push(reg_event_name, payload={})

    # event_name = f"omni.graph.action.{event_name}"
    # carb.eventdispatcher.get_eventdispatcher().dispatch_event(event_name, payload={})


def get_reduced_ref_time(numerator, denominator):
    if numerator == 0 or denominator == 0:
        return numerator, denominator

    d = gcd(numerator, denominator)

    numerator = numerator // d
    denominator = denominator // d
    return numerator, denominator


def create_material(mtl_url: str, mtl_name: str, mtl_path: str):
    stage = omni.usd.get_context().get_stage()

    mtl_path = omni.usd.get_stage_next_free_path(stage, mtl_path, False)

    # create Looks folder
    parts = str(mtl_path).split("/")
    parts.pop()
    prim_path = ""
    for part in parts:
        prim_path = f"{prim_path}/{part}" if part else prim_path
        prim = stage.GetPrimAtPath(Sdf.Path(prim_path)) if prim_path else None
        if prim_path and not prim:
            stage.DefinePrim(prim_path, "Scope")

    # create material
    mat_prim = stage.DefinePrim(mtl_path, "Material")
    material_prim = UsdShade.Material.Get(stage, mat_prim.GetPath())
    if material_prim:
        shader_mtl_path = stage.DefinePrim("{}/Shader".format(mtl_path), "Shader")
        shader_prim = UsdShade.Shader.Get(stage, shader_mtl_path.GetPath())
        if shader_prim:
            shader_out = shader_prim.CreateOutput("out", Sdf.ValueTypeNames.Token)
            shader_out.SetRenderType("material")

            material_prim.CreateSurfaceOutput("mdl").ConnectToSource(shader_out)
            material_prim.CreateVolumeOutput("mdl").ConnectToSource(shader_out)
            material_prim.CreateDisplacementOutput("mdl").ConnectToSource(shader_out)
            shader_prim.GetImplementationSourceAttr().Set(UsdShade.Tokens.sourceAsset)
            shader_prim.SetSourceAsset(Sdf.AssetPath(mtl_url.replace("\\", "/")), "mdl")
            shader_prim.SetSourceAssetSubIdentifier(mtl_name, "mdl")
        else:
            stage.RemovePrim(material_prim)
            carb.log_warn(f"failed to create shader {shader_mtl_path}")
    else:
        carb.log_warn(f"failed to create prim {mat_prim.GetPath().pathString}")


def _find_replicator_triggers() -> List[og.Node]:
    """Find any Replicator Triggers in the current scene"""
    REPLICATOR_TRIGGERS = [
        "omni.replicator.core.OgnOnFrame",
        "omni.replicator.core.OgnOnTime",
        "omni.replicator.core.OgnOnCondition",
    ]

    replicator_triggers = []

    usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
    for prim_path in usdrt_stage.GetPrimsWithTypeName("OmniGraphNode"):
        type_name = str(usdrt_stage.GetPrimAtPath(prim_path).GetAttribute("node:type").Get())
        if type_name in REPLICATOR_TRIGGERS:
            replicator_triggers.append(og.Controller().node(str(prim_path)))

    return replicator_triggers


def _evaluate_graphs_from_nodes(nodes: List[og.Node]) -> None:
    """Evaluate graphs from the provided nodes

    For each node, find corresponding graph and evaluate each graph once.

    Args:
        nodes: nodes from which to evaluate graphs
    """
    triggered_graphs = []
    for n in nodes:
        n_graph = n.get_graph()
        if n_graph not in triggered_graphs:
            og.Controller().evaluate_sync(graph_id=n_graph)
            triggered_graphs.append(n_graph)


def open_stage(stage_path: Union[str, Sdf.Path, usdrt.Sdf.Path]) -> Usd.Stage:
    """Helper method to open a new stage from a Usd file

    Args:
        stage_path: File path to the stage to load
    """
    omni.usd.get_context().open_stage(str(stage_path))
    return omni.usd.get_context().get_stage()


def get_decal_bounds_transform_from_normalized(
    prim_path: Union[Usd.Prim, str, Sdf.Path],
    bounds_vector: Gf.Vec3d = Gf.Vec3d(0, 0, 1),
    offset: float = 0.01,
    rotation: Gf.Vec3d = Gf.Vec3d(),
    scale: Gf.Vec3d = Gf.Vec3d(1, 1, 1),
):
    EPS = 1e-5

    # Not really a normalized vector, but each axis should be clamped from -1 to 1
    normalized_position = Gf.Vec3d(bounds_vector[0], bounds_vector[1], bounds_vector[2])
    for idx, val in enumerate(normalized_position):
        normalized_position[idx] = max(-1, min(1, val))

    additional_rotation = rotation

    stage = omni.usd.get_context().get_stage()
    timeline_iface = omni.timeline.get_timeline_interface()
    time = timeline_iface.get_current_time() * timeline_iface.get_time_codes_per_seconds()

    # Get input mesh extent
    if isinstance(prim_path, (str, Sdf.Path, usdrt.Sdf.Path)) and Sdf.Path.IsValidPathString(str(prim_path)):
        prim = stage.GetPrimAtPath(str(prim_path))
    elif isinstance(prim_path, Usd.Prim):
        prim = prim_path
    else:
        raise ValueError(f"Invalid prim_path specified: {prim_path}")

    if not prim.IsValid():
        carb.log_error(f"Target prim is not valid!")
        return False

    # Get the extent of the input prim
    cache = UsdGeom.BBoxCache(time=time, includedPurposes=[UsdGeom.Tokens.default_], useExtentsHint=True)
    bounds = compute_aabb(cache, prim)
    size = bounds[-3:] - bounds[:3]
    translation = (bounds[-3:] + bounds[:3]) / 2

    # Get the world translation value from the "normalized" input on the bounds
    x_pos = (size[0] * 0.5 * normalized_position[0]) + translation[0]
    y_pos = (size[1] * 0.5 * normalized_position[1]) + translation[1]
    z_pos = (size[2] * 0.5 * normalized_position[2]) + translation[2]
    target = Gf.Vec3d(x_pos, y_pos, z_pos)

    # Get the world translation value from the outer bounds
    vector_as_list = [normalized_position[0], normalized_position[1], normalized_position[2]]
    largest_axis = max(vector_as_list, key=abs)
    axis_to_offset = vector_as_list.index(largest_axis)
    eye = Gf.Vec3d(target[0], target[1], target[2])

    if largest_axis < 0:
        eye[axis_to_offset] -= offset / UsdGeom.GetStageMetersPerUnit(stage)
    else:
        eye[axis_to_offset] += offset / UsdGeom.GetStageMetersPerUnit(stage)

    # Calculate the rotation so the decal -Z aligns with a vector between the two points
    if UsdGeom.GetStageUpAxis(stage) == "Z":
        up_axis = Gf.Vec3d(0, 0, 1)
    else:
        up_axis = Gf.Vec3d(0, 1, 0)

    eye_target_vec = target - eye

    is_collinear = np.all(np.cross(np.array(eye_target_vec), np.array(up_axis)) == 0)

    # Offset eye a little bit when look at axis is align with up axis
    if is_collinear:
        if UsdGeom.GetStageUpAxis(stage) == "Y":
            eye = eye + Gf.Vec3d(0, 0, EPS)
        else:
            eye = eye + Gf.Vec3d(EPS, 0, 0)

    new_tf = Gf.Matrix4d().SetLookAt(eye, target, up_axis).GetInverse().GetOrthonormalized()

    angles = new_tf.ExtractRotation().Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis())
    x_index, y_index, z_index = 2, 1, 0
    rotationXYZ = Gf.Vec3d(angles[x_index], angles[y_index], angles[z_index])

    # Add any additional input rotation after the -Z is facing the face
    rotationXYZ += additional_rotation

    # Update scale
    new_scale = Gf.Vec3d(
        size[0] * scale[0] * UsdGeom.GetStageMetersPerUnit(stage),
        size[1] * scale[1] * UsdGeom.GetStageMetersPerUnit(stage),
        size[2] * scale[2] * UsdGeom.GetStageMetersPerUnit(stage),
    )

    # Return the values that will be used for the translate and rotateXYZ
    return eye, rotationXYZ, new_scale


def select_rotation_op(prim: Usd.Prim) -> str:
    """Select a rotation operation for specified prim.

    Loop through all rotation operations in the prim's ``xformOpOrder`` attribute. If a ``transform``op is encountered,
    use ``transform``, otherwise use the first rotation op. If no rotation op is found, create a ``rotateXYZ`` rotation
    op. Remove any additional rotation operations encountered. If a new rotation op is added, ensure any ``scale`` op
    in ``xformOpOrder`` occurs last.

    Args:
        prim: Prim for which to select a rotation operation.

    Returns:
        The selected rotation operation name.
    """
    # Get or create xformOpOrder attribute
    op_order_attr = prim.GetAttribute("xformOpOrder")
    if not op_order_attr:
        op_order_attr = prim.CreateAttribute("xformOpOrder", Sdf.ValueTypeNames.TokenArray, True)
        op_order_attr.Set([])

    op_order = op_order_attr.Get()
    if not op_order:
        op_order = []

    # Find transform and rotation ops
    rotation_op = None
    first_rotation_op = None
    rotation_ops_to_remove = []
    scale_index = -1

    for i, op in enumerate(op_order):
        if op == "xformOp:transform":
            rotation_op = op
            break  # Transform takes precedence, no need to continue
        elif op == "xformOp:orient" or op.startswith("xformOp:rotate"):
            if first_rotation_op is None:
                first_rotation_op = op
            else:
                rotation_ops_to_remove.append(i)
        elif op == "xformOp:scale":
            scale_index = i

    # If no transform op found, use first rotation op
    if rotation_op is None:
        rotation_op = first_rotation_op

    # Handle case where no rotation ops exist
    is_new_op = False
    if rotation_op is None:
        if not prim.HasAttribute("xformOp:rotateXYZ"):
            UsdGeom.Xformable(prim).AddRotateXYZOp()
        rotation_op = "xformOp:rotateXYZ"
        is_new_op = True

    # Update op_order if we need to remove ops or add new one
    needs_update = bool(rotation_ops_to_remove) or is_new_op
    if needs_update:
        # Convert to list for modification
        op_order = list(op_order)

        # Remove unused rotation ops (in reverse order to maintain indices)
        for i in reversed(rotation_ops_to_remove):
            op_order.pop(i)

        # Add new rotation op if needed
        if is_new_op:
            # Insert before scale op if it exists, otherwise at end
            insert_idx = scale_index if scale_index != -1 else len(op_order)
            # Adjust insert index if we removed ops before scale
            if scale_index != -1:
                removed_before_scale = sum(1 for i in rotation_ops_to_remove if i < scale_index)
                insert_idx = scale_index - removed_before_scale
            op_order.insert(insert_idx, rotation_op)

        # Update the attribute
        op_order_attr.Set(op_order)

    return rotation_op


def look_at(
    target: Union[Tuple[float, float, float], List[float], Gf.Vec3d],
    look_at_up_axis: Union[Tuple[float, float, float], List[float], Gf.Vec3d] = (0, 1, 0),
    eye: Union[Tuple[float, float, float], List[float], Gf.Vec3d] = (0, 0, 0),
    stage_up_axis: str = "Y",
    use_usdrt: bool = False,
) -> Gf.Rotation:
    """Calculate rotation to look at a target point.

    Args:
        target: Target point to look at, specified as (x, y, z) coordinates
        look_at_up_axis: Up vector for the look-at calculation, specified as (x, y, z) coordinates.
            Defaults to (0, 1, 0) which represents the Y-up axis.
        eye: Eye/camera position, specified as (x, y, z) coordinates.
            Defaults to (0, 0, 0) which represents the origin.
        use_usdrt: If True, use UsdRT functions, otherwise use PXR functions.

    Returns:
        Gf.Rotation object that can be used to get quaternion or matrix representation

    Raises:
        ValueError: If look_at_up_axis is zero vector or target yis at eye position
    """
    mod = usdrt if use_usdrt else pxr
    # Convert target to Vec3d if needed
    if isinstance(target, (tuple, list)):
        target = mod.Gf.Vec3d(*target)

    # Convert up axis to Vec3d if needed
    if isinstance(look_at_up_axis, (tuple, list)):
        look_at_up_axis = mod.Gf.Vec3d(*look_at_up_axis)

    # Convert eye position to Vec3d if needed
    if isinstance(eye, (tuple, list)):
        eye = mod.Gf.Vec3d(*eye)

    # Validate inputs
    target_eye_vec = target - eye
    if look_at_up_axis.GetLength() < 1e-6:
        raise ValueError("look_at_up_axis cannot be zero vector")
    if target_eye_vec.GetLength() < 1e-6:
        raise ValueError("target cannot be at eye position")
    is_collinear = np.all(np.cross(np.array(target_eye_vec), np.array(look_at_up_axis)) == 0)
    # Offset eye a little bit when look at axis is align with up axis
    if is_collinear:
        EPS = 1e-6
        if stage_up_axis == "Y":
            eye = eye + mod.Gf.Vec3d(0, 0, EPS)
        else:
            eye = eye + mod.Gf.Vec3d(EPS, 0, 0)

    # Normalize up vector
    up_vector = look_at_up_axis.GetNormalized()

    # Create look-at matrix
    look_at_matrix = mod.Gf.Matrix4d().SetLookAt(eye, target, up_vector)
    rotation_matrix = look_at_matrix.GetInverse().GetOrthonormalized()

    # Extract rotation
    return rotation_matrix.ExtractRotation()


def set_rotation_by_op(prim: Usd.Prim, rotation_op: str, rotation_value: Gf.Rotation):
    """Set the prim's rotation based on the rotation op provided

    Args:
        prim: Prim to rotate
        rotation_op: Rotation operation name (eg. rotateXYZ, rotateYZX, orientation, etc.)
        rotation_value: Value to set the rotation to.
    """
    if rotation_op == "xformOp:rotateXYZ":
        rotation_decomp = rotation_value.Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis())
        prim.GetAttribute(rotation_op).Set(Gf.Vec3f(rotation_decomp[2], rotation_decomp[1], rotation_decomp[0]))
    if rotation_op == "xformOp:rotateXZY":
        rotation_decomp = rotation_value.Decompose(Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis(), Gf.Vec3d.XAxis())
        prim.GetAttribute(rotation_op).Set(Gf.Vec3f(rotation_decomp[2], rotation_decomp[0], rotation_decomp[1]))
    elif rotation_op == "xformOp:rotateYXZ":
        rotation_decomp = rotation_value.Decompose(Gf.Vec3d.ZAxis(), Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis())
        prim.GetAttribute(rotation_op).Set(Gf.Vec3f(rotation_decomp[1], rotation_decomp[2], rotation_decomp[0]))
    elif rotation_op == "xformOp:rotateYZX":
        rotation_decomp = rotation_value.Decompose(Gf.Vec3d.XAxis(), Gf.Vec3d.ZAxis(), Gf.Vec3d.YAxis())
        prim.GetAttribute(rotation_op).Set(Gf.Vec3f(rotation_decomp[0], rotation_decomp[2], rotation_decomp[1]))
    elif rotation_op == "xformOp:rotateZXY":
        rotation_decomp = rotation_value.Decompose(Gf.Vec3d.YAxis(), Gf.Vec3d.XAxis(), Gf.Vec3d.ZAxis())
        prim.GetAttribute(rotation_op).Set(Gf.Vec3f(rotation_decomp[1], rotation_decomp[0], rotation_decomp[2]))
    elif rotation_op == "xformOp:rotateZYX":
        rotation_decomp = rotation_value.Decompose(Gf.Vec3d.XAxis(), Gf.Vec3d.YAxis(), Gf.Vec3d.ZAxis())
        prim.GetAttribute(rotation_op).Set(Gf.Vec3f(rotation_decomp[0], rotation_decomp[1], rotation_decomp[2]))
    elif rotation_op == "xformOp:orient":
        op_type = prim.GetAttribute(rotation_op).GetTypeName()
        if op_type == Sdf.ValueTypeNames.Quatf:
            quat = Gf.Quatf(rotation_value.GetQuat())
        elif op_type == Sdf.ValueTypeNames.Quatd:
            quat = Gf.Quatd(rotation_value.GetQuat())
        else:
            raise ValueError(
                f"Unable to set {rotation_op} on prim {prim.GetPath()}. Expected `quatf` or quatd` and got {op_type.aliasesAsStrings}"
            )
        prim.GetAttribute(rotation_op).Set(quat)
    elif rotation_op == "xformOp:transform":
        transform = Gf.Transform(prim.GetAttribute(rotation_op).Get())
        transform.SetRotation(rotation_value)
        prim.GetAttribute(rotation_op).Set(transform.GetMatrix())


def is_camera_prim(prim: Union[Usd.Prim, Sdf.Path, usdrt.Usd.Prim, usdrt.Sdf.Path]) -> bool:
    """Check if the prim is a camera prim

    Args:
        prim: Prim to check
    """
    stage = omni.usd.get_context().get_stage()
    if isinstance(prim, (Sdf.Path, usdrt.Sdf.Path)):
        prim = stage.GetPrimAtPath(str(prim))

    if prim.GetTypeName() == "Xform" and prim.HasAttribute("replicatorCameraXform"):
        for child in prim.GetChildren():
            if child.GetTypeName() == "Camera":
                return True
        return False
    else:
        return prim.GetTypeName() == "Camera"
