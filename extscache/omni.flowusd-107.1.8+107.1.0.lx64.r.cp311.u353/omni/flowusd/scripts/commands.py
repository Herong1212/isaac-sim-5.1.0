# Copyright (c) 2020-2023, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import os
from pathlib import Path
from typing import Optional

import carb
import carb.settings
import omni.kit.commands
import omni.usd
from omni.flowusd import _flowusd
from pxr import Gf, Sdf, Usd, UsdGeom
from usdrt import Usd as UsdRT

from . import common

CURRENT_PATH = Path(__file__).parent.parent.parent.parent
PRESETS_DIR = CURRENT_PATH.joinpath("data").joinpath("presets")


# this needs to be called to register the commands defined in this file
def register_all_flow_commands():
    omni.kit.commands.register_all_commands_in_module(__name__)


def get_next_layer():
    max_layer_id = 0
    context = omni.usd.get_context()
    stage = context.get_stage() if context else None
    if stage is None:
        return 0

    stage_rt = UsdRT.Stage.Attach(context.get_stage_id()) if context else None
    if stage_rt is None:
        return 0

    paths = stage_rt.GetPrimsWithTypeName("FlowSimulate") if stage_rt else []

    for path in paths:
        prim = stage.GetPrimAtPath(path.GetString())
        if prim and prim.HasAttribute("layer"):
            prim_layer = prim.GetAttribute("layer")
            max_layer_id = max(max_layer_id, prim_layer.Get())

    return max_layer_id + 1


# command to create a prim
# first checks to ensure the prim doesn't already exist
#
# prim_path: path of the prim
# type_name: type of the prim
#
# returns the prim on success, None on failure
class FlowCreatePrimCommand(omni.kit.commands.Command):
    # include all params that go into creating a Flow prim
    # don't want to pull data from UI or generate random numbers inside the command
    # it won't be deterministic to redo in that case
    def __init__(
        self,
        prim_path: str,
        type_name: str,
        stage: Optional[Usd.Stage] = None,
    ):
        self._stage = omni.usd.get_context().get_stage() if stage is None else stage
        self._prim_path = prim_path
        self._type_name = type_name

    def do(self):
        # make prim path unique
        self._prim_path = omni.usd.get_stage_next_free_path(self._stage, self._prim_path, False)

        # make sure the prim doesn't already exist
        self._prim_exists = self._stage.GetPrimAtPath(self._prim_path)
        if self._prim_exists:
            raise Exception(f"Prim {self._prim_path} already exists")

        return self._stage.DefinePrim(self._prim_path, self._type_name)

    def undo(self):
        # don't remove the prim if it already existed when the command was run, something else owns it in that case
        return not getattr(self, "_prim_exists", False) and self._stage.RemovePrim(self._prim_path)


