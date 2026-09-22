# Copyright (c) 2021-2024, NVIDIA CORPORATION. All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto. Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import asyncio
import os
import shutil
from enum import Enum, IntEnum
from functools import partial
from pathlib import Path
from typing import Dict, List, Optional, Union

import carb
import omni.client
import omni.client.utils as clientutils
import omni.kit.app
import omni.kit.tool.asset_importer as ai
import omni.ui as ui
import omni.usd
from omni.kit.asset_converter import OmniClientWrapper
from pxr import Gf, Sdf, Tf, Usd, UsdGeom

from .potree_utils import PotreeWatch, create_point_cloud_prim, update_point_cloud_prim
from .progress_window import ProgressWindow, modal_import_error
from .render import run_flow_renderer, run_index_renderer, run_rtx_renderer

MAX_SCANS_WARN = 100
MAX_RTX_POINTS = 89478485

WRITTEN_ATTR = "written"
READ_ATTR = "read"
POINTS_COUNT_ATTR = "points_count"
SCANS_COUNT_ATTR = "scans_count"
TOTAL_COUNT_ATTR = "total_count"
LOCAL_POTREE_SUFFIX = ".potree"
USD_SUFFIX = ".usd"

SETTINGS_ROOT = "/exts/omni.kit.pointclouds/"
SETTING_TRIGGER_SOURCES = SETTINGS_ROOT + "trigger_sources"
SETTING_GENERATE_LOCAL_CACHE = SETTINGS_ROOT + "local_cache_generation"
SETTING_LOCAL_POTREE_CONVERSION = SETTINGS_ROOT + "local_potree_conversion"
SETTING_SHOW_IMPORT_OPTIONS = SETTINGS_ROOT + "show_import_options"
CACHE_PATH_SETTINGS_KEY = "/persistent/exts/omni.pointcloud.manager/cache_path"


class Potree(IntEnum):
    NONE = 0
    POTREE = 1
    USD = 2
    USD_POTREE_ASYNC = 3
    USD_POTREE_SYNC = 4


class CacheMethod(Enum):
    LOAD = 0
    GENERATE = 1
    LOAD_USD = 2


class ImportMethod(Enum):
    # number is the order of radios in the import menu
    LOAD = 0
    STREAM = 1


class Representation(Enum):
    # number is the order of radios in the import menu
    POINTS = 0
    VOLUMETRIC = 1


RENDER_MODE = ["Points", "Volume"]


class E57_Renderer(Enum):
    NONE = 0  # RTX is set as default when PCM is not loaded
    RTX = 1
    INDEX = 2  # default for points when point cloud is loaded
    FLOW = 3  # default for volumetrics when point cloud is loaded


