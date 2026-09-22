# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from typing import Any, Callable

import carb.settings
import omni.usd
import usdrt
from omni.kit.property.adapter.core import AttributeAdapter, PrimAdapter, PropertyType, StageAdapter
from pxr import Sdf, Usd, UsdUtils

from .change_tracker_wrapper import RtChangeTrackerWrapper
from .convert import convert_usdrt_to_usd

UNSUPPORT_TYPES = ["unknown", "double (timecode)", "double16 (frame)", "double4 (matrix)"]
WRITE_PRIORITY_SETTINGS = "/exts/omni.kit.property.adapter.fabric/priority_write"
READ_PRIORITY_SETTINGS = "/exts/omni.kit.property.adapter.fabric/priority_read"


class FabricAttributeAdapter(AttributeAdapter):
    """
    Adapter to provide usdrt attributes with a unified interface so
    that Fabric property can work with UsdProperty code.
    """

    def __init__(self, attribute: usdrt.Usd.Attribute):
        self._attribute = attribute
        self._metadata = {Sdf.PrimSpec.TypeNameKey: self._attribute.GetTypeName().GetAsToken()}

    def __getattr__(self, attr):
        return getattr(self._attribute, attr, self.unsupport)

    @property
    def attribute(self):
        return self._attribute

    def IsHidden(self):  # noqa: N802
        return False

    def GetPrim(self):  # noqa: N802
        return FabricPrimAdapter(self._attribute.GetPrim())

    def GetDisplayGroup(self):  # noqa: N802
        return self._attribute.GetNamespace()

    def GetMetadata(self, key=None):  # noqa: N802
        return self._metadata.get(key, None)

    def GetAllMetadata(self):  # noqa: N802
        return self._metadata

    def GetNumTimeSamples(self):  # noqa: N802
        return 0

    def GetPropertyType(self):  # noqa: N802
        if isinstance(self._attribute, usdrt.Usd.Attribute):
            return PropertyType.ATTRIBUTE
        if isinstance(self._attribute, usdrt.Usd.Relationship):
            return PropertyType.RELATIONSHIP
        return type(self._attribute)

    def GetPropertyStack(self, *args, **kwargs) -> list["PropertySpecAdapter"]:  # noqa: N802, F821
        # TODO make this a proper adapter class if needed in wider use case.
        class PropertySpecAdapter:
            def __init__(self, attribute: usdrt.Usd.Attribute):
                self._attribute = attribute

            def HasDefaultValue(self) -> bool:  # noqa: N802
                return True

            @property
            def layer(self) -> Sdf.Layer | None:
                # since there's no layer concept in fabric, return the root layer path for the stage
                stagecache = UsdUtils.StageCache.Get()
                pxr_stage = stagecache.Find(Usd.StageCache.Id.FromLongInt(self._attribute.GetStage().GetStageId()))
                return pxr_stage.GetRootLayer() if pxr_stage else None

        return [PropertySpecAdapter(self._attribute)]

    def unsupport(self, *args, **kwargs):
        return None


class FabricPrimAdapter(PrimAdapter):
    """
    Adapter to provide usdrt attributes with a unified interface so
    that Fabric property can work with UsdProperty code.
    """

    def __init__(self, prim: usdrt.Usd.Prim):
        self._prim = prim

    def __getattr__(self, attr):
        return getattr(self._prim, attr, self.unsupport)

    @property
    def prim(self):
        return self._prim

    def GetProperties(self) -> FabricAttributeAdapter:  # noqa: N802
        return [FabricAttributeAdapter(a) for a in self._prim.GetAttributes()]

    def GetPropertyOrder(self):  # noqa: N802
        return []

    def GetAttribute(self, path: str) -> FabricAttributeAdapter:  # noqa: N802
        attr = self._prim.GetAttribute(path)
        if attr.GetTypeName().GetAsToken() in UNSUPPORT_TYPES:
            return None
        return FabricAttributeAdapter(attr)

    def GetPrimDefinition(self):  # noqa: N802
        return None

    def IsInstanceProxy(self):  # noqa: N802
        return False

    def unsupport(self, *args, **kwargs):
        return None


