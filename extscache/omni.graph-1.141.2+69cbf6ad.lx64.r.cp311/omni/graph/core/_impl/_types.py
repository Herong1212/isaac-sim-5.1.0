"""This module contains the definitions for the data type classes and annotations of OmniGraph attributes."""

import ctypes
from typing import Type, cast

import numpy as np
import omni.graph.core as og

# Implementation Note: These types are patterned of the Warp types as defined in omni.warp.core/warp/types.py with
#                      the intention of switching over to the Warp native types directly at some point. Using the
#                      same naming and structuring conventions will make that easier. Some type names that are not
#                      currently supported in OmniGraph, such as int8, are omitted here.
#
# Lint error N801 is ignored everywhere to allow the lower-case class names to be used, as they are in numpy and Warp


# This appears at the top of the file to make sure it can be used by any of the definitions
class array:  # noqa: N801
    """Base class type for arrays of any type"""


# ==============================================================================================================
# This section contains definitions for the low level types. These are all represented as single values that can be
# added as members of tuples or arrays.
#   ____                   _____        _          _______
#  |  _ \                 |  __ \      | |        |__   __|
#  | |_) | __ _ ___  ___  | |  | | __ _| |_ __ _     | |_   _ _ __   ___  ___
#  |  _ < / _` / __|/ _ \ | |  | |/ _` | __/ _` |    | | | | | '_ \ / _ \/ __|
#  | |_) | (_| \__ \  __/ | |__| | (_| | || (_| |    | | |_| | |_) |  __/\__ \
#  |____/ \__,_|___/\___| |_____/ \__,_|\__\__,_|    |_|\__, | .__/ \___||___/
#                                                        __/ | |
#                                                       |___/|_|
class bool:  # noqa: N801, A001, PLW0622
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'bool', which is
    a single True of False value."""

    _length_ = 1
    _type_ = ctypes.c_bool
    _ogn_name_ = "bool"
    _default_ = False

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class half:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'half', which is a
    16-bit precision floating point value."""

    _length_ = 1
    _type_ = ctypes.c_uint16
    _ogn_name_ = "half"
    _default_ = 0.0

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class float:  # noqa: N801, A001, PLW0622
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'float', which is a
    single-precision floating point value."""

    _length_ = 1
    _type_ = ctypes.c_float
    _ogn_name_ = "float"
    _default_ = 0.0

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class double:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'double', which is a
    double-precision floating point value."""

    _length_ = 1
    _type_ = ctypes.c_double
    _ogn_name_ = "double"
    _default_ = 0.0

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class int:  # noqa: N801, A001, PLW0622
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'int', which is a
    32-bit signed integer."""

    _length_ = 1
    _type_ = ctypes.c_int32
    _ogn_name_ = "int"
    _default_ = 0

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class int64:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'int64', which is a
    64-bit signed integer."""

    _length_ = 1
    _type_ = ctypes.c_int64
    _ogn_name_ = "int64"
    _default_ = 0

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class uchar:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'uchar', which is an
    8-bit unsigned integer."""

    _length_ = 1
    _type_ = ctypes.c_uint8
    _ogn_name_ = "uchar"
    _default_ = 0

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class uint:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'uint', which is a
    32-bit unsigned integer."""

    _length_ = 1
    _type_ = ctypes.c_uint32
    _ogn_name_ = "uint"
    _default_ = 0

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class uint64:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'uint64', which is a
    64-bit unsigned integer."""

    _length_ = 1
    _type_ = ctypes.c_uint64
    _ogn_name_ = "uint64"
    _default_ = 0

    def __init__(self, x=_default_):
        self.value = x


# ==============================================================================================================
# Tuple types for base data types that support a fixed tuple length such as int[2] and float[3]
#   _______          _        _______
#  |__   __|        | |      |__   __|
#     | |_   _ _ __ | | ___     | |_   _ _ __   ___  ___
#     | | | | | '_ \| |/ _ \    | | | | | '_ \ / _ \/ __|
#     | | |_| | |_) | |  __/    | | |_| | |_) |  __/\__ \
#     |_|\__,_| .__/|_|\___|    |_|\__, | .__/ \___||___/
#             | |                   __/ | |
#             |_|                  |___/|_|
class double2:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'double[2]', which is a
    2-tuple of double-precision floating point values."""

    _length_ = 2
    _type_ = ctypes.c_double
    _ogn_name_ = "double[2]"
    _default_ = np.array([0.0, 0.0], dtype=np.float64)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class double3:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'double[3]', which is a
    3-tuple of double-precision floating point values."""

    _length_ = 3
    _type_ = ctypes.c_double
    _ogn_name_ = "double[3]"
    _default_ = np.array([0.0, 0.0, 0.0], dtype=np.float64)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class double4:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'double[4]', which is a
    4-tuple of double-precision floating point values."""

    _length_ = 4
    _type_ = ctypes.c_double
    _ogn_name_ = "double[4]"
    _default_ = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float64)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class float2:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'float[2]', which is a
    2-tuple of single-precision floating point values."""

    _length_ = 2
    _type_ = ctypes.c_float
    _ogn_name_ = "float[2]"
    _default_ = np.array([0.0, 0.0], dtype=np.float32)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class float3:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'float[3]', which is a
    3-tuple of single-precision floating point values."""

    _length_ = 3
    _type_ = ctypes.c_float
    _ogn_name_ = "float[3]"
    _default_ = np.array([0.0, 0.0, 0.0], dtype=np.float32)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class float4:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'float[4]', which is a
    4-tuple of single-precision floating point values."""

    _length_ = 4
    _type_ = ctypes.c_float
    _ogn_name_ = "float[4]"
    _default_ = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class half2:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'half[2]', which is a
    2-tuple of half precision floating point values."""

    _length_ = 2
    _type_ = ctypes.c_uint16
    _ogn_name_ = "half[2]"
    _default_ = np.array([0.0, 0.0], dtype=np.float16)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class half3:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'half[3]', which is a
    3-tuple of half precision floating point values."""

    _length_ = 3
    _type_ = ctypes.c_uint16
    _ogn_name_ = "half[3]"
    _default_ = np.array([0.0, 0.0, 0.0], dtype=np.float16)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class half4:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'half[4]', which is a
    4-tuple of half precision floating point values."""

    _length_ = 4
    _type_ = ctypes.c_uint16
    _ogn_name_ = "half[4]"
    _default_ = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float16)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class int2:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'int[2]', which is a
    2-tuple of int precision floating point values."""

    _length_ = 2
    _type_ = ctypes.c_int32
    _ogn_name_ = "int[2]"
    _default_ = np.array([0, 0], dtype=np.int32)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class int3:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'int[3]', which is a
    3-tuple of int precision floating point values."""

    _length_ = 3
    _type_ = ctypes.c_int32
    _ogn_name_ = "int[3]"
    _default_ = np.array([0, 0, 0], dtype=np.int32)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class int4:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'int[4]', which is a
    4-tuple of int precision floating point values."""

    _length_ = 4
    _type_ = ctypes.c_int32
    _ogn_name_ = "int[4]"
    _default_ = np.array([0, 0, 0, 0], dtype=np.int32)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class string:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'string', which is an
    array of uchars that are the characters in the string plus a uint64 that is the length of the string."""

    _length_ = 1
    _type_ = ctypes.c_char
    _ogn_name_ = "string"
    _default_ = ""

    def __init__(self, x=_default_):
        self.value = x


