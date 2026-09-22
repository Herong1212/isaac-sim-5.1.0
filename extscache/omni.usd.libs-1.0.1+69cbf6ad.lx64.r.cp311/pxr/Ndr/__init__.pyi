from __future__ import annotations
import pxr.Ndr._ndr
import typing
import Boost.Python
import pxr.Ndr
import pxr.Tf

__all__ = [
    "DiscoveryPlugin",
    "DiscoveryPluginContext",
    "DiscoveryPluginList",
    "DiscoveryUri",
    "FsHelpersDiscoverFiles",
    "FsHelpersDiscoverNodes",
    "FsHelpersSplitShaderIdentifier",
    "Node",
    "NodeDiscoveryResult",
    "NodeList",
    "Property",
    "Registry",
    "Version",
    "VersionFilter",
    "VersionFilterAllVersions",
    "VersionFilterDefaultOnly"
]


class DiscoveryPlugin(Boost.Python.instance):
    @staticmethod
    def DiscoverNodes(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSearchURIs(*args, **kwargs) -> typing.Any: ...
    @property
    def expired(self) -> None:
        """
        True if this object has expired, False otherwise.

        :type: None
        """
    pass
class DiscoveryPluginContext(Boost.Python.instance):
    @staticmethod
    def GetSourceType(*args, **kwargs) -> typing.Any: ...
    @property
    def expired(self) -> None:
        """
        True if this object has expired, False otherwise.

        :type: None
        """
    pass
class DiscoveryPluginList(Boost.Python.instance):
    @staticmethod
    def append(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def extend(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 48
    pass
class DiscoveryUri(Boost.Python.instance):
    @property
    def resolvedUri(self) -> None:
        """
        :type: None
        """
    @property
    def uri(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 88
    pass
class Node(Boost.Python.instance):
    @staticmethod
    def GetContext(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetFamily(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetIdentifier(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInfoString(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInput(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInputNames(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMetadata(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetName(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetOutput(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetOutputNames(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetResolvedDefinitionURI(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetResolvedImplementationURI(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSourceCode(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSourceType(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetVersion(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsValid(*args, **kwargs) -> typing.Any: ...
    pass
class NodeDiscoveryResult(Boost.Python.instance):
    @property
    def blindData(self) -> None:
        """
        :type: None
        """
    @property
    def discoveryType(self) -> None:
        """
        :type: None
        """
    @property
    def family(self) -> None:
        """
        :type: None
        """
    @property
    def identifier(self) -> None:
        """
        :type: None
        """
    @property
    def metadata(self) -> None:
        """
        :type: None
        """
    @property
    def name(self) -> None:
        """
        :type: None
        """
    @property
    def resolvedUri(self) -> None:
        """
        :type: None
        """
    @property
    def sourceCode(self) -> None:
        """
        :type: None
        """
    @property
    def sourceType(self) -> None:
        """
        :type: None
        """
    @property
    def subIdentifier(self) -> None:
        """
        :type: None
        """
    @property
    def uri(self) -> None:
        """
        :type: None
        """
    @property
    def version(self) -> None:
        """
        :type: None
        """
    pass
class NodeList(Boost.Python.instance):
    @staticmethod
    def append(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def extend(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 48
    pass
class Property(Boost.Python.instance):
    @staticmethod
    def CanConnectTo(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetArraySize(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetDefaultValue(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetInfoString(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMetadata(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetName(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetType(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetTypeAsSdfType(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsArray(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsConnectable(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsDynamicArray(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsOutput(*args, **kwargs) -> typing.Any: ...
    pass
class Registry(Boost.Python.instance):
    @staticmethod
    def GetAllNodeSourceTypes(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNodeByIdentifier(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNodeByIdentifierAndType(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNodeByName(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNodeByNameAndType(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNodeFromAsset(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNodeFromSourceCode(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNodeIdentifiers(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNodeNames(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNodesByFamily(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNodesByIdentifier(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetNodesByName(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSearchURIs(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetExtraDiscoveryPlugins(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetExtraParserPlugins(*args, **kwargs) -> typing.Any: ...
    pass
class Version(Boost.Python.instance):
    @staticmethod
    def GetAsDefault(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMajor(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetMinor(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetStringSuffix(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsDefault(*args, **kwargs) -> typing.Any: ...
    pass
class VersionFilter(pxr.Tf.Tf_PyEnumWrapper, pxr.Tf.Enum, Boost.Python.instance):
    @staticmethod
    def GetValueFromName(*args, **kwargs) -> typing.Any: ...
    _baseName = ''
    allValues: tuple # value = (Ndr.VersionFilterDefaultOnly, Ndr.VersionFilterAllVersions)
    pass
class _AnnotatedBool(Boost.Python.instance):
    @property
    def message(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 64
    pass
class _FilesystemDiscoveryPlugin(DiscoveryPlugin, Boost.Python.instance):
    class Context(DiscoveryPluginContext, Boost.Python.instance):
        @property
        def expired(self) -> None:
            """
            True if this object has expired, False otherwise.

            :type: None
            """
        pass
    @staticmethod
    def DiscoverNodes(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSearchURIs(*args, **kwargs) -> typing.Any: ...
    @property
    def expired(self) -> None:
        """
        True if this object has expired, False otherwise.

        :type: None
        """
    pass
def FsHelpersDiscoverFiles(*args, **kwargs) -> typing.Any:
    pass
def FsHelpersDiscoverNodes(*args, **kwargs) -> typing.Any:
    pass
def FsHelpersSplitShaderIdentifier(*args, **kwargs) -> typing.Any:
    pass
def _ValidateProperty(*args, **kwargs) -> typing.Any:
    pass
VersionFilterAllVersions: pxr.Ndr.VersionFilter # value = Ndr.VersionFilterAllVersions
VersionFilterDefaultOnly: pxr.Ndr.VersionFilter # value = Ndr.VersionFilterDefaultOnly
__MFB_FULL_PACKAGE_NAME = 'ndr'
