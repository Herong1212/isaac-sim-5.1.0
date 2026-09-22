import omni.kit.commands
from omni.kit.usd_undo import UsdLayerUndo
from typing import List, Tuple, Callable, Optional, Dict, Set
from pxr import Usd, Sdf, Tf
import AnimGraphSchema
from omni.usd.commands import CreatePrimCommand, DeletePrimsCommand, AddRelationshipTargetCommand, RemoveRelationshipTargetCommand, MovePrimCommand
from .command import AnimGraphUIReplaceRelationshipTargetCommand, AnimGraphUISetRelationshipTargetsCommand
from .node import Port, Node, VariableNode, ReadVariableNode
from .sparse_list import SparseList
from .utils import relationship_has_target


def _blend_tree_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    input_pose_rel = prim.CreateRelationship("inputs:pose")
    if input_pose_rel:
        return Node(
            prim,
            [Port(Port.Type.Object, Port.Kind.Input, node_graph, input_pose_rel.GetName(), f"{input_pose_rel.GetDisplayName()} (Final)")], node_graph)


def _animation_clip_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    animation_clip = AnimGraphSchema.AnimationClip(prim)
    if animation_clip:
        return Node(
            prim,
            [Port(Port.Type.Object, Port.Kind.Output, node_graph, "outputs:pose", "Pose")], node_graph
        )


def _blend_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    blend = AnimGraphSchema.Blend(prim)
    if blend:
        return Node(
            prim,
            [Port(Port.Type.Object, Port.Kind.Output, node_graph, "outputs:pose", "Pose"),
             Port(Port.Type.Object, Port.Kind.Input, node_graph, blend.GetInputsPose0Rel().GetName(), blend.GetInputsPose0Rel().GetDisplayName()),
             Port(Port.Type.Object, Port.Kind.Input, node_graph, blend.GetInputsPose1Rel().GetName(), blend.GetInputsPose1Rel().GetDisplayName()),
             Port(Port.Type.Float, Port.Kind.Input, node_graph, blend.GetInputsBlendWeightRel().GetName(), blend.GetInputsBlendWeightRel().GetDisplayName())],
            node_graph
        )


def _condition_compare_variable_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    condition = AnimGraphSchema.ConditionCompareVariable(prim)
    if condition:
        # TODO: this needs to be dynamic when we support multiple value types.
        prim.CreateAttribute("inputs:value", Sdf.ValueTypeNames.String, True, Sdf.VariabilityUniform)

        return Node(
            prim,
            [Port(Port.Type.Bool, Port.Kind.Output, node_graph, "outputs:result", "Result")],
            node_graph
        )


def _condition_time_fraction_crossed_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    condition = AnimGraphSchema.ConditionTimeFractionCrossed(prim)
    if condition:
        return Node(
            prim,
            [Port(Port.Type.Bool, Port.Kind.Output, node_graph, "outputs:result", "Result")],
            node_graph
        )


def _condition_speed_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    condition = AnimGraphSchema.ConditionSpeed(prim)
    if condition:
        return Node(
            prim,
            [Port(Port.Type.Bool, Port.Kind.Output, node_graph, "outputs:result", "Result")],
            node_graph
        )

def _condition_and_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    condition = AnimGraphSchema.ConditionAND(prim)
    if condition:
        return Node(
            prim,
            [Port(Port.Type.Bool, Port.Kind.Input, node_graph, condition.GetInputsCondition0Rel().GetName(), condition.GetInputsCondition0Rel().GetDisplayName()),
            Port(Port.Type.Bool, Port.Kind.Input, node_graph, condition.GetInputsCondition1Rel().GetName(), condition.GetInputsCondition1Rel().GetDisplayName()),
            Port(Port.Type.Bool, Port.Kind.Output, node_graph, "outputs:result", "Result")],
            node_graph
        )

def _condition_or_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    condition = AnimGraphSchema.ConditionOR(prim)
    if condition:
        return Node(
            prim,
            [Port(Port.Type.Bool, Port.Kind.Input, node_graph, condition.GetInputsCondition0Rel().GetName(), condition.GetInputsCondition0Rel().GetDisplayName()),
            Port(Port.Type.Bool, Port.Kind.Input, node_graph, condition.GetInputsCondition1Rel().GetName(), condition.GetInputsCondition1Rel().GetDisplayName()),
            Port(Port.Type.Bool, Port.Kind.Output, node_graph, "outputs:result", "Result")],
            node_graph
        )

def _filter_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    filter = AnimGraphSchema.Filter(prim)
    if filter:
        return Node(
            prim,
            [Port(Port.Type.Object, Port.Kind.Output, node_graph, "outputs:pose", "Pose"),
             Port(Port.Type.Object, Port.Kind.Input, node_graph, filter.GetInputsPoseRel().GetName(), filter.GetInputsPoseRel().GetDisplayName())],
            node_graph
        )


def _look_at_ik_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    look_at_ik = AnimGraphSchema.LookAtIK(prim)
    if look_at_ik:
        return Node(
            prim,
            [Port(Port.Type.Object, Port.Kind.Output, node_graph, "outputs:pose", "Pose"),
             Port(Port.Type.Object, Port.Kind.Input, node_graph, look_at_ik.GetInputsPoseRel().GetName(), look_at_ik.GetInputsPoseRel().GetDisplayName()),
             Port(Port.Type.Float3, Port.Kind.Input, node_graph, look_at_ik.GetInputsTargetPositionRel().GetName(), look_at_ik.GetInputsTargetPositionRel().GetDisplayName()),
             Port(Port.Type.Float, Port.Kind.Input, node_graph, look_at_ik.GetInputsBlendWeightRel().GetName(), look_at_ik.GetInputsBlendWeightRel().GetDisplayName())],
            node_graph
        )


def _two_bone_ik_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    two_bone_ik = AnimGraphSchema.TwoBoneIK(prim)
    if two_bone_ik:
        return Node(
            prim,
            [Port(Port.Type.Object, Port.Kind.Output, node_graph, "outputs:pose", "Pose"),
             Port(Port.Type.Object, Port.Kind.Input, node_graph, two_bone_ik.GetInputsPoseRel().GetName(), two_bone_ik.GetInputsPoseRel().GetDisplayName()),
             Port(Port.Type.Float3, Port.Kind.Input, node_graph, two_bone_ik.GetInputsTargetPositionRel().GetName(), two_bone_ik.GetInputsTargetPositionRel().GetDisplayName()),
             Port(Port.Type.Float, Port.Kind.Input, node_graph, two_bone_ik.GetInputsBlendWeightRel().GetName(), two_bone_ik.GetInputsBlendWeightRel().GetDisplayName())],
            node_graph
        )


def _motion_matching_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    motion_matching = AnimGraphSchema.MotionMatching(prim)
    if motion_matching:
        return Node(
            prim,
            [Port(Port.Type.Object, Port.Kind.Output, node_graph, "outputs:pose", "Pose"),
             Port(Port.Type.Float3Array, Port.Kind.Input, node_graph, motion_matching.GetInputsPathPointsRel().GetName(), motion_matching.GetInputsPathPointsRel().GetDisplayName()),
             Port(Port.Type.Float3, Port.Kind.Input, node_graph, motion_matching.GetInputsMovementDirectionRel().GetName(), motion_matching.GetInputsMovementDirectionRel().GetDisplayName()),
             Port(Port.Type.Float3, Port.Kind.Input, node_graph, motion_matching.GetInputsForwardDirectionRel().GetName(), motion_matching.GetInputsForwardDirectionRel().GetDisplayName())],
            node_graph,
        )


