from __future__ import annotations
import usdrt.Sdf._Sdf
import typing

__all__ = [
    "AncestorsRange",
    "AssetPath",
    "Path",
    "ValueTypeName",
    "ValueTypeNames"
]


class AncestorsRange():
    def GetPath(self) -> Path: ...
    def __init__(self, arg0: Path) -> None: ...
    def __iter__(self) -> typing.Iterator: ...
    pass
class AssetPath():
    def __eq__(self, arg0: AssetPath) -> bool: ...
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, path: str) -> None: ...
    @typing.overload
    def __init__(self, path: str, resolvedPath: str) -> None: ...
    def __ne__(self, arg0: AssetPath) -> bool: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def path(self) -> str:
        """
        :type: str
        """
    @property
    def resolvedPath(self) -> str:
        """
        :type: str
        """
    __hash__ = None
    pass
class Path():
    def AppendChild(self, childName: TfToken) -> Path: ...
    def AppendPath(self, newSuffix: Path) -> Path: ...
    def AppendProperty(self, propName: TfToken) -> Path: ...
    def ContainsPropertyElements(self) -> bool: ...
    def GetAbsoluteRootOrPrimPath(self) -> Path: ...
    @staticmethod
    def GetAncestorsRange(*args, **kwargs) -> typing.Any: ...
    def GetCommonPrefix(self, path: Path) -> Path: ...
    def GetNameToken(self) -> TfToken: ...
    def GetParentPath(self) -> Path: ...
    def GetPrefixes(self) -> typing.List[Path]: ...
    def GetPrimPath(self) -> Path: ...
    def GetString(self) -> str: ...
    def GetText(self) -> str: ...
    def GetToken(self) -> TfToken: ...
    def HasPrefix(self, prefix: Path) -> bool: ...
    def IsAbsolutePath(self) -> bool: ...
    def IsAbsoluteRootOrPrimPath(self) -> bool: ...
    def IsAbsoluteRootPath(self) -> bool: ...
    def IsEmpty(self) -> bool: ...
    def IsNamespacedPropertyPath(self) -> bool: ...
    def IsPrimPath(self) -> bool: ...
    def IsPrimPropertyPath(self) -> bool: ...
    def IsPropertyPath(self) -> bool: ...
    def IsRootPrimPath(self) -> bool: ...
    @staticmethod
    def IsValidIdentifier(name: str) -> bool: ...
    @staticmethod
    def IsValidNamespacedIdentifier(name: str) -> bool: ...
    @staticmethod
    def IsValidPathString(pathString: str) -> bool: ...
    @staticmethod
    @typing.overload
    def JoinIdentifier(lhs: str, rhs: str) -> str: ...
    @staticmethod
    @typing.overload
    def JoinIdentifier(lhs: TfToken, rhs: TfToken) -> str: ...
    @staticmethod
    @typing.overload
    def JoinIdentifier(names: typing.List[TfToken]) -> str: ...
    def RemoveCommonSuffix(self, otherPath: Path, stopAtRootPrim: bool = False) -> typing.Tuple[Path, Path]: ...
    def ReplaceName(self, newName: TfToken) -> Path: ...
    def ReplacePrefix(self, oldPrefix: Path, newPrefix: Path, fixTargetPaths: bool = True) -> Path: ...
    @staticmethod
    def StripPrefixNamespace(name: str, matchNamespace: str) -> tuple: ...
    @staticmethod
    def StripSuffixNamespace(name: str, matchNamespace: str) -> tuple: ...
    @staticmethod
    def TokenizeIdentifier(name: str) -> typing.List[str]: ...
    def __eq__(self, arg0: Path) -> bool: ...
    def __hash__(self) -> int: ...
    @typing.overload
    def __init__(self, arg0: str) -> None: ...
    @typing.overload
    def __init__(self, arg0: Path) -> None: ...
    @typing.overload
    def __init__(self) -> None: ...
    def __lt__(self, arg0: Path) -> bool: ...
    def __ne__(self, arg0: Path) -> bool: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def isEmpty(self) -> bool:
        """
        :type: bool
        """
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def pathC(self) -> usdrt.helpers._helpers.PathC:
        """
        :type: usdrt.helpers._helpers.PathC
        """
    @property
    def pathElementCount(self) -> int:
        """
        :type: int
        """
    @property
    def pathString(self) -> str:
        """
        :type: str
        """
    absoluteRootPath: usdrt.Sdf._Sdf.Path # value = Sdf.Path('/')
    emptyPath: usdrt.Sdf._Sdf.Path # value = Sdf.Path('')
    pass
