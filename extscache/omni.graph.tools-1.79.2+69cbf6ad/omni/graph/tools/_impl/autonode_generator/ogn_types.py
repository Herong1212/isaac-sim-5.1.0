"""Helper which contains utilities and data for converting between type representations used by OmniGraph"""

import enum
import logging
from collections import namedtuple
from contextlib import suppress
from pprint import pformat
from typing import NewType

ALL_OGN_DATA_TYPES = []
"""This is a list containing annotations for all of the supported OmniGraph data
types. They can be used for type annotations on functions that process attribute data:

    .. code-block:: python

        import omni.graph.tools._impl.autonode_generator.ogn_types as ogdt

        def add_two_floats(float1: ogdt.Float, float2: ogdt.Float) -> ogdt.Float:
            return float1 + float2

To see information on any individual type in the list you can ask for its help information:

    .. code-block:: bash

        $ import omni.graph.tools._impl.autonode_generator.ogn_types as ogdt
        $ help(ogdt.Float3)
        Float3 = omni.graph.tools._impl.autonode_generator.ogn_types.Float3
            This type annotation corresponds to the OGN type 'float[3]'
"""

_logger = logging.getLogger("AutoNode")


# ==============================================================================================================
class OmniGraphDataType:
    """Simple base class that provides a common type definition for all OmniGraph-specific data types"""


# ==============================================================================================================
def _define_data_type_annotation(
    ogn_type_name: str, type_var_name: str, supports_arrays: bool
) -> tuple[type, type] | type:  # pragma: no cover    Unsupported code
    """Create new type annotations for the given type specifications
    Args:
        ogn_type_name: Name of the data type used by OmniGraph, especially in the .ogn file
        type_var_name: Name of the variable that will hold the data type
        supports_arrays: True if the data type can also have a version with arrays
    Returns:
        The type definition for the non-array type, optionally as a tuple where the second element is the type
        definition for that array version of the type
    """
    _logger.debug(
        "Defining data type '%s' as '%s'%s",
        ogn_type_name,
        type_var_name,
        f" and array '{type_var_name}Array" if supports_arrays else "",
    )

    simple_type = NewType(type_var_name, OmniGraphDataType)
    simple_type.__doc__ = f"Type annotation to use for OmniGraph attribute data of type '{ogn_type_name}'"
    ALL_OGN_DATA_TYPES.append(simple_type)

    if supports_arrays:
        array_type = NewType(f"{type_var_name}Array", OmniGraphDataType)
        array_type.__doc__ = f"Type annotation to use for OmniGraph attribute aray data of type '{ogn_type_name}[]'"
        ALL_OGN_DATA_TYPES.append(array_type)
        return (simple_type, array_type)

    return simple_type


