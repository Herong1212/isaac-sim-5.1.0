# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import gc
import os

import carb
import carb.events
import omni.kit.ui
import omni.replicator.core as rep
import omni.timeline
import omni.ui as ui
from omni.kit.menu.utils import MenuItemDescription, MenuItemOrder
from omni.replicator.core import orchestrator

from .parser import parse

WINDOW_NAME = "Replicator YAML"
MENU_PATH = f"Replicator/{WINDOW_NAME}"
DEFAULT_YAML_PATH = "python/scripts/data/parameters/profiles/warehouse.yaml"


class ReplicatorYAMLExtension(omni.ext.IExt):
    def on_startup(self, ext_id: str):
        """Caled to load the extension"""

        self._ext_id = ext_id
        window_visible = False
        self._window = ui.Window(WINDOW_NAME, dockPreference=ui.DockPreference.RIGHT_BOTTOM, visible=window_visible)
        self._window.deferred_dock_in("Property", omni.ui.DockPolicy.DO_NOTHING)

        action_registry = omni.kit.actions.core.get_action_registry()
        actions_tag = "Replicator YAML Menu Actions"
        flags_tag = "Replicator YAML Menu Flags"
        extension_id = "omni.replicator.replicator_yaml"
        action_registry.register_action(
            extension_id,
            "toggle_replicator_yaml_menu",
            self._menu_callback,
            display_name="Toggle Replicator YAML menu",
            description="Toggle Replicator YAML menu",
            tag=flags_tag,
        )
        self._menu_items = [
            MenuItemDescription(appear_after=[MenuItemOrder.LAST]),
            MenuItemDescription(
                name=WINDOW_NAME,
                ticked=True,
                ticked_fn=self._is_visible,
                onclick_action=(extension_id, "toggle_replicator_yaml_menu"),
                appear_after=[MenuItemOrder.LAST],
            ),
        ]
        omni.kit.menu.utils.add_menu_items(self._menu_items, "Replicator")
        omni.kit.menu.utils.refresh_menu_items("Replicator")
        self._window.set_visibility_changed_fn(self._visibility_changed_fn)

        self._orchestrator_status = None
        self._in_running_state = False

        # Orchestrator status update callback
        self._orchestrator_status_cb = rep.orchestrator.register_status_callback(self._on_orchestrator_status_changed)

        # Stage event callback
        self._stage_closing_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.usd.get_context().stage_event_name(omni.usd.StageEventType.CLOSING),
            on_event=self._on_stage_closing,
            observer_name="omni.replicator.replicator_yaml:stage_closing",
        )

        # Editor quit callback
        self._sub_shutdown = (
            omni.kit.app.get_app()
            .get_shutdown_event_stream()
            .create_subscription_to_pop_by_type(
                omni.kit.app.POST_QUIT_EVENT_TYPE,
                self._on_editor_quit_event,
                name="omni.replicator.replicator_yaml::shutdown_callback",
                order=0,
            )
        )
        self._shutdown_sub = carb.eventdispatcher.get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_POST_QUIT,
            on_event=self._on_editor_quit_event,
            observer_name="omni.replicator.replicator_yaml::shutdown_callback",
        )

        # ReplicatorYAML
        self._composer = None
        self._scene_frame_collapsed = False
        self._control_frame_collapsed = False
        self._load_button = None
        self._start_stop_button = None
        self._pause_resume_button = None
        self._preview_button = None
        self._step_button = None

        self._input_path = DEFAULT_YAML_PATH
        self._root_path = os.path.dirname(
            os.path.abspath(os.path.join(os.path.realpath(os.path.expanduser(__file__)), "../.."))
        )
        self._nucleus_server = "ov-isaac-dev.nvidia.com"

        # Build the window ui
        self._build_window_ui()

        # Autorun
        omni.kit.async_engine.run_coroutine(self._autorun())

    @staticmethod
    async def _autorun(exit_on_complete=True):
        # Wait for the stage to be ready
        while not omni.kit.app.get_app().is_app_ready() or not omni.usd.get_context().get_stage():
            await omni.kit.app.get_app().next_update_async()

        carb_settings = carb.settings.get_settings()
        yaml_path = carb_settings.get("/omni/replicator/replicatorYaml/yamlPath")
        nucleus_server = carb_settings.get("/omni/replicator/replicatorYaml/nucleusServer")
        root_dir = carb_settings.get("/omni/replicator/replicatorYaml/rootDir")
        script_path = carb_settings.get("/omni/replicator/script")

        # Support both `/omni/replicator/replicatorYaml/yamlPath` setting
        # and general `/omni/replicator/script` setting
        yaml_script = None
        if yaml_path:
            yaml_script = yaml_path
        elif str(script_path).lower().endswith(".yaml") or str(script_path).lower().endswith(".yml"):
            yaml_script = script_path

        if yaml_script:
            if not os.path.exists(yaml_script):
                carb.log_error(f"Yaml file not found at {yaml_script}")
                raise FileNotFoundError(f"Yaml file not found at {yaml_script}")

            carb.log_info(f"Running ReplicatorYaml for {yaml_script}")

            # Catch if parse for yaml fail.
            try:
                parse(yaml_script, root_dir=root_dir, nucleus_server=nucleus_server)
            except Exception as e:
                carb.log_error(f"Parse failed for '{yaml_script}'.\n{e}")
                carb.settings.get_settings().set("/app/file/ignoreUnsavedOnExit", True)
                omni.kit.app.get_app().post_quit()

            await rep.orchestrator.run_until_complete_async()

            if exit_on_complete:
                carb.settings.get_settings().set("/app/file/ignoreUnsavedOnExit", True)
                omni.kit.app.get_app().post_quit()

    def _menu_callback(self):
        self._window.visible = not self._window.visible
        return self._window.visible

    def _visibility_changed_fn(self, visible):
        omni.kit.menu.utils.refresh_menu_items("Replicator")

    def _is_visible(self):
        return self._window.visible if self._window else False

    def _on_orchestrator_status_changed(self, status):
        new_status = status is not self._orchestrator_status
        if new_status:
            self._orchestrator_status = status
            # Check if replicator_yaml was running and it stopped because it reached the number of requested frames
            has_finished_recording = self._in_running_state and status is rep.orchestrator.Status.STOPPED
            if has_finished_recording:
                self._disable_all_buttons()
                self._enable_buttons(case="stop")
                self._in_running_state = False

    def _on_stage_closing(self, e):
        self._disable_all_buttons()
        if self._orchestrator_status is not orchestrator.Status.STOPPED:
            rep.orchestrator.stop()
        self._composer = None
        self._enable_buttons(case="reset")

    def _on_editor_quit_event(self, e: carb.events.IEvent):
        if self._orchestrator_status is not orchestrator.Status.STOPPED:
            rep.orchestrator.stop()

    def on_shutdown(self):
        if self._orchestrator_status is not orchestrator.Status.STOPPED:
            rep.orchestrator.stop()
        if self._stage_closing_sub is not None:
            self._stage_closing_sub.reset()
        self._orchestrator_status_cb.unregister()

        omni.kit.menu.utils.remove_menu_items(menu=self._menu_items, name="Replicator")
        self._menu = None
        self._window = None
        self._composer = None
        gc.collect()

    def _disable_all_buttons(self):
        self._load_button.enabled = False
        self._start_stop_button.enabled = False
        self._pause_resume_button.enabled = False
        self._step_button.enabled = False
        self._preview_button.enabled = False

    def _enable_buttons(self, case="reset"):
        if case == "reset":
            self._load_button.enabled = True
            self._start_stop_button.enabled = True
            self._step_button.enabled = True
            self._preview_button.enabled = True
            self._start_stop_button.text = "Start"
            self._pause_resume_button.text = "Pause"
        elif case == "start":
            self._start_stop_button.text = "Stop"
            self._start_stop_button.enabled = True
            self._pause_resume_button.enabled = True
        elif case == "stop":
            self._start_stop_button.text = "Start"
            self._pause_resume_button.text = "Pause"
            self._start_stop_button.enabled = True
            self._step_button.enabled = True
            self._preview_button.enabled = True

    def _load_scene(self):
        self._load_button.enabled = False
        if self._composer is not None:
            print("There is already a replicator_yaml scene loaded. Overwriting existing one.")
        try:
            parse(
                yaml_path=self._input_path,
                root_dir=self._root_path,
                nucleus_server=self._nucleus_server,
            )
        except Exception as e:
            print(f"Error loading replicator_yaml scene: {e}")
            self._composer = None
        finally:
            self._load_button.enabled = True

    async def _start_stop_async(self):
        if self._composer is None:
            print("No replicator_yaml scene is loaded")
            return
        if self._orchestrator_status is orchestrator.Status.STOPPED:
            self._disable_all_buttons()
            await rep.orchestrator.run_async()
            self._in_running_state = True
            self._enable_buttons(case="start")
        elif self._orchestrator_status in [orchestrator.Status.STARTED, orchestrator.Status.PAUSED]:
            self._disable_all_buttons()
            await rep.orchestrator.stop_async()
            self._in_running_state = False
            self._enable_buttons(case="stop")
        else:
            carb.log_warn(
                f"Replicator's current state({self._orchestrator_status.name}) is different state than STOPPED, STARTED or PAUSED. Try again in a bit."
            )

    def _pause_resume(self):
        self._pause_resume_button.enabled = False
        if self._orchestrator_status is orchestrator.Status.STARTED:
            rep.orchestrator.pause()
            self._pause_resume_button.text = "Resume"
        elif self._orchestrator_status is orchestrator.Status.PAUSED:
            rep.orchestrator.resume()
            self._pause_resume_button.text = "Pause"
        else:
            carb.log_warn(
                f"Replicator's current state ({self._orchestrator_status.name}) is different state than STARTED or PAUSED. Try again in a bit."
            )
        self._pause_resume_button.enabled = True

    async def _step_async(self):
        if self._composer is None:
            print("No replicator_yaml scene is loaded")
            return
        await rep.orchestrator.step_async()

    async def _preview_async(self):
        if self._composer is None:
            print("No replicator_yaml scene is loaded")
            return
        await rep.orchestrator.preview_async()

    def _build_composer_scene_ui(self):
        with ui.VStack(spacing=5):
            with ui.HStack(spacing=5):
                ui.Spacer(width=10)
                ui.Label("Input path", tooltip="Path to the yaml file (relative to workspace or absolute)")
                input_path_model = ui.StringField().model
                input_path_model.set_value(self._input_path)

                def input_path_changed(m):
                    self._input_path = m.as_string

                input_path_model.add_value_changed_fn(input_path_changed)

            with ui.HStack(spacing=5):
                ui.Spacer(width=10)
                ui.Label("Root path", tooltip="Used for relative paths (e.g. path/to/file)")
                root_path_model = ui.StringField().model
                root_path_model.set_value(self._root_path)

                def root_path_changed(m):
                    self._root_path = m.as_string

                root_path_model.add_value_changed_fn(root_path_changed)

            with ui.HStack(spacing=5):
                ui.Spacer(width=10)
                ui.Label("Nucleus (omniverse://)", tooltip="If empty it will default to localhost")
                nucleus_server_model = ui.StringField().model
                nucleus_server_model.set_value(self._nucleus_server)

                def nucleus_server_changed(m):
                    self._nucleus_server = m.as_string

                nucleus_server_model.add_value_changed_fn(nucleus_server_changed)

            with ui.HStack(spacing=5):
                self._load_button = ui.Button(
                    "Load", clicked_fn=self._load_scene, enabled=True, tooltip="Load replicator_yaml scene"
                )
            ui.Spacer(height=2)

    def _build_composer_control_ui(self):
        with ui.HStack(spacing=5):
            self._start_stop_button = ui.Button(
                "Start",
                clicked_fn=lambda: omni.kit.async_engine.run_coroutine(self._start_stop_async()),
                enabled=True,
                tooltip="Start/stop replicator_yaml recording",
            )
            self._pause_resume_button = ui.Button(
                "Pause", clicked_fn=self._pause_resume, enabled=False, tooltip="Pause/resume replicator_yaml recording"
            )
            self._step_button = ui.Button(
                "Step",
                clicked_fn=lambda: omni.kit.async_engine.run_coroutine(self._step_async()),
                enabled=True,
                tooltip="Step a replicator_yaml recording",
            )
            self._preview_button = ui.Button(
                "Preview",
                clicked_fn=lambda: omni.kit.async_engine.run_coroutine(self._preview_async()),
                enabled=True,
                tooltip="Preview a randomization",
            )

    def _build_composer_ui(self):
        with ui.VStack(spacing=5):
            composer_scene_frame = ui.CollapsableFrame("Scene", height=0, collapsed=self._scene_frame_collapsed)
            with composer_scene_frame:

                def on_collapsed_changed(collapsed):
                    self._scene_frame_collapsed = collapsed

                composer_scene_frame.set_collapsed_changed_fn(on_collapsed_changed)
                self._build_composer_scene_ui()

            composer_control_frame = ui.CollapsableFrame("Control", height=0, collapsed=self._scene_frame_collapsed)
            with composer_control_frame:

                def on_collapsed_changed(collapsed):
                    self._control_frame_collapsed = collapsed

                composer_control_frame.set_collapsed_changed_fn(on_collapsed_changed)
                self._build_composer_control_ui()

    def _build_window_ui(self):
        with self._window.frame:
            with ui.ScrollingFrame():
                self._build_composer_ui()