def _pose_provider_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    pose_provider = AnimGraphSchema.PoseProvider(prim)
    if pose_provider:
        return Node(
            prim,
            [Port(Port.Type.Object, Port.Kind.Output, node_graph, "outputs:pose", "Pose"),
            Port(Port.Type.Float3Array, Port.Kind.Input, node_graph, pose_provider.GetInputsJointsPositionsRel().GetName(), pose_provider.GetInputsJointsPositionsRel().GetDisplayName()),
            Port(Port.Type.Float4Array, Port.Kind.Input, node_graph, pose_provider.GetInputsJointsRotationsRel().GetName(), pose_provider.GetInputsJointsRotationsRel().GetDisplayName()),
            Port(Port.Type.Float3, Port.Kind.Input, node_graph, pose_provider.GetInputsRootPositionDisplacementRel().GetName(), pose_provider.GetInputsRootPositionDisplacementRel().GetDisplayName()),
            Port(Port.Type.Float4, Port.Kind.Input, node_graph, pose_provider.GetInputsRootRotationDisplacementRel().GetName(), pose_provider.GetInputsRootRotationDisplacementRel().GetDisplayName()),
            Port(Port.Type.FloatArray, Port.Kind.Input, node_graph, pose_provider.GetInputsBlendShapesRel().GetName(), pose_provider.GetInputsBlendShapesRel().GetDisplayName())],
            node_graph
        )

def _full_body_ik_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    full_body_ik = AnimGraphSchema.FullBodyIK(prim)
    if full_body_ik:
        return Node(
            prim,
            [Port(Port.Type.Object, Port.Kind.Output, node_graph, "outputs:pose", "Pose"),
            Port(Port.Type.Object, Port.Kind.Input, node_graph, full_body_ik.GetInputsPoseRel().GetName(), full_body_ik.GetInputsPoseRel().GetDisplayName())],
            node_graph
        )

def _set_effector_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    set_effector = AnimGraphSchema.SetEffector(prim)
    if set_effector:
        return Node(
            prim,
            [Port(Port.Type.Object, Port.Kind.Output, node_graph, "outputs:pose", "Pose"),
             Port(Port.Type.Object, Port.Kind.Input, node_graph, set_effector.GetInputsPoseRel().GetName(), set_effector.GetInputsPoseRel().GetDisplayName()),
             Port(Port.Type.Float3, Port.Kind.Input, node_graph, set_effector.GetInputsPositionRel().GetName(), set_effector.GetInputsPositionRel().GetDisplayName()),
             Port(Port.Type.Float4, Port.Kind.Input, node_graph, set_effector.GetInputsRotationRel().GetName(), set_effector.GetInputsRotationRel().GetDisplayName()),
             Port(Port.Type.Float, Port.Kind.Input, node_graph, set_effector.CreateInputsPosition_alphaRel().GetName(), set_effector.CreateInputsPosition_alphaRel().GetDisplayName()),
             Port(Port.Type.Float, Port.Kind.Input, node_graph, set_effector.CreateInputsRotation_alphaRel().GetName(), set_effector.CreateInputsRotation_alphaRel().GetDisplayName())],
            node_graph
        )
def _state_builder(prim: Usd.Prim, node_graph: "NodeGraph", sub_graph=None) -> Node:
    if not sub_graph:
        sub_graph = NodeGraphDependency(prim, _blend_tree_builder, node_graph)

    return Node (
        prim,
        [Port(Port.Type.Flow, Port.Kind.Output, node_graph, "inputs:state", "State", True),
         Port(Port.Type.Flow, Port.Kind.Input, node_graph, "outputs:state", "State", True)],
        node_graph,
        sub_graph
    )


def _state_machine_root_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    node = Node(prim, [], node_graph)
    node.visible = False
    return node


def _state_machine_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    state_machine = AnimGraphSchema.StateMachine(prim)
    if state_machine:
        if isinstance(node_graph, NodeGraphStateMachine):
            return _state_builder(prim, node_graph, NodeGraphStateMachine(prim, node_graph))

        return Node(
            prim,
            [Port(Port.Type.Object, Port.Kind.Output, node_graph, "outputs:pose", "Pose")],
            node_graph,
            NodeGraphStateMachine(prim, node_graph)
        )


def _condition_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    inputs_condition_rel = prim.GetRelationship("inputs:condition")
    if inputs_condition_rel:
        return Node(
            prim,
            [Port(Port.Type.Bool, Port.Kind.Input, node_graph, inputs_condition_rel.GetName(), f"{inputs_condition_rel.GetDisplayName()} (Final)")],
            node_graph
        )


def _transition_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    if prim.IsA(AnimGraphSchema.Transition):
        node = Node(
            prim,
            [],
            node_graph,
            NodeGraphDependency(prim, _condition_builder, node_graph)
        )
        node.visible = False
        return node


def _read_variable_builder(prim: Usd.Prim, node_graph: "NodeGraph") -> Node:
    return ReadVariableNode(prim, node_graph)


_node_builder_table: Dict[str, Callable[[Usd.Prim, "NodeGraph"], Node]] = {
    "AnimationGraph": _blend_tree_builder,
    "ReadVariable": _read_variable_builder,
    "AnimationClip": _animation_clip_builder,
    "Blend": _blend_builder,
    "Filter": _filter_builder,
    "LookAtIK": _look_at_ik_builder,
    "TwoBoneIK": _two_bone_ik_builder,
    "MotionMatching": _motion_matching_builder,
    "PoseProvider": _pose_provider_builder,
    "FullBodyIK": _full_body_ik_builder,
    "SetEffector": _set_effector_builder,
    "StateMachine": _state_machine_builder,
    "State": _state_builder,
    "Transition": _transition_builder,
    "ConditionCompareVariable": _condition_compare_variable_builder,
    "ConditionTimeFractionCrossed": _condition_time_fraction_crossed_builder,
    "ConditionSpeed": _condition_speed_builder,
    "ConditionAND": _condition_and_builder,
    "ConditionOR": _condition_or_builder,
}

_variable_types: List[Sdf.ValueTypeName] = [
    Sdf.ValueTypeNames.Float,
    Sdf.ValueTypeNames.FloatArray,
    Sdf.ValueTypeNames.Float3,
    Sdf.ValueTypeNames.Float3Array,
    Sdf.ValueTypeNames.Float4,
    Sdf.ValueTypeNames.Float4Array,
    Sdf.ValueTypeNames.Bool,
    # Sdf.ValueTypeNames.BoolArray,
    Sdf.ValueTypeNames.Int,
    # Sdf.ValueTypeNames.IntArray,
    Sdf.ValueTypeNames.String,
    # Sdf.ValueTypeNames.StringArray,
    # Sdf.ValueTypeNames.Token,
    Sdf.ValueTypeNames.TokenArray
]


ANIM_GRAPH_VARIABLE_PREFIX = "anim:graph:variable:"


def _get_variable_attribute_name(variable_name: str):
    if variable_name.startswith(ANIM_GRAPH_VARIABLE_PREFIX):
        return variable_name

    return f"{ANIM_GRAPH_VARIABLE_PREFIX}{variable_name}"


