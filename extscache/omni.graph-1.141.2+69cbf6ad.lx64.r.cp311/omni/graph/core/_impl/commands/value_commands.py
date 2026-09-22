"""
Commands that modify values of an existing OmniGraph
"""

from typing import Optional

import carb
import omni.graph.core as og
import omni.kit
import omni.kit.commands
import omni.usd
from omni.graph.core._impl.utils import ValueToSet_t
from pxr import Sdf

from ...typing import Attribute_t
from .command_type_wrappers import (
    CommandAttributeWrapper,
    CommandGraphWrapper,
    CommandNodeWrapper,
    CommandVariableWrapper,
)


# ==============================================================================================================
class DisableNodeCommand(omni.kit.commands.Command):
    """
    Disable Node **Command**.  Causes a node to be disabled in the compute graph

    Args:
        node: The node to disable
    """

    def __init__(self, node: og.Node):
        self._node = CommandNodeWrapper(node)
        self._did_doit = False

    def do(self):
        disabled = self._node.object.is_disabled()
        if not disabled:
            self._node.object.set_disabled(True)
            self._did_doit = True

    def undo(self):
        if self._did_doit:
            self._node.object.set_disabled(False)


# ==============================================================================================================
class EnableNodeCommand(omni.kit.commands.Command):
    """
    Enable Node **Command**.  Causes a node to be enabled in the compute graph

    Args:
        node: The node to enable
    """

    def __init__(self, node: og.Node):
        self._node = CommandNodeWrapper(node)
        self._did_doit = False

    def do(self):
        disabled = self._node.object.is_disabled()
        if disabled:
            self._node.object.set_disabled(False)
            self._did_doit = True

    def undo(self):
        if self._did_doit:
            self._node.object.set_disabled(True)


# ==============================================================================================================
class DisableGraphCommand(omni.kit.commands.Command):
    """
    Disable Graph **Command**.  Causes a graph to be disabled

    Args:
        graph: The graph to disable
    """

    def __init__(self, graph):
        self._graph = CommandGraphWrapper(graph)
        self._did_doit = False

    def do(self):
        disabled = self._graph.object.is_disabled()
        if not disabled:
            self._graph.object.set_disabled(True)
            self._did_doit = True

    def undo(self):
        if self._did_doit:
            self._graph.object.set_disabled(False)


# ==============================================================================================================
class EnableGraphCommand(omni.kit.commands.Command):
    """
    Enable Graph **Command**.  Causes a graph to be enabled

    Args:
        graph: The graph to enable
    """

    def __init__(self, graph: og.Graph):
        self._graph = CommandGraphWrapper(graph)
        self._did_doit = False

    def do(self):
        disabled = self._graph.object.is_disabled()
        if disabled:
            self._graph.object.set_disabled(False)
            self._did_doit = True

    def undo(self):
        if self._did_doit:
            self._graph.object.set_disabled(True)


# ==============================================================================================================
class EnableGraphUSDHandlerCommand(omni.kit.commands.Command):
    """
    Enable Graph USD Handler **Command**.  Causes a graph's USD
    notice handdler to be enabled.

    Args:
        graph: The graph to enable notice handling
    """

    def __init__(self, graph: og.Graph):
        self._graph = CommandGraphWrapper(graph)
        self._did_doit = False

    def do(self):
        enabled = self._graph.object.usd_notice_handling_enabled()
        if not enabled:
            self._graph.object.set_usd_notice_handling_enabled(True)
            self._did_doit = True

    def undo(self):
        if self._did_doit:
            self._graph.object.set_usd_notice_handling_enabled(False)


# ==============================================================================================================
class DisableGraphUSDHandlerCommand(omni.kit.commands.Command):
    """
    Disable Graph USD Handler **Command**.  Causes a graph's USD
    notice handdler to be disabled.

    Args:
        graph: The graph to disable enotice handling
    """

    def __init__(self, graph: og.Graph):
        self._graph = CommandGraphWrapper(graph)
        self._did_doit = False

    def do(self):
        enabled = self._graph.object.usd_notice_handling_enabled()
        if enabled:
            self._graph.object.set_usd_notice_handling_enabled(False)
            self._did_doit = True

    def undo(self):
        if self._did_doit:
            self._graph.object.set_usd_notice_handling_enabled(True)


