# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Union

import carb.settings
import omni.usd
import usdrt
from pxr import PhysxSchema, Usd, UsdGeom, UsdPhysics

from .utils import ReplicatorItem, ReplicatorWrapper, auto_connect, create_node

RENDER_MODE = "/rtx/rendermode"
REALTIME_ANTIALIASING = "/rtx/post/aa/op"
PATHTRACED_TOTAL_SAMPLES_PER_PIXEL = "/rtx/pathtracing/totalSpp"


@ReplicatorWrapper
def carb_settings(setting: str, value: Union[List, float, ReplicatorItem]) -> ReplicatorItem:
    """Set a specific carb setting

    Carb settings are settings controlling anything from render parameters to specific extension behaviours. Any of
    these can be controlled and randomized through Replicator. Because settings can be introduced and removed by
    extensions, an providing an exhaustive list of available settings is not possible. Below you will find a subset of
    settings that may be useful for SDG workflows:

    Common Render Settings:
        See https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_common.html

    RealTime Render Settings:
        See https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_rt.html

    PathTracing Render Settings:
        See https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx-renderer_pt.html

    PostProcess Render Settings:
        See https://docs.omniverse.nvidia.com/materials-and-rendering/latest/rtx_post-processing.html

    Replicator Settings:
        - ``/omni/replicator/captureMotionBlur`` (bool): Capture a motion blur effect. In RealTime render mode, this is
          equivalent to enabling ``/rtx/post/motionblur/enabled``. In Pathtrace mode, a timestep is split into ``N``
          subframes where ``N`` is equal to ``/rtx/pathtracing/totalSpp``.
        - ``/omni/replicator/pathTracedMotionBlurSubSamples`` (float): Number of sub samples to render if in PathTracing
          render mode and motion blur is enabled.
        - ``/omni/replicator/totalRenderProductPixels`` (int): Number of total pixels created when calling
          rep.create.render_product. Used to calculate maxSamplePerLaunch inside orchestrator.py.

    Args:
        setting: Carb setting to modify.
        value: Value to set the carb setting to.

    Example:
        >>> import omni.replicator.core as rep
        >>> # Randomize film grain post process effect
        >>> tv_noise = rep.settings.carb_settings("/rtx/post/tvNoise/enabled", True)
        >>> with rep.trigger.on_frame():
        ...     flicker = rep.settings.carb_settings(
        ...         "/rtx/post/tvNoise/enableGhostFlickering",
        ...         rep.distribution.choice([True, False]),
        ...     )
        ...     grain_size = rep.settings.carb_settings(
        ...         "/rtx/post/tvNoise/grainSize",
        ...         rep.distribution.uniform(1.5, 5.0),
        ...     )
    """
    node = None
    if isinstance(value, ReplicatorItem):
        node = create_node("omni.replicator.core.OgnWriteCarbSetting", setting=setting)
        auto_connect(value.node, node)
    else:
        carb.settings.get_settings().set(setting, value)
    return node


def get_physx_timestep() -> float:
    stage = omni.usd.get_context().get_stage()

    usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
    physics_scenes = usdrt_stage.GetPrimsWithTypeName("PhysicsScene")
    if physics_scenes:
        physx_scene = physics_scenes[0]  # Select the first
        physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath(str(physx_scene)))
        return physx_scene.GetTimeStepsPerSecondAttr().Get()

    return None


def set_physx_timestep(physx_delta_time: float) -> None:
    stage = omni.usd.get_context().get_stage()

    usdrt_stage = usdrt.Usd.Stage.Attach(omni.usd.get_context().get_stage_id())
    physics_scenes = usdrt_stage.GetPrimsWithTypeName("PhysicsScene")

    if physics_scenes:
        physx_scene = physics_scenes[0]  # Select the first
        physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath(str(physx_scene)))
    else:
        UsdPhysics.Scene.Define(stage, "/PhysicsScene")
        physx_scene = PhysxSchema.PhysxSceneAPI.Apply(stage.GetPrimAtPath("/PhysicsScene"))
    physx_scene.GetTimeStepsPerSecondAttr().Set(1.0 / physx_delta_time)


def set_render_rtx_realtime(antialiasing: Union[str, ReplicatorItem] = "FXAA") -> None:
    """Setup RTX Realtime render mode

    Args:
        antialiasing: Antialiasing algorithm. Select from [Off, FXAA, DLSS, TAA, DLAA]. FXAA is recommended
            for non-sequential data generation as it does not accumulate samples across frames.

    Example:
        >>> import omni.replicator.core as rep
        >>> rep.settings.set_render_rtx_realtime(antialiasing="DLSS")
    """
    carb_settings(RENDER_MODE, "RaytracedLighting")

    # From `omni.rtx.settings.dev/omni/rtx/settings/dev/dev_stack.py`
    aa_mapping = {
        "off": 0,
        "taa": 1,
        "fxaa": 2,
        "dlss": 3,
        "dlaa": 4,
    }
    if antialiasing.lower() not in aa_mapping:
        raise ValueError(
            f"Invalid antialiasing argument `{antialiasing}`. Select from {[aa.upper() for aa in aa_mapping]}"
        )
    if antialiasing.lower() not in ["dlss", "dlaa"]:
        carb.log_info("Disabling AA limited ops.")
        carb_settings("/rtx-transient/post/aa/limitedOps", False)
    carb_settings(REALTIME_ANTIALIASING, aa_mapping[antialiasing.lower()])


def set_render_pathtraced(samples_per_pixel: Union[int, ReplicatorItem] = 64) -> None:
    """Setup PathTraced render mode

    Args:
        samples_per_pixel: Select the total number of samples to sample for each pixel per frame. Valid
            range [1, inf]

    Example:
        >>> import omni.replicator.core as rep
        >>> rep.settings.set_render_pathtraced(samples_per_pixel=512)
    """
    carb_settings(RENDER_MODE, "PathTracing")
    carb_settings(PATHTRACED_TOTAL_SAMPLES_PER_PIXEL, samples_per_pixel)


def set_stage_meters_per_unit(meters_per_unit: float) -> None:
    """Set up the meters per unit for the stage.

    Args:
        meters_per_unit: Set the stage meters per unit value.

    Example:
        >>> import omni.replicator.core as rep
        >>> rep.settings.set_stage_meters_per_unit(1.0)
    """
    stage = omni.usd.get_context().get_stage()

    if not stage:
        raise Exception("There is no stage currently opened, unable to set stage meters per unit.")

    root_layer = stage.GetRootLayer()
    root_layer.SetPermissionToEdit(True)
    with Usd.EditContext(stage, root_layer):
        UsdGeom.SetStageMetersPerUnit(stage, meters_per_unit)


def set_stage_up_axis(up_axis: str) -> None:
    """Set the up axis of the stage

    Args:
        up_axis: Specify stage up axis. Select from  `[Y, Z]`

    Example:
        >>> import omni.replicator.core as rep
        >>> rep.settings.set_stage_up_axis("Z")
    """
    valid_up_axes = ["Y", "Z"]
    if up_axis.upper() not in valid_up_axes:
        raise ValueError(f"Stage up axis can only be set to `{valid_up_axes}`, specified invalid value `{up_axis}`.")
    stage = omni.usd.get_context().get_stage()
    if stage is None:
        raise Exception("There is no stage currently opened, unable to set stage up axis.")
    root_layer = stage.GetRootLayer()
    root_layer.SetPermissionToEdit(True)
    with Usd.EditContext(stage, root_layer):
        UsdGeom.SetStageUpAxis(stage, up_axis.upper())