# ==============================================================================================================
# Definition of all supported data types. Currently these are solely used for type annotations, however in the future
# they might be expanded to be actual type handlers (OM-86318 for details)
Any = _define_data_type_annotation("any", "Any", False)
Bool, BoolArray = _define_data_type_annotation("bool", "Bool", True)
Bundle = _define_data_type_annotation("bundle", "Bundle", False)
Color3d, Color3dArray = _define_data_type_annotation("colord[3]", "Color3d", True)
Color3f, Color3fArray = _define_data_type_annotation("colorf[3]", "Color3f", True)
Color3h, Color3hArray = _define_data_type_annotation("colorh[3]", "Color3h", True)
Color4d, Color4dArray = _define_data_type_annotation("colord[4]", "Color4d", True)
Color4f, Color4fArray = _define_data_type_annotation("colorf[4]", "Color4f", True)
Color4h, Color4hArray = _define_data_type_annotation("colorh[4]", "Color4h", True)
Double, DoubleArray = _define_data_type_annotation("double", "Double", True)
Double2, Double2Array = _define_data_type_annotation("double[2]", "Double2", True)
Double3, Double3Array = _define_data_type_annotation("double[3]", "Double3", True)
Double4, Double4Array = _define_data_type_annotation("double[4]", "Double4", True)
Execution = _define_data_type_annotation("execution", "Execution", False)
Float, FloatArray = _define_data_type_annotation("float", "Float", True)
Float2, Float2Array = _define_data_type_annotation("float[2]", "Float2", True)
Float3, Float3Array = _define_data_type_annotation("float[3]", "Float3", True)
Float4, Float4Array = _define_data_type_annotation("float[4]", "Float4", True)
Frame, FrameArray = _define_data_type_annotation("frame[4]", "Frame", True)
Half, HalfArray = _define_data_type_annotation("half", "Half", True)
Half2, Half2Array = _define_data_type_annotation("half[2]", "Half2", True)
Half3, Half3Array = _define_data_type_annotation("half[3]", "Half3", True)
Half4, Half4Array = _define_data_type_annotation("half[4]", "Half4", True)
Int, IntArray = _define_data_type_annotation("int", "Int", True)
Int2, Int2Array = _define_data_type_annotation("int[2]", "Int2", True)
Int3, Int3Array = _define_data_type_annotation("int[3]", "Int3", True)
Int4, Int4Array = _define_data_type_annotation("int[4]", "Int4", True)
Int64, Int64Array = _define_data_type_annotation("int64", "Int64", True)
Matrix2d, Matrix2dArray = _define_data_type_annotation("matrixd[2]", "Matrix2d", True)
Matrix3d, Matrix3dArray = _define_data_type_annotation("matrixd[3]", "Matrix3d", True)
Matrix4d, Matrix4dArray = _define_data_type_annotation("matrixd[4]", "Matrix4d", True)
Normal3d, Normal3dArray = _define_data_type_annotation("normald[3]", "Normal3d", True)
Normal3f, Normal3fArray = _define_data_type_annotation("normalf[3]", "Normal3f", True)
Normal3h, Normal3hArray = _define_data_type_annotation("normalh[3]", "Normal3h", True)
ObjectId, ObjectIdArray = _define_data_type_annotation("objectId", "ObjectId", True)
Path = _define_data_type_annotation("path", "Path", False)
Point3d, Point3dArray = _define_data_type_annotation("pointd[3]", "Point3d", True)
Point3f, Point3fArray = _define_data_type_annotation("pointf[3]", "Point3f", True)
Point3h, Point3hArray = _define_data_type_annotation("pointh[3]", "Point3h", True)
Quatd, QuatdArray = _define_data_type_annotation("quatd[4]", "Quatd", True)
Quatf, QuatfArray = _define_data_type_annotation("quatf[4]", "Quatf", True)
Quath, QuathArray = _define_data_type_annotation("quath[4]", "Quath", True)
String = _define_data_type_annotation("string", "String", False)
Target = _define_data_type_annotation("target", "Target", False)
TexCoord2d, TexCoord2dArray = _define_data_type_annotation("texcoordd[2]", "TexCoord2d", True)
TexCoord2f, TexCoord2fArray = _define_data_type_annotation("texcoordf[2]", "TexCoord2f", True)
TexCoord2h, TexCoord2hArray = _define_data_type_annotation("texcoordh[2]", "TexCoord2h", True)
TexCoord3d, TexCoord3dArray = _define_data_type_annotation("texcoordd[3]", "TexCoord3d", True)
TexCoord3f, TexCoord3fArray = _define_data_type_annotation("texcoordf[3]", "TexCoord3f", True)
TexCoord3h, TexCoord3hArray = _define_data_type_annotation("texcoordh[3]", "TexCoord3h", True)
Timecode, TimecodeArray = _define_data_type_annotation("timecode", "Timecode", True)
Token, TokenArray = _define_data_type_annotation("token", "Token", True)
UChar, UCharArray = _define_data_type_annotation("uchar", "UChar", True)
UInt, UIntArray = _define_data_type_annotation("uint", "UInt", True)
UInt64, UInt64Array = _define_data_type_annotation("uint64", "UInt64", True)
Vector3d, Vector3dArray = _define_data_type_annotation("vectord[3]", "Vector3d", True)
Vector3f, Vector3fArray = _define_data_type_annotation("vectorf[3]", "Vector3f", True)
Vector3h, Vector3hArray = _define_data_type_annotation("vectorh[3]", "Vector3h", True)


TypeDesc = namedtuple(
    "TypeDesc",
    [
        "type",
        "ogn_type",
        "type_to_og",
        "type_to_og_conversion_method",
        "og_to_type",
        "og_to_type_conversion_method",
        "default",
    ],
)
"""Container for the set of conversion operators for a given OmniGraph type/Python type combination"""