# ==============================================================================================================
class RenameNodeCommand(omni.kit.commands.Command):
    """
    Rename Node **Command**.  Renames an existing node in a compute graph

    Args:
        graph: The graph in which the node is located
        path: The location in the USD stage
        new_path: The new path of the node
    """

    def __init__(self, graph: og.Graph, path: str, new_path: str):
        self._graph = CommandGraphWrapper(graph)
        self._node_path = path
        self._new_node_path = new_path
        self._did_doit = False
        self._node = None

    def do(self):
        if not Sdf.Path.IsValidPathString(self._new_node_path):
            carb.log_error(f"Cannot rename {self._node_path} to {self._new_node_path} as it is not a valid USD path")
        elif self._graph.object.get_node(self._new_node_path).is_valid():
            carb.log_error(f"Cannot rename {self._node_path} to {self._new_node_path} as it already exists")
        else:
            self._node = self._graph.object.get_node(self._node_path)
            if self._node is not None and self._node.is_valid():
                if self._node.is_backed_by_usd():
                    # TODO: we want to rename the prim inside graph.rename_node() instead of using MovePrimCommand
                    #       see Graph::renameNodePath() in Graph.cpp for details
                    # Since we are doing it this hack'ish way, we need to disable USD notice handling in the graph
                    # so it doesn't respond to the move prim command, and so the subsequent call to rejig the graph
                    # state can happen free of interference from that other code path
                    omni.kit.commands.execute("DisableGraphUSDHandler", graph=self._graph.object)
                    omni.kit.commands.execute("MovePrim", path_from=self._node_path, path_to=self._new_node_path)
                    omni.kit.commands.execute("EnableGraphUSDHandler", graph=self._graph.object)

                # rename_node should come after USD rename
                self._graph.object.rename_node(self._node_path, self._new_node_path)
                self._did_doit = True

    def undo(self):
        if self._did_doit:
            # All the previously executed commands should undo automatically
            self._graph.object.rename_node(self._new_node_path, self._node_path)
            self._node = None
            self._did_doit = False


# ==============================================================================================================
class RenameSubgraphCommand(omni.kit.commands.Command):
    """
    Rename Subgraph **Command**.  Renames an existing subgraph in a compute graph

    Args:
        graph: The graph in which the subgraph is located
        path: The location in the USD stage
        new_path: The new path of the subgraph
    """

    def __init__(self, graph: og.Graph, path: str, new_path: str):
        self._graph = CommandGraphWrapper(graph)
        self._subgraph_path = path
        self._new_subgraph_path = new_path
        self._did_doit = False
        self._subgraph = None

    def do(self):
        if not Sdf.Path.IsValidPathString(self._new_subgraph_path):
            carb.log_error(
                f"Cannot rename {self._subgraph_path} to {self._new_subgraph_path} as it is not a valid USD path"
            )
        elif self._graph.object.get_subgraph(self._new_subgraph_path).is_valid():
            carb.log_error(f"Cannot rename {self._subgraph_path} to {self._new_subgraph_path} as it already exists")
        else:
            self._subgraph = self._graph.object.get_subgraph(self._subgraph_path)
            if self._subgraph is not None and self._subgraph.is_valid():
                # TODO: we want to rename the prim inside graph.rename_subgraph(), instead of using MovePrimCommand
                #       see Graph::renameSubgraphPath() in Graph.cpp for details
                omni.kit.commands.execute("DisableGraphUSDHandler", graph=self._graph.object)
                omni.kit.commands.execute("MovePrim", path_from=self._subgraph_path, path_to=self._new_subgraph_path)
                omni.kit.commands.execute("EnableGraphUSDHandler", graph=self._graph.object)
                # rename_subgraph should come after USD rename
                self._graph.object.rename_subgraph(self._subgraph_path, self._new_subgraph_path)
                self._did_doit = True
            else:
                carb.log_error(f"Subgraph path {self._subgraph_path} did not contain a valid subgraph")
        return self._did_doit

    def undo(self):
        if self._did_doit:
            # All the previously executed commands should undo automatically
            self._graph.object.rename_subgraph(self._new_subgraph_path, self._subgraph_path)
            self._did_doit = False
        return not self._did_doit


