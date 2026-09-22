# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Callable

import carb.settings
import omni.usd
from omni.kit.property.adapter.core import AttributeAdapter, PrimAdapter, PropertyType, StageAdapter
from pxr import Sdf, Usd

from .notice_wrapper import TfNoticeWrapper

WRITE_PRIORITY_SETTINGS = "/exts/omni.kit.property.adapter.usd/priority_write"
READ_PRIORITY_SETTINGS = "/exts/omni.kit.property.adapter.usd/priority_read"


class UsdPrimAdapter(PrimAdapter):
    """
    Adapter to provide usd attributes with a unified interface so
    that Fabric property can work with UsdProperty code.
    """

    def __init__(self, prim: Usd.Prim):
        self._prim = prim

    def __getattr__(self, attr):
        return getattr(self._prim, attr)

    @property
    def prim(self):
        return self._prim


class UsdAttributeAdapter(AttributeAdapter):
    """
    Adapter to provide usd attributes with a unified interface so
    that Fabric property can work with UsdProperty code.
    """

    def __init__(self, attribute: Usd.Attribute):
        self._attribute = attribute

    def __getattr__(self, attr):
        return getattr(self._attribute, attr)

    @property
    def attribute(self):
        return self._attribute

    def GetPrim(self) -> UsdPrimAdapter:  # noqa: N802
        return UsdPrimAdapter(self._attribute.GetPrim())

    def GetPropertyType(self):  # noqa: N802
        if isinstance(self._attribute, Usd.Attribute):
            return PropertyType.ATTRIBUTE
        if isinstance(self._attribute, Usd.Relationship):
            return PropertyType.RELATIONSHIP
        return type(self._attribute)


class UsdStageAdapter(StageAdapter):
    """
    Adapter to provide usd attributes with a unified interface so
    that Fabric property can work with UsdProperty code.
    """

    def __init__(self, stage: Usd.Stage):
        self._stage = stage
        settings = carb.settings.get_settings()
        self._priority_read = settings.get(READ_PRIORITY_SETTINGS) or 200
        self._priority_write = settings.get(WRITE_PRIORITY_SETTINGS) or 100

    def __getattr__(self, attr):
        return getattr(self._stage, attr)

    @property
    def name(self) -> str:
        return "usd"

    @property
    def priority_read(self) -> int:
        return self._priority_read

    @property
    def priority_write(self) -> int:
        return self._priority_write

    @property
    def stage(self):
        return self._stage

    def GetPrimAtPath(self, path: Sdf.Path) -> UsdPrimAdapter:  # noqa: N802
        prim = self._stage.GetPrimAtPath(path.pathString)
        if prim:
            return UsdPrimAdapter(prim)
        return None

    def GetAttributeAtPath(self, path: Sdf.Path) -> UsdAttributeAdapter:  # noqa: N802
        attr = self._stage.GetAttributeAtPath(path.pathString)
        if attr:
            return UsdAttributeAdapter(attr)
        return None

    def get_frame_time_code(self, current_time):
        return Usd.TimeCode(omni.usd.get_frame_time_code(current_time, self._stage.GetTimeCodesPerSecond()))

    def CreateChangeTracker(  # noqa: N802
        self,
        attr_names: list[str],
        prim_paths: list[Sdf.Path],
        callback: Callable[[Usd.Notice.ObjectsChanged, Usd.Stage], None],
    ) -> TfNoticeWrapper:

        return TfNoticeWrapper(attr_names, prim_paths, callback, self._stage)

    def GetChangeAttributeArgs(self, path, new_value, old_value):  # noqa: N802
        return [], {}, self._stage

    def convert_data(self, value, dst_adapter_name: str):
        if self.name == dst_adapter_name:
            return value

        carb.log_warn(f"Unsupported convert data from {self.name} to {dst_adapter_name}")
        return None

    def resolve_path_array(self, path, resolved_path: str, path_list, index):
        value = path
        if not isinstance(path, Sdf.AssetPath):
            if resolved_path:
                value = Sdf.AssetPath(path, resolved_path)
            else:
                value = Sdf.AssetPath(path)

        vec_value = Sdf.AssetPathArray(path_list)
        vec_value[index] = value
        return vec_value

    def get_notice_paths(self, stage, notice):
        resynced_paths = []
        changed_info_paths = []
        is_usd_stage = False
        if isinstance(stage, Usd.Stage):
            is_usd_stage = True
            resynced_paths = notice.GetResyncedPaths()
            changed_info_paths = notice.GetChangedInfoOnlyPaths()
        return is_usd_stage, resynced_paths, changed_info_paths
