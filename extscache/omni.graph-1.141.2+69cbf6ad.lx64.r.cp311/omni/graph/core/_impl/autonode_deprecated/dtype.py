"""Manage the information pertaining to allowed OmniGraph data types.

This is an internal class that aids in setting up the module definitions for the OmniGraph data types. In ordinary
usage a user will not import it directly, but rather use the symbols that an API-level module has imported.
"""

# TODO: This is hardcoded to CPU data. The more general solution should consider GPU data as separate types.
import ctypes
from typing import NewType

import carb
import omni.graph.core as og


# ==============================================================================================================
# Generic class type that serves as a root type for array definitions. In the fullness of time it will define the
# actual array protocol required for array return types, which includes the standard parameters used by types such
# as numpy.ndarray
#    shape: tuple[int, ...]   Shape of created array.
#    dtype: DType             Any object that can be interpreted as a data type.
#    buffer: BufferProtocol   Used to fill the array with data.
#    offset: int              Offset of array data in buffer.
#    strides: tuple[int, ...] Strides of data in memory.
#    order: "C" | "F"         Row-major (C-style) or column-major (Fortran-style) order.
#
class _ArrayProtocol:
    pass


# ==============================================================================================================
class DType:
    """Base class for all OmniGraph data type definitions"""

    _CTYPES_BY_BASE_TYPE = {
        og.BaseDataType.BOOL: ctypes.c_bool,
        og.BaseDataType.FLOAT: ctypes.c_float,
        og.BaseDataType.DOUBLE: ctypes.c_double,
        og.BaseDataType.HALF: ctypes.c_int16,
        og.BaseDataType.INT: ctypes.c_int32,
        og.BaseDataType.INT64: ctypes.c_int64,
        og.BaseDataType.UCHAR: ctypes.c_uint8,
        og.BaseDataType.UINT: ctypes.c_uint32,
        og.BaseDataType.UINT64: ctypes.c_uint64,
        og.BaseDataType.TOKEN: ctypes.c_uint64,
        og.BaseDataType.ASSET: ctypes.c_uint64,
        og.BaseDataType.PRIM: ctypes.c_uint64,
        og.BaseDataType.RELATIONSHIP: ctypes.c_uint64,
        og.BaseDataType.UNKNOWN: ctypes.c_uint64,
    }
    """Internal mapping of the base data type onto the corresponding C type storing its memory"""

    def __init__(self, type_name: str, name: str):
        """Create a custom data type definition with its own custom docstrings for easy inspection"""

        class _DataTypeAnnotation(NewType):
            """Override the type annotation NewType so that custom representations can be returned"""

            def __str__(self) -> str:
                return name

            def __repr__(self) -> str:
                return f"omni.graph.core.typing.{name}"

        self.type_name = type_name
        self.name = name
        self.__doc__ = """This is a list containing annotations for all of the supported OmniGraph data
types. They can be used for type annotations on functions that process attribute data:

    import omni.graph.core.typing as ogt

    def add_two_floats(float1: ogt.Float, float2: ogt.Float) -> ogt.Float:
        return float1 + float2

To see information on any individual type in the list you can ask for its help information:

    > import omni.graph.core.typing as ogt
    > help(ogt.Float3)
    Float3 = omni.graph.core.typing.Float3
        This type annotation corresponds to the OGN type 'float[3]'
"""
        try:
            self.og_type = og.AttributeType.type_from_ogn_type_name(type_name)
        except RuntimeError:
            # This is what happens when running a docs build since it cannot access og.AttributeType. The actual types
            # don't matter in that case so just blank them out.
            self.og_type = None
            self.type = None
            return

        if self.og_type.base_type == og.BaseDataType.UNKNOWN:  # noqa: SIM102
            # This is checking to see if the function is just a .pyi capsule, which is what happens during a docs
            # build, which does not need the error emitted.
            if not hasattr(og.AttributeType.type_from_ogn_type_name, "__self__"):
                carb.log_error(f"Tried to define type based on unknown type name '{type_name}'")
        if self.og_type.tuple_count > 1 or self.og_type.array_depth > 0:
            data_type = _ArrayProtocol
        else:
            data_type = self._CTYPES_BY_BASE_TYPE[self.og_type.base_type]
        self.type = _DataTypeAnnotation(name, data_type)
        self.type.__doc__ = f"Type annotation to use for OmniGraph attribute data of type '{type_name}'"
        self.__doc__ = self.type.__doc__

    def is_array_type(self) -> bool:
        """Returns True if the data type represented by this type annotation is an array type"""
        return self.og_type.array_depth > 0

    def is_matrix_type(self) -> bool:
        """Returns True if the data type represented by this type annotation is a matrix type"""
        return self.og_type.role in [og.AttributeRole.FRAME, og.AttributeRole.MATRIX]

    def shape(self) -> tuple[int, ...]:
        """Returns the shape of data returned by this type, with free array dimensions set to size 0"""
        if self.og_type.tuple_count > 1:
            if self.is_matrix_type():
                the_shape = (self.og_type.tuple_count, self.og_type.tuple_count, 0)
            elif self.is_array_type():
                the_shape = (self.og_type.tuple_count, 0)
            else:
                the_shape = (self.og_type.tuple_count,)
        else:
            the_shape = ()
        return the_shape

    def __str__(self) -> str:
        """Returns the string representation of this data type as the name by which it will be imported"""
        return self.name

    def __repr__(self) -> str:
        """Returns the repr representation of this data type as the full name the user will typically import"""
        return repr(self.type)


