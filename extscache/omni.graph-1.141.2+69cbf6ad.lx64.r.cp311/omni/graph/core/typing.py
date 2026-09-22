"""OmniGraph submodule that handles all of the OmniGraph API typing information.

.. code-block:: python

    import omni.graph.core.typing as ogty
    def do_attribute_stuff(attribute: ogty.Attribute_t):
        pass

The types that can be used to annotate values from any of the legal attribute data types can be found in the
list omni.graph.core.typing.ALL_DATA_TYPES.
"""

from ._impl.autonode_deprecated.data_typing import TypeConversion
from ._impl.type_aliases import (
    Attribute_t,
    Attributes_t,
    AttributeSpec_t,
    AttributeSpecs_t,
    AttributesWithValues_t,
    AttributeType_t,
    AttributeTypeSpec_t,
    AttributeWithValue_t,
    ExtendedAttribute_t,
    Graph_t,
    Graphs_t,
    GraphSpec_t,
    GraphSpecs_t,
    NewNode_t,
    Node_t,
    Nodes_t,
    NodeSpec_t,
    NodeSpecs_t,
    NodeType_t,
    Prim_t,
    PrimAttrs_t,
    Prims_t,
)
from ._impl.utils import AttributeValue_t, AttributeValues_t, ValueToSet_t

__all__ = [
    "Attribute_t",
    "Attributes_t",
    "AttributeSpec_t",
    "AttributeSpecs_t",
    "AttributesWithValues_t",
    "AttributeType_t",
    "AttributeTypeSpec_t",
    "AttributeValue_t",
    "AttributeValues_t",
    "AttributeWithValue_t",
    "ExtendedAttribute_t",
    "Graph_t",
    "Graphs_t",
    "GraphSpec_t",
    "GraphSpecs_t",
    "NewNode_t",
    "Node_t",
    "Nodes_t",
    "NodeSpec_t",
    "NodeSpecs_t",
    "NodeType_t",
    "Prim_t",
    "PrimAttrs_t",
    "Prims_t",
    "ValueToSet_t",
    "TypeConversion",
]
