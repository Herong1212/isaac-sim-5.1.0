r"""This file contains the implementation for the dtype information describing Python data types.

It's mostly a repackaging of the information understood by OGN and Fabric of the supported data types.
They can be passed around to provide identification of data whose type is not explicit, or ambiguous. (e.g. a Python
int is used to represent all of the integer and unsigned integer types so these types can disambiguate)

The dtype information is analagous to the dtype information in numpy, just tuned to our particular data types.

All of these types are exported into the omni.graph.core namespace so type names are generic. Typical usage is:

    import omni.graph.core as og
    my_float3_type = og.Float3

 __      ___   ___ _  _ ___ _  _  ___
 \ \    / /_\ | _ \ \| |_ _| \| |/ __|
  \ \/\/ / _ \|   / .` || || .` | (_ |
   \_/\_/_/ \_\_|_\_|\_|___|_|\_|\___|

These data types will eventually be moved and/or replaced so do not import directly.
"""

import ctypes
from dataclasses import dataclass

import omni.graph.core as og


# ==============================================================================================================
@dataclass
class Dtype:
    """Common base type for dtypes, defining the members each needs to populate
    Attributes:
        tuple_count: The number of atomic elements in this type
        size: The total size in bytes of this type
        base_type: The base data type of this type
        ctype: The ctypes representation used by this data type in Fabric
    """

    tuple_count: int = None
    size: int = None
    base_type: og.BaseDataType = None
    ctype: object = None

    @classmethod
    def is_matrix_type(cls) -> bool:
        """Returns true if the dtype is a matrix. Uses derived class knowledge to keep it simple"""
        return hasattr(cls, "matrix_dim")


# ==============================================================================================================
@dataclass
class Bool(Dtype):
    tuple_count: int = 1
    size: int = 1
    base_type: og.BaseDataType = og.BaseDataType.BOOL
    ctype: object = ctypes.c_bool


# ==============================================================================================================
@dataclass
class BundleOutput(Dtype):
    tuple_count: int = 1
    size: int = 8
    base_type: og.BaseDataType = og.BaseDataType.RELATIONSHIP
    ctype: object = ctypes.c_uint64


# ==============================================================================================================
@dataclass
class Double(Dtype):
    tuple_count: int = 1
    size: int = 8
    base_type: og.BaseDataType = og.BaseDataType.DOUBLE
    ctype: object = ctypes.c_double


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Double2(Dtype):
    tuple_count: int = 2
    size: int = 16
    base_type: og.BaseDataType = og.BaseDataType.DOUBLE
    ctype: object = ctypes.c_double


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Double3(Dtype):
    tuple_count: int = 3
    size: int = 24
    base_type: og.BaseDataType = og.BaseDataType.DOUBLE
    ctype: object = ctypes.c_double


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Double4(Dtype):
    tuple_count: int = 4
    size: int = 32
    base_type: og.BaseDataType = og.BaseDataType.DOUBLE
    ctype: object = ctypes.c_double


# ==============================================================================================================
@dataclass
class Float(Dtype):
    tuple_count: int = 1
    size: int = 4
    base_type: og.BaseDataType = og.BaseDataType.FLOAT
    ctype: object = ctypes.c_float


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Float2(Dtype):
    tuple_count: int = 2
    size: int = 8
    base_type: og.BaseDataType = og.BaseDataType.FLOAT
    ctype: object = ctypes.c_float


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Float3(Dtype):
    tuple_count: int = 3
    size: int = 12
    base_type: og.BaseDataType = og.BaseDataType.FLOAT
    ctype: object = ctypes.c_float


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Float4(Dtype):
    tuple_count: int = 4
    size: int = 16
    base_type: og.BaseDataType = og.BaseDataType.FLOAT
    ctype: object = ctypes.c_float


# ==============================================================================================================
@dataclass
class Half(Dtype):
    tuple_count: int = 1
    size: int = 2
    # Physically this is a 2-byte int, but the size implication is the same for a 2-byte float
    base_type: og.BaseDataType = og.BaseDataType.HALF
    ctype: object = ctypes.c_ushort


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Half2(Dtype):
    tuple_count: int = 2
    size: int = 4
    base_type: og.BaseDataType = og.BaseDataType.HALF
    ctype: object = ctypes.c_ushort


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Half3(Dtype):
    tuple_count: int = 3
    size: int = 6
    base_type: og.BaseDataType = og.BaseDataType.HALF
    ctype: object = ctypes.c_ushort


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Half4(Dtype):
    tuple_count: int = 4
    size: int = 8
    base_type: og.BaseDataType = og.BaseDataType.HALF
    ctype: object = ctypes.c_ushort


# ==============================================================================================================
@dataclass
class Int(Dtype):
    tuple_count: int = 1
    size: int = 4
    base_type: og.BaseDataType = og.BaseDataType.INT
    ctype: object = ctypes.c_int


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Int2(Dtype):
    tuple_count: int = 2
    size: int = 8
    base_type: og.BaseDataType = og.BaseDataType.INT
    ctype: object = ctypes.c_int


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Int3(Dtype):
    tuple_count: int = 3
    size: int = 12
    base_type: og.BaseDataType = og.BaseDataType.INT
    ctype: object = ctypes.c_int


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Int4(Dtype):
    tuple_count: int = 4
    size: int = 16
    base_type: og.BaseDataType = og.BaseDataType.INT
    ctype: object = ctypes.c_int


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Int64(Dtype):
    tuple_count: int = 1
    size: int = 8
    base_type: og.BaseDataType = og.BaseDataType.INT64
    ctype: object = ctypes.c_longlong


# ==============================================================================================================
@dataclass
class Matrix2d(Dtype):
    tuple_count: int = 4
    size: int = 32
    base_type: og.BaseDataType = og.BaseDataType.DOUBLE
    ctype: object = ctypes.c_double
    matrix_dim: int = 2


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Matrix3d(Dtype):
    tuple_count: int = 9
    size: int = 72
    base_type: og.BaseDataType = og.BaseDataType.DOUBLE
    ctype: object = ctypes.c_double
    matrix_dim: int = 3


# --------------------------------------------------------------------------------------------------------------
@dataclass
class Matrix4d(Dtype):
    tuple_count: int = 16
    size: int = 128
    base_type: og.BaseDataType = og.BaseDataType.DOUBLE
    ctype: object = ctypes.c_double
    matrix_dim: int = 4


# ==============================================================================================================
@dataclass
class Token(Dtype):
    tuple_count: int = 1
    size: int = 8
    base_type: og.BaseDataType = og.BaseDataType.TOKEN
    ctype: object = ctypes.c_uint64


# ==============================================================================================================
@dataclass
class UChar(Dtype):
    tuple_count: int = 1
    size: int = 1
    base_type: og.BaseDataType = og.BaseDataType.UCHAR
    ctype: object = ctypes.c_ubyte


# --------------------------------------------------------------------------------------------------------------
@dataclass
class UInt(Dtype):
    tuple_count: int = 1
    size: int = 4
    base_type: og.BaseDataType = og.BaseDataType.UINT
    ctype: object = ctypes.c_uint32


# --------------------------------------------------------------------------------------------------------------
@dataclass
class UInt64(Dtype):
    tuple_count: int = 1
    size: int = 8
    base_type: og.BaseDataType = og.BaseDataType.UINT64
    ctype: object = ctypes.c_uint64
