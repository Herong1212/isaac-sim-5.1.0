import math
import omni.kit.commands
from enum import Enum, auto
from pxr import Usd, Sdf, Tf
from typing import List, Tuple, Optional, Dict

from .command import AnimGraphUISetNodePositionCommand
from .config import Settings


class Port:
    class Kind(Enum):
        Output = auto()
        Input = auto()

    class Type(Enum):
        Unknown = auto()
        Flow = auto()
        Bool = auto()
        BoolArray = auto()
        Int = auto()
        IntArray = auto()
        Float = auto()
        FloatArray = auto()
        Token = auto()
        TokenArray = auto()
        String = auto()
        StringArray = auto()
        Float3 = auto()
        Float3Array = auto()
        Float4 = auto()
        Float4Array = auto()
        Object = auto()

        def __str__(self):
            return self.name

    def __init__(
        self,
        port_type: Type,
        port_kind: Kind,
        node_graph: "NodeGraph",
        rel_token: str = None,
        name: str = None,
        allow_multiple_connections: bool = False
    ):
        self._type = port_type
        self.kind = port_kind
        self.node_graph = node_graph
        self.rel_token = rel_token
        self._name = name
        self.allow_multiple_connections = allow_multiple_connections
        self.connected_ports: List[Port] = []
        self.position: Optional[Tuple[float, float]] = None
        self.transition_nodes: Dict[Port, Node] = {}

    @property
    def name(self):
        if self._name is not None:
            return self._name
        if self.rel_token is not None:
            return self.rel_token
        return ""

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def rel(self):
        if not self.rel_token:
            return
        node_path = self.node_graph.get_node_path(self)
        if node_path:
            node = self.node_graph.get_node(node_path)
            if node:
                prim = node.prim
                if prim:
                    return prim.GetRelationship(self.rel_token)

    @property
    def type(self) -> Type:
        return self._type

    @type.setter
    def type(self, value: Type):
        self._type = value

    def destroy(self):
        self._type = None
        self.kind = None
        self.node_graph = None
        self.rel_token = None
        self._name = None
        self.allow_multiple_connections = None
        self.connected_ports = None
        self.position = None
        self.transition_nodes = None


class Node:
    def __init__(
        self,
        prim: Usd.Prim,
        ports: List[Port],
        node_graph: "NodeGraph",
        sub_graph: "NodeGraph" = None
    ):
        self._prim = prim
        self.ports = ports
        self.node_graph = node_graph
        self.sub_graph = sub_graph
        self.visible = True
        self._compile_errors = None

    def destroy(self):
        self.prim = None

        for port in self.ports:
            port.destroy()

        self.ports = None
        self.node_graph = None

        if self.sub_graph:
            self.sub_graph.destroy()

        self.sub_graph = None
        self._compile_errors = None

    @property
    def prim(self):
        return self._prim

    @prim.setter
    def prim(self, value: Usd.Prim):
        self._prim = value

    @property
    def type(self):
        if not self.prim:
            return None
        return self.prim.GetTypeName()

    @property
    def name(self):
        if not self.prim:
            return None
        if self.prim.GetTypeName() == "State" or not Settings.get_show_name_as_type():
            return self.prim.GetName()
        else:
            return self.prim.GetTypeName()

    @name.setter
    def name(self, value):
        if not self.prim:
            return
        old_path = self.prim.GetPath()
        new_path = old_path.ReplaceName(Tf.MakeValidIdentifier(value))
        if old_path == new_path:
            return
        omni.kit.commands.execute("MovePrim", path_from=old_path, path_to=new_path)

    @property
    def description(self):
        if not self.prim:
            return None
        return self.prim.GetDocumentation()

    @property
    def position(self) -> Tuple[float, float]:
        attr_name = self._position_attribute_name
        if self.prim and self.prim.HasAttribute(attr_name):
            return self.prim.GetAttribute(attr_name).Get()
        return 0, 0

    @position.setter
    def position(self, value: Optional[Tuple[float, float]]):
        self.set_position(value)

    def set_position(self, value: Optional[Tuple[float, float]], disable_undo=False):
        def is_tuple_equal(a: Tuple[float, float], b: Tuple[float, float]):
            return math.isclose(a[0], b[0], rel_tol=1e-01) and math.isclose(a[1], b[1], rel_tol=1e-01)

        if value is None or not self.prim or is_tuple_equal(value, self.position):
            return

        if not disable_undo:
            omni.kit.commands.execute("AnimGraphUISetNodePositionCommand",
                                      prim=self.prim,
                                      position_attribute_name=self._position_attribute_name,
                                      value=value
                                      )
        else:
            AnimGraphUISetNodePositionCommand(
                prim=self.prim,
                position_attribute_name=self._position_attribute_name,
                value=value
            ).do()

    def has_sub_graph(self) -> bool:
        return self.sub_graph is not None

    @property
    def input(self) -> Port:
        for port in self.ports:
            if port.kind == Port.Kind.Input:
                return port

    @property
    def output(self) -> Port:
        for port in self.ports:
            if port.kind == Port.Kind.Output:
                return port

    @property
    def _position_attribute_name(self) -> str:
        if self.node_graph.parent_graph and self.node_graph.root_node == self:
            return "ui:subGraphPosition"
        return "ui:position"

    @property
    def errors(self) -> Optional[List[str]]:
        return self._compile_errors

    def set_compile_errors(self, node: Optional["Node"], compile_errors: List[str]):
        self._compile_errors = compile_errors
        self.node_graph._graph_changed(node)
        self.node_graph._graph_changed()