class NodeGraph:
    def __init__(
        self,
        prim: Usd.Prim,
        root_node_builder: Callable[[Usd.Prim], Node],
        parent_graph: Optional["NodeGraph"]
    ):
        self._prim: Usd.Prim = prim
        self._stage = prim.GetStage()
        self._nodes: List[Node] = []
        self.parent_graph = parent_graph

        self._path_to_node: Dict[Sdf.Path, Node] = {}
        self._port_to_path: Dict[Port, Sdf.Path] = {}

        self._graph_changed_callbacks: SparseList[Callable[[Node], None]] = SparseList[Callable[[Node], None]]()

        self._sub_graph_callback_ids: Dict[Node, int] = {}

        self.root_node = self._create_node_from_prim(prim, root_node_builder)

        for child in prim.GetChildren():
            self._create_node_from_prim(child)

        self._create_connections()

    def destroy(self):
        self._prim = None
        self._stage = None

        for node in self._nodes:
            node.destroy()

        self._nodes = None
        self.parent_graph = None
        self._path_to_node = None
        self._port_to_path = None
        self._graph_changed_callbacks = None
        self._sub_graph_callback_ids = None
        self.root_node = None

    @property
    def prim(self) -> Usd.Prim:
        return self._prim

    @property
    def nodes(self) -> List[Node]:
        return [node for node in self._nodes if node.visible]

    @property
    def root_graph(self) -> "NodeGraphRoot":
        graph = self
        while not isinstance(graph, NodeGraphRoot):
            graph = graph.parent_graph

        return graph

    def is_valid(self) -> bool:
        return self._prim is not None

    def create_node(self, type_name: str, position: Tuple[float, float], node_name: str = None) -> Optional[Node]:
        return self._create_node(type_name, position, node_name)

    def delete_node(self, node: Node):
        self._delete_node(node)

    def get_node(self, path: Sdf.Path) -> Optional[Node]:
        return self._path_to_node.get(path)

    def get_node_path(self, port: Port) -> Optional[Sdf.Path]:
        return self._port_to_path.get(port)

    def search_node(self, path: Sdf.Path) -> Tuple[bool, Optional["NodeGraph"], Optional[Node]]:
        root_graph_path = self._prim.GetPath()
        if not path.HasPrefix(root_graph_path):
            return False, None, None

        graph = self
        relative_path = path.MakeRelativePath(root_graph_path)
        prefixes = relative_path.GetPrefixes()
        prefix_count = len(prefixes)

        if prefix_count > 0:
            for i in range(prefix_count - 1):
                found_node = graph._path_to_node.get(root_graph_path.AppendPath(prefixes[i]))
                if not found_node:
                    return False, None, None

                if not found_node.has_sub_graph():
                    break

                graph = found_node.sub_graph

        result_node = graph._path_to_node.get(path)
        if result_node:
            return True, graph, result_node

        return False, None, None

    def create_connection(self, output_port: Port, input_port: Port):
        self._create_connection(output_port, input_port)

    def delete_connection(self, output_port: Port, input_port: Port):
        self._delete_connection(output_port, input_port)

    def delete_connections(self, node: Node):
        self._delete_connections(node)

    def add_graph_changed_callback(self, callback: Callable[[Node], None]) -> Optional[int]:
        return self._graph_changed_callbacks.add(callback)

    def remove_graph_changed_callback(self, index: int) -> bool:
        return self._graph_changed_callbacks.remove(index)

    @staticmethod
    def set_skel_animation(anim_source_prim: Usd.Prim, skel_anim_prim: Usd.Prim):
        if skel_anim_prim.GetTypeName() != "SkelAnimation" or not anim_source_prim.IsA(AnimGraphSchema.AnimationClip):
            return

        anim_clip = AnimGraphSchema.AnimationClip(anim_source_prim)
        if anim_clip:
            source_rel = anim_clip.GetInputsAnimationSourceRel()
            if source_rel:
                omni.kit.commands.execute(
                    'AnimGraphUISetRelationshipTargetsCommand',
                    relationship=source_rel,
                    targets=[skel_anim_prim.GetPath()]
                )

    @staticmethod
    def get_supported_variable_types():
        return _variable_types

    def _create_node_from_prim(self, node_prim: Usd.Prim, node_builder: Callable[[Usd.Prim], Node] = None) \
            -> Optional[Node]:

        if not node_builder:
            type_name = node_prim.GetTypeName()
            node_builder = _node_builder_table.get(type_name)

        if node_builder:
            node = node_builder(node_prim, self)
            if node:
                self._nodes.append(node)
                prim_path = node_prim.GetPath()
                self._path_to_node[prim_path] = node
                for port in node.ports:
                    self._port_to_path[port] = prim_path

                NodeGraph.__set_last_node_path(node_prim)

                if node.has_sub_graph():
                    def sub_graph_changed(n: Node):
                        if n:
                            self._graph_changed(n)
                        else:
                            self._graph_changed(node)

                    self._sub_graph_callback_ids[node] = node.sub_graph.add_graph_changed_callback(sub_graph_changed)

                return node

        return None

    def _create_node(
        self,
        type_name: str,
        position: Tuple[float, float],
        node_name: str = None,
        disable_undo=False,
        select_new_prim=True
    ) -> Optional[Node]:
        if not self._prim:
            return None

        if not node_name:
            node_name = type_name

        path_string = omni.usd.get_stage_next_free_path(
            self._stage,
            self._prim.GetPath().AppendChild(node_name).pathString,
            False
        )

        def create():
            if disable_undo:
                CreatePrimCommand(
                    prim_type=type_name,
                    prim_path=path_string,
                    select_new_prim=select_new_prim
                ).do()
            else:
                omni.kit.commands.execute(
                    'CreatePrimCommand',
                    prim_type=type_name,
                    prim_path=path_string,
                    select_new_prim=select_new_prim
                )

            # Force USD update to trigger node creation
            self._usd_update()

            node = self._path_to_node.get(Sdf.Path(path_string))
            if node:
                node.set_position(position, disable_undo)
                if isinstance(node, VariableNode):
                    var_name_attr = node.variable_name_attribute
                    if var_name_attr:
                        var_name_attr.Set(node_name)

                if node.has_sub_graph():
                    # Certain node types may need to create new subnodes that should be included
                    # in a single undo command.
                    child_success = node.sub_graph._create_automatic_child_nodes(disable_undo)

                    if not child_success:
                        node = None

            return node

        if disable_undo:
            return create()
        else:
            with omni.kit.undo.group():
                return create()

    def _create_automatic_child_nodes(self, disable_undo=False) -> bool:
        return True

    def _delete_node(self, node: Node, disable_undo=False):
        if not node.prim:
            return

        node_path = node.prim.GetPath()
        if not self._path_to_node.get(node_path):
            return

        if disable_undo:
            DeletePrimsCommand(paths=[node_path]).do()
        else:
            omni.kit.commands.execute('DeletePrimsCommand', paths=[node_path])

    def _create_connection(self, output_port: Port, input_port: Port, disable_undo=False):
        pass

    def _delete_connection(self, output_port: Port, input_port: Port, disable_undo=False):
        pass

    def _create_connections(self):
        pass

    def _delete_connections(self, node: Node, disable_undo=False):
        if node not in self._nodes:
            return

        def delete():
            for port in node.ports:
                # create a copy of the list, as we are modifying it by deleting connections
                for connected_port in list(port.connected_ports):
                    if port.kind == Port.Kind.Output:
                        self._delete_connection(port, connected_port, disable_undo)
                    else:
                        self._delete_connection(connected_port, port, disable_undo)

        if disable_undo:
            delete()
        else:
            with omni.kit.undo.group():
                delete()

    def _update_all_connections(self):
        pass

    def _update_node_relationship(self, node: Node, rel: Usd.Relationship):
        pass

    def _graph_changed(self, node: Node = None):
        for callback in self._graph_changed_callbacks:
            if callback:
                callback(node)

    def _usd_update(self):
        self.parent_graph._usd_update()

    def _on_move_node(self, old_path: Sdf.Path, new_path: Sdf.Path):
        node = self._path_to_node.get(old_path)
        if not node:
            return

        new_prim = self._stage.GetPrimAtPath(new_path)
        if not new_prim:
            return

        if self._prim.GetPath() == old_path:
            self._prim = new_prim

        self._path_to_node.pop(old_path)

        node.prim = new_prim
        self._path_to_node[new_path] = node
        for port in node.ports:
            self._port_to_path[port] = new_path

        NodeGraph.__set_last_node_path(new_prim)

        if node.has_sub_graph():
            node.sub_graph._on_move_node(old_path, new_path)

        if node == self.root_node:
            for path in self._path_to_node.copy().keys():
                if path.HasPrefix(old_path):
                    self._on_move_node(path, path.ReplacePrefix(old_path, new_path))

    def _on_delete_node(self, delete_path: Sdf.Path):
        node = self._path_to_node.get(delete_path)
        if not node:
            return

        callback_id = self._sub_graph_callback_ids.get(node)
        if callback_id:
            if node.has_sub_graph():
                node.sub_graph.remove_graph_changed_callback(callback_id)

            self._sub_graph_callback_ids.pop(node)

        self._delete_connections(node, True)

        for port in node.ports:
            self._port_to_path.pop(port)

        self._path_to_node.pop(delete_path)
        self._nodes.remove(node)
        node.destroy()

        self._graph_changed()

    def _get_node_restore_data(self, node: Node) -> UsdLayerUndo:
        pass

    def _on_create_node(self, create_path: Sdf.Path) -> Tuple[bool, Optional[Node]]:
        node = self._path_to_node.get(create_path)
        if node:
            return False, node

        prim = self._stage.GetPrimAtPath(create_path)
        if prim:
            node = self._create_node_from_prim(prim)
            if node:
                self._graph_changed()
                return True, node

        return False, None

    @staticmethod
    def __set_last_node_path(node_prim):
        stage = node_prim.GetStage()
        with Usd.EditContext(stage, stage.GetEditTargetForLocalLayer(stage.GetSessionLayer())):
            node_prim.CreateAttribute(
                "lastNodePath",
                Sdf.ValueTypeNames.Token,
                True,
                Sdf.VariabilityUniform) \
                .Set(node_prim.GetPath().pathString)


