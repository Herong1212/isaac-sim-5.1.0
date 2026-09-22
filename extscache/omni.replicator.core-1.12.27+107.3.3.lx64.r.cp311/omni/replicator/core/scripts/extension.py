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

import importlib
import os
import sys
import time
from pathlib import Path
from typing import List

import carb
import carb.eventdispatcher
import carb.settings
import omni.ext
import omni.kit
import omni.kit.async_engine
import toml
import warp as wp

from ..bindings._omni_replicator_core import Schema_omni_replicator_extinfo_1_0, acquire_interface, release_interface
from .orchestrator import Status, _Orchestrator, run_until_complete_async
from .orchestrator_actions import create_menu, deregister_actions, register_actions
from .utils import utils
from .utils import viewport_manager as vp_manager
from .utils.annotator_utils import AnnotatorCache
from .writers import WriterRegistry

EXTENSION_NAME = "Omni Replicator"
SETTING_SCRIPT = "/omni/replicator/script"
_EXTENSION = None


def registered_event_name(event_name):
    """Returns the internal name used for the given custom event name"""
    name = "omni.replicator.core." + event_name
    return carb.events.type_from_string(name)


def _modify_material_toml(material_config_file: str, mdl_folder: str, mdl_files: List[str]):
    config_file = Path(material_config_file)
    is_modified = False

    # Load the existing TOML file
    with open(config_file, "r", encoding="utf-8") as file:
        data = toml.load(file)

    # Append the new custom path to the searchPaths.custom list
    if "searchPaths" in data and "custom" in data["searchPaths"]:
        if mdl_folder not in data["searchPaths"]["custom"]:
            data["searchPaths"]["custom"].append(mdl_folder)
            is_modified = True
    else:
        data["searchPaths"] = {"custom": [mdl_folder]}
        is_modified = True

    # Append the new values to the materialGraph.userAllowList
    if "materialGraph" in data and "userAllowList" in data["materialGraph"]:
        for mdl in mdl_files:
            if mdl not in data["materialGraph"]["userAllowList"]:
                data["materialGraph"]["userAllowList"].append(mdl)
                is_modified = True
    else:
        data["materialGraph"] = {"userAllowList": mdl_files}
        is_modified = True

    # Save the updated data back to the TOML file
    if is_modified:
        with open(config_file, "w", encoding="utf-8") as file:
            toml.dump(data, file, encoding="utf-8")
        carb.log_warn("Material config file modified! Relaunch the app to apply changes!")
        carb.log_warn(f"Material config file location: {config_file}")


def _modify_material_settings(mdl_folder: str, mdl_files: List[str]):
    settings = carb.settings.get_settings()

    material_config = settings.get("/materialConfig") or {}

    carb.log_warn("No material configuration file, adding configuration to material settings directly.")

    material_config.setdefault("searchPaths", {})
    # also add graph user allow list
    material_config.setdefault("materialGraph", {})

    material_graph_config = material_config["materialGraph"]
    material_graph_config.setdefault("userAllowList", [])
    user_allow_list = material_graph_config["userAllowList"]
    if isinstance(user_allow_list, tuple):
        user_allow_list = list(user_allow_list)
    # allow mdl files here
    for mdl in mdl_files:
        if mdl not in user_allow_list:
            user_allow_list.append(mdl)

    material_graph_config["userAllowList"] = user_allow_list

    material_config["searchPaths"].setdefault("custom", [])
    custom_paths = material_config["searchPaths"]["custom"]
    if isinstance(custom_paths, tuple):
        custom_paths = list(custom_paths)

    if mdl_folder not in custom_paths:
        custom_paths.append(mdl_folder)

    material_config["searchPaths"]["custom"] = list(custom_paths)

    # now set options
    material_config.setdefault("options", {})

    material_config["options"]["noStandardPath"] = False

    carb.log_info(f"materialConfig: {material_config}")
    settings.set("/materialConfig", material_config)


