from __future__ import annotations
import pxr.Sdr._sdr
import typing
import Boost.Python
import pxr.Ndr

__all__ = [
    "NodeContext",
    "NodeMetadata",
    "NodeRole",
    "PropertyMetadata",
    "PropertyRole",
    "PropertyTypes",
    "Registry",
    "ShaderNode",
    "ShaderNodeList",
    "ShaderProperty"
]


class NodeContext(Boost.Python.instance):
    Displacement = 'displacement'
    DisplayFilter = 'displayFilter'
    Light = 'light'
    LightFilter = 'lightFilter'
    Pattern = 'pattern'
    PixelFilter = 'pixelFilter'
    SampleFilter = 'sampleFilter'
    Surface = 'surface'
    Volume = 'volume'
    pass
class NodeMetadata(Boost.Python.instance):
    Category = 'category'
    Departments = 'departments'
    Help = 'help'
    ImplementationName = '__SDR__implementationName'
    Label = 'label'
    Pages = 'pages'
    Primvars = 'primvars'
    Role = 'role'
    SdrDefinitionNameFallbackPrefix = 'sdrDefinitionNameFallbackPrefix'
    SdrUsdEncodingVersion = 'sdrUsdEncodingVersion'
    Target = '__SDR__target'
    pass
class NodeRole(Boost.Python.instance):
    Field = 'field'
    Math = 'math'
    Primvar = 'primvar'
    Texture = 'texture'
    pass
class PropertyMetadata(Boost.Python.instance):
    Colorspace = '__SDR__colorspace'
    Connectable = 'connectable'
    DefaultInput = '__SDR__defaultinput'
    Help = 'help'
    Hints = 'hints'
    ImplementationName = '__SDR__implementationName'
    IsAssetIdentifier = '__SDR__isAssetIdentifier'
    IsDynamicArray = 'isDynamicArray'
    Label = 'label'
    Options = 'options'
    Page = 'page'
    RenderType = 'renderType'
    Role = 'role'
    SdrUsdDefinitionType = 'sdrUsdDefinitionType'
    Tag = 'tag'
    Target = '__SDR__target'
    ValidConnectionTypes = 'validConnectionTypes'
    VstructConditionalExpr = 'vstructConditionalExpr'
    VstructMemberName = 'vstructMemberName'
    VstructMemberOf = 'vstructMemberOf'
    Widget = 'widget'
    pass
class PropertyRole(Boost.Python.instance):
    pass
class PropertyTypes(Boost.Python.instance):
    Color = 'color'
    Color4 = 'color4'
    Float = 'float'
    Int = 'int'
    Matrix = 'matrix'
    Normal = 'normal'
    Point = 'point'
    String = 'string'
    Struct = 'struct'
    Terminal = 'terminal'
    Unknown = 'unknown'
    Vector = 'vector'
    Vstruct = 'vstruct'
    pass
class Registry(Boost.Python.instance):
    @staticmethod
    def GetShaderNodeByIdentifier(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetShaderNodeByIdentifierAndType(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetShaderNodeByName(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetShaderNodeByNameAndType(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetShaderNodeFromAsset(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetShaderNodeFromSourceCode(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetShaderNodesByFamily(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetShaderNodesByIdentifier(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetShaderNodesByName(*args, **kwargs) -> typing.Any: ...
    @property
    def expired(self) -> None:
        """
        True if this object has expired, False otherwise.

        :type: None
        """
    pass
class ShaderNode(pxr.Ndr.Node, Boost.Python.instance):
    @staticmethod
    def GetAdditionalPrimvarProperties(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetAllVstructNames(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetAssetIdentifierInputNames(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetCategory(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDefaultInput(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDepartments(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetHelp(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetImplementationName(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLabel(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetPages(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetPrimvars(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetPropertyNamesForPage(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetRole(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetShaderInput(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetShaderOutput(*args, **kwargs) -> typing.Any: ...
    pass
class ShaderNodeList(Boost.Python.instance):
    @staticmethod
    def append(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def extend(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 48
    pass
class ShaderProperty(pxr.Ndr.Property, Boost.Python.instance):
    @staticmethod
    def GetDefaultValueAsSdfType(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetHelp(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetHints(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetImplementationName(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetLabel(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetOptions(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetPage(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetVStructConditionalExpr(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetVStructMemberName(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetVStructMemberOf(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetValidConnectionTypes(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetWidget(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsAssetIdentifier(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsDefaultInput(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsVStruct(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsVStructMember(*args, **kwargs) -> typing.Any: ...
    pass
__MFB_FULL_PACKAGE_NAME = 'sdr'