class NodeGraphDependency(NodeGraph):
    def __init__(
        self,
        prim: Usd.Prim,
        root_node_builder: Callable[[Usd.Prim], Node],
        parent_graph: Optional[NodeGraph]
    ):
        super().__init__(prim, root_node_builder, parent_graph)

    def _create_connection(self, output_port: Port, input_port: Port, disable_undo=False):
        if output_port.kind != Port.Kind.Output or input_port.kind != Port.Kind.Input:
            return

        def create():
            replaced_output: Optional[Port] = None
            if not input_port.allow_multiple_connections and len(input_port.connected_ports) > 0:
                replaced_output = input_port.connected_ports[0]
                if input_port in replaced_output.connected_ports:
                    replaced_output.connected_ports.remove(input_port)
                input_port.connected_ports[0] = output_port
            else:
                input_port.connected_ports.append(output_port)

            if not output_port.allow_multiple_connections and len(output_port.connected_ports) > 0:
                replaced_input = output_port.connected_ports[0]
                if output_port in replaced_input.connected_ports:
                    replaced_input.connected_ports.remove(output_port)
                output_port.connected_ports[0] = input_port
                rel = replaced_input.rel
                if rel:
                    target_path = self.get_node_path(output_port)
                    if relationship_has_target(rel, target_path):
                        if disable_undo:
                            RemoveRelationshipTargetCommand(relationship=rel, target=target_path).do()
                        else:
                            omni.kit.commands.execute('RemoveRelationshipTargetCommand',
                                                      relationship=rel,
                                                      target=target_path)
            else:
                output_port.connected_ports.append(input_port)

            if replaced_output:
                if disable_undo:
                    AnimGraphUIReplaceRelationshipTargetCommand(
                        relationship=input_port.rel,
                        old_target=self.get_node_path(replaced_output),
                        new_target=self.get_node_path(output_port)
                    ).do()
                else:
                    omni.kit.commands.execute('AnimGraphUIReplaceRelationshipTargetCommand',
                                              relationship=input_port.rel,
                                              old_target=self.get_node_path(replaced_output),
                                              new_target=self.get_node_path(output_port))
            else:
                rel = input_port.rel
                if rel:
                    target_path = self.get_node_path(output_port)
                    if not relationship_has_target(rel, target_path):
                        if disable_undo:
                            AddRelationshipTargetCommand(relationship=rel, target=target_path).do()
                        else:
                            omni.kit.commands.execute('AddRelationshipTargetCommand',
                                                      relationship=rel,
                                                      target=target_path)

        if disable_undo:
            create()
        else:
            with omni.kit.undo.group():
                create()

        self._graph_changed()

    def _delete_connection(self, output_port: Port, input_port: Port, disable_undo=False):
        if output_port.kind != Port.Kind.Output or input_port.kind != Port.Kind.Input:
            return

        if input_port in output_port.connected_ports:
            output_port.connected_ports.remove(input_port)

        if output_port in input_port.connected_ports:
            input_port.connected_ports.remove(output_port)

        rel = input_port.rel
        if rel:
            target_path = self.get_node_path(output_port)
            if relationship_has_target(rel, target_path):
                if disable_undo:
                    RemoveRelationshipTargetCommand(relationship=rel, target=target_path).do()
                else:
                    omni.kit.commands.execute('RemoveRelationshipTargetCommand',
                                              relationship=rel,
                                              target=target_path)

        self._graph_changed()

    def _create_connections(self):
        for node in self._nodes:
            for port in node.ports:
                if port.kind == Port.Kind.Input:
                    rel = port.rel
                    if rel:
                        for target in rel.GetTargets():
                            target_node = self._path_to_node.get(target)
                            if target_node:
                                output = target_node.output
                                if output:
                                    port.connected_ports.append(output)
                                    output.connected_ports.append(port)

    def _update_all_connections(self):
        for node in self._nodes:
            for port in node.ports:
                if port.kind == Port.Kind.Input:
                    self._update_input_port(port)

    def _update_node_relationship(self, node: Node, rel: Usd.Relationship):
        for port in node.ports:
            if port.kind == Port.Kind.Input and port.rel == rel:
                self._update_input_port(port)
                break

    def _get_node_restore_data(self, node: Node) -> UsdLayerUndo:
        usd_undo = UsdLayerUndo(self._stage.GetEditTarget().GetLayer())
        for port in node.ports:
            if port.kind == Port.Kind.Output:
                for connected_port in port.connected_ports:
                    rel = connected_port.rel
                    if rel:
                        usd_undo.reserve(rel.GetPath())

        return usd_undo

    def _update_input_port(self, port: Port):
        if not port.kind == Port.Kind.Input:
            return

        rel = port.rel
        if not rel:
            return

        found_ports: Set[Port] = set()

        connected_ports = port.connected_ports.copy()
        targets = rel.GetTargets()
        for path in targets:
            found: bool = False
            for connected_port in connected_ports:
                if connected_port.kind == Port.Kind.Output and path == self.get_node_path(connected_port):
                    found_ports.add(connected_port)
                    found = True
                    break

            if not found:
                output_node = self._path_to_node.get(path)
                if output_node:
                    output_port = output_node.output
                    if output_port:
                        self._create_connection(output_port, port, True)

        deleted_connections: Set[Port] = set(connected_ports).difference(found_ports)
        for connected_port in deleted_connections:
            self._delete_connection(connected_port, port, True)