def _add_ext_mdl_folder_to_material_config(mdl_folder: str, mdl_files: List[str]):
    settings = carb.settings.get_settings()

    material_config = settings.get("/materialConfig") or {}
    config_file_path = settings.get("/materialConfig/configFilePath") or ""

    if material_config and Path(config_file_path).is_file() and Path(config_file_path).suffix == ".toml":
        _modify_material_toml(config_file_path, mdl_folder, mdl_files)
    else:
        _modify_material_settings(mdl_folder, mdl_files)

    # this is to make sure neuraylib see the path too
    current_sps = settings.get("/app/mdl/additionalUserPaths") or []
    if mdl_folder not in current_sps:
        current_sps.append(mdl_folder)
    settings.set_string_array("/app/mdl/additionalUserPaths", current_sps)


class Extension(omni.ext.IExt):
    _frame_start = -1
    _frame_stop = -1
    _menu_state_start = True
    _menu_items = []

    def __init__(self):
        super().__init__()
        global _EXTENSION
        _EXTENSION = self
        self.orchestrator = _Orchestrator()
        self._refresh_menu = True
        wp.init()  # required as of warp 1.1.1

    def on_startup(self, ext_id):
        # ignore import outside toplevel due to Kit startup timing
        from .annotators_default import register_annotators  # noqa: PLC0415
        from .augmentations_default import register_augmentations  # noqa: PLC0415
        from .backends import register_backends  # noqa: PLC0415
        from .writers_default import register_writers  # noqa: PLC0415

        carb.log_info("[omni.syntheticdata] SyntheticData startup")
        start = time.time()
        self._telemetry = Schema_omni_replicator_extinfo_1_0()
        self.__interface = acquire_interface()

        self._observers = [
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                order=0,
                event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
                on_event=self._on_main_thread_update,
                observer_name="omni.replicator.core.extension:update",
            ),
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.CLOSING),
                on_event=self._on_stage_closing,
                observer_name="omni.replicator.core.extension:stage_closing",
            ),
            carb.eventdispatcher.get_eventdispatcher().observe_event(
                event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.CLOSED),
                on_event=self._on_stage_closed,
                observer_name="omni.replicator.core.extension:stage_closed",
            ),
        ]

        self.set_default_settings()
        self._settings = carb.settings.get_settings()
        self._settings.set("/rtx/materialDb/syncLoads", True)
        self._settings.set("/omni.kit.plugin/syncUsdLoads", True)
        self._settings.set("/rtx/hydra/materialSyncLoads", True)

        # Add MDL folder to material library
        manager = omni.kit.app.get_app().get_extension_manager()
        ext_path = manager.get_extension_path(ext_id)
        ext_id = manager.get_extension_id_by_module("omni.replicator.core")
        ext_settings = manager.get_extension_dict(ext_id)
        mdl_folder = str(Path(ext_path).joinpath("mdl").as_posix())
        mdl_files = [file.stem for file in Path(mdl_folder).glob("*.mdl")]
        _add_ext_mdl_folder_to_material_config(mdl_folder, mdl_files)

        # Add Replicator snippets folder
        rep_snippets_folder = str(Path(ext_path).joinpath("snippets").as_posix())

        snippets_folders = self._settings.get("/exts/omni.kit.window.script_editor/snippetFolders") or []
        if rep_snippets_folder not in snippets_folders:
            snippets_folders.append(rep_snippets_folder)
        self._settings.set_string_array("/exts/omni.kit.window.script_editor/snippetFolders", snippets_folders)

        script_path = self._settings.get(SETTING_SCRIPT)
        if str(script_path).lower().endswith(".py"):
            omni.kit.async_engine.run_coroutine(self.run_script_async(script_path))

        self.__setting_subs = [
            carb.settings.get_settings().subscribe_to_node_change_events(
                "/omni/replicator/captureOnPlay", self._on_capture_on_play_change
            ),
        ]
        # Catch current `captureOnPlay` setting state
        self._on_capture_on_play_change()

        register_actions()
        # Accessing protected members here is intentional within the same package
        self.orchestrator._register_status_callback(self._on_status_changed)  # noqa: PLW0212
        self.orchestrator._setup_subscribers()  # noqa: PLW0212
        self._menu_items = []
        # Create menus using asyncio to decrease startup time (+ ~120 ms)
        omni.kit.async_engine.run_coroutine(self._create_menu_async())

        end = time.time()

        self._telemetry.startup_sendEvent(
            ext_settings["package/version"],
            omni.kit.app.get_app().get_app_name(),
            omni.kit.app.get_app().get_app_version(),
            end - start,
        )

        # Register default capabilities
        register_annotators()
        register_augmentations()
        register_backends()
        register_writers()

    def on_shutdown(self):
        # Unsubscribe observers
        for observer in self._observers:
            observer.reset()
        global _EXTENSION
        _EXTENSION = None
        for setting_sub in self.__setting_subs:
            carb.settings.get_settings().unsubscribe_to_change_events(setting_sub)
        # Accessing a protected member is intentional within package scope
        self.orchestrator._unregister_status_callback(self._on_status_changed)  # noqa: PLW0212
        vp_manager.destroy_hydra_textures()
        self.orchestrator.shutdown()
        release_interface(self.__interface)
        self.__interface = None
        self._destroy_menu()
        deregister_actions()
        # Reset internal caches; accessing protected methods intentionally
        WriterRegistry._reset()  # noqa: PLW0212
        utils.ReplicatorItem._reset()  # noqa: PLW0212

    async def _create_menu_async(self):
        self._menu_items = create_menu()

    async def run_script_async(self, script_path, exit_on_complete=True):
        # 100 frame delay to allow app to set itself up (FIX for OV Code startup behaviour)
        if not os.path.exists(script_path):
            raise ValueError(f"Script file not found at {script_path}")

        for _ in range(100):
            await omni.kit.app.get_app().next_update_async()

        script_name, ext = os.path.splitext(os.path.split(script_path)[-1])

        is_path_valid = os.path.exists(script_path) or not os.path.isfile(script_path)
        is_python_file = ext == ".py"
        if not is_path_valid or not is_python_file:
            raise ValueError(f"Script path {script_path} is not a valid Python file.")

        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()

        utils.get_graph()
        await omni.kit.app.get_app().next_update_async()

        spec = importlib.util.spec_from_file_location(script_name, script_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[script_name] = module
        spec.loader.exec_module(module)

        await run_until_complete_async()

        if exit_on_complete:
            carb.settings.get_settings().set("/app/file/ignoreUnsavedOnExit", True)
            omni.kit.app.get_app().post_quit()

    def _on_stage_closing(self, event):
        self.orchestrator.reset()
        WriterRegistry._reset()  # noqa: PLW0212
        utils.ReplicatorItem._reset()  # noqa: PLW0212
        AnnotatorCache.clear()

    def _on_stage_closed(self, event):
        vp_manager.destroy_hydra_textures()

    def _on_main_thread_update(self, event):
        # og.Controller().evaluate_sync() # FIXME: Remove once OM-87854 is addressed
        if self._refresh_menu:
            omni.kit.menu.utils.refresh_menu_items("Replicator")
            self._refresh_menu = False

    def _on_capture_on_play_change(self, *args):
        omni.kit.menu.utils.refresh_menu_items("Replicator")

    def _destroy_menu(self):
        omni.kit.menu.utils.remove_menu_items(menu=self._menu_items, name="Replicator")
        self._menu_items = []

    def _on_status_changed(self, status):
        if status not in [Status.STEPPED, Status.STEPPING]:
            self._refresh_menu = True

    def get_name(self):
        return EXTENSION_NAME

    def set_default_settings(self):
        settings = carb.settings.get_settings()
        settings.set_default_bool("/exts/omni.replicator.core/Orchestrator/enabled", True)
        settings.set_default_bool("/exts/omni.replicator.core/Orchestrator/enableEvalTriggers", False)


def get_extension():
    return _EXTENSION
