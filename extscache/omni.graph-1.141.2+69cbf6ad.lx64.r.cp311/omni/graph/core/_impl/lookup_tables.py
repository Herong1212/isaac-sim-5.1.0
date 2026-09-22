"""
Support file for other functional modules. Kept separate just to keep the other scripts readable.
"""

from typing import Callable, Optional, Tuple

import omni.graph.core as og

__all__ = [
    "IDX_ARRAY_GET",
    "IDX_ARRAY_GET_TENSOR",
    "IDX_ARRAY_SET",
    "IDX_GET",
    "IDX_GET_TENSOR",
    "IDX_SET",
    "type_access_methods",
    "UNSUPPORTED_METHODS",
]


# ----------------------------------------------------------------------
# Lookup tables mapping attributes to the methods to use for getting or setting their data.
# Avoids deep if/else chain since there are over 50 types to support.
#   0 = Get array data
#   1 = Get array tensor data
#   2 = Set array data
#   3 = Get non-tensor data
#   4 = Get tensor data
#   5 = Set data
IDX_ARRAY_GET = 0
IDX_ARRAY_GET_TENSOR = 1
IDX_ARRAY_SET = 2
IDX_GET = 3
IDX_GET_TENSOR = 4
IDX_SET = 5
CTX = og.GraphContext  # Syntactic sugar
# Helper constants that describe why a method is not available in the arrays below
UNSUPPORTED = None  # TODO: The methods supporting the type have not yet been written
NOT_APPLICABLE = None  # The method does not apply to the data type - e.g. tensors of a single integer value
UNSUPPORTED_METHODS = [UNSUPPORTED, UNSUPPORTED, UNSUPPORTED, UNSUPPORTED, UNSUPPORTED, UNSUPPORTED]
DOUBLE_MATRIX_METHODS = [
    CTX.get_attribute_as_nested_doublearray,
    UNSUPPORTED,
    CTX.set_nested_doublearray_attribute,
    CTX.get_attribute_as_doublearray,
    UNSUPPORTED,
    CTX.set_double_matrix_attribute,
]