# command to create flow preset (internal use only, see FlowCreatePresetsCommand if creating from outside of the extension)
# returns a tuple of prims created as a result of the command
#
# path: base path to use for creating prims
# layer: Flow layer to reference for prims that need it, zero layer is global, negative layer will get next free layer
# preset_name: name of the preset
# url: path to the usda file
#
# return tuple of created prims that result from this command on success, empty tuple on failure
class FlowCreateUsdPresetCommand(omni.kit.commands.Command):
    # include all params that go into creating a Flow preset
    # don't want to pull data from UI or generate random numbers inside the command
    # it won't be deterministic to redo in that case
    def __init__(
        self,
        path: str,
        layer: int,
        preset_name: str,
        url: str,
        is_copy: bool,
        emitter_only: bool,
        on_session_layer=False,
    ):
        self._path = path
        self._layer = layer
        self._name = preset_name
        self._url = url
        self._is_copy = is_copy
        self._emitter_only = emitter_only
        self._path_to = None
        self._on_session_layer = on_session_layer

        if layer < 0:
            self._layer = get_next_layer()

    def do(self):
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        working_layer = stage.GetSessionLayer() if self._on_session_layer else stage.GetRootLayer()
        self._up_axis = UsdGeom.GetStageUpAxis(stage)
        prev_selected = usd_context.get_selection().get_selected_prim_paths()

        def adjust_layer(prim):
            if prim and prim.HasAttribute("layer"):
                layer_attr = prim.GetAttribute("layer")
                layer_attr.Set(self._layer)

        with Usd.EditContext(stage, working_layer):
            if self._is_copy:
                temp_path = omni.usd.get_stage_next_free_path(stage, "/Flow_Tmp_Ref", True)
                omni.kit.commands.execute(
                    "CreateReference",
                    path_to=temp_path,
                    asset_path=self._url,
                    usd_context=usd_context,
                    select_prim=False,
                )

                preset_root = stage.GetPrimAtPath(self._path)
                if not preset_root.IsValid():
                    omni.kit.commands.execute("FlowCreatePrim", prim_path=self._path, type_name="Xform")

                prim = stage.GetPrimAtPath(temp_path)
                paths_from = []
                paths_to = []
                if prim:
                    for child in prim.GetAllChildren():
                        paths_from.append(child.GetPath())
                        paths_to.append(self._path + "/" + child.GetName())

                omni.kit.commands.execute("CopyPrims", paths_from=paths_from, paths_to=paths_to)

                if self._emitter_only:
                    path = self._path
                    # point cloud preset has an additional root prim
                    if len(paths_to) == 1 and "flowPointCloud" in paths_to[0]:
                        path += "/flowPointCloud"

                    base_prim = stage.GetPrimAtPath(path)
                    if base_prim.IsValid():
                        flowSimulate_prim_path = None
                        flowOffscreen_prim_path = None
                        flowRender_prim_path = None
                        flowEmitter_prim_path = None
                        for flow_prim in base_prim.GetAllChildren():
                            type_name = flow_prim.GetTypeName()
                            if type_name == "FlowSimulate":
                                flowSimulate_prim_path = flow_prim.GetPath()
                            elif type_name == "FlowOffscreen":
                                flowOffscreen_prim_path = flow_prim.GetPath()
                            elif type_name == "FlowRender":
                                flowRender_prim_path = flow_prim.GetPath()
                            elif "FlowEmitter" in type_name:
                                flowEmitter_prim_path = flow_prim.GetPath()

                        if flowSimulate_prim_path:
                            omni.kit.commands.execute("DeletePrims", paths=[flowSimulate_prim_path])
                        if flowOffscreen_prim_path:
                            omni.kit.commands.execute("DeletePrims", paths=[flowOffscreen_prim_path])
                        if flowRender_prim_path:
                            omni.kit.commands.execute("DeletePrims", paths=[flowRender_prim_path])
                        if flowEmitter_prim_path:
                            prim = stage.GetPrimAtPath(flowEmitter_prim_path)
                            adjust_layer(prim)
                else:
                    # adjust layer ids of copied prims
                    for path in paths_to:
                        prim = stage.GetPrimAtPath(path)
                        adjust_layer(prim)

                omni.kit.commands.execute("DeletePrimsCommand", paths=[temp_path])
            else:
                path_to = self._path + "/" + self._name
                self._path_to = Sdf.Path(omni.usd.get_stage_next_free_path(stage, path_to, False))
                omni.kit.commands.execute(
                    "CreateReferenceCommand",
                    path_to=self._path_to,
                    asset_path=self._url,
                    usd_context=usd_context,
                    select_prim=False,
                )

                # adjust layer ids of referenced prims
                prim_to = stage.GetPrimAtPath(self._path_to)
                for child in prim_to.GetAllChildren():
                    adjust_layer(child)

            # presets are currently saved with Y up axis
            if self._up_axis == "Z":
                base_prim = stage.GetPrimAtPath(self._path)
                if not self._is_copy:
                    # root is world
                    base_prim = stage.GetPrimAtPath(self._path_to)
                if base_prim.IsValid():
                    flowSimulate_prim = None
                    flowEmitter_prim = None
                for flow_prim in base_prim.GetAllChildren():
                    type_name = flow_prim.GetTypeName()
                    if type_name == "FlowSimulate":
                        flowSimulate_prim = flow_prim
                    elif "FlowEmitter" in type_name:
                        flowEmitter_prim = flow_prim

                if flowSimulate_prim:
                    flowAdvection_prim = None
                    for flow_prim in flowSimulate_prim.GetAllChildren():
                        type_name = flow_prim.GetTypeName()
                        if type_name == "FlowAdvectionCombustionParams":
                            flowAdvection_prim = flow_prim
                    if flowAdvection_prim:
                        attr = flowAdvection_prim.GetAttribute("gravity")
                        if attr.IsValid():
                            value = attr.Get()
                            attr.Set(Gf.Vec3f(value[2], value[0], value[1]))
                if flowEmitter_prim:
                    attr = flowEmitter_prim.GetAttribute("velocity")
                    if attr.IsValid():
                        value = attr.Get()
                        attr.Set(Gf.Vec3f(value[2], value[0], value[1]))

        usd_context.get_selection().set_selected_prim_paths(prev_selected, True)

    def undo(self):
        # nothing to do here, undo on FlowCreateBasicEffectCommand will take care of cleaning up prims created
        # but if any state changes happen other than prims being created, they need to be rolled back here
        pass