# ==============================================================================================================
class TypeConversion:  # pragma: no cover    Unsupported code
    """Static class for storing conversion methods between python types and Omnigraph types"""

    class ToConvert(enum.Enum):
        ASSIGN = (0,)
        """Return the value to be assigned to the destination"""
        MODIFY = 1
        """Pass in the destination object to be modified in place"""

    # List of all accepted type descriptions. In addition to the specific type definitions above the native Python
    # types are also recognized, where the type definition can be converted into one of those types directly. This
    # allows the users to write functions using normal Python types if they wish, though using the type definitions
    # is preferred and unambiguous.
    # TODO: It would be nice if users could just use generic Python types like int, float, tuple[int, int], etc.
    #       It should be possible to create converters for them, it's just a matter of creating a type identifier
    _TYPE_DEFINITIONS = [
        (Any, "any", None),
        (Bool, "bool", False),
        (BoolArray, "bool[]", []),
        (Bundle, "bundle", None),
        (Color3d, "colord[3]", (0.0, 0.0, 0.0)),
        (Color3f, "colorf[3]", (0.0, 0.0, 0.0)),
        (Color3h, "colorh[3]", (0.0, 0.0, 0.0)),
        (Color4d, "colord[4]", (0.0, 0.0, 0.0, 0.0)),
        (Color4f, "colorf[4]", (0.0, 0.0, 0.0, 0.0)),
        (Color4h, "colorh[4]", (0.0, 0.0, 0.0, 0.0)),
        (Color3dArray, "colord[3][]", []),
        (Color3fArray, "colorf[3][]", []),
        (Color3hArray, "colorh[3][]", []),
        (Color4dArray, "colord[4][]", []),
        (Color4fArray, "colorf[4][]", []),
        (Color4hArray, "colorh[4][]", []),
        (Double, "double", 0.0),
        (Double2, "double[2]", (0.0, 0.0)),
        (Double3, "double[3]", (0.0, 0.0, 0.0)),
        (Double4, "double[4]", (0.0, 0.0, 0.0, 0.0)),
        (DoubleArray, "double[]", []),
        (Double2Array, "double[2][]", []),
        (Double3Array, "double[3][]", []),
        (Double4Array, "double[4][]", []),
        (Execution, "execution", 0),
        (Float, "float", 0.0),
        (Float2, "float[2]", (0.0, 0.0)),
        (Float3, "float[3]", (0.0, 0.0, 0.0)),
        (Float4, "float[4]", (0.0, 0.0, 0.0, 0.0)),
        (FloatArray, "float[]", 0.0),
        (Float2Array, "float[2][]", []),
        (Float3Array, "float[3][]", []),
        (Float4Array, "float[4][]", []),
        (Frame, "frame[4]", [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]),
        (FrameArray, "frame[4][]", []),
        (Half, "half", 0.0),
        (Half2, "half[2]", (0.0, 0.0)),
        (Half3, "half[3]", (0.0, 0.0, 0.0)),
        (Half4, "half[4]", (0.0, 0.0, 0.0, 0.0)),
        (HalfArray, "half[]", 0.0),
        (Half2Array, "half[2][]", []),
        (Half3Array, "half[3][]", []),
        (Half4Array, "half[4][]", []),
        (Int, "int", 0),
        (Int2, "int[2]", (0, 0)),
        (Int3, "int[3]", (0, 0, 0)),
        (Int4, "int[4]", (0, 0, 0, 0)),
        (Int64, "int64", 0),
        (IntArray, "int[]", []),
        (Int2Array, "int[2][]", []),
        (Int3Array, "int[3][]", []),
        (Int4Array, "int[4][]", []),
        (Int64Array, "int64[]", []),
        (Matrix2d, "matrixd[2]", [[1.0, 0.0], [0.0, 1.0]]),
        (Matrix3d, "matrixd[3]", [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
        (
            Matrix4d,
            "matrixd[4]",
            [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
        ),
        (Matrix2dArray, "matrixd[2][]", []),
        (Matrix3dArray, "matrixd[3][]", []),
        (Matrix4dArray, "matrixd[4][]", []),
        (Normal3d, "normald[3]", (0.0, 0.0, 0.0)),
        (Normal3f, "normalf[3]", (0.0, 0.0, 0.0)),
        (Normal3h, "normalh[3]", (0.0, 0.0, 0.0)),
        (Normal3dArray, "normald[3][]", []),
        (Normal3fArray, "normalf[3][]", []),
        (Normal3hArray, "normalh[3][]", []),
        (ObjectId, "objectId", 0),
        (ObjectIdArray, "objectId[]", 0),
        (Path, "path", ""),
        (Point3d, "pointd[3]", (0.0, 0.0, 0.0)),
        (Point3f, "pointf[3]", (0.0, 0.0, 0.0)),
        (Point3h, "pointh[3]", (0.0, 0.0, 0.0)),
        (Point3dArray, "pointd[3][]", []),
        (Point3fArray, "pointf[3][]", []),
        (Point3hArray, "pointh[3][]", []),
        (Quatd, "quatd[4]", (0.0, 0.0, 0.0, 0.0)),
        (Quatf, "quatf[4]", (0.0, 0.0, 0.0, 0.0)),
        (Quath, "quath[4]", (0.0, 0.0, 0.0, 0.0)),
        (QuatdArray, "quatd[4][]", []),
        (QuatfArray, "quatf[4][]", []),
        (QuathArray, "quath[4][]", []),
        (String, "string", ""),
        (Target, "target", []),
        (TexCoord2d, "texcoordd[2]", (0.0, 0.0)),
        (TexCoord2f, "texcoordf[2]", (0.0, 0.0)),
        (TexCoord2h, "texcoordh[2]", (0.0, 0.0)),
        (TexCoord3d, "texcoordd[3]", (0.0, 0.0, 0.0)),
        (TexCoord3f, "texcoordf[3]", (0.0, 0.0, 0.0)),
        (TexCoord3h, "texcoordh[3]", (0.0, 0.0, 0.0)),
        (TexCoord2dArray, "texcoordd[2][]", []),
        (TexCoord2fArray, "texcoordf[2][]", []),
        (TexCoord2hArray, "texcoordh[2][]", []),
        (TexCoord3dArray, "texcoordd[3][]", []),
        (TexCoord3fArray, "texcoordf[3][]", []),
        (TexCoord3hArray, "texcoordh[3][]", []),
        (Timecode, "timecode", 0.0),
        (TimecodeArray, "timecode[]", []),
        (Token, "token", ""),
        (TokenArray, "token[]", []),
        (UChar, "uchar", 0),
        (UInt, "uint", 0),
        (UInt64, "uint64", 0),
        (UCharArray, "uchar[]", []),
        (UIntArray, "uint[]", []),
        (UInt64Array, "uint64[]", []),
        (Vector3d, "vectord[3]", (0.0, 0.0, 0.0)),
        (Vector3f, "vectorf[3]", (0.0, 0.0, 0.0)),
        (Vector3h, "vectorh[3]", (0.0, 0.0, 0.0)),
        (Vector3dArray, "vectord[3][]", []),
        (Vector3fArray, "vectorf[3][]", []),
        (Vector3hArray, "vectorh[3][]", []),
    ]
    # More efficient storage for lookups
    _TYPES = {}
    _OGN_TYPES = {}
    _USER_TYPES = {}
    _OGN_USER_TYPES = {}
    _ASSIGN = (ToConvert.ASSIGN, None, ToConvert.ASSIGN)  # To keep lines short
    for type_def, ogn_type_name, default_value in _TYPE_DEFINITIONS:
        _TYPES[type_def.__name__] = TypeDesc(type_def, ogn_type_name, None, *_ASSIGN, default_value)
        _OGN_TYPES[ogn_type_name] = TypeDesc(type_def, ogn_type_name, None, *_ASSIGN, default_value)

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def from_type(cls, type_desc: type | str) -> TypeDesc:
        """Searches the conversion registry using a Python type.

        Args:
            type_desc: Python type or name of Python type to convert
        Returns:
            TypeDesc for the found Python type if it's found
        Raises:
            ValueError: If the type description was not one of the known parseable types
        """
        try:
            type_name = type_desc.__name__
        except AttributeError:
            # Remove the namespace from the type as it could be anything, depending on how the user defined the import
            type_name = type_desc.split(".")[-1]

        with suppress(KeyError):
            return cls._USER_TYPES[type_name]

        try:
            # NOTE (oshapira): Here we do a conversion to string of the candidate type.
            # This is because currently the compiler is merely a parser, and can't determine types in the environment.
            # This will end up changing and we'll have a parser from an existing compiler like mypy that will be able
            # to do a deeper type conversion. but for now, we need to convert manually.
            #
            return cls._TYPES[type_name]
        except KeyError as error:
            accepted_types = pformat(list(cls._USER_TYPES.keys()) + list(cls._TYPES.keys()), indent=2, compact=True)
            raise ValueError(f"Type '{type_desc}' not one of the accepted types {accepted_types}") from error

    # --------------------------------------------------------------------------------------------------------------
    @classmethod
    def from_ogn_type(cls, ogn_type: str) -> TypeDesc:
        """Searches the conversion registry using an Omnigraph type.
        Searches the user types first, defaults to the system types.

        Args:
            ogn_type: string representing the incoming ogn type
        Returns:
            TypeDesc for the found Python type if it's found
        Raises:
            ValueError: If the type description was not one of the known parseable types
        """
        with suppress(KeyError):
            return cls._OGN_USER_TYPES[ogn_type]

        try:
            # NOTE (oshapira): Here we do a conversion to string of the candidate type.
            # This is because currently the compiler is merely a parser, and can't determine types in the environment.
            # This will end up changing and we'll have a parser from an existing compiler like mypy that will be able
            # to do a deeper type conversion. but for now, we need to convert manually.
            #
            return cls._OGN_TYPES[ogn_type]
        except KeyError as error:
            accepted_types = list(cls._OGN_USER_TYPES.keys()) + list(cls._OGN_TYPES.keys())
            accepted_types = pformat(accepted_types, indent=2, compact=True)
            raise ValueError(f"Type '{ogn_type}' not one of the recognized types {accepted_types}") from error