BOOL_METHODS = [
    CTX.get_attribute_as_boolarray,
    UNSUPPORTED,
    CTX.set_boolarray_attribute,
    CTX.get_attribute_as_bool,
    NOT_APPLICABLE,
    CTX.set_bool_attribute,
]
DOUBLE_METHODS = [
    CTX.get_attribute_as_doublearray,
    UNSUPPORTED,
    CTX.set_doublearray_attribute,
    CTX.get_attribute_as_double,
    NOT_APPLICABLE,
    CTX.set_double_attribute,
]
DOUBLE_ARRAY_METHODS = [
    CTX.get_attribute_as_nested_doublearray,
    UNSUPPORTED,
    CTX.set_nested_doublearray_attribute,
    CTX.get_attribute_as_doublearray,
    UNSUPPORTED,
    CTX.set_doublearray_attribute,
]
FLOAT_METHODS = [
    CTX.get_attribute_as_floatarray,
    UNSUPPORTED,
    CTX.set_floatarray_attribute,
    CTX.get_attribute_as_float,
    NOT_APPLICABLE,
    CTX.set_float_attribute,
]
FLOAT_ARRAY_METHODS = [
    CTX.get_attribute_as_nested_floatarray,
    UNSUPPORTED,
    CTX.set_nested_floatarray_attribute,
    CTX.get_attribute_as_floatarray,
    UNSUPPORTED,
    CTX.set_floatarray_attribute,
]
HALF_METHODS = [
    CTX.get_attribute_as_halfarray,
    UNSUPPORTED,
    CTX.set_halfarray_attribute,
    CTX.get_attribute_as_half,
    NOT_APPLICABLE,
    CTX.set_half_attribute,
]
HALF_ARRAY_METHODS = [
    CTX.get_attribute_as_nested_halfarray,
    UNSUPPORTED,
    CTX.set_nested_halfarray_attribute,
    CTX.get_attribute_as_halfarray,
    UNSUPPORTED,
    CTX.set_halfarray_attribute,
]
INT_METHODS = [
    CTX.get_attribute_as_intarray,
    UNSUPPORTED,
    CTX.set_intarray_attribute,
    CTX.get_attribute_as_int,
    NOT_APPLICABLE,
    CTX.set_int_attribute,
]
INT_ARRAY_METHODS = [
    CTX.get_attribute_as_nested_intarray,
    UNSUPPORTED,
    CTX.set_nested_intarray_attribute,
    CTX.get_attribute_as_intarray,
    UNSUPPORTED,
    CTX.set_intarray_attribute,
]
INT64_METHODS = [
    CTX.get_attribute_as_int64array,
    UNSUPPORTED,
    CTX.set_int64array_attribute,
    CTX.get_attribute_as_int64,
    NOT_APPLICABLE,
    CTX.set_int64_attribute,
]
INT64_ARRAY_METHODS = [
    UNSUPPORTED,
    UNSUPPORTED,
    UNSUPPORTED,
    CTX.get_attribute_as_int64array,
    UNSUPPORTED,
    CTX.set_int64array_attribute,
]
STRING_METHODS = [
    UNSUPPORTED,
    UNSUPPORTED,
    UNSUPPORTED,
    CTX.get_attribute_as_string,
    NOT_APPLICABLE,
    CTX.set_string_attribute,
]
UCHAR_METHODS = [
    CTX.get_attribute_as_uchararray,
    UNSUPPORTED,
    CTX.set_uchararray_attribute,
    CTX.get_attribute_as_uchar,
    NOT_APPLICABLE,
    CTX.set_uchar_attribute,
]
UCHAR_ARRAY_METHODS = [
    UNSUPPORTED,
    UNSUPPORTED,
    UNSUPPORTED,
    CTX.get_attribute_as_uchararray,
    UNSUPPORTED,
    CTX.set_uchararray_attribute,
]
UINT_METHODS = [
    CTX.get_attribute_as_uintarray,
    UNSUPPORTED,
    CTX.set_uintarray_attribute,
    CTX.get_attribute_as_uint,
    NOT_APPLICABLE,
    CTX.set_uint_attribute,
]
UINT_ARRAY_METHODS = [
    UNSUPPORTED,
    UNSUPPORTED,
    UNSUPPORTED,
    CTX.get_attribute_as_uintarray,
    UNSUPPORTED,
    CTX.set_uintarray_attribute,
]
UINT64_METHODS = [
    CTX.get_attribute_as_uint64array,
    UNSUPPORTED,
    CTX.set_uint64array_attribute,
    CTX.get_attribute_as_uint64,
    NOT_APPLICABLE,
    CTX.set_uint64_attribute,
]
UINT64_ARRAY_METHODS = [
    UNSUPPORTED,
    UNSUPPORTED,
    UNSUPPORTED,
    CTX.get_attribute_as_uint64array,
    UNSUPPORTED,
    CTX.set_uint64array_attribute,
]
PATH_ARRAY_METHODS = [
    UNSUPPORTED,
    UNSUPPORTED,
    UNSUPPORTED,
    NOT_APPLICABLE,
    NOT_APPLICABLE,
    NOT_APPLICABLE,
]


# ==============================================================================================================
def type_access_methods(
    ogn_type: og.Type,
) -> Tuple[Tuple[Callable, Callable, Callable, Callable, Callable, Callable], Optional[str]]:
    """Returns the tuple of lookup methods used for accessing attribute data of the passed in ogn_type"""

    if ogn_type.role in [og.AttributeRole.TRANSFORM, og.AttributeRole.MATRIX, og.AttributeRole.FRAME]:
        return [DOUBLE_MATRIX_METHODS, "double"]

    if ogn_type.base_type == og.BaseDataType.BOOL:
        return [BOOL_METHODS, None]

    if ogn_type.role in [og.AttributeRole.TEXT, og.AttributeRole.PATH] or ogn_type.base_type == og.BaseDataType.TOKEN:
        return [STRING_METHODS, None]

    if ogn_type.base_type == og.BaseDataType.DOUBLE:
        if ogn_type.tuple_count > 1:
            return [DOUBLE_ARRAY_METHODS, "double"]
        return [DOUBLE_METHODS, None]

    if ogn_type.base_type == og.BaseDataType.FLOAT:
        if ogn_type.tuple_count > 1:
            return [FLOAT_ARRAY_METHODS, "float"]
        return [FLOAT_METHODS, None]

    if ogn_type.base_type == og.BaseDataType.HALF:
        if ogn_type.tuple_count > 1:
            return [HALF_ARRAY_METHODS, "half"]
        return [HALF_METHODS, None]

    if ogn_type.base_type == og.BaseDataType.INT:
        if ogn_type.tuple_count > 1:
            return [INT_ARRAY_METHODS, "int"]
        return [INT_METHODS, None]

    if ogn_type.base_type == og.BaseDataType.INT64:
        return [INT64_METHODS, None]

    if ogn_type.base_type == og.BaseDataType.UCHAR:
        return [UCHAR_METHODS, None]

    if ogn_type.base_type == og.BaseDataType.UINT:
        return [UINT_METHODS, None]

    if ogn_type.base_type == og.BaseDataType.UINT64:
        return [UINT64_METHODS, None]

    if ogn_type.base_type == og.BaseDataType.RELATIONSHIP and ogn_type.role == og.AttributeRole.TARGET:
        return [PATH_ARRAY_METHODS, None]

    return [[], None]


