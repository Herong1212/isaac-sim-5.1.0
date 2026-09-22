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

import weakref
from typing import Tuple

import carb
import omni.usd
from omni.syntheticdata import SyntheticData
from pxr import Usd

from . import viewport_manager_legacy as vm_legacy

ht_available = True
try:
    import omni.hydratexture
except:
    carb.log_info("HydraTexture is not available")
    ht_available = False

vp1_available = True
try:
    import omni.kit.viewport_legacy
except:
    carb.log_info("Viewport 1.0 is not available")
    vp1_available = False


USE_HYDRA_TEXTURES = ht_available
WINDOW_DOCK_TIMEOUT = 10
RP_PREFIX_SETTING = "/exts/omni.kit.hydra_texture/renderProduct/path/prefix"
LEGACY_RP_PREFIX = "RenderProduct_"


# Single HydraTexture for a Camera/View
class HydraTexture:
    def __init__(
        self,
        name: str,
        camera_path: str,
        resolution,
        async_rendering: bool = False,
        usd_context_name: str = None,
        engine_name: str = None,
        hydra_texture_factory=None,
    ):
        self.__name = name
        self._path_prefix = carb.settings.get_settings().get_as_string(RP_PREFIX_SETTING) or LEGACY_RP_PREFIX

        if usd_context_name is None:
            usd_context_name = ""
        if engine_name is None:
            engine_name = "rtx"
        if hydra_texture_factory is None:
            self.__hydra_texture_factory = omni.hydratexture.acquire_hydra_texture_factory_interface()
            hydra_texture_factory = self.__hydra_texture_factory
        self.hydra_texture = hydra_texture_factory.create_hydra_texture(
            self.__name, resolution[0], resolution[1], usd_context_name, str(camera_path), engine_name, async_rendering
        )

    @property
    def path(self):
        return f"/Render/{self._path_prefix}{self.__name}"

    def __del__(self):
        if self.hydra_texture:
            self.destroy()

    def destroy(self):
        if self.hydra_texture is not None:
            self.hydra_texture.set_updates_enabled(False)
        self.__drawable_change_sub = None
        self.hydra_texture = None
        self.__hydra_texture_factory = None

        # Reset synthetic data references to render product
        sd = SyntheticData.Get()
        sd_nodes_to_reset = []
        for node_path in sd._nodeGraphs.keys():
            if node_path.startswith(self.path):
                sd_nodes_to_reset.append(node_path)
        for node_path in sd_nodes_to_reset:
            sd._reset_node_graph(sd._nodeGraphs.pop(node_path))

        # Remove render product prim
        stage = omni.usd.get_context().get_stage()
        if stage:
            # Delete the render product from all layers
            for layer in stage.GetLayerStack():
                with Usd.EditContext(stage, layer):
                    prim = stage.GetPrimAtPath(self.path)
                    if not prim.IsValid():
                        continue
                    stage.RemovePrim(self.path)


# Manage multiple HydraTextureWrapper
class MultiTexture:
    def __init__(self):
        self.__hydra_texture_factory = None
        self.__hydra_textures = {}

    def __del__(self):
        self.destroy()

    @property
    def _hydra_textures(self):
        valid_textures = {}
        for ctx in self.__hydra_textures:
            for ht in self.__hydra_textures[ctx]:
                if ht.hydra_texture is not None:
                    valid_textures.setdefault(ctx, []).append(ht)
        self.__hydra_textures = valid_textures
        return self.__hydra_textures

    def destroy(self, context: str = None):
        if context is None:
            # Destroy all textures
            for texture_lists in self._hydra_textures.values():
                for texture in texture_lists:
                    texture.destroy()
            self.__hydra_textures = {}
            self.__hydra_texture_factory = None
        elif context in self.__hydra_textures:
            textures_to_destroy = self.__hydra_textures.pop(context)
            for texture in textures_to_destroy:
                texture.destroy()

    def add_texture(self, context=None, *args, **kwargs):
        if context is None:
            context = "default"
        if self.__hydra_texture_factory is None:
            self.__hydra_texture_factory = omni.hydratexture.acquire_hydra_texture_factory_interface()
        self.__hydra_textures.setdefault(context, []).append(
            HydraTexture(*args, **kwargs, hydra_texture_factory=self.__hydra_texture_factory)
        )

    @property
    def hydra_textures(self):
        for tex in self._hydra_textures.values():
            yield weakref.proxy(tex)

    def get(self, context, render_product_path):
        if context is None:
            context = "default"
        for texture in self._hydra_textures.get(context, []):
            rp_path = texture.hydra_texture.get_render_product_path()
            if rp_path == render_product_path:
                return texture
        raise ValueError(f"Render Product {render_product_path} not found")


def destroy_hydra_textures(context: str = None):
    ViewportManager().destroy(context)


# async def _deferred_dock(window_name, target_window_name, position, ratio):
#     target_window = ui.Workspace.get_window(target_window_name)
#     cur_time = time.time()
#     while ui.Workspace.get_window(window_name) is None and time.time() < cur_time + WINDOW_DOCK_TIMEOUT:
#         await asyncio.sleep(0.1)

#     ui.Workspace.get_window(window_name).dock_in(target_window, position, ratio)
#     target_window.focus()


