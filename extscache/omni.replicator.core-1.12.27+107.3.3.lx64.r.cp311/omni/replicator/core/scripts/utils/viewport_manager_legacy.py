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

import asyncio
import math
import time
from typing import Tuple

import carb
import omni.kit
import omni.kit.async_engine
import omni.usd
from omni import ui

WINDOW_DOCK_TIMEOUT = 10


async def _deferred_dock(window_name, target_window_name, position, ratio):
    target_window = ui.Workspace.get_window(target_window_name)
    cur_time = time.time()
    while ui.Workspace.get_window(window_name) is None and time.time() < cur_time + WINDOW_DOCK_TIMEOUT:
        await asyncio.sleep(0.1)

    ui.Workspace.get_window(window_name).dock_in(target_window, position, ratio)
    target_window.focus()


def _create_viewport(camera_path, resolution):
    vp_iface = omni.kit.viewport_legacy.get_viewport_interface()
    viewport_instance = vp_iface.create_instance()
    viewport = vp_iface.get_viewport_window(viewport_instance)
    viewport_name = vp_iface.get_viewport_window_name(viewport_instance)
    viewport.set_window_size(400, 300)
    viewport.set_texture_resolution(*resolution)
    viewport.set_active_camera(str(camera_path))

    return viewport_name


def _create_viewport_grid(viewport_names):
    prev_name = None
    if len(viewport_names) == 0:
        return
    cols = math.ceil(math.sqrt(len(viewport_names)))
    rows = math.ceil(len(viewport_names) / cols)
    for i, vp_name in enumerate(viewport_names):
        position = ui.DockPosition.RIGHT
        if i >= cols:
            position = ui.DockPosition.BOTTOM
            ratio = 1 - 1 / (rows - (i // cols) + 1)
            if i == cols:
                prev_name = "Viewport"
            else:
                prev_name = f"Viewport {i - cols + 1}"
        else:
            ratio = 1 - (1 / ((cols + 1) - i))
        if prev_name is not None:
            omni.kit.async_engine.run_coroutine(_deferred_dock(vp_name, prev_name, position, ratio))
        prev_name = vp_name


def _get_camera_resolution(camera):
    # Use camera width and height
    if camera.HasProperty("renderWidth") and camera.HasProperty("renderHeight"):
        width = int(camera.GetAttribute("renderWidth").Get())
        height = int(camera.GetAttribute("renderHeight").Get())
    # Use global width and height
    else:
        width = int(carb.settings.get_settings().get("/app/renderer/resolution/width"))
        height = int(carb.settings.get_settings().get("/app/renderer/resolution/height"))
    return width, height


def get_render_product(camera_path: str, resolution: Tuple[int, int]) -> None:
    """Returns a render product with camera attached.

    Identify an available render product and attach a camera. Render products attached to the default "Perspective"
    camera are considered as available. If no available render products are found, create a new one. If a render product
    already exists with the same resolution and camera, return it.

    """
    AVAILABLE_CAMERA = "/OmniverseKit_Persp"

    camera_path = str(camera_path)

    vp_iface = omni.kit.viewport_legacy.get_viewport_interface()
    viewport_instances = vp_iface.get_instance_list()
    stage = omni.usd.get_context().get_stage()

    # Get camera to viewport mapping
    camera_viewport_map = {}
    viewports = []
    used_viewports = []
    for vpi in viewport_instances:
        vp = vp_iface.get_viewport_window(vpi)
        vp_name = vp_iface.get_viewport_window_name(vpi)
        camera_viewport_map.setdefault(vp.get_active_camera(), []).append(vp_name)
        viewports.append(vp_name)
        if vp.get_active_camera() != AVAILABLE_CAMERA:
            used_viewports.append(vp_name)

    camera = stage.GetPrimAtPath(camera_path)
    if not camera:
        raise ValueError(f"Camera at {camera_path} was not found.")

    found_vp = False
    if camera_path in camera_viewport_map:
        for vp_name in camera_viewport_map[camera_path]:
            vp = vp_iface.get_viewport_window(vp_iface.get_instance(vp_name))
            vp_res = vp.get_texture_resolution()
            if vp_res == resolution:
                found_vp = True
                break

    if not found_vp:
        if AVAILABLE_CAMERA in camera_viewport_map:
            vp_name = camera_viewport_map[AVAILABLE_CAMERA][0]
        else:
            vp_name = _create_viewport(resolution=resolution, camera_path=camera_path)

    vp = vp_iface.get_viewport_window(vp_iface.get_instance(vp_name))
    render_product = vp.get_render_product_path()
    vp.set_texture_resolution(*resolution)
    vp.set_active_camera(str(camera_path))
    vp.show_hide_window(True)
    omni.kit.ui.get_editor_menu().set_value(f"Window/{vp_name}", True)

    used_viewports.append(vp_name)
    _create_viewport_grid(used_viewports)

    # Hide any remaining viewports
    for vp_name in viewports:
        vp = vp_iface.get_viewport_window(vp_iface.get_instance(vp_name))
        if vp.get_active_camera() == AVAILABLE_CAMERA and camera_path != AVAILABLE_CAMERA:
            vp.show_hide_window(False)
            omni.kit.ui.get_editor_menu().set_value(f"Window/{vp_name}", False)

    return render_product
