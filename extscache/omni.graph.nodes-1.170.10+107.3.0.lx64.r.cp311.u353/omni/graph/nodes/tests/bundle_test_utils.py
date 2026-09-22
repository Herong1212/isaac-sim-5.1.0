"""Collection of utilities to help with testing bundled attributes on OmniGraph nodes"""

import ast
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import omni.graph.core as og
import omni.graph.core.tests as ogts
import omni.graph.tools.ogn as ogn
from omni.graph.core.typing import Node_t, PrimAttrs_t

__all__ = [
    "bundle_inspector_results",
    "BundleInspectorResults_t",
    "BundleResultKeys",
    "enable_debugging",
    "filter_bundle_inspector_results",
    "get_bundle_with_all_results",
    "prim_with_everything_definition",
    "verify_bundles_are_equal",
]


# ==============================================================================================================
@dataclass
class BundleResultKeys:
    """Container for the keys used in the bundle result values and the index in the return tuple that each one uses"""

    COUNT = "outputs:count"
    NAME = "outputs:names"
    TYPE = "outputs:types"
    TYPE_IDX = 0
    TUPLE_COUNT = "outputs:tupleCounts"
    TUPLE_COUNT_IDX = 1
    ARRAY_DEPTH = "outputs:arrayDepths"
    ARRAY_DEPTH_IDX = 2
    ROLE = "outputs:roles"
    ROLE_IDX = 3
    VALUE = "outputs:values"
    VALUE_IDX = 4


# ==============================================================================================================
BundleInspectorResults_t = Tuple[int, Dict[str, Tuple[str, str, int, int, Any]]]
"""Results extracted from a bundle inspector's output attributes by NAME:VALUE. The first value is the count output.
The dictionary is a mapping of name to (type, role, arrayDepth, tupleCount, value). It's stored this way to make it
easier to guarantee ordering of the lists so that they can be easily compared.
"""


# ======================================================================
# Special value used by the bundle inspector node when the output for the bundled attribute is not yet supported
_BUNDLE_INSPECTOR_UNSUPPORTED_DATA = "__unsupported__"


# ======================================================================
def enable_debugging(bundle_inspector_node_name: Union[og.Node, str]):
    """Sets the debugging input value to true on the given omnigraph.nodes.bundleInspector
    Raises:
        AttributeError if the node is not a bundle inspector type
    """
    graph = og.get_all_graphs()[0]
    if isinstance(bundle_inspector_node_name, og.Node):
        bundle_node = bundle_inspector_node_name
    else:
        bundle_node = graph.get_node(bundle_inspector_node_name)
    print_attribute = bundle_node.get_attribute("inputs:print")
    og.Controller.set(print_attribute, True)


# ======================================================================
def prim_with_everything_definition(
    type_names_to_filter: Optional[List[str]] = None, filter_for_inclusion: bool = True
) -> PrimAttrs_t:
    """Generates an og.Controller prim creation specification for a prim containing one of every attribute.

    The name of the attribute is derived from the type.
        int -> IntAttr
        int[] -> IntArrayAttr
        int[3] -> Int3Attr
        int[3][] -> Int3ArrayAttr

    Args:
        type_names_to_filter: List of type names to check for inclusion. If empty no filtering happens. The type names
                              should be in OGN format (e.g. "int[3][]")
        filter_for_inclusion: If True then the type_names_to_filter is treated as the full list of type names to
                              include, otherwise it is treated as a list of types to exclude from the list of all types.

    Return:
        A dictionary containing a prim definition that matches what is required by og.Controller.create_prim with
        all of the specified attributes defined on the prim.
    """

    def __type_passes_filter(type_name: str) -> bool:
        """Returns True iff the filters allow the type_name to be included"""
        # The deprecated transform type always fails the filter
        if type_name.startswith("transform"):
            return False
        if filter_for_inclusion:
            return type_names_to_filter is None or type_name in type_names_to_filter
        return type_names_to_filter is None or type_name not in type_names_to_filter

    definition = {}
    for attribute_type_name in ogn.supported_attribute_type_names():
        # Skip the types that are filtered
        if not __type_passes_filter(attribute_type_name):
            continue
        manager = ogn.get_attribute_manager_type(attribute_type_name)
        sdf_type_name = manager.sdf_type_name()
        # Skip the types that don't correspond to USD types
        if sdf_type_name is not None:
            attribute_name = f"{sdf_type_name}Attr"
            values = manager.sample_values()
            definition[attribute_name] = (attribute_type_name, values[0])

    return definition