# command to create flow preset (internal use only, see FlowCreatePresetCommand if creating from outside of the extension)
# handles creating prims and attributes on them based on the given base path and (optional) layer
# returns a tuple of prims created as a result of the command
#
# paths: list of prims where to put the preset
# layer: layer id for Flow prims, 0 is a global if meaning the Flow prims are put under the stage root
#        and only emitters go under the prims in the path
# preset_name: name of the preset
# url: path to the usda file
# is_global: global preset only exists once for each preset name
# is_copy: copy prim, not reference it
# create_ref: is set as !is_copy, kept for backward compatibility, was used for drag&drop
# emitter_only: only emitter of the preset is created
#
# return True if preset layer given was used already and should be increased
class FlowCreateUsdPresetMultipleCommand(omni.kit.commands.Command):
    # include all params that go into creating a Flow preset
    # don't want to pull data from UI or generate random numbers inside the command
    # it won't be deterministic to redo in that case
    def __init__(
        self,
        paths: list,
        preset_name: str,
        url: str,
        is_copy=False,
        layer=0,
        emitter_only=False,
        is_global=False,
        on_session_layer=False,
    ):
        self._paths = paths
        self._layer = layer
        self._name = preset_name
        self._url = url
        self._is_global = is_global
        self._is_copy = is_copy
        self._create_ref = not is_copy
        self._emitter_only = emitter_only
        self._on_session_layer = on_session_layer

    def do(self):
        layer = self._layer
        emitter_only = self._emitter_only

        stage = omni.usd.get_context().get_stage()
        if common.PRESET_POINT_CLOUD_ITEM in self._url:
            preset_root = "/PointCloud/flowPointCloud"

            # overwrite layer id for pointclouds to be always 0
            layer = common.GLOBAL_LAYER_ID
        else:
            preset_root = "/" + self._name

        default_prim_path = str(stage.GetDefaultPrim().GetPath()) if stage.HasDefaultPrim() else ""
        prim_selected = self._paths and len(self._paths) > 0 and self._paths[0] != default_prim_path
        prim_paths = self._paths
        if common.PRESET_POINT_CLOUD_ITEM in self._url and not prim_selected:
            prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
            prim_selected = len(prim_paths) > 0

        if self._is_global or self._layer == common.GLOBAL_LAYER_ID:
            path = default_prim_path + preset_root
            preset_prim = stage.GetPrimAtPath(path)
            if preset_prim.IsValid():
                emitter_only = True
                carb.log_info(f"Global preset on `{path}` already exists, adding an emitter on the same layer.")
                for child in preset_prim.GetAllChildren():
                    layer_attr = child.GetAttribute("layer")
                    if layer_attr:
                        layer = layer_attr.Get()
                        break
            else:
                if not prim_selected:
                    if common.PRESET_POINT_CLOUD_ITEM in self._url:
                        # when points are not selected, use bunny preset
                        self._paths = ["/World/pointData/pointcloud"]
                    else:
                        self._paths = [self._name]

        if common.PRESET_POINT_CLOUD_ITEM in self._url and prim_selected:
            for point_path in prim_paths:
                base_prim = stage.GetPrimAtPath(point_path)
                if base_prim.IsValid():
                    self._url = get_preset_url(common.PRESET_POINT_CLOUD_NATIVE)

        if emitter_only and common.PRESET_POINT_CLOUD_ITEM in self._url:
            xform_path = default_prim_path + preset_root
            flow_prim = stage.GetPrimAtPath(xform_path)
            if flow_prim.IsValid():
                emitter = None
                # point path
                for child in flow_prim.GetAllChildren():
                    if child.GetTypeName() == "FlowEmitterPoint":
                        emitter = child
                if emitter:
                    relationship = emitter.GetRelationship("pointsPrim")
                    if not relationship:
                        relationship = emitter.CreateRelationship("pointsPrim")
                    for path in self._paths:
                        relationship.AddTarget(path)
                # volume path
                for child in flow_prim.GetAllChildren():
                    if child.GetTypeName() == "FlowEmitterNanoVdb":
                        emitter = child
                if emitter:
                    relationship = emitter.GetRelationship("volumePrim")
                    if not relationship:
                        relationship = emitter.CreateRelationship("volumePrim")
                    for path in self._paths:
                        relationship.AddTarget(path)
        elif emitter_only:
            if common.PRESET_POINT_CLOUD_ITEM in self._url and self._paths[0] == default_prim_path:
                carb.log_warn("Select imported prim with points to create a point cloud emitter.")
                return

            # will be only adding emitter to the selected layer
            for path in self._paths:
                prim = stage.GetPrimAtPath(path)
                if not prim:
                    carb.log_warn("Prim does not exist.")
                    return

                # check if this or any children is a flow prim has layer attribute (assuming it will be a flow prim)
                if prim.HasAttribute("layer"):
                    layer_attr = prim.GetAttribute("layer")
                    if layer_attr:
                        layer = layer_attr.Get()
                else:
                    for child in prim.GetAllChildren():
                        layer_attr = child.GetAttribute("layer")
                        if layer_attr:
                            layer = layer_attr.Get()
                            break

                omni.kit.commands.execute(
                    "FlowCreateUsdPreset",
                    path=path,
                    layer=layer,
                    preset_name=self._name,
                    url=self._url,
                    is_copy=self._is_copy,
                    emitter_only=True,
                    on_session_layer=self._on_session_layer,
                )

        elif common.PRESET_POINT_CLOUD_ITEM in self._url:
            omni.kit.commands.execute(
                "FlowCreateUsdPreset",
                path=default_prim_path,
                layer=layer,
                preset_name=self._name,
                url=self._url,
                is_copy=self._is_copy,
                emitter_only=False,
                on_session_layer=self._on_session_layer,
            )
            xform_path = default_prim_path + preset_root
            flow_prim = stage.GetPrimAtPath(xform_path)
            if flow_prim.IsValid():
                emitter = None
                # point path
                for child in flow_prim.GetAllChildren():
                    if child.GetTypeName() == "FlowEmitterPoint":
                        emitter = child
                if emitter:
                    relationship = emitter.GetRelationship("pointsPrim")
                    if relationship:
                        relationship.ClearTargets(True)
                    else:
                        relationship = emitter.CreateRelationship("pointsPrim")
                    for path in self._paths:
                        relationship.AddTarget(path)
                # volume path
                for child in flow_prim.GetAllChildren():
                    if child.GetTypeName() == "FlowEmitterNanoVdb":
                        emitter = child
                if emitter:
                    relationship = emitter.GetRelationship("volumePrim")
                    if relationship:
                        relationship.ClearTargets(True)
                    else:
                        relationship = emitter.CreateRelationship("volumePrim")
                    for path in self._paths:
                        relationship.AddTarget(path)
        else:
            for path in self._paths:
                if self._is_copy:
                    if path == default_prim_path:
                        xform_path = path + preset_root
                        (success, xform_prim) = omni.kit.commands.execute(
                            "FlowCreatePrim", prim_path=xform_path, type_name="Xform"
                        )
                        if success:
                            path = xform_prim.GetPath().pathString
                if not path.startswith("/"):
                    path = "/" + path

                omni.kit.commands.execute(
                    "FlowCreateUsdPreset",
                    path=path,
                    layer=layer,
                    preset_name=self._name,
                    url=self._url,
                    is_copy=self._is_copy,
                    emitter_only=emitter_only,
                    on_session_layer=self._on_session_layer,
                )
                emitter_only = True

        next_layer = get_next_layer()
        settings = carb.settings.get_settings()
        settings.set("/exts/omni.flowusd/next_layer", next_layer)

        return layer == self._layer

    def undo(self):
        # nothing to do here, undo on FlowCreateBasicEffectCommand will take care of cleaning up prims created
        # but if any state changes happen other than prims being created, they need to be rolled back here
        pass


