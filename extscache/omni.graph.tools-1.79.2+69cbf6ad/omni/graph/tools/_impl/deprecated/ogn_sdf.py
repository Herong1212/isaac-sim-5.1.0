"""Helper which contains utilities and data for converting between type representations"""

from pxr import Sdf

from ..deprecate import deprecated_function

# ==============================================================================================================
# Mapping of pxr.Sdf.ValueTypeNames to corresponding OGN types (not including the Array/[] suffixes)
_SDF_BASE_NAME_TO_OGN = {
    "Bool": "bool",
    "Color3d": "colord[3]",
    "Color3f": "colorf[3]",
    "Color3h": "colorh[3]",
    "Color4d": "colord[4]",
    "Color4f": "colorf[4]",
    "Color4h": "colorh[4]",
    "Double": "double",
    "Double2": "double[2]",
    "Double3": "double[3]",
    "Double4": "double[4]",
    "Float": "float",
    "Float2": "float[2]",
    "Float3": "float[3]",
    "Float4": "float[4]",
    "Frame4d": "framed[4]",
    "Half": "half",
    "Half2": "half[2]",
    "Half3": "half[3]",
    "Half4": "half[4]",
    "Int": "int",
    "Int2": "int[2]",
    "Int3": "int[3]",
    "Int4": "int[4]",
    "Int64": "int64",
    "Matrix2d": "matrixd[2]",
    "Matrix3d": "matrixd[3]",
    "Matrix4d": "matrixd[4]",
    "Normal3d": "normald[3]",
    "Normal3f": "normalf[3]",
    "Normal3h": "normalh[3]",
    "Point3d": "pointd[3]",
    "Point3f": "pointf[3]",
    "Point3h": "pointh[3]",
    "Quatd": "quatd[4]",
    "Quatf": "quatf[4]",
    "Quath": "quath[4]",
    "String": "string",
    "TexCoord2d": "texcoordd[2]",
    "TexCoord2f": "texcoordf[2]",
    "TexCoord2h": "texcoordh[2]",
    "TexCoord3d": "texcoordd[3]",
    "TexCoord3f": "texcoordf[3]",
    "TexCoord3h": "texcoordh[3]",
    "TimeCode": "timecode",
    "Token": "token",
    "UChar": "uchar",
    "UInt": "uint",
    "UInt64": "uint64",
    "Vector3d": "vectord[3]",
    "Vector3f": "vectorf[3]",
    "Vector3h": "vectorh[3]",
}

# Mapping of OGN types to SDF - not all OGN types can be translated directly
_OGN_TO_SDF_BASE_NAME = {value: key for key, value in _SDF_BASE_NAME_TO_OGN.items()}

# As the Sdf.ValueTypeNames are static Boost objects create a mapping of them back to OGN to avoid linear lookup
_SDF_TO_OGN = {getattr(Sdf.ValueTypeNames, key): value for key, value in _SDF_BASE_NAME_TO_OGN.items()}
_SDF_TO_OGN.update(
    {getattr(Sdf.ValueTypeNames, f"{key}Array"): f"{value}[]" for key, value in _SDF_BASE_NAME_TO_OGN.items()}
)


# ==============================================================================================================
@deprecated_function("Use omni.graph.tools.type_conversion.convert_type_name instead")
def ogn_to_sdf(ogn_type: str) -> Sdf.ValueTypeNames | None:  # pragma: no cover
    """Convert an OGN type string to the equivalent SDF value type name

    Args:
        ogn_type: String representation of the OGN type as described in its documentation

    Return:
        Equivalent pxr.Sdf.ValueTypeNames value, or None if there is no equivalent
    """
    is_array = False
    if ogn_type[-2:] == "[]":
        is_array = True
        ogn_type = ogn_type[:-2]

    try:
        sdf_type_name = _OGN_TO_SDF_BASE_NAME[ogn_type]
        if is_array:
            sdf_type_name += "Array"
        sdf_type = getattr(Sdf.ValueTypeNames, sdf_type_name, None)
    except KeyError:
        sdf_type = None

    return sdf_type


# ==============================================================================================================
@deprecated_function("Use omni.graph.tools.type_conversion.convert_type_name instead")
def sdf_to_ogn(sdf_type: Sdf.ValueTypeName) -> str | None:  # pragma: no cover
    """Convert an SDF type to the equivalent OGN type name

    Args:
        sdf_type: String representation of the SDF type as described in its documentation

    Return:
        Equivalent OGN string name value, or None if there is no equivalent
    """
    is_array = False
    if str(sdf_type)[-5:] == "Array":
        is_array = True

    try:
        ogn_type_name = _SDF_TO_OGN[sdf_type]
        if is_array:
            ogn_type_name += "[]"
    except KeyError:
        ogn_type_name = None

    return ogn_type_name