class FabricStageAdapter(StageAdapter):
    """
    Adapter to provide usdrt attributes with a unified interface so
    that Fabric property can work with UsdProperty code.
    """

    def __init__(self, stage: Usd.Stage):
        self._usd_stage = stage
        settings = carb.settings.get_settings()
        self._priority_read = settings.get(READ_PRIORITY_SETTINGS) or 100
        self._priority_write = settings.get(WRITE_PRIORITY_SETTINGS) or 200
        context = omni.usd.get_context_from_stage(stage)
        if context:
            stage_id = context.get_stage_id()
            self._stage = usdrt.Usd.Stage.Attach(stage_id) if stage_id >= 0 else None
        else:
            self._stage = None

    def __getattr__(self, attr):
        return getattr(self._stage, attr, self.unsupport)

    @property
    def name(self) -> str:
        return "fabric"

    @property
    def priority_read(self) -> int:
        return self._priority_read

    @property
    def priority_write(self) -> int:
        return self._priority_write

    @property
    def stage(self):
        return self._stage

    @property
    def usd_stage(self):
        return self._usd_stage

    def unsupport(self, *args, **kwargs):
        return None

    def GetPrimAtPath(self, path: Sdf.Path) -> FabricPrimAdapter:  # noqa: N802
        return FabricPrimAdapter(self._stage.GetPrimAtPath(usdrt.Sdf.Path(path.pathString)))

    def GetPropertyAtPath(self, path: Sdf.Path) -> FabricAttributeAdapter:  # noqa: N802
        prop = self._stage.GetAttributeAtPath(usdrt.Sdf.Path(path.pathString))
        if prop.GetTypeName().GetAsToken() in UNSUPPORT_TYPES:
            return None
        return FabricAttributeAdapter(prop)

    def GetAttributeAtPath(self, path: Sdf.Path) -> FabricAttributeAdapter:  # noqa: N802
        attr = self._stage.GetAttributeAtPath(usdrt.Sdf.Path(path.pathString))
        if attr.GetTypeName().GetAsToken() in UNSUPPORT_TYPES:
            return None
        return FabricAttributeAdapter(attr)

    def GetTimeCodesPerSecond(self):  # noqa: N802
        return 0

    def GetObjectAtPath(self, path: Sdf.Path):  # noqa: N802
        return self._usd_stage.GetObjectAtPath(path)

    def GetPathResolverContext(self):  # noqa: N802
        return None

    def GetLayerStack(self):  # noqa: N802
        return {}

    def GetRootLayer(self):  # noqa: N802
        return None

    def get_frame_time_code(self, current_time) -> usdrt.Usd.TimeCode:
        return usdrt.Usd.TimeCode(omni.usd.get_frame_time_code(current_time, self.GetTimeCodesPerSecond()))

    def CreateChangeTracker(  # noqa: N802
        self,
        attr_names: list[str],
        prim_paths: list[Sdf.Path],
        callback: Callable[[RtChangeTrackerWrapper.Notice, Usd.Stage], None],
    ) -> RtChangeTrackerWrapper:

        prim_paths_rt = []
        for path in prim_paths:
            prim_paths_rt.append(usdrt.Sdf.Path(path.pathString))

        return RtChangeTrackerWrapper(attr_names, prim_paths_rt, callback, self._stage)

    def GetChangeAttributeArgs(self, path: Sdf.Path, new_value: Any, old_value: Any):  # noqa: N802
        cmd_args = ["ChangeFabricAttribute"]
        cmd_kwargs = {
            "attr_path": usdrt.Sdf.Path(path.pathString),
            "value": new_value,
            "prev": old_value,
            "stage": self._stage,
        }
        return cmd_args, cmd_kwargs, self._stage

    def convert_data(self, value, dst_adapter_name: str):
        if self.name == dst_adapter_name:
            return value

        if dst_adapter_name == "usd":
            return convert_usdrt_to_usd(value)

        carb.log_warn(f"Unsupported convert data from {self.name} to {dst_adapter_name}")
        return None

    def resolve_path_array(self, path, resolved_path: str, path_list, index):
        value = path
        if isinstance(path_list, usdrt.Vt.AssetArray):
            if resolved_path:
                value = usdrt.Sdf.AssetPath(path, resolved_path)
            else:
                value = usdrt.Sdf.AssetPath(path)

        # copy
        vec_value = []
        for v in path_list:
            vec_value.append(v)
        vec_value[index] = value
        return vec_value

    def get_notice_paths(self, stage, notice):
        resynced_paths = []
        changed_info_paths = []
        is_rt_stage = False
        if isinstance(stage, usdrt.Usd.Stage):
            is_rt_stage = True
            for path in notice.GetResyncedPaths():
                resynced_paths.append(Sdf.Path(path.pathString))
            for path in notice.GetChangedInfoOnlyPaths():
                changed_info_paths.append(Sdf.Path(path.pathString))
        return is_rt_stage, resynced_paths, changed_info_paths