# ======================================================================
def get_bundle_with_all_results(
    prim_source_path: Optional[str] = None,
    type_names_to_filter: Optional[List[str]] = None,
    filter_for_inclusion: bool = True,
    prim_source_type: Optional[str] = None,
) -> BundleInspectorResults_t:
    """Generates a dictionary of expected bundle inspector contents from a bundle constructed with a filtered list
    of all attribute types.

    The name of the attribute is derived from the type.
        int -> IntAttr
        int[] -> IntArrayAttr
        int[3] -> Int3Attr
        int[3][] -> Int3ArrayAttr

    Args:
        prim_source_path: Source of the prim from which the bundle was extracted (to correctly populate the extra
                          attribute the ReadPrim nodes add). If None then no prim addition is required.
        type_names_to_filter: List of type names to check for inclusion. If empty no filtering happens. The type names
                              should be in OGN format (e.g. "int[3][]")
        filter_for_inclusion: If True then the type_names_to_filter is treated as the full list of type names to
                              include, otherwise it is treated as a list of types to exclude from the list of all types.
        prim_source_type: Type of the source prim.

    Return:
        A dictionary containing a BundleInspector attribute name mapped onto the value of that attribute. Only the
        output attributes are considered.
    """

    def __type_passes_filter(type_name: str) -> bool:
        """Returns True iff the filters allow the type_name to be included"""
        # The deprecated transform type always fails the filter
        if type_name.startswith("transform"):
            return False
        if filter_for_inclusion:
            return type_names_to_filter is None or type_name in type_names_to_filter
        return type_names_to_filter is None or type_name not in type_names_to_filter

    # This token is hardcoded into the ReadPrimBundle node and will always be present regardless of the prim contents.
    # This requires either the prim path be "TestPrim", or the value be adjusted to reflect the actual prim
    per_name_results = {}

    for attribute_type_name in ogn.supported_attribute_type_names():
        # Skip the types that are filtered
        if not __type_passes_filter(attribute_type_name):
            continue
        manager = ogn.get_attribute_manager_type(attribute_type_name)
        sdf_type_name = manager.sdf_type_name()
        # Skip the types that don't correspond to USD types
        if sdf_type_name is not None:
            attribute_type = og.AttributeType.type_from_ogn_type_name(attribute_type_name)
            attribute_name = f"{sdf_type_name}Attr"
            values = manager.sample_values()
            per_name_results[attribute_name] = (
                attribute_type.get_base_type_name(),
                attribute_type.tuple_count,
                attribute_type.array_depth,
                attribute_type.get_role_name(),
                values[0],
            )
    if prim_source_path is not None:
        per_name_results.update({"sourcePrimPath": ("token", 1, 0, "none", prim_source_path)})

    if prim_source_type is not None:
        per_name_results.update({"sourcePrimType": ("token", 1, 0, "none", prim_source_type)})

    return (len(per_name_results), per_name_results)


# ======================================================================
def bundle_inspector_results(inspector_spec: Node_t) -> BundleInspectorResults_t:
    """Returns attribute values computed from a bundle inspector in the same form as inspected_bundle_values

    Args:
        inspector_spec: BundleInspector node from which to extract the output values

    Return:
        Output values of the bundle inspector, formatted for easier comparison.

    Raises:
        og.OmniGraphError if anything in the inspector outputs could not be interpreted
    """
    inspector_node = og.Controller.node(inspector_spec)
    output = {}
    for inspector_attribute in inspector_node.get_attributes():
        attribute_name = inspector_attribute.get_name()
        if inspector_attribute.get_port_type() != og.AttributePortType.ATTRIBUTE_PORT_TYPE_OUTPUT:
            continue
        if inspector_attribute.get_type_name() == "bundle":
            continue
        values = og.Controller.get(inspector_attribute)
        if inspector_attribute.get_name().endswith("values"):
            # Bundled values are formatted as strings but are actually a mixture of types
            values = [
                (
                    ast.literal_eval(value)
                    if value != _BUNDLE_INSPECTOR_UNSUPPORTED_DATA
                    else _BUNDLE_INSPECTOR_UNSUPPORTED_DATA
                )
                for value in values
            ]
        output[attribute_name] = values

    # Catch the case of an empty bundle separately
    if not output:
        return (0, {})

    try:
        count = output[BundleResultKeys.COUNT]
        per_name_values = {
            name: (v1, v2, v3, v4, v5)
            for name, v1, v2, v3, v4, v5 in zip(
                output[BundleResultKeys.NAME],
                output[BundleResultKeys.TYPE],
                output[BundleResultKeys.TUPLE_COUNT],
                output[BundleResultKeys.ARRAY_DEPTH],
                output[BundleResultKeys.ROLE],
                output[BundleResultKeys.VALUE],
            )
        }
    except Exception as error:
        raise og.OmniGraphError(error)

    return (count, per_name_values)