# ====================================================================================================
# Conversion table for attribute base names in OGN to their base data type and role in the og.Type object
OGN_NAMES_TO_TYPES = {
    "any": (og.BaseDataType.TOKEN, og.AttributeRole.NONE),
    "bool": (og.BaseDataType.BOOL, og.AttributeRole.NONE),
    "bundle": (og.BaseDataType.RELATIONSHIP, og.AttributeRole.BUNDLE),
    "colord": (og.BaseDataType.DOUBLE, og.AttributeRole.COLOR),
    "colorf": (og.BaseDataType.FLOAT, og.AttributeRole.COLOR),
    "colorh": (og.BaseDataType.HALF, og.AttributeRole.COLOR),
    "double": (og.BaseDataType.DOUBLE, og.AttributeRole.NONE),
    "execution": (og.BaseDataType.UINT, og.AttributeRole.EXECUTION),
    "float": (og.BaseDataType.FLOAT, og.AttributeRole.NONE),
    "frame": (og.BaseDataType.DOUBLE, og.AttributeRole.FRAME),
    "half": (og.BaseDataType.HALF, og.AttributeRole.NONE),
    "int": (og.BaseDataType.INT, og.AttributeRole.NONE),
    "int64": (og.BaseDataType.INT64, og.AttributeRole.NONE),
    "matrixd": (og.BaseDataType.DOUBLE, og.AttributeRole.MATRIX),
    "normald": (og.BaseDataType.DOUBLE, og.AttributeRole.NORMAL),
    "normalf": (og.BaseDataType.FLOAT, og.AttributeRole.NORMAL),
    "normalh": (og.BaseDataType.HALF, og.AttributeRole.NORMAL),
    "objectId": (og.BaseDataType.UINT64, og.AttributeRole.OBJECT_ID),
    "path": (og.BaseDataType.UCHAR, og.AttributeRole.PATH),
    "pointd": (og.BaseDataType.DOUBLE, og.AttributeRole.POSITION),
    "pointf": (og.BaseDataType.FLOAT, og.AttributeRole.POSITION),
    "pointh": (og.BaseDataType.HALF, og.AttributeRole.POSITION),
    "quatd": (og.BaseDataType.DOUBLE, og.AttributeRole.QUATERNION),
    "quatf": (og.BaseDataType.FLOAT, og.AttributeRole.QUATERNION),
    "quath": (og.BaseDataType.HALF, og.AttributeRole.QUATERNION),
    "string": (og.BaseDataType.UCHAR, og.AttributeRole.TEXT),
    "target": (og.BaseDataType.RELATIONSHIP, og.AttributeRole.TARGET),
    "texcoordd": (og.BaseDataType.DOUBLE, og.AttributeRole.TEXCOORD),
    "texcoordf": (og.BaseDataType.FLOAT, og.AttributeRole.TEXCOORD),
    "texcoordh": (og.BaseDataType.HALF, og.AttributeRole.TEXCOORD),
    "timecode": (og.BaseDataType.DOUBLE, og.AttributeRole.TIMECODE),
    "token": (og.BaseDataType.TOKEN, og.AttributeRole.NONE),
    "transform": (og.BaseDataType.DOUBLE, og.AttributeRole.TRANSFORM),
    "uchar": (og.BaseDataType.UCHAR, og.AttributeRole.NONE),
    "uint": (og.BaseDataType.UINT, og.AttributeRole.NONE),
    "uint64": (og.BaseDataType.UINT64, og.AttributeRole.NONE),
    "vectord": (og.BaseDataType.DOUBLE, og.AttributeRole.VECTOR),
    "vectorf": (og.BaseDataType.FLOAT, og.AttributeRole.VECTOR),
    "vectorh": (og.BaseDataType.HALF, og.AttributeRole.VECTOR),
}


