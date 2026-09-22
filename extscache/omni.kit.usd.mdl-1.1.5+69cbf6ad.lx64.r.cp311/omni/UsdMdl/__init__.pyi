from __future__ import annotations
import omni.UsdMdl._usdMdl
import typing
import Boost.Python
import pxr.Ndr
import pxr.Sdr

__all__ = [
    "ExpressionKinds",
    "FunctionDefinitionTypes",
    "GetAllMetadataTokens",
    "Metadata",
    "Neuray",
    "Notice",
    "OmniSdrShaderNode",
    "OmniSdrShaderNodeList",
    "RegistryUtils",
    "StructTypes",
    "Tokens",
    "TypeModifiers",
    "Types"
]


class ExpressionKinds(Boost.Python.instance):
    Call = 'Call'
    Parameter = 'Parameter'
    pass
class FunctionDefinitionTypes(Boost.Python.instance):
    Function = 'function'
    Material = 'material'
    pass
class Metadata(Boost.Python.instance):
    Annotation = 'annotation'
    ArrayDeferredSizeSymbol = 'deferred_symbol'
    ArrayElementType = 'element_renderType'
    DefinitionType = 'definitionType'
    ExpressionKind = 'expressionKind'
    ExpressionValue = 'expressionValue'
    MdlName = 'mdlName'
    Modifier = 'modifier'
    Module = 'module'
    Semantic = 'semantic'
    StructType = 'structType'
    Symbol = 'symbol'
    TextureGamma = 'gamma'
    TextureSelector = 'selector'
    Thumbnail = 'thumbnail'
    Type = 'type'
    Value = 'value'
    Version = 'version'
    pass
class Neuray(Boost.Python.instance):
    @staticmethod
    def Shutdown(*args, **kwargs) -> typing.Any: ...
    pass
class Notice(Boost.Python.instance):
    class ModuleLoaded(ModuleNotice, pxr.Tf.Notice, Boost.Python.instance):
        @staticmethod
        def GetResolvedPath(*args, **kwargs) -> typing.Any: ...
        pass
    class ModuleNotice(pxr.Tf.Notice, Boost.Python.instance):
        pass
    class ModuleReloaded(ModuleNotice, pxr.Tf.Notice, Boost.Python.instance):
        @staticmethod
        def GetResolvedPath(*args, **kwargs) -> typing.Any: ...
        pass
    pass
class OmniSdrShaderNode(pxr.Sdr.ShaderNode, pxr.Ndr.Node, Boost.Python.instance):
    @staticmethod
    def GetAssetPath(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDefinitionType(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetModuleUsdIdentifier(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetModuleVersion(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNameWithSignature(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSubIdentifier(*args, **kwargs) -> typing.Any: ...
    pass
class OmniSdrShaderNodeList(Boost.Python.instance):
    @staticmethod
    def append(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def extend(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 48
    pass
class RegistryUtils(Boost.Python.instance):
    @staticmethod
    def AddModuleToRegistry(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def AddModulesToRegistry(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def FindShaderNodeForPrim(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIdentifierForAsset(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetOverloads(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetShaderNode(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetShaderNodeForPrim(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSubIdentifierFromIdentifier(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSubIdentifiersForAsset(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsModuleLoaded(*args, **kwargs) -> typing.Any: ...
    pass
class StructTypes(Boost.Python.instance):
    Material = 'material'
    Material_Emission = 'material_emission'
    Material_Geometry = 'material_geometry'
    Material_Surface = 'material_surface'
    Material_Volume = 'material_volume'
    User = 'user'
    pass
class Tokens(Boost.Python.instance):
    DefaultOutputPortName = 'out'
    Mdl = 'mdl'
    pass
class TypeModifiers(Boost.Python.instance):
    Uniform = 'uniform'
    Varying = 'varying'
    pass
class Types(Boost.Python.instance):
    Array = '[]'
    Bool = 'bool'
    Bool2 = 'bool2'
    Bool3 = 'bool3'
    Bool4 = 'bool4'
    Bsdf = 'bsdf'
    Bsdf_Measurement = 'bsdf_measurement'
    Color = 'color'
    Double = 'double'
    Double2 = 'double2'
    Double2x2 = 'double2x2'
    Double2x3 = 'double2x3'
    Double2x4 = 'double2x4'
    Double3 = 'double3'
    Double3x2 = 'double3x2'
    Double3x3 = 'double3x3'
    Double3x4 = 'double3x4'
    Double4 = 'double4'
    Double4x2 = 'double4x2'
    Double4x3 = 'double4x3'
    Double4x4 = 'double4x4'
    Edf = 'edf'
    Enum = 'enum'
    Float = 'float'
    Float2 = 'float2'
    Float2x2 = 'float2x2'
    Float2x3 = 'float2x3'
    Float2x4 = 'float2x4'
    Float3 = 'float3'
    Float3x2 = 'float3x2'
    Float3x3 = 'float3x3'
    Float3x4 = 'float3x4'
    Float4 = 'float4'
    Float4x2 = 'float4x2'
    Float4x3 = 'float4x3'
    Float4x4 = 'float4x4'
    Hair_Bsdf = 'hair_bsdf'
    Int = 'int'
    Int2 = 'int2'
    Int3 = 'int3'
    Int4 = 'int4'
    Light_Profile = 'light_profile'
    String = 'string'
    Struct = 'struct'
    Texture2d = 'texture_2d'
    Texture3d = 'texture_3d'
    TextureBsdfData = 'texture_bsdf_data'
    TextureCube = 'texture_cube'
    TexturePtex = 'texture_ptex'
    Vdf = 'vdf'
    pass
def GetAllMetadataTokens(*args, **kwargs) -> typing.Any:
    pass
__MFB_FULL_PACKAGE_NAME = 'usdMdl'