# ==============================================================================================================
def verify_bundles_are_equal(
    actual_values: BundleInspectorResults_t, expected_values: BundleInspectorResults_t, check_values: bool = True
):
    """Check that the contents of the actual values received from a bundle inspector match the expected values.

    Args:
        actual_values: Bundle contents read from the graph
        expected_values: Test bundle contents expected
        check_values: If True then check that attribute values as well as the type information, otherwise just types

    Raises:
        ValueError: if the contents differ. The message in the exception explains how they differ
    """
    (actual_count, actual_results) = actual_values
    (expected_count, expected_results) = expected_values

    def __compare_attributes(attribute_name: str):
        """Compare a single attribute's result from the bundle inspected, raising ValueError if not equal"""
        actual_value = actual_results[attribute_name]
        expected_value = expected_results[attribute_name]
        try:
            if actual_value[0] != expected_value[0]:
                raise ValueError("Type mismatch")
            if actual_value[1] != expected_value[1]:
                raise ValueError("Tuple count mismatch")
            if actual_value[2] != expected_value[2]:
                raise ValueError("Array depth mismatch")
            if actual_value[3] != expected_value[3]:
                raise ValueError("Role mismatch")
            if check_values:
                ogts.verify_values(actual_value[4], expected_value[4], "Value mismatch")
        except ValueError as error:
            raise ValueError(
                f"Actual value for '{attribute_name}' of '{actual_value}' did not match expected value"
                f" of '{expected_value}'"
            ) from error

    actual_names = set(actual_results.keys())
    expected_names = set(expected_results.keys())
    name_difference = actual_names.symmetric_difference(expected_names)
    if name_difference:
        problems = []
        extra_actual_results = actual_names.difference(expected_names)
        if extra_actual_results:
            problems.append(f"Actual members {extra_actual_results} not expected.")
        extra_expected_results = expected_names.difference(actual_names)
        if extra_expected_results:
            problems.append(f"Expected members {extra_expected_results} not found.")
        problem = "\n".join(problems)
        raise ValueError(f"Actual output attribute names differ from expected list: {problem}")

    if actual_count != expected_count:
        raise ValueError(f"Expected {expected_count} results, actual value was {actual_count}")

    for output_attribute_name in actual_results.keys():
        __compare_attributes(output_attribute_name)


# ==============================================================================================================
def filter_bundle_inspector_results(
    raw_results: BundleInspectorResults_t,
    names_to_filter: Optional[List[str]] = None,
    filter_for_inclusion: bool = True,
) -> BundleInspectorResults_t:
    """Filter out the results retrieved from a bundle inspector by name

    Args:
        names_to_filter: List of attribute names to check for inclusion.
        filter_for_inclusion: If True then the names_to_filter is treated as the full list of names to include,
                              otherwise it is treated as a list of names to exclude from the list of all names.

    Return:
        The raw_results with the above filtering performed
    """

    def __type_passes_filter(name: str) -> bool:
        """Returns True iff the filters allow the name to be included"""
        if filter_for_inclusion:
            return names_to_filter is None or name in names_to_filter
        return names_to_filter is None or name not in names_to_filter

    (_, results) = raw_results
    filtered_results = {}
    for attribute_name, attribute_values in results.items():
        if __type_passes_filter(attribute_name):
            filtered_results[attribute_name] = attribute_values

    return (len(filtered_results), filtered_results)
