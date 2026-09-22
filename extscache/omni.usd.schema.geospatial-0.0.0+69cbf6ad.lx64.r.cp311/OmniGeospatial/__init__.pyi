from __future__ import annotations
import OmniGeospatial._omniGeospatial
import typing
import Boost.Python
import pxr.Usd

__all__ = [
    "Tokens",
    "WGS84LocalPositionAPI",
    "WGS84ReferencePositionAPI"
]


class Tokens(Boost.Python.instance):
    ENU = 'ENU'
    NED = 'NED'
    OmniWGS84LocalPositionAPI = 'OmniWGS84LocalPositionAPI'
    OmniWGS84ReferencePositionAPI = 'OmniWGS84ReferencePositionAPI'
    omniGeospatialWgs84LocalPosition = 'omni:geospatial:wgs84:local:position'
    omniGeospatialWgs84ReferenceOrientation = 'omni:geospatial:wgs84:reference:orientation'
    omniGeospatialWgs84ReferenceReferencePosition = 'omni:geospatial:wgs84:reference:referencePosition'
    omniGeospatialWgs84ReferenceTangentPlane = 'omni:geospatial:wgs84:reference:tangentPlane'
    pass
class WGS84LocalPositionAPI(pxr.Usd.APISchemaBase, pxr.Usd.SchemaBase, Boost.Python.instance):
    @staticmethod
    def Apply(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def CanApply(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def CreatePositionAttr(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Get(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetPositionAttr(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSchemaAttributeNames(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def _GetStaticTfType(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 56
    pass
class WGS84ReferencePositionAPI(pxr.Usd.APISchemaBase, pxr.Usd.SchemaBase, Boost.Python.instance):
    @staticmethod
    def Apply(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def CanApply(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def CreateOrientationAttr(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def CreateReferencePositionAttr(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def CreateTangentPlaneAttr(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def Get(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetOrientationAttr(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetReferencePositionAttr(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetSchemaAttributeNames(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def GetTangentPlaneAttr(*args, **kwargs) -> typing.Any: ...
    @staticmethod
    def _GetStaticTfType(*args, **kwargs) -> typing.Any: ...
    __instance_size__ = 56
    pass
class _CanApplyResult(Boost.Python.instance):
    @property
    def whyNot(self) -> None:
        """
        :type: None
        """
    __instance_size__ = 64
    pass
__MFB_FULL_PACKAGE_NAME = 'omniGeospatial'