_variable_attr_type_to_port_type = {
    Sdf.ValueTypeNames.Bool: Port.Type.Bool,
    Sdf.ValueTypeNames.BoolArray: Port.Type.BoolArray,
    Sdf.ValueTypeNames.Float: Port.Type.Float,
    Sdf.ValueTypeNames.FloatArray: Port.Type.FloatArray,
    Sdf.ValueTypeNames.Int: Port.Type.Int,
    Sdf.ValueTypeNames.IntArray: Port.Type.IntArray,
    Sdf.ValueTypeNames.Token: Port.Type.Token,
    Sdf.ValueTypeNames.TokenArray: Port.Type.TokenArray,
    Sdf.ValueTypeNames.String: Port.Type.String,
    Sdf.ValueTypeNames.StringArray: Port.Type.StringArray,
    Sdf.ValueTypeNames.Float3: Port.Type.Float3,
    Sdf.ValueTypeNames.Float3Array: Port.Type.Float3Array,
    Sdf.ValueTypeNames.Float4: Port.Type.Float4,
    Sdf.ValueTypeNames.Float4Array: Port.Type.Float4Array
}


class VariableNodePort(Port):
    def __init__(
        self,
        node: "VariableNode",
        port_kind: Port.Kind,
        node_graph: "NodeGraph",
        allow_multiple_connections: bool = False,
        hide_name: bool = False
    ):
        self._node = node
        self._hide_name = hide_name

        super().__init__(Port.Type.Unknown, port_kind, node_graph, None, None, allow_multiple_connections)

    @property
    def name(self):
        if self._hide_name:
            return ""

        return self._node.name

    @property
    def type(self) -> Port.Type:
        variable_name = self._node.name
        if variable_name:
            variable_type = self.node_graph.root_graph.get_variable_type(variable_name)
            if variable_type:
                return _variable_attr_type_to_port_type.get(variable_type, Port.Type.Unknown)

        return Port.Type.Unknown


class VariableNode(Node):
    def __init__(self, prim: Usd.Prim, ports: List[VariableNodePort], node_graph: "NodeGraph"):
        self.__create_variable_name_attr(prim)

        super().__init__(prim, ports, node_graph)

    @Node.prim.setter
    def prim(self, value: Usd.Prim):
        self._prim = value
        if value:
            self.__create_variable_name_attr(value)

    @property
    def name(self):
        if not self._name_attr:
            return super().name
        name = self._name_attr.Get()
        if not name or len(name) == 0:
            return super().name
        return name

    @name.setter
    def name(self, value):
        if not self._name_attr:
            return
        if not self.node_graph.root_graph.has_variable(value):
            return
        omni.kit.commands.execute("ChangePropertyCommand", prop_path=self._name_attr.GetPath().pathString, value=value, prev=self._name_attr.Get())

    @property
    def variable_name_attribute(self):
        return self._name_attr

    @staticmethod
    def get_output_port_type(variable_type):
        return _variable_attr_type_to_port_type.get(variable_type)

    def __create_variable_name_attr(self, prim):
        self._name_attr = prim.CreateAttribute("inputs:variableName", Sdf.ValueTypeNames.Token, True, Sdf.VariabilityUniform)
        if not self._name_attr.Get():
            self._name_attr.Set(prim.GetName())


class ReadVariableNode(VariableNode):
    def __init__(self, prim: Usd.Prim, node_graph: "NodeGraph"):
        super().__init__(prim, [VariableNodePort(self, Port.Kind.Output, node_graph, True)], node_graph)