# ==============================================================================================================
class TypeFactory:
    """Factory class that allows easy definition of data type annotation objects.
    TypeFactory.define_type(...) is called for every legal type to define their annotation objects, which can
    be made available for type annotations on any function that processes OmniGraph attribute data.

    Then the defined types can be added to a module for import by calling TypeFactory.add_all_types_to_module(m).
    """

    # By subclassing list we can provide a custom docstring to the data type list that is more explanatory.
    class _TypeAnnotationList(list):
        """List of type annotations for all supported OmniGraph attribute data types"""

    ALL_DATA_TYPES = _TypeAnnotationList()
    _ALL_DATA_TYPE_DEFINITIONS = {}

    @classmethod
    def define_type(cls, type_name: str, obj_name: str, supports_arrays: bool) -> tuple[DType, DType | None]:
        """Define a new data type annotation definition
        Args:
            type_name: Name of the type, as specified by OGN (e.g. "bool" or "float[3]")
            obj_name: Name of the constructed type annotation object (e.g. "Bool" or "Float3")
            supports_arrays: True if the data type can also be an array (e.g. add "BoolArray" and "Float3Array)
        """
        new_type = DType(type_name, obj_name)
        cls._ALL_DATA_TYPE_DEFINITIONS[type_name] = new_type
        cls.ALL_DATA_TYPES.append(new_type.type)
        # Automatically populate the array type definitions for those types supporting arrays
        if supports_arrays:
            array_type_name = f"{type_name}[]"
            array_obj_name = f"{obj_name}Array"
            new_array_type = DType(array_type_name, array_obj_name)
            cls._ALL_DATA_TYPE_DEFINITIONS[array_type_name] = new_array_type
            cls.ALL_DATA_TYPES.append(new_array_type.type)
        else:
            new_array_type = None
        return (new_type, new_array_type)


# ==============================================================================================================
# The way the factory is set up just declaring the types is enough to add them to the list of all available types.
Any, _ = TypeFactory.define_type("any", "Any", False)
Bool, BoolArray = TypeFactory.define_type("bool", "Bool", True)
Bundle, _ = TypeFactory.define_type("bundle", "Bundle", False)
Color3d, Color3dArray = TypeFactory.define_type("colord[3]", "Color3d", True)
Color3f, Color3fArray = TypeFactory.define_type("colorf[3]", "Color3f", True)
Color3h, Color3hArray = TypeFactory.define_type("colorh[3]", "Color3h", True)
Color4d, Color4dArray = TypeFactory.define_type("colord[4]", "Color4d", True)
Color4f, Color4fArray = TypeFactory.define_type("colorf[4]", "Color4f", True)
Color4h, Color4hArray = TypeFactory.define_type("colorh[4]", "Color4h", True)
Double, DoubleArray = TypeFactory.define_type("double", "Double", True)
Double2, Double2Array = TypeFactory.define_type("double[2]", "Double2", True)
Double3, Double3Array = TypeFactory.define_type("double[3]", "Double3", True)
Double4, Double4Array = TypeFactory.define_type("double[4]", "Double4", True)
Execution, _ = TypeFactory.define_type("execution", "Execution", False)
Float, FloatArray = TypeFactory.define_type("float", "Float", True)
Float2, Float2Array = TypeFactory.define_type("float[2]", "Float2", True)
Float3, Float3Array = TypeFactory.define_type("float[3]", "Float3", True)
Float4, Float4Array = TypeFactory.define_type("float[4]", "Float4", True)
Frame, FrameArray = TypeFactory.define_type("frame[4]", "Frame", True)
Half, HalfArray = TypeFactory.define_type("half", "Half", True)
Half2, Half2Array = TypeFactory.define_type("half[2]", "Half2", True)
Half3, Half3Array = TypeFactory.define_type("half[3]", "Half3", True)
Half4, Half4Array = TypeFactory.define_type("half[4]", "Half4", True)
Int, IntArray = TypeFactory.define_type("int", "Int", True)
Int2, Int2Array = TypeFactory.define_type("int[2]", "Int2", True)
Int3, Int3Array = TypeFactory.define_type("int[3]", "Int3", True)
Int4, Int4Array = TypeFactory.define_type("int[4]", "Int4", True)
Int64, Int64Array = TypeFactory.define_type("int64", "Int64", True)
Matrix2d, Matrix2dArray = TypeFactory.define_type("matrixd[2]", "Matrix2d", True)
Matrix3d, Matrix3dArray = TypeFactory.define_type("matrixd[3]", "Matrix3d", True)
Matrix4d, Matrix4dArray = TypeFactory.define_type("matrixd[4]", "Matrix4d", True)
Normal3d, Normal3dArray = TypeFactory.define_type("normald[3]", "Normal3d", True)
Normal3f, Normal3fArray = TypeFactory.define_type("normalf[3]", "Normal3f", True)
Normal3h, Normal3hArray = TypeFactory.define_type("normalh[3]", "Normal3h", True)
ObjectId, ObjectIdArray = TypeFactory.define_type("objectId", "ObjectId", True)
Path, _ = TypeFactory.define_type("path", "Path", False)
Point3d, Point3dArray = TypeFactory.define_type("pointd[3]", "Point3d", True)
Point3f, Point3fArray = TypeFactory.define_type("pointf[3]", "Point3f", True)
Point3h, Point3hArray = TypeFactory.define_type("pointh[3]", "Point3h", True)
Quatd, QuatdArray = TypeFactory.define_type("quatd[4]", "Quatd", True)
Quatf, QuatfArray = TypeFactory.define_type("quatf[4]", "Quatf", True)
Quath, QuathArray = TypeFactory.define_type("quath[4]", "Quath", True)
String, _ = TypeFactory.define_type("string", "String", False)
Target, _ = TypeFactory.define_type("target", "Target", False)
TexCoord2d, TexCoord2dArray = TypeFactory.define_type("texcoordd[2]", "TexCoord2d", True)
TexCoord2f, TexCoord2fArray = TypeFactory.define_type("texcoordf[2]", "TexCoord2f", True)
TexCoord2h, TexCoord2hArray = TypeFactory.define_type("texcoordh[2]", "TexCoord2h", True)
TexCoord3d, TexCoord3dArray = TypeFactory.define_type("texcoordd[3]", "TexCoord3d", True)
TexCoord3f, TexCoord3fArray = TypeFactory.define_type("texcoordf[3]", "TexCoord3f", True)
TexCoord3h, TexCoord3hArray = TypeFactory.define_type("texcoordh[3]", "TexCoord3h", True)
Timecode, TimecodeArray = TypeFactory.define_type("timecode", "Timecode", True)
Token, TokenArray = TypeFactory.define_type("token", "Token", True)
UChar, UCharArray = TypeFactory.define_type("uchar", "UChar", True)
UInt, UIntArray = TypeFactory.define_type("uint", "UInt", True)
UInt64, UInt64Array = TypeFactory.define_type("uint64", "UInt64", True)
Vector3d, Vector3dArray = TypeFactory.define_type("vectord[3]", "Vector3d", True)
Vector3f, Vector3fArray = TypeFactory.define_type("vectorf[3]", "Vector3f", True)
Vector3h, Vector3hArray = TypeFactory.define_type("vectorh[3]", "Vector3h", True)