class ValueTypeName():
    def GetAsString(self) -> str: ...
    def GetAsToken(self) -> TfToken: ...
    @staticmethod
    def GetAsTypeC(*args, **kwargs) -> typing.Any: ...
    def __eq__(self, arg0: ValueTypeName) -> bool: ...
    def __hash__(self) -> int: ...
    def __init__(self) -> None: ...
    def __ne__(self, arg0: ValueTypeName) -> bool: ...
    def __repr__(self) -> str: ...
    @property
    def arrayType(self) -> ValueTypeName:
        """
        :type: ValueTypeName
        """
    @property
    def isArray(self) -> bool:
        """
        :type: bool
        """
    @property
    def isScalar(self) -> bool:
        """
        :type: bool
        """
    @property
    def scalarType(self) -> ValueTypeName:
        """
        :type: ValueTypeName
        """
    pass
class ValueTypeNames():
    AncestorPrimTypeTag: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('tag (ancestorPrimTypeName)')
    AppliedSchemaTypeTag: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('tag (appliedSchema)')
    Asset: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('asset')
    AssetArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('asset[]')
    Bool: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('bool')
    BoolArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('bool[]')
    Color3d: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double3 (color)')
    Color3dArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double3[] (color)')
    Color3f: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float3 (color)')
    Color3fArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float3[] (color)')
    Color3h: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half3 (color)')
    Color3hArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half3[] (color)')
    Color4d: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double4 (color)')
    Color4dArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double4[] (color)')
    Color4f: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float4 (color)')
    Color4fArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float4[] (color)')
    Color4h: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half4 (color)')
    Color4hArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half4[] (color)')
    Double: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double')
    Double2: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double2')
    Double2Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double2[]')
    Double3: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double3')
    Double3Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double3[]')
    Double4: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double4')
    Double4Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double4[]')
    DoubleArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double[]')
    Float: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float')
    Float2: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float2')
    Float2Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float2[]')
    Float3: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float3')
    Float3Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float3[]')
    Float4: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float4')
    Float4Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float4[]')
    FloatArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float[]')
    Frame4d: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double16 (frame)')
    Frame4dArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double16[] (frame)')
    Half: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half')
    Half2: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half2')
    Half2Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half2[]')
    Half3: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half3')
    Half3Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half3[]')
    Half4: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half4')
    Half4Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half4[]')
    HalfArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half[]')
    Int: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('int')
    Int2: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('int2')
    Int2Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('int2[]')
    Int3: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('int3')
    Int3Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('int3[]')
    Int4: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('int4')
    Int4Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('int4[]')
    Int64: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('int64')
    Int64Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('int64[]')
    IntArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('int[]')
    Matrix2d: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double4 (matrix)')
    Matrix2dArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double4[] (matrix)')
    Matrix3d: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double9 (matrix)')
    Matrix3dArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double9[] (matrix)')
    Matrix4d: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double16 (matrix)')
    Matrix4dArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double16[] (matrix)')
    Normal3d: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double3 (normal)')
    Normal3dArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double3[] (normal)')
    Normal3f: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float3 (normal)')
    Normal3fArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float3[] (normal)')
    Normal3h: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half3 (normal)')
    Normal3hArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half3[] (normal)')
    Point3d: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double3 (position)')
    Point3dArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double3[] (position)')
    Point3f: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float3 (position)')
    Point3fArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float3[] (position)')
    Point3h: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half3 (position)')
    Point3hArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half3[] (position)')
    PrimTypeTag: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('tag (primTypeName)')
    Quatd: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double4 (quaternion)')
    QuatdArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double4[] (quaternion)')
    Quatf: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float4 (quaternion)')
    QuatfArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float4[] (quaternion)')
    Quath: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half4 (quaternion)')
    QuathArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half4[] (quaternion)')
    Range3d: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double6')
    String: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('uchar[] (text)')
    StringArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('uchar[][] (text)')
    Tag: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('tag')
    TexCoord2d: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double2 (texCoord)')
    TexCoord2dArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double2[] (texCoord)')
    TexCoord2f: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float2 (texCoord)')
    TexCoord2fArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float2[] (texCoord)')
    TexCoord2h: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half2 (texCoord)')
    TexCoord2hArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half2[] (texCoord)')
    TexCoord3d: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double3 (texCoord)')
    TexCoord3dArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double3[] (texCoord)')
    TexCoord3f: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float3 (texCoord)')
    TexCoord3fArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float3[] (texCoord)')
    TexCoord3h: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half3 (texCoord)')
    TexCoord3hArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half3[] (texCoord)')
    TimeCode: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double (timecode)')
    TimeCodeArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double[] (timecode)')
    Token: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('token')
    TokenArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('token[]')
    UChar: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('uchar')
    UCharArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('uchar[]')
    UInt: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('uint')
    UInt64: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('uint64')
    UInt64Array: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('uint64[]')
    UIntArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('uint[]')
    Vector3d: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double3 (vector)')
    Vector3dArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('double3[] (vector)')
    Vector3f: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float3 (vector)')
    Vector3fArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('float3[] (vector)')
    Vector3h: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half3 (vector)')
    Vector3hArray: usdrt.Sdf._Sdf.ValueTypeName # value = Sdf.ValueTypeName('half3[] (vector)')
    pass