# ==============================================================================================================
# Matrix types for values that are represented as 2d arrays, such as matrixd[2] and frame[4]
#   __  __       _        _        _______
#  |  \/  |     | |      (_)      |__   __|
#  | \  / | __ _| |_ _ __ ___  __    | |_   _ _ __   ___  ___
#  | |\/| |/ _` | __| '__| \ \/ /    | | | | | '_ \ / _ \/ __|
#  | |  | | (_| | |_| |  | |>  <     | | |_| | |_) |  __/\__ \
#  |_|  |_|\__,_|\__|_|  |_/_/\_\    |_|\__, | .__/ \___||___/
#                                        __/ | |
#                                       |___/|_|
class matrix2d:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'matrixd[2]', which is a
    2x2 array of double-precision floating point values."""

    _length_ = 4
    _type_ = ctypes.c_double
    _ogn_name_ = "matrixd[2]"
    _default_ = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float64)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class matrix3d:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'matrixd[3]', which is a
    3x3 array of double-precision floating point values."""

    _length_ = 9
    _type_ = ctypes.c_double
    _ogn_name_ = "matrixd[3]"
    _default_ = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], dtype=np.float64)

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class matrix4d:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'matrixd[4]', which is a
    4x4 array of double-precision floating point values."""

    _length_ = 16
    _type_ = ctypes.c_double
    _ogn_name_ = "matrixd[4]"
    _default_ = np.array(
        [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], dtype=np.float64
    )

    def __init__(self, x=_default_):
        self.value = x


# ==============================================================================================================
# Specialized types that are used by OmniGraph but not others like Warp or numpy.
#    _____                 _       _   _______
#   / ____|               (_)     | | |__   __|
#  | (___  _ __   ___  ___ _  __ _| |    | |_   _ _ __   ___  ___
#   \___ \| '_ \ / _ \/ __| |/ _` | |    | | | | | '_ \ / _ \/ __|
#   ____) | |_) |  __/ (__| | (_| | |    | | |_| | |_) |  __/\__ \
#  |_____/| .__/ \___|\___|_|\__,_|_|    |_|\__, | .__/ \___||___/
#         | |                                __/ | |
#         |_|                               |___/|_|
#
class any:  # noqa: N801, A001, PLW0622
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'any', which is a
    64-bit unsigned integer that is a placeholder indicating that the actual data type can only be determined
    at runtime, and which can be any of the available attribute concrete data types."""

    _length_ = 1
    _type_ = ctypes.c_uint64
    _ogn_name_ = "any"
    _default_ = 0

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class bundle:  # noqa: N801, A001, PLW0622
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'bundle', which is a
    collection of named attributes with any of the other types, including bundle but excluding 'any' and 'union'.
    """

    _length_ = 1
    _type_ = ctypes.c_uint64
    _ogn_name_ = "bundle"
    _default_ = None

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class execution:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'execution', which is a
    32-bit signed integer used for tagging execution states."""

    _length_ = 1
    _type_ = ctypes.c_int
    _ogn_name_ = "execution"
    _default_ = og.ExecutionAttributeState.DISABLED

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class objectid:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'objectId', which is a
    64-bit unsigned integer used to uniquely identify object types."""

    _length_ = 1
    _type_ = ctypes.c_uint64
    _ogn_name_ = "objectId"
    _default_ = 0

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class target(array):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'target', which is a
    list of 64-bit unsigned integers that each map to an Sdf.Path on the USD stage."""

    _length_ = 1
    _type_ = ctypes.c_uint64
    _ogn_name_ = "target"
    _default_ = []

    def __init__(self, x=None):
        self.value = x if x else []