def get_preset_url(name):
    """
    Get preset stored in the extension folder (not shown in the Presets browser).
    Used in commands and when creating a point cloud preset to selected points.
    """
    # TODO rework if we have more presets
    dir = name
    if common.PRESET_POINT_CLOUD_STREAMING in name or common.PRESET_POINT_CLOUD_NATIVE in name:
        dir = common.PRESET_POINT_CLOUD_ITEM
    url = str(PRESETS_DIR.joinpath(dir).joinpath(name)) + ".usda"

    return url


# command to get available point cloud presets
# returns list of names
class FlowGetPointCloudPresetsCommand(omni.kit.commands.Command):
    def __init__(self):
        pass

    def do(self):
        names = []
        for file in os.listdir(PRESETS_DIR.joinpath(common.PRESET_POINT_CLOUD_ITEM)):
            if file.endswith(".usda") or file.endswith(".usd"):
                name = os.path.splitext(file)[0]
                names.append(name)

        return names

    def undo(self):
        pass


# command to create point cloud preset, meant to be called from outside of the extension
# paths: list of point prims where to put the emitter
# name: name of the point cloud preset
class FlowCreatePointCloudPresetCommand(omni.kit.commands.Command):
    def __init__(self, paths: str, preset_name=common.PRESET_POINT_CLOUD_NATIVE, on_session_layer=False):
        self._paths = paths
        self._preset_name = preset_name
        self._url = get_preset_url(preset_name)
        self._layer = common.GLOBAL_LAYER_ID
        self._on_session_layer = on_session_layer

    def do(self):
        usd_context = omni.usd.get_context()
        if self._preset_name == common.PRESET_POINT_CLOUD_NATIVE:
            omni.kit.commands.execute(
                "FlowCreateUsdPresetMultiple",
                paths=self._paths,
                preset_name=self._preset_name,
                url=self._url,
                is_copy=True,
                is_global=True,
                on_session_layer=self._on_session_layer,
            )

        elif common.PRESET_POINT_CLOUD_STREAMING in self._preset_name:
            stage = usd_context.get_stage()
            default_prim_path = str(stage.GetDefaultPrim().GetPath()) if stage.HasDefaultPrim() else ""

            omni.kit.commands.execute(
                "FlowCreateUsdPreset",
                path=default_prim_path,
                layer=self._layer,
                preset_name=self._preset_name,
                url=self._url,
                is_copy=False,
                emitter_only=False,
                on_session_layer=self._on_session_layer,
            )

            emitter_path = default_prim_path + "/" + self._preset_name + "/emitterData"
            emitter_prim = stage.GetPrimAtPath(emitter_path)
            if not emitter_prim:
                carb.log_error("Error in point cloud preset, missing emitter data")
                return

            # add point prim paths
            point_prims_attr = emitter_prim.GetAttribute("inputs:pointPrims")
            if point_prims_attr:
                point_prims_attr.Set(self._paths)

            target_layers_attr = emitter_prim.GetAttribute("inputs:targetLayers")
            if target_layers_attr:
                target_layers_attr.Set([self._layer] * len(self._paths))

    def undo(self):
        pass