class NodeGraphRoot(NodeGraphDependency):
    def __init__(
        self,
        prim: Usd.Prim
    ):
        super().__init__(prim, _blend_tree_builder, None)

        self._usd_changed = False
        self._paths_to_add = set()
        self._paths_to_remove = set()
        self._parent_paths_to_remove = set()
        self._variable_props_to_add = set()
        self._variable_props_to_remove = set()
        self._renamed_variable_data = set()
        self._changed_property_paths = set()

        self._usd_listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self.__process_usd_change, None)

        update_event_stream = omni.kit.app.get_app_interface().get_update_event_stream()
        self._update_event_sub = update_event_stream.create_subscription_to_pop(
            lambda e: self._usd_update(),
            name=prim.GetName()
        )

        self._variables_changed_callbacks: SparseList[Callable[[str], None]] = SparseList[Callable[[str], None]]()

        self._deleted_prim_undo_map: Dict[Sdf.Path, UsdLayerUndo] = {}
        self._deleted_prop_undo_map: Dict[Sdf.Path, UsdLayerUndo] = {}
        self._changed_type_undo_map: Dict[Sdf.Path, UsdLayerUndo] = {}

        self._duplicated_paths: Dict[Sdf.Path, Sdf.Path] = {}

        def on_pre_duplicate(info):
            path_from = info.get("path_from", None)
            path_to = info.get("path_to", None)
            if path_from and path_to:
                self._duplicated_paths[Sdf.Path(path_from)] = Sdf.Path(path_to)

        self._duplicate_callback_sub = omni.kit.commands.register_callback(
            "CopyPrim",
            omni.kit.commands.PRE_DO_CALLBACK,
            on_pre_duplicate
        )

    def destroy(self):
        self._usd_listener = None
        self._update_event_sub.unsubscribe()
        self._update_event_sub = None

        self._usd_changed = None
        self._paths_to_add = None
        self._paths_to_remove = None
        self._parent_paths_to_remove = None
        self._variable_props_to_add = None
        self._variable_props_to_remove = None
        self._renamed_variable_data = None
        self._changed_property_paths = None
        self._variables_changed_callbacks = None
        self._deleted_prim_undo_map = None
        self._deleted_prop_undo_map = None
        self._changed_type_undo_map = None

        omni.kit.commands.unregister_callback(self._duplicate_callback_sub)
        self._duplicated_paths = None

        super().destroy()

    def create_variable(
        self,
        variable_name: str,
        variable_type: Sdf.ValueTypeName,
        default_value=None
    ) -> bool:
        if len(variable_name) == 0:
            return False

        attr_name = _get_variable_attribute_name(Tf.MakeValidIdentifier(variable_name))

        if self._prim.HasAttribute(attr_name):
            return False

        omni.kit.commands.execute(
            "CreateUsdAttribute",
            prim=self._prim,
            attr_name=attr_name,
            attr_type=variable_type,
            variability=Sdf.VariabilityUniform,
            attr_value=default_value
        )

        return self._prim.HasAttribute(attr_name)

    def delete_variable(self, variable_name: str) -> bool:
        attr_name = _get_variable_attribute_name(variable_name)
        if not self._prim.HasAttribute(attr_name):
            return False

        omni.kit.commands.execute(
            "RemoveProperty",
            prop_path=self._prim.GetPath().AppendProperty(attr_name)
        )

        return not self._prim.HasAttribute(attr_name)

    def get_variable_property(self, variable_name: str) -> Optional[Usd.Property]:
        attr_name = _get_variable_attribute_name(variable_name)
        if not self._prim.HasAttribute(attr_name):
            return None

        return self._prim.GetProperty(attr_name)

    def rename_variable(self, old_variable_name: str, new_variable_name: str) -> bool:
        if old_variable_name == new_variable_name:
            return False

        old_attr_name = _get_variable_attribute_name(old_variable_name)
        new_attr_name = _get_variable_attribute_name(new_variable_name)

        if not self._prim.HasAttribute(old_attr_name) or self._prim.HasAttribute(new_attr_name):
            return False

        omni.kit.commands.execute(
            "RenameAnimationGraphVariableAttributeCommand",
            prim=self._prim,
            old_attr_name=old_attr_name,
            new_attr_name=new_attr_name
        )

        return not self._prim.HasAttribute(old_attr_name) and self._prim.HasAttribute(new_attr_name)

    def change_variable_type(
        self,
        variable_name: str,
        new_variable_type: Sdf.ValueTypeName,
        new_variable_value=None
    ) -> bool:
        attr_name = _get_variable_attribute_name(variable_name)
        if not self._prim.HasAttribute(attr_name):
            return False

        if self.get_variable_type(variable_name) == new_variable_type:
            return False

        omni.kit.commands.execute(
            "SetAnimationGraphVariableAttributeTypeCommand",
            prim=self._prim,
            attr_name=attr_name,
            new_type=new_variable_type,
            new_value=new_variable_value
        )

        return self.get_variable_type(variable_name) == new_variable_type

    def get_variable_names(self):
        local_names = []
        for attr in self._prim.GetAttributes():
            attr_name = attr.GetName()
            if attr_name.startswith(ANIM_GRAPH_VARIABLE_PREFIX):
                local_names.append(Sdf.Path.StripNamespace(attr_name))

        return local_names

    def has_variable(self, variable_name: str):
        return self._prim.HasAttribute(_get_variable_attribute_name(variable_name))

    def get_variable_type(self, variable_name: str):
        attr = self._prim.GetAttribute(_get_variable_attribute_name(variable_name))
        if attr:
            return attr.GetTypeName()

        return None

    def get_variable_description(self, variable_name: str):
        attr = self._prim.GetAttribute(_get_variable_attribute_name(variable_name))
        if attr:
            return attr.GetDocumentation()

        return None

    def set_variable_description(self, variable_name: str, description: str):
        attr_name = _get_variable_attribute_name(variable_name)
        if not self._prim.HasAttribute(attr_name):
            return False

        if self.get_variable_description(variable_name) == description:
            return False

        omni.kit.commands.execute(
            "SetAnimationGraphVariableDescriptionCommand",
            prim=self._prim,
            attr_name=attr_name,
            description=description
        )

        return self.get_variable_description(variable_name) == description

    def add_variables_changed_callback(self, fn: Callable[[str], None]) -> Optional[int]:
        return self._variables_changed_callbacks.add(fn)

    def remove_variables_changed_callback(self, callback_id: int) -> bool:
        return self._variables_changed_callbacks.remove(callback_id)

    def get_next_variable_name(self, name: str):
        new_variable_name = name
        counter = 1
        while True:
            if not self.has_variable(new_variable_name):
                break

            new_variable_name = "{}{:02d}".format(name, counter)
            counter += 1

        return new_variable_name

    def __process_usd_change(self, objects_changed, stage):
        if stage is None or stage != self._stage:
            return

        variable_props_to_add = set()
        variable_props_to_remove = set()

        graph_path = self._prim.GetPath()
        for resync_path in objects_changed.GetResyncedPaths():
            if resync_path.IsPrimPath():
                prim = stage.GetPrimAtPath(resync_path)
                if prim:
                    self._paths_to_add.add(resync_path)
                elif graph_path.HasPrefix(resync_path):
                    self._parent_paths_to_remove.add(resync_path)
                elif resync_path.HasPrefix(graph_path):
                    self._paths_to_remove.add(resync_path)
            elif resync_path.IsPropertyPath():
                prop = stage.GetPropertyAtPath(resync_path)
                if prop:
                    self._changed_property_paths.add(resync_path)

                if resync_path.HasPrefix(graph_path) and resync_path.name.startswith(ANIM_GRAPH_VARIABLE_PREFIX):
                    if prop:
                        variable_props_to_add.add(resync_path)
                    else:
                        variable_props_to_remove.add(resync_path)

        if len(variable_props_to_add) == 1 and len(variable_props_to_remove) == 1:
            self._renamed_variable_data.add(
                (variable_props_to_remove.pop(), variable_props_to_add.pop())
            )
        else:
            self._variable_props_to_add.update(variable_props_to_add)
            self._variable_props_to_remove.update(variable_props_to_remove)

        self._changed_property_paths.update(
            [path for path in objects_changed.GetChangedInfoOnlyPaths() if path.IsPropertyPath()]
        )

        self._usd_changed = True

    def _usd_update(self):
        if not self._usd_changed or not self._stage:
            return

        paths_to_add = self._paths_to_add
        paths_to_remove = self._paths_to_remove
        parent_paths_to_remove = self._parent_paths_to_remove
        variable_props_to_add = self._variable_props_to_add
        variable_props_to_remove = self._variable_props_to_remove
        renamed_variable_data = self._renamed_variable_data
        changed_property_paths = self._changed_property_paths
        changed_variable_props = [path for path in changed_property_paths if
                                  path.name.startswith(ANIM_GRAPH_VARIABLE_PREFIX) and
                                  path not in variable_props_to_add and
                                  path not in variable_props_to_remove]
        duplicated_paths = self._duplicated_paths

        self._usd_changed = False
        self._paths_to_add = set()
        self._paths_to_remove = set()
        self._parent_paths_to_remove = set()
        self._variable_props_to_add = set()
        self._variable_props_to_remove = set()
        self._renamed_variable_data = set()
        self._changed_property_paths = set()
        self._duplicated_paths = {}

        self.__handle_moved_prims(paths_to_add, paths_to_remove, parent_paths_to_remove)

        if not self._prim:
            return

        self.__handle_deleted_prims(paths_to_remove)
        self.__handle_added_prims(paths_to_add, duplicated_paths)
        self.__handle_variable_changes(
            variable_props_to_add,
            variable_props_to_remove,
            renamed_variable_data,
            changed_variable_props
        )
        self.__handle_changed_properties(changed_property_paths)

    def __handle_moved_prims(self, paths_to_add: set, paths_to_remove: set, parent_paths_to_remove: set):
        graph_path = self._prim.GetPath()

        for removed_path in parent_paths_to_remove:
            for added_path in paths_to_add.copy():
                moved_path = graph_path.ReplacePrefix(removed_path, added_path)
                moved_prim = self._stage.GetPrimAtPath(moved_path)
                if moved_prim and moved_prim.HasAttribute("lastNodePath"):
                    last_path = Sdf.Path(moved_prim.GetAttribute("lastNodePath").Get())
                    if last_path == graph_path:
                        paths_to_add.remove(added_path)
                        self.__on_move_nodes([(self, graph_path, moved_path)])

        if len(paths_to_add) > 0 and len(paths_to_remove) > 0:
            path_move_tuples = []
            for added_path in paths_to_add.copy():
                new_prim = self._stage.GetPrimAtPath(added_path)
                if not new_prim or not new_prim.HasAttribute("lastNodePath"):
                    continue

                last_path = Sdf.Path(new_prim.GetAttribute("lastNodePath").Get())
                if last_path in paths_to_remove:
                    found, result_graph, result_node = self.search_node(last_path)
                    if not found:
                        continue

                    if not added_path.HasPrefix(result_graph.prim.GetPath()):
                        continue

                    path_move_tuples.append((result_graph, last_path, added_path))
                    paths_to_remove.remove(last_path)
                    paths_to_add.remove(added_path)

            if len(path_move_tuples) > 0:
                self.__on_move_nodes(path_move_tuples)

    def __handle_deleted_prims(self, paths_to_remove: set):
        for removed_path in paths_to_remove:
            if removed_path == self._prim.GetPath():
                continue

            found, result_graph, result_node = self.search_node(removed_path)
            if not found:
                continue

            if not omni.kit.undo.can_redo():
                self._deleted_prim_undo_map[removed_path] = result_graph._get_node_restore_data(result_node)

            result_graph._on_delete_node(removed_path)

    def __handle_added_prims(self, paths_to_add: set, duplicated_paths: Dict[Sdf.Path, Sdf.Path]):
        for added_path in paths_to_add:
            if not added_path.HasPrefix(self._prim.GetPath()):
                continue

            parent_path = added_path.GetParentPath()

            found, graph, parent_node = self.search_node(parent_path)
            if not found:
                continue

            if graph._prim.GetPath() == parent_path.GetParentPath() and parent_node.has_sub_graph():
                graph = parent_node.sub_graph

            if graph._prim.GetPath() == parent_path:
                success, new_node = graph._on_create_node(added_path)
                if success:
                    if omni.kit.undo.can_redo() and added_path in self._deleted_prim_undo_map.keys():
                        usd_undo = self._deleted_prim_undo_map.pop(added_path)
                        usd_undo.undo()
                    else:
                        for port in new_node.ports:
                            removed_path = False
                            new_paths = []

                            port_rel = port.rel
                            if not port_rel:
                                continue

                            paths = port_rel.GetTargets()
                            for target in paths:
                                if target in paths_to_add:
                                    new_paths.append(target)
                                else:
                                    removed_path = True

                                    if target in duplicated_paths.keys():
                                        new_paths.append(duplicated_paths[target])

                            if removed_path:
                                port_rel.SetTargets(new_paths)

                    graph._update_all_connections()

                    if added_path in duplicated_paths.values():
                        new_node.position += (40.0, 40.0)

    def __handle_changed_properties(self, changed_property_paths):
        for property_path in changed_property_paths:
            prim_path = property_path.GetPrimPath()
            prim = self._stage.GetPrimAtPath(prim_path)
            if not prim:
                continue

            found, result_graph, result_node = self.search_node(prim_path)
            if not found:
                continue

            prop_name = property_path.name
            if prim.HasRelationship(prop_name):
                rel = prim.GetRelationship(prop_name)

                if result_node.has_sub_graph():
                    sub_graph = result_node.sub_graph
                    sub_graph._update_node_relationship(sub_graph.root_node, rel)

                result_graph._update_node_relationship(result_node, rel)
            elif isinstance(result_node, VariableNode):
                var_name_attr = result_node.variable_name_attribute
                if var_name_attr and property_path == var_name_attr.GetPath():
                    value = var_name_attr.Get()
                    if self.has_variable(value):
                        output_port = result_node.output
                        output_port_type = output_port.type
                        for connected_port in output_port.connected_ports.copy():
                            if connected_port.type != output_port_type:
                                result_graph._delete_connection(output_port, connected_port, True)

                    result_graph._graph_changed()
            else:
                result_graph._graph_changed(result_node)

    def __on_move_nodes(self, path_move_tuples: List[Tuple[NodeGraph, Sdf.Path, Sdf.Path]]):
        for path_move_data in path_move_tuples:
            path_move_data[0]._on_move_node(path_move_data[1], path_move_data[2])

        for path_move_data in path_move_tuples:
            graph = path_move_data[0]
            old_path = path_move_data[1]
            new_path = path_move_data[2]

            for node in graph._nodes:
                prim = node.prim
                if prim:
                    for rel in prim.GetRelationships():
                        targets = rel.GetTargets()
                        update_rel = False
                        for i in range(len(targets)):
                            if targets[i].HasPrefix(old_path):
                                targets[i] = targets[i].ReplacePrefix(old_path, new_path)
                                update_rel = True

                        if update_rel:
                            rel.SetTargets(targets)

        self._graph_changed()

    def __handle_variable_changes(
        self,
        variable_props_to_add,
        variable_props_to_remove,
        renamed_variable_data,
        changed_variable_props
    ):
        def variables_changed_callbacks(name):
            for callback in self._variables_changed_callbacks:
                if callback is not None:
                    callback(name)

        for path in variable_props_to_add:
            variable_name = Sdf.Path.StripNamespace(path.name)
            if omni.kit.undo.can_redo() and path in self._deleted_prop_undo_map.keys():
                usd_undo = self._deleted_prop_undo_map.pop(path)
                usd_undo.undo()

            self.__handle_changed_variable_type(variable_name)
            variables_changed_callbacks(variable_name)

        for path in variable_props_to_remove:
            variable_name = Sdf.Path.StripNamespace(path.name)
            undo_data = self.__handle_deleted_variable(variable_name)
            if not omni.kit.undo.can_redo():
                self._deleted_prop_undo_map[path] = undo_data

            variables_changed_callbacks(variable_name)

        for rename_pair in renamed_variable_data:
            old_variable_name = Sdf.Path.StripNamespace(rename_pair[0].name)
            new_variable_name = Sdf.Path.StripNamespace(rename_pair[1].name)
            self.__handle_renamed_variable(old_variable_name, new_variable_name)
            variables_changed_callbacks(new_variable_name)

        for path in changed_variable_props:
            variables_changed_callbacks(Sdf.Path.StripNamespace(path.name))

    def __handle_deleted_variable(self, variable_name: str) -> UsdLayerUndo:
        usd_undo = UsdLayerUndo(self._stage.GetEditTarget().GetLayer())

        nodes = set(self._nodes)
        while len(nodes) > 0:
            node = nodes.pop()
            if isinstance(node, VariableNode) and node.name == variable_name:
                usd_undo.reserve(node.prim.GetPath())
                node.node_graph._delete_node(node, True)
                continue

            if node.has_sub_graph():
                nodes.update(node.sub_graph._nodes)

        return usd_undo

    def __handle_renamed_variable(self, old_variable_name: str, new_variable_name: str):
        nodes = set(self._nodes)
        while len(nodes) > 0:
            node = nodes.pop()
            if isinstance(node, VariableNode) and node.name == old_variable_name:
                var_name_attr = node.variable_name_attribute
                if var_name_attr:
                    var_name_attr.Set(new_variable_name)

                    old_prim_name = node.prim.GetName()
                    new_prim_name = old_prim_name.replace(old_variable_name, new_variable_name)
                    if old_prim_name != new_prim_name:
                        old_path = node.prim.GetPath()
                        new_path = old_path.ReplaceName(new_prim_name)
                        MovePrimCommand(
                            path_from=old_path,
                            path_to=new_path
                        ).do()

                    self._graph_changed(None)
                continue

            if node.has_sub_graph():
                nodes.update(node.sub_graph._nodes)

    def __handle_changed_variable_type(self, variable_name: str):
        nodes = set(self._nodes)
        while len(nodes) > 0:
            node = nodes.pop()
            if isinstance(node, VariableNode) and node.name == variable_name:
                path = node.prim.GetPath()
                if omni.kit.undo.can_redo():
                    if path in self._changed_type_undo_map.keys():
                        usd_undo = self._changed_type_undo_map.pop(path)
                        usd_undo.undo()
                else:
                    output_port = node.output
                    output_port_type = output_port.type
                    invalid_connections = []
                    for connected_port in output_port.connected_ports:
                        if connected_port.type != output_port_type:
                            invalid_connections.append(connected_port)

                    if len(invalid_connections) > 0:
                        node_graph = node.node_graph
                        self._changed_type_undo_map[path] = node_graph._get_node_restore_data(node)
                        for connection in invalid_connections:
                            node_graph._delete_connection(output_port, connection, True)

                self._graph_changed(None)
                continue

            if node.has_sub_graph():
                nodes.update(node.sub_graph._nodes)


