from __future__ import annotations
import pxr.Ar._ar
import typing
import Boost.Python
import pxr.Ar

__all__ = [
    "AssetInfo",
    "DefaultResolver",
    "DefaultResolverContext",
    "GetRegisteredURISchemes",
    "GetResolver",
    "GetUnderlyingResolver",
    "IsPackageRelativePath",
    "JoinPackageRelativePath",
    "Notice",
    "ResolvedPath",
    "Resolver",
    "ResolverContext",
    "ResolverContextBinder",
    "ResolverScopedCache",
    "SetPreferredResolver",
    "SplitPackageRelativePathInner",
    "SplitPackageRelativePathOuter",
    "Timestamp"
]


class AssetInfo(Boost.Python.instance):
    @property
    def assetName(self) -> None:
        """
        :type: None
        """
    @property
    def resolverInfo(self) -> None:
        """
        :type: None
        """
    @property
    def version(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 136
    pass
class DefaultResolver(Resolver, Boost.Python.instance):
    @staticmethod
    def SetDefaultSearchPath(*args, **kwargs) -> typing.Any: ...
    pass
class DefaultResolverContext(Boost.Python.instance):
    @staticmethod
    def GetSearchPath(*args, **kwargs) -> typing.Any: ...
    pass
class Notice(Boost.Python.instance):
    class ResolverChanged(ResolverNotice, pxr.Tf.Notice, Boost.Python.instance):
        @staticmethod
        def AffectsContext(*args, **kwargs) -> typing.Any: ...
        pass
    class ResolverNotice(pxr.Tf.Notice, Boost.Python.instance):
        pass
    pass
class ResolvedPath(Boost.Python.instance):
    @staticmethod
    def GetPathString(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 56
    pass
class Resolver(Boost.Python.instance):
    @staticmethod
    def CanWriteAssetToPath(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def CreateContextFromString(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def CreateContextFromStrings(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def CreateDefaultContext(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def CreateDefaultContextForAsset(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def CreateIdentifier(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def CreateIdentifierForNewAsset(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetAssetInfo(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetCurrentContext(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetExtension(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetModificationTimestamp(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsContextDependentPath(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def RefreshContext(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Resolve(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def ResolveForNewAsset(*args, **kwargs) -> typing.Any: ...
    pass
class ResolverContext(Boost.Python.instance):
    @staticmethod
    def Get(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDebugString(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsEmpty(*args, **kwargs) -> typing.Any: ...
    pass
class ResolverContextBinder(Boost.Python.instance):
    __instance_size__ = 56
    pass
class ResolverScopedCache(Boost.Python.instance):
    __instance_size__ = 32
    pass
class Timestamp(Boost.Python.instance):
    @staticmethod
    def GetTime(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsValid(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 32
    pass
class _PyAnnotatedBoolResult(Boost.Python.instance):
    @property
    def whyNot(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 64
    pass
def GetRegisteredURISchemes(*args, **kwargs) -> typing.Any:
    pass
def GetResolver(*args, **kwargs) -> typing.Any:
    pass
def GetUnderlyingResolver(*args, **kwargs) -> typing.Any:
    pass
def IsPackageRelativePath(*args, **kwargs) -> typing.Any:
    pass
def JoinPackageRelativePath(*args, **kwargs) -> typing.Any:
    pass
def SetPreferredResolver(*args, **kwargs) -> typing.Any:
    pass
def SplitPackageRelativePathInner(*args, **kwargs) -> typing.Any:
    pass
def SplitPackageRelativePathOuter(*args, **kwargs) -> typing.Any:
    pass
def _TestImplicitConversion(*args, **kwargs) -> typing.Any:
    pass
__MFB_FULL_PACKAGE_NAME = 'ar'
