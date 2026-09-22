from __future__ import annotations
import pxr.UsdUtils._usdUtils
import typing
import Boost.Python

__all__ = [
    "AuthorCollection",
    "CoalescingDiagnosticDelegate",
    "CoalescingDiagnosticDelegateItem",
    "CoalescingDiagnosticDelegateSharedItem",
    "CoalescingDiagnosticDelegateUnsharedItem",
    "ComputeAllDependencies",
    "ComputeCollectionIncludesAndExcludes",
    "ComputeUsdStageStats",
    "ConditionalAbortDiagnosticDelegate",
    "ConditionalAbortDiagnosticDelegateErrorFilters",
    "CopyLayerMetadata",
    "CreateCollections",
    "CreateNewARKitUsdzPackage",
    "CreateNewUsdzPackage",
    "DependencyInfo",
    "ExtractExternalReferences",
    "FlattenLayerStack",
    "FlattenLayerStackResolveAssetPath",
    "GenerateClipManifestName",
    "GenerateClipTopologyName",
    "GetAlphaAttributeNameForColor",
    "GetDirtyLayers",
    "GetMaterialsScopeName",
    "GetModelNameFromRootLayer",
    "GetPrefName",
    "GetPrimAtPathWithForwarding",
    "GetPrimaryCameraName",
    "GetPrimaryUVSetName",
    "GetRegisteredVariantSets",
    "LocalizeAsset",
    "ModifyAssetPaths",
    "RegisteredVariantSet",
    "SparseAttrValueWriter",
    "SparseValueWriter",
    "StageCache",
    "StitchClips",
    "StitchClipsManifest",
    "StitchClipsTemplate",
    "StitchClipsTopology",
    "StitchInfo",
    "StitchLayers",
    "TimeCodeRange",
    "UninstancePrimAtPath",
    "UsdStageStatsKeys"
]