# --------------------------------------------------------------------------------------------------------------
class token:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'token', which is a
    64-bit unsigned integer that maps to a unique, shared string value."""

    _length_ = 1
    _type_ = ctypes.c_uint64
    _ogn_name_ = "token"
    _default_ = 0

    def __init__(self, x=_default_):
        self.value = x


# --------------------------------------------------------------------------------------------------------------
class union:  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'union', which is a
    64-bit unsigned integer that is a placeholder indicating that the actual data type can only be determined
    at runtime, and which can be one of a specified subset of all attribute data types."""

    _length_ = 1
    _type_ = ctypes.c_uint64
    _ogn_name_ = None
    _default_ = 0

    def __init__(self, x=_default_):
        self.value = x


# ==============================================================================================================
# Type names corresponding to data types that have specific roles assigned to them, even though the underlying
# data corresponds to simple data types. The data representations are aliases to types from above and the
# type name is used as the role identifier.
#   _____       _             ____                     _   _______
#  |  __ \     | |           |  _ \                   | | |__   __|
#  | |__) |___ | | ___ ______| |_) | __ _ ___  ___  __| |    | |_   _ _ __   ___  ___
#  |  _  // _ \| |/ _ \______|  _ < / _` / __|/ _ \/ _` |    | | | | | '_ \ / _ \/ __|
#  | | \ \ (_) | |  __/      | |_) | (_| \__ \  __/ (_| |    | | |_| | |_) |  __/\__ \
#  |_|  \_\___/|_|\___|      |____/ \__,_|___/\___|\__,_|    |_|\__, | .__/ \___||___/
#                                                                __/ | |
#                                                               |___/|_|
class color3d(double3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'colord[3]', which is a
    3-tuple of double-precision floating point values representing a color."""


class color3f(float3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'colorf[3]', which is a
    3-tuple of single-precision floating point values representing a color."""


class color3h(half3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'colorh[3]', which is a
    3-tuple of half-precision floating point values representing a color."""


class color4d(double4):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'colord[4]', which is a
    4-tuple of double-precision floating point values representing a color."""


class color4f(float4):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'colorf[4]', which is a
    4-tuple of single-precision floating point values representing a color."""


class color4h(half4):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'colorh[4]', which is a
    4-tuple of half-precision floating point values representing a color."""


# --------------------------------------------------------------------------------------------------------------
class frame4d(matrix4d):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'framed[4]', which is a
    4x4 array of double-precision floating point values representing a Cartesian coordinate frame."""


# --------------------------------------------------------------------------------------------------------------
class normal3d(double3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'normald[3]', which is a
    3-tuple of double-precision floating point values representing a normal."""


class normal3f(float3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'normalf[3]', which is a
    3-tuple of single-precision floating point values representing a normal."""


class normal3h(half3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'normalh[3]', which is a
    3-tuple of half-precision floating point values representing a normal."""


# --------------------------------------------------------------------------------------------------------------
class point3d(double3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'pointd[3]', which is a
    3-tuple of double-precision floating point values representing a point."""


class point3f(float3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'pointf[3]', which is a
    3-tuple of single-precision floating point values representing a point."""


class point3h(half3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'pointh[3]', which is a
    3-tuple of half-precision floating point values representing a point."""


# --------------------------------------------------------------------------------------------------------------
class quatd(double4):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'quatd[4]', which is a
    4-tuple of double-precision floating point values representing a quaternion."""


class quatf(float4):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'quatf[4]', which is a
    4-tuple of single-precision floating point values representing a quaternion."""


class quath(half4):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'quath[4]', which is a
    4-tuple of half-precision floating point values representing a quaternion."""


# --------------------------------------------------------------------------------------------------------------
class timecode(double):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'timecode', which is a
    double-precision floating point value encoding a time value."""


# --------------------------------------------------------------------------------------------------------------
class texcoord2d(double2):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'texcoordd[2]', which is a
    2-tuple of double-precision floating point values representing a texture coordinate."""


class texcoord2f(float2):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'texcoordf[2]', which is a
    2-tuple of single-precision floating point values representing a texture coordinate."""


class texcoord2h(half2):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'texcoordh[2]', which is a
    2-tuple of half-precision floating point values representing a texture coordinate."""


class texcoord3d(double3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'texcoordd[3]', which is a
    3-tuple of double-precision floating point values representing a texture coordinate."""


class texcoord3f(float3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'texcoordf[3]', which is a
    3-tuple of single-precision floating point values representing a texture coordinate."""


class texcoord3h(half3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'texcoordh[3]', which is a
    3-tuple of half-precision floating point values representing a texture coordinate."""


# --------------------------------------------------------------------------------------------------------------
class vector3d(double3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'vectord[3]', which is a
    3-tuple of double-precision floating point values representing a vector."""


class vector3f(float3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'vectorf[3]', which is a
    3-tuple of single-precision floating point values representing a vector."""


class vector3h(half3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'vectorh[3]', which is a
    3-tuple of half-precision floating point values representing a vector."""


# ==============================================================================================================
# Array types for base and tuple data types that support a list of an arbitrary number of them, such as
# float[], int[2][], and matrixd[3][]
#                                   _______
#      /\                          |__   __|
#     /  \   _ __ _ __ __ _ _   _     | |_   _ _ __   ___  ___
#    / /\ \ | '__| '__/ _` | | | |    | | | | | '_ \ / _ \/ __|
#   / ____ \| |  | | | (_| | |_| |    | | |_| | |_) |  __/\__ \
#  /_/    \_\_|  |_|  \__,_|\__, |    |_|\__, | .__/ \___||___/
#                            __/ |        __/ | |
#                           |___/        |___/|_|
class boolarray(array, bool):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'bool[]', which is an
    array of indeterminate length of True or False values."""


# --------------------------------------------------------------------------------------------------------------
class color3darray(array, color3d):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'colord[3][]', which is an
    arbitrary length array of 3-tuples of double-precision floating point values representing a color."""


class color3farray(array, color3f):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'colorf[3][]', which is an
    arbitrary length array of 3-tuples of single-precision floating point values representing a color."""


class color3harray(array, color3h):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'colorh[3][]', which is an
    arbitrary length array of 3-tuples of half-precision floating point values representing a color."""


class color4darray(array, color4d):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'colord[4][]', which is an
    arbitrary length array of 4-tuples of double-precision floating point values representing a color."""


class color4farray(array, color4f):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'colorf[4][]', which is an
    arbitrary length array of 4-tuples of single-precision floating point values representing a color."""


class color4harray(array, color4h):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'colorh[4][]', which is an
    arbitrary length array of 4-tuples of half-precision floating point values representing a color."""


# --------------------------------------------------------------------------------------------------------------
class doublearray(array, double):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'double[]', which is an
    array of double-precision floating point values."""


class double2array(array, double2):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'double2[]', which is an
    array of two double-precision floating point values."""


class double3array(array, double3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'double3[]', which is an
    array of three double-precision floating point values."""


class double4array(array, double4):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'double4[]', which is an
    array of four double-precision floating point values."""


# --------------------------------------------------------------------------------------------------------------
class floatarray(array, float):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'float[]', which is an
    array of single-precision floating point values."""


class float2array(array, float2):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'float2[]', which is an
    array of two single-precision floating point values."""


class float3array(array, float3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'float3[]', which is an
    array of three single-precision floating point values."""


class float4array(array, float4):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'float4[]', which is an
    array of four single-precision floating point values."""


# --------------------------------------------------------------------------------------------------------------
class frame4darray(array, frame4d):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'framed[4][]', which is a
    4x4 matrix of double-precision floating point values."""


# --------------------------------------------------------------------------------------------------------------
class halfarray(array, half):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'half[]', which is an
    array of half-precision floating point values."""


class half2array(array, half2):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'half2[]', which is an
    array of two half-precision floating point values."""


class half3array(array, half3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'half3[]', which is an
    array of three half-precision floating point values."""


class half4array(array, half4):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'half4[]', which is an
    array of four half-precision floating point values."""


# --------------------------------------------------------------------------------------------------------------
class intarray(array, int):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'int[]', which is an
    array of 32-bit integers."""


class int2array(array, int2):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'int2[]', which is an
    array of two 32-bit integers."""


class int3array(array, int3):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'int3[]', which is an
    array of three 32-bit integers."""


class int4array(array, int4):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'int4[]', which is an
    array of four 32-bit integers."""


# --------------------------------------------------------------------------------------------------------------
class int64array(array, int64):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'int64[]', which is an
    array of 64-bit integers."""


# --------------------------------------------------------------------------------------------------------------
class matrix2darray(array, matrix2d):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'matrixd[2][]', which is a
    2x2 matrix of double-precision floating point values."""


class matrix3darray(array, matrix3d):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'matrixd[3][]', which is a
    3x3 matrix of double-precision floating point values."""


class matrix4darray(array, matrix4d):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'matrixd[4][]', which is a
    4x4 matrix of double-precision floating point values."""


# --------------------------------------------------------------------------------------------------------------
class normal3darray(array, normal3d):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'normald[3][]', which is an
    arbitrary length array of 3-tuples of double-precision floating point values representing a normal."""


class normal3farray(array, normal3f):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'normalf[3][]', which is an
    arbitrary length array of 3-tuples of single-precision floating point values representing a normal."""


class normal3harray(array, normal3h):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'normalh[3][]', which is an
    arbitrary length array of 3-tuples of half-precision floating point values representing a normal."""


# --------------------------------------------------------------------------------------------------------------
class objectidarray(array, objectid):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'objectid[]', which is an
    array of 64-bit unsigned integers used to uniquely identify object types."""


# --------------------------------------------------------------------------------------------------------------
class point3darray(array, point3d):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'pointd[3][]', which is an
    arbitrary length array of 3-tuples of double-precision floating point values representing a point in space."""


class point3farray(array, point3f):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'pointf[3][]', which is an
    arbitrary length array of 3-tuples of single-precision floating point values representing a point in space."""


class point3harray(array, point3h):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'pointh[3][]', which is an
    arbitrary length array of 3-tuples of half-precision floating point values representing a point in space."""


# --------------------------------------------------------------------------------------------------------------
class quatdarray(array, quatd):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'quatd[4][]', which is an
    arbitrary length array of 4-tuples of double-precision floating quaternions."""


class quatfarray(array, quatf):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'quatf[4][]', which is an
    arbitrary length array of 4-tuples of single-precision floating quaternions."""


class quatharray(array, quath):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'quath[4][]', which is an
    arbitrary length array of 4-tuples of half-precision floating quaternions."""


# --------------------------------------------------------------------------------------------------------------
class texcoord2darray(array, texcoord2d):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'texcoordd[2][]', which is an
    arbitrary length array of 2-tuples of double-precision floating point values representing a texture coordinate."""


class texcoord2farray(array, texcoord2f):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'texcoordf[2][]', which is an
    arbitrary length array of 2-tuples of single-precision floating point values representing a texture coordinate."""


class texcoord2harray(array, texcoord2h):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'texcoordh[2][]', which is an
    arbitrary length array of 2-tuples of half-precision floating point values representing a texture coordinate."""


class texcoord3darray(array, texcoord3d):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'texcoordd[3][]', which is an
    arbitrary length array of 3-tuples of double-precision floating point values representing a texture coordinate."""


class texcoord3farray(array, texcoord3f):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'texcoordf[3][]', which is an
    arbitrary length array of 3-tuples of single-precision floating point values representing a texture coordinate."""


class texcoord3harray(array, texcoord3h):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'texcoordh[3][]', which is an
    arbitrary length array of 3-tuples of half-precision floating point values representing a texture coordinate."""


# --------------------------------------------------------------------------------------------------------------
class timecodearray(array, timecode):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'timecode[]', which is an
    array of timecode values, represented as double-precision floating point values."""


class tokenarray(array, token):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'token[]', which is an
    array of token values, represented as strings."""


class uchararray(array, uchar):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'uchar[]', which is an
    array of 8-bit unsigned integers."""


class uintarray(array, uint):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'uint[]', which is an
    array of 32-bit unsigned integers."""


class uint64array(array, uint64):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'uint64[]', which is an
    array of 64-bit unsigned integers."""


# --------------------------------------------------------------------------------------------------------------
class vector3darray(array, vector3d):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'vectord[3][]', which is an
    arbitrary length array of 3-tuples of double-precision floating vector values representing a vector in space."""


class vector3farray(array, vector3f):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'vectorf[3][]', which is an
    arbitrary length array of 3-tuples of single-precision floating vector values representing a vector in space."""


class vector3harray(array, vector3h):  # noqa: N801
    """Type definition for Python data corresponding to the OmniGraph attribute data type 'vectorh[3][]', which is an
    arbitrary length array of 3-tuples of half-precision floating vector values representing a vector in space."""


# ==============================================================================================================
# Type names that are aliases for the above ones to give a name set that more closely corresponds with the
# OmniGraph type names (the above names are used by Warp), e.g. "float" instead of "float32"
#   _______                          _ _
#  |__   __|                   /\   | (_)
#     | |_   _ _ __   ___     /  \  | |_  __ _ ___  ___  ___
#     | | | | | '_ \ / _ \   / /\ \ | | |/ _` / __|/ _ \/ __|
#     | | |_| | |_) |  __/  / ____ \| | | (_| \__ \  __/\__ \
#     |_|\__, | .__/ \___| /_/    \_\_|_|\__,_|___/\___||___/
#         __/ | |
#        |___/|_|
#
boolean = cast(Type[bool], bool)
float16 = cast(Type[half], half)
float32 = cast(Type[float], float)
float64 = cast(Type[double], double)
int32 = cast(Type[int], int)
uint8 = cast(Type[uchar], uchar)
uint32 = cast(Type[uint], uint)