class E57Importer(ai.AbstractImporterDelegate):
    def __init__(self, extension_path) -> None:
        super().__init__()
        self._name = "E57 Pointcloud Importer"
        self._filters = [".*\\.e57$"]
        self._descriptions = ["e57 Files (*.e57)"]
        self._cancelled = False
        # converted geom points are copied to the stage if True, otherwise referenced usd file is created
        self._copy_data = True
        self._combine_scans = True
        self._center_pointcloud = False
        self._representation = Representation.POINTS
        self._import_method = ImportMethod.LOAD
        self._cache_method = CacheMethod.LOAD

        self._extension_path = extension_path  # used for icon paths

        self._export_folder: str = None
        self._usd_subs = []

        settings = carb.settings.get_settings()
        self._renderer = E57_Renderer.NONE
        self._cache_path = settings.get(CACHE_PATH_SETTINGS_KEY)
        self._trigger_sources = settings.get(SETTING_TRIGGER_SOURCES)
        settings.set_default_bool(SETTING_SHOW_IMPORT_OPTIONS, False)

        # load value updated form Settings on the dialog build
        self._generate_local_cache = False
        self._convert_potree = False

        ext_manager = omni.kit.app.get_app().get_extension_manager()

        self._index_warning_icon = None
        self._index_enabled = False
        self._index_hook = ext_manager.subscribe_to_extension_enable(
            on_enable_fn=lambda _: self._on_index_enabled(True),
            on_disable_fn=lambda _: self._on_index_enabled(False),
            ext_name="omni.rtx.index_composite",
            hook_name="kit.pointclouds.index",
        )

        self._pcm_enabled = False
        self._pcm_hook = ext_manager.subscribe_to_extension_enable(
            on_enable_fn=lambda _: self._on_pcm_enabled(True),
            on_disable_fn=lambda _: self._on_pcm_enabled(False),
            ext_name="omni.pointcloud.manager",
            hook_name="kit.pointclouds.pcm",
        )

        if not self._pcm_enabled:
            self._set_pcm_disabled()

        self.reset()

    def destroy(self):
        self.reset()

        self._index_hook = None

    def reset(self):
        self._parent_prims = []
        self.progress_window = None

        # dummy values
        self.total_count = [0]
        self.scans_count = [0]
        self.points_count = [0]

        for i in range(len(self._usd_subs)):
            self._usd_subs = None

        self._usd_subs = []
        self._potree_import = None

        PotreeWatch().stop_all()

    @property
    def name(self) -> str:
        return self._name

    @property
    def filter_regexes(self) -> List[str]:
        return self._filters

    @property
    def filter_descriptions(self) -> List[str]:
        return self._descriptions

    def _set_pcm_disabled(self):
        self._copy_data = False
        self._renderer = E57_Renderer.RTX
        self._representation = Representation.POINTS
        self._import_method = ImportMethod.LOAD
        self._cache_method = CacheMethod.LOAD
        self._generate_local_cache = False
        self._convert_potree = False
        # Also no options are visible when PCM is disabled

    def _on_index_enabled(self, enabled):
        self._index_enabled = enabled
        if self._index_warning_icon:
            self._index_warning_icon.visible = enabled

    def _on_pcm_enabled(self, enabled):
        self._pcm_enabled = enabled
        if not enabled:
            self._set_pcm_disabled()

    async def _show_progress_window(self, title, button_text):
        """Progress window shown while converting to USD or copying to the stage"""
        self.progress_window = ProgressWindow(
            title, status_text="Preparing...", button_text=button_text, has_progress=True, has_warning=True
        )
        self.progress_window.show()
        # wait for the progress window to appear
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        return self.progress_window

    def _cancel_operation(self):
        self._cancelled = True

        # delete what has not been imported yet
        delete_prims = []
        done_prims = []
        stage = omni.usd.get_context().get_stage()
        for prim_path in self._parent_prims:
            xform_prim = stage.GetPrimAtPath(prim_path)
            if xform_prim:
                scans_count_attr = xform_prim.GetAttribute(SCANS_COUNT_ATTR)
                scans_count = scans_count_attr.Get() if scans_count_attr else 0
                scans_written_attr = xform_prim.GetAttribute(WRITTEN_ATTR)
                scans_written = scans_written_attr.Get() if scans_written_attr else 0
                if scans_count > 0 and scans_count == scans_written:
                    done_prims.append(prim_path)
                else:
                    delete_prims.append(prim_path)

        self._post_import(done_prims)
        omni.kit.commands.execute("DeletePrims", paths=delete_prims)

        self.reset()

    def get_cache_path(self, uri: str, import_method=ImportMethod.STREAM, export_path=""):
        try:
            from omni.pointcloud.manager import get_pointcloud_cache_path

            pcm_loaded = True
        except ImportError:
            pcm_loaded = False

        is_local = clientutils.is_local_url(uri)
        if is_local or not pcm_loaded or import_method == ImportMethod.LOAD:
            basename = os.path.basename(uri)
            file_name, _ = os.path.splitext(basename)

            suffix = ""
            if import_method == ImportMethod.STREAM:
                # output directory name, where cloud.js will be created
                suffix = LOCAL_POTREE_SUFFIX
            elif import_method == ImportMethod.LOAD:
                suffix = USD_SUFFIX

            file_name_with_ext = file_name + suffix

            if export_path == "":
                output_dir = self._export_folder if self._export_folder else os.path.dirname(uri)
                path = os.path.join(output_dir, file_name_with_ext)
                cache_path = path.replace("\\", "/")
            else:
                cache_path = export_path

            cache_exists = OmniClientWrapper.exists_sync(cache_path)
            return cache_path, cache_exists

        if pcm_loaded:
            cache_path = get_pointcloud_cache_path(uri)
            if cache_path and cache_path != "":
                cache_exists = OmniClientWrapper.exists_sync(cache_path)
            else:
                cache_exists = False
            # return point cloud uri, which is set into the point cloud prim, not the cache path
            return uri, cache_exists

        return None, False

    def build_options(self, paths: List[str]) -> None:
        settings = carb.settings.get_settings()
        # OMPE-56834: prepare for the removal of additional renderers and cached generation
        if not settings.get(SETTING_SHOW_IMPORT_OPTIONS):
            self._renderer = E57_Renderer.INDEX
            self._representation = Representation.POINTS
            self._import_method = ImportMethod.LOAD
            self._generate_local_cache = False
            self._convert_potree = False
            return True

        LABEL_FONT_SIZE = 14
        RADIO_SIZE = 30

        self._generate_local_cache = settings.get_as_bool(SETTING_GENERATE_LOCAL_CACHE)
        self._convert_potree = settings.get_as_bool(SETTING_LOCAL_POTREE_CONVERSION)

        RADIOBUTTON_STYLE = {
            "RadioButton": {"background_color": ui.color.transparent},
            "RadioButton:checked": {"background_color": ui.color.transparent},
            "RadioButton.Image": {"image_url": f"{self._extension_path}/icons/radio_off.svg"},
            "RadioButton.Image:checked": {"image_url": f"{self._extension_path}/icons/radio_on.svg"},
        }
        STYLE = {
            "Rectangle::hovering": {"background_color": 0x0, "border_radius": 2, "margin": 0, "padding": 0},
            "Rectangle::hovering:hovered": {"background_color": 0xFF9E9E9E},
            "Button.Image::folder": {"image_url": f"{self._extension_path}/data/folder.png"},
            "Button.Image::folder:checked": {"image_url": f"{self._extension_path}/data/folder.png"},
            "Button::folder": {"background_color": 0x0, "margin": 0},
            "Button::folder:checked": {"background_color": 0x0, "margin": 0},
            "Button::folder:pressed": {"background_color": 0x0, "margin": 0},
            "Button::folder:hovered": {"background_color": 0x0, "margin": 0},
        }
        # ICON_WARN_STYLE = {"image_url": f"{self._extension_path}/icons/warn.svg"}

        def set_renderer():
            if self._pcm_enabled:
                return

            if self._representation == Representation.VOLUMETRIC:
                if self._renderer != E57_Renderer.FLOW:
                    self._renderer = E57_Renderer.FLOW

            elif self._representation == Representation.POINTS and self._renderer == E57_Renderer.FLOW:
                if self._index_enabled:
                    self._renderer = E57_Renderer.INDEX
                else:
                    self._renderer = E57_Renderer.RTX

            renderer_option.model.set_value(self._renderer.value)

        def representation_changed(representation):
            if self._pcm_enabled:
                return

            self._representation = representation
            self._flow_stack.visible = representation == Representation.VOLUMETRIC
            self._rtx_stack.visible = representation == Representation.POINTS
            if self._index_enabled:
                self._index_stack.visible = representation == Representation.POINTS

            set_renderer()

        def import_method_changed(import_method):
            self._import_method = import_method

        def renderer_changed(renderer):
            self._renderer = renderer

        absolute_path = clientutils.normalize_url(paths[0])
        is_local = clientutils.is_local_url(absolute_path)
        cache_exists = False
        asset_export_path, cache_exists = self.get_cache_path(absolute_path)

        with ui.VStack(height=0, spacing=2, style=STYLE):
            with ui.HStack(width=ui.Percent(100)):
                ui.Label(
                    "Representation",
                    width=0,
                    style={"font_size": LABEL_FONT_SIZE},
                    alignment=ui.Alignment.LEFT,
                )
            representation_option = ui.RadioCollection()
            with ui.HStack(width=ui.Percent(100), style=RADIOBUTTON_STYLE):
                radio_flow = ui.RadioButton(radio_collection=representation_option, width=RADIO_SIZE, height=RADIO_SIZE)
                radio_flow.set_clicked_fn(partial(representation_changed, Representation.POINTS))
                ui.Label("Points", name="text")
            with ui.HStack(width=ui.Percent(100), style=RADIOBUTTON_STYLE):
                radio_rtx = ui.RadioButton(radio_collection=representation_option, width=RADIO_SIZE, height=RADIO_SIZE)
                radio_rtx.set_clicked_fn(partial(representation_changed, Representation.VOLUMETRIC))
                ui.Label("Volume", name="text")
                ui.Spacer(width=7)
            representation_option.model.set_value(self._representation.value)
            if not self._pcm_enabled:
                # only applicable without PCM, otherwise PCM choses the renderer
                ui.Spacer(height=2)
                with ui.HStack(width=ui.Percent(100)):
                    ui.Label(
                        "Renderer",
                        width=0,
                        style={"font_size": LABEL_FONT_SIZE},
                        alignment=ui.Alignment.LEFT,
                    )
                    renderer_option = ui.RadioCollection()
                with ui.HStack(width=ui.Percent(100), style=RADIOBUTTON_STYLE):
                    radio_no_renderer = ui.RadioButton(
                        radio_collection=renderer_option, width=RADIO_SIZE, height=RADIO_SIZE
                    )
                    radio_no_renderer.set_clicked_fn(partial(renderer_changed, E57_Renderer.NONE))
                    ui.Label("No renderer", name="text")
                    ui.Spacer()
                self._rtx_stack = ui.HStack(
                    width=ui.Percent(100),
                    style=RADIOBUTTON_STYLE,
                    visible=self._representation == Representation.POINTS,
                )
                with self._rtx_stack:
                    radio_rtx = ui.RadioButton(radio_collection=renderer_option, width=RADIO_SIZE, height=RADIO_SIZE)
                    radio_rtx.set_clicked_fn(partial(renderer_changed, E57_Renderer.RTX))
                    ui.Label("RTX", name="text")
                    ui.Spacer()
                self._index_stack = ui.HStack(
                    width=ui.Percent(100),
                    style=RADIOBUTTON_STYLE,
                    visible=self._index_enabled and self._representation == Representation.POINTS,
                )
                with self._index_stack:
                    radio_index = ui.RadioButton(radio_collection=renderer_option, width=RADIO_SIZE, height=RADIO_SIZE)
                    radio_index.set_clicked_fn(partial(renderer_changed, E57_Renderer.INDEX))
                    ui.Label("IndeX", name="text")
                    ui.Spacer()
                self._flow_stack = ui.HStack(
                    width=ui.Percent(100),
                    style=RADIOBUTTON_STYLE,
                    visible=self._representation == Representation.VOLUMETRIC,
                )
                with self._flow_stack:
                    radio_flow = ui.RadioButton(radio_collection=renderer_option, width=RADIO_SIZE, height=RADIO_SIZE)
                    radio_flow.set_clicked_fn(partial(renderer_changed, E57_Renderer.FLOW))
                    ui.Label("Flow", name="text")
                    ui.Spacer()
                set_renderer()
                ui.Spacer(height=2)

            if is_local and not self._convert_potree:
                self._import_method = ImportMethod.LOAD
            elif cache_exists or self._generate_local_cache or self._convert_potree:
                with ui.HStack(width=ui.Percent(100)):
                    ui.Label(
                        "Import Method",
                        width=0,
                        style={"font_size": LABEL_FONT_SIZE},
                        alignment=ui.Alignment.LEFT,
                    )
                import_method_option = ui.RadioCollection()
                with ui.HStack(width=ui.Percent(100), style=RADIOBUTTON_STYLE):
                    radio_rtx = ui.RadioButton(
                        radio_collection=import_method_option, width=RADIO_SIZE, height=RADIO_SIZE
                    )
                    radio_rtx.set_clicked_fn(partial(import_method_changed, ImportMethod.LOAD))
                    ui.Label("Load", name="text")
                if cache_exists or (self._convert_potree and is_local) or self._generate_local_cache:
                    with ui.HStack(width=ui.Percent(100), style=RADIOBUTTON_STYLE):
                        radio_flow = ui.RadioButton(
                            radio_collection=import_method_option, width=RADIO_SIZE, height=RADIO_SIZE
                        )
                        radio_flow.set_clicked_fn(partial(import_method_changed, ImportMethod.STREAM))
                        if cache_exists:
                            ui.Label("Stream", name="text")
                        else:
                            if self._convert_potree and is_local:
                                ui.Label("Convert and Stream", name="text")
                            elif self._generate_local_cache:
                                ui.Label("Generate Cache", name="text")

                import_method_option.model.set_value(self._import_method.value)
                ui.Spacer(height=2)

        return True

    async def get_asset_path(self, absolute_path, export_path):
        absolute_path = clientutils.normalize_url(absolute_path)
        basename = os.path.basename(absolute_path)

        is_local = clientutils.is_local_url(absolute_path)

        # output directory name, where cloud.js will be created
        asset_export_path, file_exists = self.get_cache_path(absolute_path, self._import_method, export_path)

        # add watcher for the cloud creation when in local folder, otherwise will be converted on a farm
        if is_local:
            if file_exists:
                self._cache_method = CacheMethod.LOAD
            elif self._convert_potree:
                self._cache_method = CacheMethod.GENERATE

            if self._import_method == ImportMethod.STREAM:
                self._potree_import = create_point_cloud_prim(asset_export_path)
            else:
                self._copy_data = False  # copy file to the current stage
                if file_exists:
                    self._cache_method = CacheMethod.LOAD_USD
                else:
                    self._cache_method = CacheMethod.LOAD

            # usd folder mmight by locked with PCM
            # if os.path.exists(asset_export_path + "/usd"):
            #     self.progress_window.set_status_text(f"Converted Potree file already exists")
            #     return None, None

            # Disabled, USD files cannot be read while the conversion is running
            # PotreeWatch().start_watch(
            #     asset_export_path, self._representation == Representation.VOLUMETRIC, asset_export_path
            # )
        elif self._import_method == ImportMethod.LOAD:
            if file_exists:
                self._cache_method = CacheMethod.LOAD_USD
            else:
                self._cache_method = CacheMethod.LOAD

        elif self._import_method == ImportMethod.STREAM:
            if file_exists:
                self._cache_method = CacheMethod.LOAD
                self._potree_import = create_point_cloud_prim(asset_export_path)
            else:
                self._cache_method = CacheMethod.GENERATE

            if self._generate_local_cache and self._cache_method == CacheMethod.GENERATE:
                # upload file to nucleus - not used ATM
                # self.progress_window.set_status_text(f"Copying '{basename}'...")
                # task_source_path = self._cache_path + "/sources/" + basename

                # start service task
                result = omni.kit.commands.execute(
                    "RunVdbTask", path=absolute_path, render_mode=RENDER_MODE[self._representation.value]
                )
                asset_export_path = None
                if result:
                    self.progress_window.set_status_text("Conversion will run on a farm service...")
                    # TOOO show progress in the progress bar
                    self.progress_window.set_progress_text("Progress is updated in the info log")
                else:
                    self.progress_window.set_status_text("Error while starting a conversion service")

                return None, None

        return basename, asset_export_path

    async def convert_assets(self, paths: List[str], **kargs) -> Dict[str, Union[str, None]]:
        export_folder = kargs.get("export_folder", "")
        export_path = ""
        if export_folder != "":
            export_filename = kargs.get("export_file_name", "") + kargs.get("export_file_format", "")
            export_path = os.path.join(export_folder, export_filename)
            export_path = export_path.replace("\\", "/")

        self.reset()

        self._cancelled = False

        absolute_paths = []
        for file_path in paths:
            if self.is_supported_format(file_path):
                absolute_paths.append(file_path)

        button_text = "OK" if self._import_method == ImportMethod.STREAM else "Cancel"
        await self._show_progress_window("E57 File Import", button_text)

        if self.progress_window and not self.progress_window.is_visible():
            carb.log_error("Error showing progress window")
        elif self.progress_window:
            self.progress_window.set_cancel_fn(self._cancel_operation)
        else:
            carb.log_error("Error creating progress window")
            return []

        converted_assets = {}
        for absolute_path in absolute_paths:
            basename, asset_export_path = await self.get_asset_path(absolute_path, export_path)
            if self._import_method == ImportMethod.STREAM:
                if self._cache_method == CacheMethod.LOAD:
                    pointcloud_path, src_path = self._potree_import
                    await update_point_cloud_prim(src_path, RENDER_MODE[self._representation.value], pointcloud_path)
                    self.progress_window.hide()
                    return []
                elif not asset_export_path:
                    return []

            if self._cache_method == CacheMethod.LOAD_USD:
                self.progress_window.hide()
                converted_assets[absolute_path] = asset_export_path
                # The reference will be created by the asset importer
                carb.log_info(f"Loading existing USD file '{asset_export_path}' ...")
                continue

            task_idx = self.progress_window.create_task()
            self.total_count.append(0)
            self.scans_count.append(0)
            self.points_count.append(0)
            text = f"Task {task_idx}: " if len(absolute_paths) > 1 else ""
            prim = None

            self.progress_window.set_task_status_text(task_idx, f"{text}Copying data from '{basename}'...")
            await omni.kit.app.get_app().next_update_async()

            if asset_export_path == self._cache_path:
                # The cache would be wiped out before the conversion
                carb.log_error(f"Invalid export path '{asset_export_path}' set")
                return []

            carb.log_info(f"Starting e57 conversion of '{absolute_path}' to '{asset_export_path}'...")
            target_stage, prim = await self._convert_assets(absolute_path, task_idx, asset_export_path)

            if not prim:
                self.progress_window.hide()
                return []

            self._parent_prims.append(prim)

            await omni.kit.app.get_app().next_update_async()
            if self._cancelled:
                break

        if converted_assets:
            return converted_assets

        self._transform_xforms()

        await omni.kit.app.get_app().next_update_async()
        if self._cancelled:
            return []

        return []

    async def added_reference(self, assets):
        """Called by the import manager after a reference has been added to the stage."""

        self._parent_prims = []
        for _, value in assets.items():
            _, prim_path = value
            self._parent_prims.append(prim_path)

        self._transform_xforms()
        self._post_import(self._parent_prims)

    def _on_scans_read_changed(self, task_idx, path):
        if task_idx >= len(self.scans_count):
            return

        if self.scans_count[task_idx] == 0:
            return

        stage = omni.usd.get_context().get_stage()
        loaded_attr = stage.GetAttributeAtPath(path)
        if not loaded_attr:
            return

        value = loaded_attr.Get()

        scans_count = self.scans_count[task_idx]
        count = self.points_count[task_idx] if scans_count == 1 else scans_count
        self.progress_window.set_task_progress(task_idx, 0 if count == 0 else value / count)

        if value == count:  # scan is read
            if self._import_method == ImportMethod.STREAM:
                self.progress_window.set_task_progress_text(task_idx, "Creating Potree files...")
                self.progress_window.set_task_progress(task_idx, 0)

    def _on_scans_written_changed(self, task_idx, path):
        if task_idx >= len(self.scans_count):
            return

        if self.scans_count[task_idx] == 0:
            return

        stage = omni.usd.get_context().get_stage()
        loaded_attr = stage.GetAttributeAtPath(path)
        if not loaded_attr:
            return

        value = loaded_attr.Get()
        if value == self.scans_count[task_idx]:

            # if self._import_method == ImportMethod.LOAD and self._representation == Representation.VOLUMETRIC:
            #     self.progress_window.set_task_progress_text(task_idx, "Creating VDB files...")
            #     self.progress_window.set_task_progress(task_idx, 0)

            #     xform_path = loaded_attr.GetPrimPath()
            #     xform = stage.GetPrimAtPath(xform_path)
            #     usd_path = ""
            #     if xform.GetReferences():
            #         ref_and_layers = omni.usd.get_composed_references_from_prim(xform)
            #         for ref, _ in ref_and_layers:
            #             usd_path = ref.assetPath
            #             break
            #     if usd_path != "":
            #         omni.kit.commands.execute("VoxelizePoints", paths=[usd_path], neural_vdb=False)

            if task_idx > 0 and task_idx - 1 < len(self._parent_prims):
                self._post_import([self._parent_prims[task_idx - 1]])

            # faster tasks do not get correctly updated, try again
            self.progress_window.set_task_progress(task_idx, 1)

            # check if all task are done
            all_done = True
            for prim_path in self._parent_prims:
                xform_prim = stage.GetPrimAtPath(prim_path)
                if xform_prim:
                    scans_count_attr = xform_prim.GetAttribute(SCANS_COUNT_ATTR)
                    scans_count = scans_count_attr.Get() if scans_count_attr else 0
                    scans_written_attr = xform_prim.GetAttribute(WRITTEN_ATTR)
                    scans_written = scans_written_attr.Get() if scans_written_attr else 0
                    if scans_count != scans_written:
                        all_done = False
            if all_done:
                self._post_import()

    def _on_total_count_changed(self, task_idx, path):
        if task_idx >= len(self.total_count):
            return

        stage = omni.usd.get_context().get_stage()
        loaded_attr = stage.GetAttributeAtPath(path)
        self.total_count[task_idx] = loaded_attr.Get()
        if self.total_count[task_idx] == 0:
            return

        if self._renderer == E57_Renderer.RTX and self.total_count[task_idx] > MAX_RTX_POINTS:
            self.progress_window.set_task_status_text(
                task_idx, "", f"""Point count exceeded the limit. The file won't be rendered."""
            )

    def _on_scans_count_changed(self, task_idx, path):
        if task_idx >= len(self.scans_count):
            return

        stage = omni.usd.get_context().get_stage()
        loaded_attr = stage.GetAttributeAtPath(path)
        self.scans_count[task_idx] = loaded_attr.Get()
        if self.scans_count[task_idx] == 0:
            return

        if not self._combine_scans and self.scans_count[task_idx] > MAX_SCANS_WARN:
            self.progress_window.set_task_warning_text(
                task_idx,
                f"""The file contains more than {MAX_SCANS_WARN} scans.
The scans can be combined during the import,
please see import options.""",
            )
        what = "scan" if self.scans_count[task_idx] == 1 else "scans"
        self.progress_window.set_task_progress_text(task_idx, f"Reading {self.scans_count[task_idx]} {what}: ")

    def _on_points_count_changed(self, task_idx, path):
        if task_idx >= len(self.points_count):
            return

        stage = omni.usd.get_context().get_stage()
        loaded_attr = stage.GetAttributeAtPath(path)
        if loaded_attr:
            self.points_count[task_idx] = loaded_attr.Get()
        if self.points_count[task_idx] == 0:
            return

        self.progress_window.set_task_warning_text(task_idx, "")
        # what = "scan" if self.points_count[task_idx] == 1 else "points"
        # self.progress_window.set_task_progress_text(task_idx, f"Reading {self.points_count[task_idx]} {what}: ")
        self.progress_window.set_task_progress_text(task_idx, "Reading 1 scan: ")

    async def _convert_assets(self, absolute_path, task_idx, export_path=""):
        """Copies assets to the target stage. This might be the current stage or a new one.
        This relies on the e57 plugin to open the stage.
        Returns stage where data has been copied into and the path to xform prim.
        """
        new_path = Path(absolute_path)
        stem = Tf.MakeValidIdentifier(new_path.stem)
        stage = omni.usd.get_context().get_stage()
        prim_path = omni.usd.get_stage_next_free_path(stage, "/" + stem, True)

        # Create the parent xform
        xform_prim = stage.DefinePrim(prim_path, "Xform")
        if not xform_prim:
            carb.log_error("Cannot create parent xform where to import the selected file.")
            return None, None

        usd_watcher = omni.usd.get_watcher()
        path = Sdf.Path(prim_path)
        self._usd_subs.append(
            usd_watcher.subscribe_to_change_info_path(
                path.AppendProperty(READ_ATTR), partial(self._on_scans_read_changed, task_idx)
            )
        )
        self._usd_subs.append(
            usd_watcher.subscribe_to_change_info_path(
                path.AppendProperty(WRITTEN_ATTR), partial(self._on_scans_written_changed, task_idx)
            )
        )
        self._usd_subs.append(
            usd_watcher.subscribe_to_change_info_path(
                path.AppendProperty(TOTAL_COUNT_ATTR), partial(self._on_total_count_changed, task_idx)
            )
        )
        self._usd_subs.append(
            usd_watcher.subscribe_to_change_info_path(
                path.AppendProperty(SCANS_COUNT_ATTR), partial(self._on_scans_count_changed, task_idx)
            )
        )
        self._usd_subs.append(
            usd_watcher.subscribe_to_change_info_path(
                path.AppendProperty(POINTS_COUNT_ATTR), partial(self._on_points_count_changed, task_idx)
            )
        )

        merge_arg = "1" if self._combine_scans else "0"
        usd_arg = "0" if self._copy_data else "1"
        center_arg = "1" if self._center_pointcloud else "0"
        rtx_arg = "1" if self._renderer == E57_Renderer.RTX else "0"
        potree = int(Potree.USD) if self._import_method == ImportMethod.STREAM else int(Potree.NONE)

        args = {
            "merge": merge_arg,
            "usd": usd_arg,
            "path": str(prim_path),
            "export": str(export_path),
            "center": str(center_arg),
            "rtx": str(rtx_arg),
            "potree": str(potree),
        }
        source_layer = Sdf.Layer.FindOrOpen(absolute_path, args)
        target_stage = None

        with omni.kit.undo.group():
            target_stage = Usd.Stage.Open(source_layer)

        xform_prim = stage.GetPrimAtPath(prim_path)
        if not xform_prim:
            modal_import_error("E57 Import Error", "There was an error importing the selected file.")
            return None, None

        if self._cancelled:
            return None, None

        return target_stage, prim_path

    def _transform_xforms(self):
        if len(self._parent_prims) == 0:
            return

        parent_prims = self._parent_prims
        stage = omni.usd.get_context().get_stage()
        adj_mat = Gf.Matrix4d().SetIdentity()

        # Rotate from z-axis up to y-axis up
        if UsdGeom.GetStageUpAxis(stage) == "Y":
            # fmt: off
            adj_mat = Gf.Matrix4d(
                0.0, 0.0, 1.0, 0.0,
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 1.0)
            # fmt: on
        elif UsdGeom.GetStageUpAxis(stage) == "X":
            # fmt: off
            adj_mat = Gf.Matrix4d(
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                1.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 1.0)
            # fmt: on

        # Fix scale (e57 is in meters)
        scale = 1.0 / UsdGeom.GetStageMetersPerUnit(stage)
        adj_mat = adj_mat * Gf.Matrix4d().SetScale(scale)

        with omni.kit.undo.group():
            for prim_path in parent_prims:
                omni.kit.commands.execute("TransformPrim", path=prim_path, new_transform_matrix=adj_mat)

    def _post_import(self, parent_prims=None):
        if not parent_prims and self.progress_window:
            self.progress_window.hide()
            return

        if self._import_method == ImportMethod.STREAM:
            omni.kit.commands.execute("DeletePrims", paths=parent_prims)

            if self._convert_potree and self._potree_import:
                pointcloud_path, src_path = self._potree_import
                asyncio.ensure_future(
                    update_point_cloud_prim(src_path, RENDER_MODE[self._representation.value], pointcloud_path)
                )
            return

        stage = omni.usd.get_context().get_stage()
        paths = []
        for prim_path in parent_prims:
            xform_prim = stage.GetPrimAtPath(prim_path)
            if xform_prim is None:
                break
            if xform_prim.GetTypeName() == "Xform":
                for child in xform_prim.GetChildren():
                    if child.GetTypeName() == "Points":
                        path = child.GetPath().pathString
                        paths.append(path)
                    elif child.GetTypeName() == "Xform":
                        for xform_child in child.GetChildren():
                            if xform_child.GetTypeName() == "Points":
                                path = xform_child.GetPath().pathString
                                paths.append(path)

        # decide which renderer will be used for loaded point clouds
        assert self._import_method == ImportMethod.LOAD
        if self._renderer == E57_Renderer.INDEX:
            asyncio.ensure_future(run_index_renderer(paths))
        elif self._renderer == E57_Renderer.RTX:
            asyncio.ensure_future(run_rtx_renderer(paths))
        elif self._renderer == E57_Renderer.FLOW:
            asyncio.ensure_future(run_flow_renderer(paths))