# ====================================================================================================
# Conversion table for attribute base names in USD to their base data type and role in the og.Type object.
# There are some subtle differences here that are best explained through the table rather than programmatically.
# The extra parameter is an override for tuple count.
# In OGN they are all explicit (quatd[4]) in USD some are implicit (quatd)
USD_NAMES_TO_TYPES = {
    "bool": (og.BaseDataType.BOOL, og.AttributeRole.NONE, None),
    "colord": (og.BaseDataType.DOUBLE, og.AttributeRole.COLOR, None),
    "colorf": (og.BaseDataType.FLOAT, og.AttributeRole.COLOR, None),
    "colorh": (og.BaseDataType.HALF, og.AttributeRole.COLOR, None),
    "double": (og.BaseDataType.DOUBLE, og.AttributeRole.NONE, None),
    "float": (og.BaseDataType.FLOAT, og.AttributeRole.NONE, None),
    "frame": (og.BaseDataType.DOUBLE, og.AttributeRole.FRAME, 16),
    "half": (og.BaseDataType.HALF, og.AttributeRole.NONE, None),
    "int": (og.BaseDataType.INT, og.AttributeRole.NONE, None),
    "int64": (og.BaseDataType.INT64, og.AttributeRole.NONE, None),
    "matrixd": (og.BaseDataType.DOUBLE, og.AttributeRole.NONE, None),
    "normald": (og.BaseDataType.DOUBLE, og.AttributeRole.NORMAL, None),
    "normalf": (og.BaseDataType.FLOAT, og.AttributeRole.NORMAL, None),
    "normalh": (og.BaseDataType.HALF, og.AttributeRole.NORMAL, None),
    "pointd": (og.BaseDataType.DOUBLE, og.AttributeRole.POSITION, None),
    "pointf": (og.BaseDataType.FLOAT, og.AttributeRole.POSITION, None),
    "pointh": (og.BaseDataType.HALF, og.AttributeRole.POSITION, None),
    "quatd": (og.BaseDataType.DOUBLE, og.AttributeRole.QUATERNION, 4),
    "quatf": (og.BaseDataType.FLOAT, og.AttributeRole.QUATERNION, 4),
    "quath": (og.BaseDataType.HALF, og.AttributeRole.QUATERNION, 4),
    "string": (og.BaseDataType.UCHAR, og.AttributeRole.TEXT, None),
    "rel": (og.BaseDataType.RELATIONSHIP, og.AttributeRole.TARGET, None),
    "texCoordd": (og.BaseDataType.DOUBLE, og.AttributeRole.TEXCOORD, None),
    "texCoordf": (og.BaseDataType.FLOAT, og.AttributeRole.TEXCOORD, None),
    "texCoordh": (og.BaseDataType.HALF, og.AttributeRole.TEXCOORD, None),
    "timecode": (og.BaseDataType.DOUBLE, og.AttributeRole.TIMECODE, None),
    "token": (og.BaseDataType.TOKEN, og.AttributeRole.NONE, None),
    "transform": (og.BaseDataType.DOUBLE, og.AttributeRole.TRANSFORM, 16),
    "uchar": (og.BaseDataType.UCHAR, og.AttributeRole.NONE, None),
    "uint": (og.BaseDataType.UINT, og.AttributeRole.NONE, None),
    "uint64": (og.BaseDataType.UINT64, og.AttributeRole.NONE, None),
    "vectord": (og.BaseDataType.DOUBLE, og.AttributeRole.VECTOR, None),
    "vectorf": (og.BaseDataType.FLOAT, og.AttributeRole.VECTOR, None),
    "vectorh": (og.BaseDataType.HALF, og.AttributeRole.VECTOR, None),
}