class CoalescingDiagnosticDelegate(Boost.Python.instance):
    @staticmethod
    def DumpCoalescedDiagnosticsToStderr(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def DumpCoalescedDiagnosticsToStdout(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def DumpUncoalescedDiagnostics(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def TakeCoalescedDiagnostics(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def TakeUncoalescedDiagnostics(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 56
    pass
class CoalescingDiagnosticDelegateItem(Boost.Python.instance):
    @property
    def sharedItem(self) -> None:
        """
        :type: None
        """
    @property
    def unsharedItems(self) -> None:
        """
        :type: None
        """
    pass
class CoalescingDiagnosticDelegateSharedItem(Boost.Python.instance):
    @property
    def sourceFileName(self) -> None:
        """
        :type: None
        """
    @property
    def sourceFunction(self) -> None:
        """
        :type: None
        """
    @property
    def sourceLineNumber(self) -> None:
        """
        :type: None
        """
    pass
class CoalescingDiagnosticDelegateUnsharedItem(Boost.Python.instance):
    @property
    def commentary(self) -> None:
        """
        :type: None
        """
    @property
    def context(self) -> None:
        """
        :type: None
        """
    pass
class ConditionalAbortDiagnosticDelegate(Boost.Python.instance):
    __instance_size__ = 128
    pass
class ConditionalAbortDiagnosticDelegateErrorFilters(Boost.Python.instance):
    @staticmethod
    def GetCodePathFilters(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetStringFilters(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetCodePathFilters(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetStringFilters(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 72
    pass
class DependencyInfo(Boost.Python.instance):
    @property
    def assetPath(self) -> None:
        """
        :type: None
        """
    @property
    def dependencies(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 80
    pass
class RegisteredVariantSet(Boost.Python.instance):
    """
    Info for registered variant set
    """
    class SelectionExportPolicy(Boost.Python.enum, int):
        Always = pxr.UsdUtils.SelectionExportPolicy.Always
        IfAuthored = pxr.UsdUtils.SelectionExportPolicy.IfAuthored
        Never = pxr.UsdUtils.SelectionExportPolicy.Never
        __slots__ = ()
        names = {'IfAuthored': pxr.UsdUtils.SelectionExportPolicy.IfAuthored, 'Always': pxr.UsdUtils.SelectionExportPolicy.Always, 'Never': pxr.UsdUtils.SelectionExportPolicy.Never}
        values = {1: pxr.UsdUtils.SelectionExportPolicy.IfAuthored, 2: pxr.UsdUtils.SelectionExportPolicy.Always, 0: pxr.UsdUtils.SelectionExportPolicy.Never}
        pass
    @property
    def name(self) -> None:
        """
        :type: None
        """
    @property
    def selectionExportPolicy(self) -> None:
        """
        :type: None
        """
    pass
class SparseAttrValueWriter(Boost.Python.instance):
    @staticmethod
    def SetTimeSample(*args, **kwargs) -> typing.Any: ...
    pass
class SparseValueWriter(Boost.Python.instance):
    @staticmethod
    def GetSparseAttrValueWriters(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def SetAttribute(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 80
    pass
class StageCache(Boost.Python.instance):
    @staticmethod
    def Get(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSessionLayerForVariantSelections(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 32
    pass
class TimeCodeRange(Boost.Python.instance):
    class Tokens(Boost.Python.instance):
        EmptyTimeCodeRange = 'NONE'
        RangeSeparator = ':'
        StrideSeparator = 'x'
        pass
    class _Iterator(Boost.Python.instance):
        pass
    @staticmethod
    def CreateFromFrameSpec(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def IsValid(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def empty(*args, **kwargs) -> typing.Any: ...
    @property
    def endTimeCode(self) -> None:
        """
        :type: None
        """
    @property
    def frameSpec(self) -> None:
        """
        :type: None
        """
    @property
    def startTimeCode(self) -> None:
        """
        :type: None
        """
    @property
    def stride(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 48
    pass
class UsdStageStatsKeys(Boost.Python.instance):
    activePrimCount = 'activePrimCount'
    approxMemoryInMb = 'approxMemoryInMb'
    assetCount = 'assetCount'
    inactivePrimCount = 'inactivePrimCount'
    instanceCount = 'instanceCount'
    instancedModelCount = 'instancedModelCount'
    modelCount = 'modelCount'
    primCounts = 'primCounts'
    primCountsByType = 'primCountsByType'
    primary = 'primary'
    prototypeCount = 'prototypeCount'
    prototypes = 'prototypes'
    pureOverCount = 'pureOverCount'
    totalInstanceCount = 'totalInstanceCount'
    totalPrimCount = 'totalPrimCount'
    untyped = 'untyped'
    usedLayerCount = 'usedLayerCount'
    pass
def AuthorCollection(*args, **kwargs) -> typing.Any:
    pass
def ComputeAllDependencies(*args, **kwargs) -> typing.Any:
    pass
def ComputeCollectionIncludesAndExcludes(*args, **kwargs) -> typing.Any:
    pass
def ComputeUsdStageStats(*args, **kwargs) -> typing.Any:
    pass
def CopyLayerMetadata(*args, **kwargs) -> typing.Any:
    pass
def CreateCollections(*args, **kwargs) -> typing.Any:
    pass
def CreateNewARKitUsdzPackage(*args, **kwargs) -> typing.Any:
    pass
def CreateNewUsdzPackage(*args, **kwargs) -> typing.Any:
    pass
def ExtractExternalReferences(*args, **kwargs) -> typing.Any:
    pass
def FlattenLayerStack(*args, **kwargs) -> typing.Any:
    pass
def FlattenLayerStackResolveAssetPath(*args, **kwargs) -> typing.Any:
    pass
def GenerateClipManifestName(*args, **kwargs) -> typing.Any:
    pass
def GenerateClipTopologyName(*args, **kwargs) -> typing.Any:
    pass
def GetAlphaAttributeNameForColor(*args, **kwargs) -> typing.Any:
    pass
def GetDirtyLayers(*args, **kwargs) -> typing.Any:
    pass
def GetMaterialsScopeName(*args, **kwargs) -> typing.Any:
    pass
def GetModelNameFromRootLayer(*args, **kwargs) -> typing.Any:
    pass
def GetPrefName(*args, **kwargs) -> typing.Any:
    pass
def GetPrimAtPathWithForwarding(*args, **kwargs) -> typing.Any:
    pass
def GetPrimaryCameraName(*args, **kwargs) -> typing.Any:
    pass
def GetPrimaryUVSetName(*args, **kwargs) -> typing.Any:
    pass
def GetRegisteredVariantSets(*args, **kwargs) -> typing.Any:
    pass
def LocalizeAsset(*args, **kwargs) -> typing.Any:
    pass
def ModifyAssetPaths(*args, **kwargs) -> typing.Any:
    pass
def StitchClips(*args, **kwargs) -> typing.Any:
    pass
def StitchClipsManifest(*args, **kwargs) -> typing.Any:
    pass
def StitchClipsTemplate(*args, **kwargs) -> typing.Any:
    pass
def StitchClipsTopology(*args, **kwargs) -> typing.Any:
    pass
def StitchInfo(*args, **kwargs) -> typing.Any:
    pass
def StitchLayers(*args, **kwargs) -> typing.Any:
    pass
def UninstancePrimAtPath(*args, **kwargs) -> typing.Any:
    pass
__MFB_FULL_PACKAGE_NAME = 'usdUtils'