# ==============================================================================================================
class SetAttrCommand(omni.kit.commands.Command):
    """
    SetAttr **Command**.  Sets the value of an attribute on a node

    Args:
        attr: The attribute to set
        value: The value to set the attribute to
        set_type: The OGN type name to set the attribute to for extended attributes that require Type resolution.
                  You can also embed the type in the value using a TypedValue
        on_gpu: If True then set the value in the GPU memory, otherwise CPU memory
        update_usd: If True then immediately propagate the new value to the USD backing, if it exists
    """

    def __init__(
        self,
        attr: og.Attribute,
        value: ValueToSet_t,
        set_type: str = None,
        on_gpu: bool = False,
        update_usd: bool = True,
    ):
        self._did_doit = False
        self._attr = CommandAttributeWrapper(attr)
        self._value = value
        self._set_type = set_type
        self._old_value = None
        self._on_gpu = on_gpu
        self._update_usd = update_usd

    @staticmethod
    def do_immediate(
        attr: og.Attribute,
        value: ValueToSet_t,
        on_gpu: bool = False,
        update_usd: bool = True,
    ):
        og.AttributeValueHelper(attr).set(value, on_gpu, update_usd)

    def do(self):

        helper = self._attr.helper
        try:
            self._old_value = helper.get(self._on_gpu)
        except og.OmniGraphError:
            # This is expected for unresolved types
            if self._attr.object.get_resolved_type().base_type != og.BaseDataType.UNKNOWN:
                raise
            self._old_value = None
        helper.set(self._value, self._on_gpu, update_usd=self._update_usd)
        self._did_doit = True

    def undo(self):
        if self._did_doit and self._old_value is not None:
            # Blindly use the same memory type, so there will be a slight inefficiency in the case of calling this
            # command to set values on the opposite device they are currently on (i.e. setting the GPU value for
            # data currently on the CPU, and vice versa). Fabric will do that work for us.
            self._attr.helper.set(self._old_value, self._on_gpu, update_usd=self._update_usd)


# ==============================================================================================================
class SetAttrDataCommand(omni.kit.commands.Command):
    """
    SetAttrData **Command**.  Sets the value of an attribute data

    Args:
        attribute_data: The attribute data to set
        value: The value to be set
        graph: The graph to operate on (deprecated and unnecessary)
        on_gpu: If True then set the value in the GPU memory, otherwise CPU memory
    """

    def __init__(
        self,
        attribute_data: og.AttributeData,
        value: ValueToSet_t,
        graph: Optional[og.Graph] = None,
        on_gpu: bool = False,
    ):
        self._did_doit = False
        self._attribute_data = attribute_data
        self._value = value
        self._on_gpu = on_gpu
        self._old_value = None
        self._helper = og.AttributeDataValueHelper(attribute_data)
        if graph is not None:
            carb.log_warn("'graph' parameter to SetAttrData is deprecated and unnecessary and will be ignored.")

    @staticmethod
    def do_immediate(
        attribute_data: og.AttributeData,
        value: ValueToSet_t,
        on_gpu: bool = False,
    ):
        helper = og.AttributeDataValueHelper(attribute_data)
        if isinstance(value, og.TypedValue):
            carb.log_warn("Type is ignored when using SetAttrData, use SetAttr instead to set explicitly typed data")
            helper.set(value.value, on_gpu)
        else:
            helper.set(value, on_gpu)

    def do(self):
        self._old_value = self._helper.get(self._on_gpu)
        if isinstance(self._value, og.TypedValue):
            carb.log_warn("Type is ignored when using SetAttrData, use SetAttr instead to set explicitly typed data")
            self._helper.set(self._value.value, self._on_gpu)
        else:
            self._helper.set(self._value, self._on_gpu)
        self._did_doit = True

    def undo(self):
        if self._did_doit:
            # Blindly use the same memory type, so there will be a slight inefficiency in the case of calling this
            # command to set values on the opposite device they are currently on (i.e. setting the GPU value for
            # data currently on the CPU, and vice versa). Fabric will do that work for us.
            self._helper.set(self._old_value, self._on_gpu)