class NodeGraphStateMachine(NodeGraph):
    def __init__(self, prim: Usd.Prim, parent_graph: NodeGraph):
        super().__init__(prim, _state_machine_root_builder, parent_graph)

    def get_start_state(self) -> Optional[Node]:
        if not self._prim:
            return
        state_machine = AnimGraphSchema.StateMachine(self._prim)
        if state_machine:
            start_state_rel = state_machine.GetInputsStartStateRel()
            if start_state_rel:
                targets = start_state_rel.GetTargets()
                if len(targets) > 0:
                    return self.get_node(targets[0])

    def set_start_state(self, node: Node):
        self._set_start_state(node)

    def _create_connection(self, output_port: Port, input_port: Port, disable_undo=False):
        if output_port.kind != Port.Kind.Output or input_port.kind != Port.Kind.Input:
            return

        if output_port in input_port.connected_ports or input_port in output_port.connected_ports:
            return

        node = self._create_node("Transition", (0, 0), None, disable_undo)
        if not node:
            return

        if not node.prim.IsA(AnimGraphSchema.Transition):
            return

        node.prim.GetRelationship("inputs:state").SetTargets([self.get_node_path(output_port)])
        node.prim.GetRelationship("outputs:state").SetTargets([self.get_node_path(input_port)])

        self._create_connection_from_transition(node)

    def _delete_connection(self, output_port: Port, input_port: Port, disable_undo=False):
        if output_port.kind != Port.Kind.Output or input_port.kind != Port.Kind.Input:
            return

        if output_port in input_port.connected_ports:
            input_port.connected_ports.remove(output_port)

        if input_port in output_port.connected_ports:
            output_port.connected_ports.remove(input_port)

        transition_node = output_port.transition_nodes.pop(input_port, None)
        input_port.transition_nodes.pop(output_port, None)

        if transition_node:
            self._delete_node(transition_node, disable_undo)

        self._graph_changed()

    def _create_automatic_child_nodes(self, disable_undo=False) -> bool:
        result_node = self._create_node("State", (0, 0), "Start", disable_undo, False)
        if result_node:
            self._set_start_state(result_node, disable_undo)
            return True
        return False

    def _create_connections(self):
        for node in self._nodes:
            if node.prim.IsA(AnimGraphSchema.Transition):
                self._create_connection_from_transition(node)

    def _delete_connections(self, node: Node, disable_undo=False):
        super()._delete_connections(node, disable_undo)

        node_prim = node.prim
        if node_prim:
            if node_prim.IsA(AnimGraphSchema.Transition):
                output_port, input_port = self._get_transition_ports(node_prim)
                if output_port and input_port:
                    self._delete_connection(output_port, input_port, disable_undo)
                else:
                    self._delete_stale_transition_connection(node, disable_undo)
        elif len(node.ports) == 0:
            # Special handling for Transition nodes, since the transition prim may be expired
            # need to traverse the graph to find the ports connected by the transition
            self._delete_stale_transition_connection(node, disable_undo)

    def _update_all_connections(self):
        self._create_connections()

    def _update_node_relationship(self, node: Node, rel: Usd.Relationship):
        if self._prim:
            state_machine = AnimGraphSchema.StateMachine(self._prim)
            if state_machine:
                if rel == state_machine.GetInputsStartStateRel():
                    self._graph_changed()
                    return

        if not node.prim.IsA(AnimGraphSchema.Transition):
            return

        is_inputs_state_rel = rel == node.prim.GetRelationship("inputs:state")
        is_outputs_state_rel = rel == node.prim.GetRelationship("outputs:state")
        if not is_inputs_state_rel and not is_outputs_state_rel:
            return

        success, output_port, input_port = self._create_connection_from_transition(node)
        if success:
            return

        connected_node = self._get_node_from_rel(rel)
        if connected_node:
            if is_inputs_state_rel:
                if connected_node.output == output_port:
                    return
            elif connected_node.input == input_port:
                return

        self._delete_stale_transition_connection(node, True)

    def _on_delete_node(self, delete_path: Sdf.Path):
        super()._on_delete_node(delete_path)

        if not self.get_start_state():
            visible_nodes = self.nodes
            if len(visible_nodes) == 1:
                self._set_start_state(visible_nodes[0], True)
            else:
                self._set_start_state(None, True)

    def _on_create_node(self, create_path: Sdf.Path) -> Tuple[bool, Optional[Node]]:
        return_tuple = super()._on_create_node(create_path)

        if not self.get_start_state():
            visible_nodes = self.nodes
            if len(visible_nodes) == 1:
                self._set_start_state(visible_nodes[0], True)

        return return_tuple

    def _get_node_restore_data(self, node: Node) -> UsdLayerUndo:
        usd_undo = UsdLayerUndo(self._stage.GetEditTarget().GetLayer())
        for port in node.ports:
            for transition_node in port.transition_nodes.values():
                usd_undo.reserve(transition_node.prim.GetPath())

        state_machine = AnimGraphSchema.StateMachine(self._prim)
        if state_machine:
            start_state_rel = state_machine.GetInputsStartStateRel()
            if start_state_rel:
                targets = start_state_rel.GetTargets()
                if (node.visible and len(self.nodes) == 2) or (len(targets) > 0 and targets[0] == node.prim.GetPath()):
                    usd_undo.reserve(start_state_rel.GetPath())

        return usd_undo

    def _delete_stale_transition_connection(self, node: Node, disable_undo=False):
        for graph_node in self._nodes:
            for port in graph_node.ports:
                for connected_port, transition_node in port.transition_nodes.items():
                    if transition_node == node:
                        if port.kind == Port.Kind.Output:
                            self._delete_connection(port, connected_port, disable_undo)
                        else:
                            self._delete_connection(connected_port, port, disable_undo)
                        return True

        return False

    def _set_start_state(self, node: Optional[Node], disable_undo=False):
        if not self._prim:
            return

        if node and (node not in self._nodes or not node.visible):
            return

        state_machine = AnimGraphSchema.StateMachine(self._prim)
        if state_machine:
            start_state_rel = state_machine.GetInputsStartStateRel()
            if start_state_rel:
                targets = start_state_rel.GetTargets()
                if node:
                    new_targets = [node.prim.GetPath()]
                else:
                    new_targets = []

                if targets != new_targets:
                    if disable_undo:
                        AnimGraphUISetRelationshipTargetsCommand(relationship=start_state_rel, targets=new_targets).do()
                    else:
                        omni.kit.commands.execute(
                            'AnimGraphUISetRelationshipTargetsCommand',
                            relationship=start_state_rel,
                            targets=new_targets
                        )

    def _create_start_connection(self, input_port: Port, disable_undo=False):
        output_port = self.root_node.output

        if output_port not in input_port.connected_ports:
            input_port.connected_ports.append(output_port)

        if input_port not in output_port.connected_ports:
            if len(output_port.connected_ports) > 0:
                old_input = output_port.connected_ports[0]
                output_port.connected_ports.remove(old_input)
                if output_port in old_input.connected_ports:
                    old_input.connected_ports.remove(output_port)

            output_port.connected_ports.append(input_port)

        self._set_start_state_rel(self.get_node_path(input_port), disable_undo)

    def _set_start_state_rel(self, path: Optional[Sdf.Path], disable_undo=False):
        state_machine = AnimGraphSchema.StateMachine(self._prim)
        if state_machine:
            start_state_rel = state_machine.GetInputsStartStateRel()
            if start_state_rel:
                targets = start_state_rel.GetTargets()
                if path:
                    new_targets = [path]
                else:
                    new_targets = []

                if targets != new_targets:
                    if disable_undo:
                        AnimGraphUISetRelationshipTargetsCommand(relationship=start_state_rel, targets=new_targets).do()
                    else:
                        omni.kit.commands.execute(
                            'AnimGraphUISetRelationshipTargetsCommand',
                            relationship=start_state_rel,
                            targets=new_targets
                        )

        self._graph_changed()

    def _create_connection_from_transition(
        self,
        transition_node: Node,
    ) -> Tuple[bool, Port, Port]:
        output_port, input_port = self._get_transition_ports(transition_node.prim)
        if not output_port or not input_port:
            return False, output_port, input_port

        if output_port in input_port.connected_ports and \
                input_port in output_port.connected_ports and \
                output_port.transition_nodes.get(input_port, None) == transition_node and \
                input_port.transition_nodes.get(output_port, None) == transition_node:
            return False, output_port, input_port

        input_port.connected_ports.append(output_port)
        input_port.transition_nodes[output_port] = transition_node
        output_port.connected_ports.append(input_port)
        output_port.transition_nodes[input_port] = transition_node

        self._graph_changed()

        return True, output_port, input_port

    def _get_node_from_rel(self, rel: Usd.Relationship) -> Optional[Node]:
        if not rel:
            return None
        paths = rel.GetTargets()
        if len(paths) == 0:
            return None
        return self._path_to_node.get(paths[0])

    def _get_transition_ports(self, transition_prim) -> Tuple[Optional[Port], Optional[Port]]:
        output_port: Optional[Port] = None
        input_state_node = self._get_node_from_rel(transition_prim.GetRelationship("inputs:state"))
        if input_state_node:
            output_port = input_state_node.output

        input_port: Optional[Port] = None
        ouput_state_node = self._get_node_from_rel(transition_prim.GetRelationship("outputs:state"))
        if ouput_state_node:
            input_port = ouput_state_node.input

        return output_port, input_port