__all__ = [
    "TypeFactory",
    "Any",
    "Bool",
    "Bundle",
    "Color3d",
    "Color3f",
    "Color3h",
    "Color4d",
    "Color4f",
    "Color4h",
    "Double",
    "Double2",
    "Double3",
    "Double4",
    "Execution",
    "Float",
    "Float2",
    "Float3",
    "Float4",
    "Frame",
    "Half",
    "Half2",
    "Half3",
    "Half4",
    "Int",
    "Int2",
    "Int3",
    "Int4",
    "Int64",
    "Matrix2d",
    "Matrix3d",
    "Matrix4d",
    "Normal3d",
    "Normal3f",
    "Normal3h",
    "ObjectId",
    "Path",
    "Point3d",
    "Point3f",
    "Point3h",
    "Quatd",
    "Quatf",
    "Quath",
    "String",
    "Target",
    "TexCoord2d",
    "TexCoord2f",
    "TexCoord2h",
    "TexCoord3d",
    "TexCoord3f",
    "TexCoord3h",
    "Timecode",
    "Token",
    "UChar",
    "UInt",
    "UInt64",
    "Vector3d",
    "Vector3f",
    "Vector3h",
    "BoolArray",
    "Color3dArray",
    "Color3fArray",
    "Color3hArray",
    "Color4dArray",
    "Color4fArray",
    "Color4hArray",
    "DoubleArray",
    "Double2Array",
    "Double3Array",
    "Double4Array",
    "FloatArray",
    "Float2Array",
    "Float3Array",
    "Float4Array",
    "FrameArray",
    "HalfArray",
    "Half2Array",
    "Half3Array",
    "Half4Array",
    "IntArray",
    "Int2Array",
    "Int3Array",
    "Int4Array",
    "Int64Array",
    "Matrix2dArray",
    "Matrix3dArray",
    "Matrix4dArray",
    "Normal3dArray",
    "Normal3fArray",
    "Normal3hArray",
    "ObjectIdArray",
    "Point3dArray",
    "Point3fArray",
    "Point3hArray",
    "QuatdArray",
    "QuatfArray",
    "QuathArray",
    "TexCoord2dArray",
    "TexCoord2fArray",
    "TexCoord2hArray",
    "TexCoord3dArray",
    "TexCoord3fArray",
    "TexCoord3hArray",
    "TimecodeArray",
    "TokenArray",
    "UCharArray",
    "UIntArray",
    "UInt64Array",
    "Vector3dArray",
    "Vector3fArray",
    "Vector3hArray",
]