# ==============================================================================================================
class ChangePipelineStageCommand(omni.kit.commands.Command):
    """
    Change Pipeline Stage **Command**. Change the pipeline stage of an existing graph.

    Args:
        graph: The graph whose pipeline stage needs to be changed
        new_pipeline_stage: The new pipeline stage of the graph
    """

    def __init__(self, graph: og.Graph, new_pipeline_stage: og.GraphPipelineStage):
        self._graph = CommandGraphWrapper(graph)
        self._new_pipeline_stage = new_pipeline_stage
        self._old_pipeline_stage = None
        self._did_doit = False

    def do(self):
        self._old_pipeline_stage = self._graph.object.get_pipeline_stage()
        self._graph.object.change_pipeline_stage(self._new_pipeline_stage)
        self._did_doit = True

    def undo(self):
        if self._did_doit:
            self._graph.object.change_pipeline_stage(self._old_pipeline_stage)


# ==============================================================================================================
class SetEvaluationModeCommand(omni.kit.commands.Command):
    """
    Set Evaluation Mode **Command**. Change the evaluation mode of an existing graph.

    Args:
        graph: The graph to change the evaluation mode on
        new_evaluation_mode: The new graph evaluation mode
    """

    def __init__(self, graph: og.Graph, new_evaluation_mode: og.GraphEvaluationMode):
        self._graph = CommandGraphWrapper(graph)
        self._new_evaluation_mode = new_evaluation_mode
        self._old_evaluation_mode = None

    def do(self):
        self._old_evaluation_mode = self._graph.object.evaluation_mode
        self._graph.object.evaluation_mode = self._new_evaluation_mode

    def undo(self):
        if self._old_evaluation_mode is not None:
            self._graph.object.evaluation_mode = self._old_evaluation_mode
            self._old_evaluation_mode = None


# ==============================================================================================================
class SetVariableTooltipCommand(omni.kit.commands.Command):
    """
    Set Variable Tooltip **Command**. Set the tooltip/description of a variable.

    Args:
        variable: The variable to set the tooltip of
        tooltip: The tooltip text to set
    """

    def __init__(self, variable: og.IVariable, tooltip: str):
        self._variable = CommandVariableWrapper(variable)
        self._tooltip = tooltip
        self._old_tooltip = None
        self._set_tooltip = False

    def do(self):
        if not self._variable:
            return

        self._old_tooltip = self._variable.object.tooltip
        if self._old_tooltip == self._tooltip:
            return

        self._variable.object.tooltip = self._tooltip
        self._set_tooltip = True

    def undo(self):
        if not self._set_tooltip:
            return

        self._variable.object.tooltip = self._old_tooltip


# ==============================================================================================================
class MapAttrCommand(omni.kit.commands.Command):
    """
    Command to map an omnigraph attribute to a fabric attribute on the graph target

    Args:
        attr: The attribute to map.
        mapping: The attribute name on the graph target to map to. Use the empty string
        to clear a mapping

    Raises:
        og.OmniGraphError if the mapping cannot be applied, raise in immediate mode only
    """

    def __init__(self, attr: Attribute_t, mapping: str):
        self._attr = CommandAttributeWrapper(attr)
        self._mapping = mapping
        self._previous_mapping = None

    def do(self):
        self._previous_mapping = self._attr.object.target_mapping or ""
        try:
            MapAttrCommand.do_immediate(self._attr.object, self._mapping)
        except og.OmniGraphError as error:  # pragma: no cover
            carb.log_error(str(error))
            return False
        return True

    @staticmethod
    def do_immediate(attr: Attribute_t, mapping: str):
        try:
            attr.map_to_target(mapping)
        except ValueError as error:  # pragma: no cover
            raise og.OmniGraphError(str(error))

    def undo(self):
        if self._previous_mapping is not None:
            try:
                MapAttrCommand.do_immediate(self._attr.object, self._previous_mapping)
            except og.OmniGraphError as error:  # pragma: no cover
                carb.log_warning(str(error))
