"""
Constants used in parsing attributes in a .ogn file
"""

import ast
from typing import List, Tuple

from ..keys import AttributeKeys

# ======================================================================
# Legacy keyword support - use the values from keys.py for new code
KEY_ATTR_DEFAULT = AttributeKeys.DEFAULT
KEY_ATTR_DESCRIPTION = AttributeKeys.DESCRIPTION
KEY_ATTR_MINIMUM = AttributeKeys.MINIMUM
KEY_ATTR_MAXIMUM = AttributeKeys.MAXIMUM
KEY_ATTR_MEMORY_TYPE = AttributeKeys.MEMORY_TYPE
KEY_ATTR_METADATA = AttributeKeys.METADATA
KEY_ATTR_OPTIONAL = AttributeKeys.OPTIONAL
KEY_ATTR_TYPE = AttributeKeys.TYPE
KEY_ATTR_UI_NAME_METADATA = AttributeKeys.UI_NAME
KEY_ATTR_UNVALIDATED = AttributeKeys.UNVALIDATED
MANDATORY_ATTR_KEYS = AttributeKeys.MANDATORY
PROCESSED_ATTR_KEYS = AttributeKeys.PROCESSED


# ======================================================================
def attributes_as_usd(attribute_info: List[Tuple[str, str]]) -> List[str]:
    """Returns a list of the attribute definitions in the USDA file format

    Most attributes are listed as their normal type, with a few exceptions:
        prim: Output bundles
        any: Extended attribute type with any value
        union[a,b,c...] Extended attribute type with any of the types a, b, c...
    """
    usd_lines = []
    metadata = {}
    for attr_type, attr_name in attribute_info:
        if attr_type == "bundle":
            usd_lines.append(f'def Output "{attr_name}" {{ }}')
        elif attr_type == "any":
            usd_lines.append(f'custom token {attr_name} = "any"')
            metadata[attr_name] = "ExtendedAttributeType-->Any"
        elif attr_type.find("union") == 0:
            type_list = ",".join(ast.literal_eval(attr_type[5:]))
            usd_lines.append(f'custom token {attr_name} = "union of {type_list}"')
            metadata[attr_name] = f"ExtendedAttributeType-->Union->{type_list}"
        else:
            usd_lines.append(f"custom {attr_type} {attr_name}")
    if metadata:
        usd_lines.append('def ComputeNodeMetaData "metaData"')
        usd_lines.append("{")
        for name, information in metadata.items():
            usd_lines.append(f'    custom token {name} = "{information}"')
        usd_lines.append("}")
    return usd_lines


# ======================================================================
def _is_type(value, type_definition):
    if type_definition == float and isinstance(value, str):
        return value.lower() in ["inf", "-inf", "+inf", "nan", "snan"]

    if isinstance(value, type_definition):
        return True

    return False


# ======================================================================
def is_type_or_list_of_types(value, type_definition, type_count: int):
    """Return True if the value is of the type passed in, or is a list of those types of the defined length"""
    if isinstance(value, (list, tuple)):
        if len(value) != type_count:
            return False
        return all(_is_type(single_value, type_definition) for single_value in value)

    return _is_type(value, type_definition)


# Support for separating roles and types
SUFFIX_TO_TYPE = {"f": "float", "d": "double", "h": "half"}


# ======================================================================
def separate_ogn_role_and_type(raw_type_name: str) -> Tuple[str, str]:
    """Extract the base data type and role name from a raw OGN type, which could include a role"""
    if raw_type_name[:-1] in ["quat", "matrix", "normal", "point", "color", "texcoord", "vector"]:
        return (SUFFIX_TO_TYPE[raw_type_name[-1]], raw_type_name[:-1])
    if raw_type_name in ["frame", "transform", "timecode"]:
        return ("double", raw_type_name)
    if raw_type_name == "execution":
        return ("uint", "execution")
    if raw_type_name == "string":
        return ("uchar", "text")
    if raw_type_name == "path":
        return ("uchar", "path")
    return (raw_type_name, "none")


# ======================================================================
def usd_type_name(type_name: str, tuple_count: int, is_array: bool) -> str:
    """Returns the USD type_name for the attribute with the given parameters

    Args:
        name: Base type (int, float, ...)
        tuple_count: Number of fixed elements (int,2 -> [int, int])
        is_array: True if the attribute has a variable number of elements ([int, int, ...])
    e.g. (int, 2, False) -> "int2"
         (float, 3, True) -> "float3[]"

    Returns:
        A string containing the USD version of the constructed name
    """
    full_type = type_name
    if tuple_count > 1:
        if type_name[:-1] in ["matrix", "point", "color", "texCoord", "frame", "transform"]:
            full_type = f"{type_name[:-1]}{tuple_count}{type_name[-1]}"
        elif type_name[:-1] != "quat":
            # Quaternions are assumed to be 4 so do not have the tuple count added
            full_type += str(tuple_count)
    if is_array:
        full_type += "[]"
    return full_type


# ======================================================================
def sdf_type_name(value_type_name: str, tuple_count: int, is_array: bool) -> str:
    """Returns the SDF ValueTypeName for the attribute with the given parameters

    Args:
        name: Base Sdf type
        tuple_count: Number of fixed elements
        is_array: True if the attribute has a variable number of elements
    e.g. (Int, 2, False) -> "Int2"
         (Float, 3, True) -> "Float3Array"

    Returns:
        A string containing the SDF ValueTypeName version corresponding to the attribute parameters
    """
    full_type = value_type_name
    if tuple_count > 1:
        if value_type_name[:-1] in ["Color", "Frame", "Matrix", "Normal", "Point", "TexCoord", "Transform", "Vector"]:
            full_type = f"{value_type_name[:-1]}{tuple_count}{value_type_name[-1]}"
        elif value_type_name[:-1] != "Quat":
            # Quaternions are assumed to be 4 so do not have the tuple count added
            full_type += str(tuple_count)
    if is_array:
        full_type += "Array"
    return full_type