# command to create a preset, meant to be called from outside of the extension
# returns a tuple of prims created as a result of the command
#
# preset_name: name of the preset
# paths: list of prims where to put the preset
# create_copy: create copy of preset if true and a reference if false
# layer: layer id for Flow prims, for copies 0 is a global copy meaning the Flow prims are put under the stage root
#        and only emitters go under the prims in the path, -1 means next free layer will be assigned
# url: path to the preset's usda file
class FlowCreatePresetsCommand(omni.kit.commands.Command):
    def __init__(self, preset_name: str, paths: list, create_copy=False, layer=-1, url="", on_session_layer=False):

        self._preset_name = preset_name
        self._paths = paths
        self._create_copy = create_copy
        self._layer = layer
        if not create_copy and layer == 0:
            carb.log_warn(
                "Creating Flow preset: global layer cannot be used for referenced preset, assigning next free layer"
            )
            self._layer = -1
        self._url = get_preset_url(self._preset_name) if url == "" else url
        self._on_session_layer = on_session_layer

    def do(self):
        return omni.kit.commands.execute(
            "FlowCreateUsdPresetMultiple",
            paths=self._paths,
            preset_name=self._preset_name,
            url=self._url,
            is_copy=self._create_copy,
            layer=self._layer,
            on_session_layer=self._on_session_layer,
        )

    def undo(self):
        pass


# command to voxelize points to a NanoVDB, using Flow
# returns a list of NanoVDBs, one for each channel RGBA
#
# points: numpy array of float3 positions
# colors: numpy array of float3 colors
# local_to_world: numpy array of double for 4x4 transform matrix
# cell_size: float voxel cell size
# max_blocks: maximum Flow blocks to use for voxelization, each Flow block has 8k voxels
class FlowVoxelizePointsAndSync(omni.kit.commands.Command):
    def __init__(self, points, colors, local_to_world, cell_size, max_blocks, vdb_local_to_world=None):

        self._points = points
        self._colors = colors
        self._local_to_world = local_to_world
        self._cell_size = cell_size
        self._max_blocks = max_blocks
        self._vdb_local_to_world = vdb_local_to_world

    def do(self):
        iflow = _flowusd.acquire_flowusd_interface()

        return iflow.voxelize_points_and_sync_v2(
            self._points,
            self._colors,
            self._local_to_world,
            self._vdb_local_to_world,
            self._cell_size,
            self._max_blocks,
        )

    def undo(self):
        pass