# def _create_viewport_grid(viewport_names):
#     prev_name = None
#     if len(viewport_names) == 0:
#         return
#     cols = math.ceil(math.sqrt(len(viewport_names)))
#     rows = math.ceil(len(viewport_names) / cols)
#     row_names = [None] * rows
#     for i, vp_name in enumerate(viewport_names):
#         position = ui.DockPosition.RIGHT
#         if i >= cols:
#             position = ui.DockPosition.BOTTOM
#             ratio = 1 - 1 / (rows - (i // cols) + 1)
#             prev_name = row_names[i % cols]
#         else:
#             ratio = 1 - (1 / ((cols + 1) - i))
#         if prev_name is None:
#             omni.kit.async_engine.run_coroutine(_deferred_dock(vp_name, "Viewport", omni.ui.DockPosition.SAME, 1))
#         else:
#             omni.kit.async_engine.run_coroutine(_deferred_dock(vp_name, prev_name, position, ratio))
#         prev_name = vp_name
#         row_names[i % cols] = vp_name


class ViewportManager:
    _instance = None
    _hydra_textures = MultiTexture()
    _windows = []
    _widgets = []
    _do_rearrange_windows = False
    _context = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def _set_context(self, name):
        self._context = name

    def get_render_product(
        self, camera_path: str, resolution: Tuple[int, int], force_new: bool = False, name: str = None
    ) -> str:
        """Returns a render product with camera attached.

        Create a new render product and attach a camera. If a render product already exists with the same resolution and
        camera, return it instead. If a name is specified, a new render product is always created.

        Note: When using Viewport 2.0, viewports are not generated to draw the render product on screen.
        Note: Render products can utilize a large amount of VRAM. Render Products no longer in use should be destroyed.

        Args:
            camera_path: Prim path to the camera to be tied to the render product
            resolution: (width, height) resolution of the render product
            force_new: If ``True``, force creation of a new render product. If ``False``, existing render products will
            be re-used if currently assigned to same camera and of the same resolution. Is overriden to ``True`` if a
            ``name`` is provided.
            name: Optionally specify the name of the render product. Name must produce a valid USD path. If name is already
                in use or if supplying multiple cameras. If a name is provided, a new render product is always created.
        """
        camera_path = str(camera_path)
        stage = omni.usd.get_context().get_stage()
        path_prefix = carb.settings.get_settings().get_as_string(RP_PREFIX_SETTING) or LEGACY_RP_PREFIX
        rp_parent = f"/Render/{path_prefix}".rsplit("/", maxsplit=1)[0]
        if not USE_HYDRA_TEXTURES:
            return vm_legacy.get_render_product(camera_path, resolution)

        if not force_new:
            session_layer = stage.GetSessionLayer()
            with Usd.EditContext(stage, session_layer):
                # Try to find an available render product
                # Only return available render product if:
                #   - camera match
                #   - resolution match
                #   - name match or name is None
                if stage.GetPrimAtPath(rp_parent):
                    for prim in stage.GetPrimAtPath(rp_parent).GetChildren():
                        cur_name = str(prim.GetPrimPath()).split(f"/Render/{path_prefix}")[-1]
                        if name is not None and name != cur_name:
                            continue
                        try:
                            rp = self._hydra_textures.get(self._context, str(prim.GetPath()))
                        except ValueError:
                            continue

                        cur_camera = rp.hydra_texture.get_camera_path()
                        cur_res = (rp.hydra_texture.width, rp.hydra_texture.height)
                        if cur_camera == camera_path and cur_res == resolution:
                            return rp

        if name is None:
            name = "Replicator"
        path_name = omni.usd.get_stage_next_free_path(stage, f"/Render/{path_prefix}{name}", False)
        name = path_name.split(f"/Render/{path_prefix}")[-1]
        self._hydra_textures.add_texture(
            name=name,
            camera_path=camera_path,
            resolution=resolution,
            usd_context_name="",
            engine_name="rtx",
            async_rendering=False,
            context=self._context,
        )
        return self._hydra_textures.get(self._context, path_name)

    def destroy(self, context: str = None):
        while self._windows:
            window = self._windows.pop()
            window.destroy()
        while self._widgets:
            widget = self._widgets.pop()
            widget.destroy()
        self._windows = []
        self._widgets = []
        self._hydra_textures.destroy(context)
        self._do_build_window = False
        self._num_views = 0


def get_render_product(camera_path: str, resolution: Tuple[int, int], force_new: bool = False, name: str = None) -> str:
    """Returns a render product with camera attached.

    Identify an available render product and attach a camera. Render products attached to the default "Perspective"
    camera are considered as available. If no available render products are found, create a new one. If a render product
    already exists with the same resolution and camera, return it.

    Note: When using Viewport 2.0, viewports are not generated to draw the render product on screen.
    Note: Render products can utilize a large amount of VRAM. Render Products no longer in use should be destroyed.

    Args:
        camera_path: Prim path to the camera to be tied to the render product
        resolution: (width, height) resolution of the render product
        force_new: If ``True``, force creation of a new render product. If ``False``, existing render products will
            be re-used if currently assigned to same camera and of the same resolution. Is overriden to ``True`` if a
            ``name`` is provided.
        name: Optionally specify the name of the render product. Name must produce a valid USD path. If name is already
            in use or if supplying multiple cameras. If a name is provided, a new render product is always created.
    """
    return ViewportManager().get_render_product(camera_path, resolution, force_new, name)


def _set_context(context: str):
    ViewportManager()._set_context(context)


def _clear_context():
    ViewportManager()._set_context(None)
