# Copyright (c) 2022-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from typing import List

import carb
import omni.kit.app
from pxr import Sdf


def get_flow_usd_version() -> List:
    manager = omni.kit.app.get_app().get_extension_manager()
    ext_list = manager.get_extensions()
    for e in ext_list:
        name = e["name"]
        enabled = e["enabled"]
        if name == "omni.flowusd" and enabled:
            return e["version"][:3]
    return None


async def run_flow_renderer(paths: List[str], preset_name="Native"):
    omni.kit.commands.execute("FlowCreatePointCloudPreset", paths=paths, preset_name=preset_name)

    stage = omni.usd.get_context().get_stage()

    for path in paths:
        point_prim = stage.GetPrimAtPath(path)
        if point_prim:
            point_prim.CreateAttribute("omni:rtx:skip", Sdf.ValueTypeNames.Bool).Set(True)


async def run_index_renderer(paths: List[str]):
    omni.kit.commands.execute("ChangeSetting", path="rtx/index/compositeEnabled", value=True)

    stage = omni.usd.get_context().get_stage()

    for path in paths:
        point_prim = stage.GetPrimAtPath(path)
        if point_prim:
            point_prim.CreateAttribute("nvindex:composite", Sdf.ValueTypeNames.Bool).Set(True)
            point_prim.CreateAttribute("omni:rtx:skip", Sdf.ValueTypeNames.Bool).Set(True)


async def run_rtx_renderer(paths: List[str]):
    stage = omni.usd.get_context().get_stage()

    for path in paths:
        point_prim = stage.GetPrimAtPath(path)
        if point_prim:
            point_prim.CreateAttribute("omni:rtx:skip", Sdf.ValueTypeNames.Bool).Set(False)
