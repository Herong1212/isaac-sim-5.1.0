"""
Utilities helpful for type resolution logic
"""

from typing import Sequence, Tuple

import omni.graph.core as og

__all__ = ["resolve_base_coupled", "resolve_fully_coupled"]


# ================================================================================
def resolve_fully_coupled(attributes: Sequence[og.Attribute]) -> None:
    """Resolves attribute types given a set of attributes which are fully type coupled.
    For example if node 'Increment' has one input attribute 'a' and one output attribute 'b'
    and we want the types of 'a' and 'b' to always match. This function will take under consideration
    the available conversions

    This function should only be called from `on_connection_type_resolve`.

    Args:
        attributes: list of extended attributes to be resolved
    """
    attributes[0].get_node().resolve_coupled_attributes(attributes)


# ================================================================================
def resolve_base_coupled(attribute_specs: Sequence[Tuple[og.Attribute, int, int, og.AttributeRole]]) -> None:
    """Resolves attribute types given a set of attributes, that can have differing tuple counts and/or array depth,
    and differing but convertible base data type.
    For example if node 'makeTuple2' has two input attributes 'a' and 'b' and one output 'c'
    and we want to resolve 'a':float, 'b':float, 'c':float[2] (convertible base types, different tuple counts)
    we would use the input:

    .. code-block:: python

        [
            (node.get_attribute("inputs:a"), None, None, None),
            (node.get_attribute("inputs:b"), None, None, None),
            (node.get_attribute("outputs:c"), None, 1, None)
        ]

    Assuming `a` gets resolved first, the None will be set to the respective values for the resolved type (`a`).
    For this example, it will use defaults tuple_count=1, array_depth=0, role=NONE.

    This function should only be called from `on_connection_type_resolve`.

    Args:
        attribute_specs: list of (attribute, tuple_count, array_depth, role) of extended attributes to be resolved.
        'None' for tuple_count, array_depth, or role means 'use the resolved type'.
    """
    attributes = [a for a, _, _, _ in attribute_specs]
    tuples = [255 if b is None else b for _, b, _, _ in attribute_specs]
    arrays = [255 if c is None else c for _, _, c, _ in attribute_specs]
    roles = [og.AttributeRole.NONE if d is None else d for _, _, _, d in attribute_specs]
    attributes[0].get_node().resolve_partially_coupled_attributes(attributes, tuples, arrays, roles)
