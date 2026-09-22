"""
Helper classes for og Commands. These classes abstract the object to protect from
the og object being destroyed by other commands.
"""

from typing import Optional

import omni.graph.core as og

from ..type_aliases import Attribute_t, Graph_t, Node_t, Variable_t


# ==============================================================================================================
class CommandNodeWrapper:
    """
    Wraps an og.Node obj for use in commands, where the underlying object may be destroyed

    Args:
        The node object to store.
    """

    def __init__(self, node: Node_t):
        self._node_path = og.ObjectLookup.node(node).get_prim_path()

    @property
    def object(self) -> og.Node:  # noqa: A003
        return og.ObjectLookup.node(self._node_path)

    @property
    def path(self) -> str:
        return self._node_path


# ==============================================================================================================
class CommandAttributeWrapper:
    """
    Wraps an og.Attribute for use in commands, where the underlying attribute object may be destroyed.

    Args:
        The attribute object to store
    """

    def __init__(self, attribute: Attribute_t):
        self._attr_path = og.ObjectLookup.attribute(attribute).get_path()

    @property
    def object(self) -> og.Attribute:  # noqa: A003
        return og.ObjectLookup.attribute(self._attr_path)

    @property
    def path(self) -> str:
        return self._attr_path

    @property
    def helper(self) -> og.AttributeValueHelper:
        return og.AttributeValueHelper(self.object)


# ==============================================================================================================
class CommandGraphWrapper:
    """
    Wraps an og.Graph for use in commands, where the underlying object may be destroyed

    Args:
        The graph object to store
    """

    def __init__(self, graph: Graph_t):
        self._graph = og.ObjectLookup.graph(graph)
        self._graph_path = self._graph.get_path_to_graph()

    @property
    def object(self) -> Optional[og.Graph]:  # noqa: A003
        if self._graph.is_valid():
            return self._graph
        if self._graph_path:
            self._graph = og.ObjectLookup.graph(self._graph_path)
            if self._graph.is_valid():
                return self._graph

        return None

    @property
    def path(self) -> str:
        return self._graph_path


# ==============================================================================================================
class CommandVariableWrapper:
    """
    Wraps an og.IVariable for use in commands, where the underlying object may be destroyed

    Args:
        The variable object to store
    """

    def __init__(self, variable: Variable_t):
        self._var_path = og.ObjectLookup.variable(variable).source_path

    @property
    def object(self) -> og.IVariable:  # noqa: A003
        return og.ObjectLookup.variable(self._var_path)

    @property
    def path(self) -> str:
        return self._var_path
