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

import carb.settings
import omni.kit.actions.core
import omni.kit.async_engine

from .orchestrator import Status, _Orchestrator, pause, preview, resume, run, step_async, stop


def toggle_capture_on_play():
    is_capture_on_play_set = carb.settings.get_settings().get_as_bool("/omni/replicator/captureOnPlay")
    carb.settings.get_settings().set("/omni/replicator/captureOnPlay", not is_capture_on_play_set)


def register_actions():
    action_registry = omni.kit.actions.core.get_action_registry()
    actions_tag = "Replicator Menu Actions"
    flags_tag = "Replicator Menu Flags"
    extension_id = "omni.replicator.core"

    action_registry.register_action(
        extension_id,
        "start",
        run,
        display_name="Replicator->Start",
        description="Run Replicator Scenario",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "resume",
        resume,
        display_name="Replicator->Resume",
        description="Run Replicator Scenario",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "stop",
        stop,
        display_name="Replicator->Stop",
        description="Stop Replicator Scenario",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "pause",
        pause,
        display_name="Replicator->Pause",
        description="Pause Replicator Scenario",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "step",
        lambda: omni.kit.async_engine.run_coroutine(step_async()),
        display_name="Replicator->Step",
        description="Step Replicator Scenario",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "preview",
        preview,
        display_name="Replicator->Preview",
        description="Preview Replicator Scenario",
        tag=actions_tag,
    )

    action_registry.register_action(
        extension_id,
        "capture_on_play",
        toggle_capture_on_play,
        display_name="Replicator->Capture On Play",
        description="Set Replicator writers to capture when timeline is playing",
        tag=flags_tag,
    )


def deregister_actions():
    extension_id = "omni.replicator.core"
    action_registry = omni.kit.actions.core.get_action_registry()
    action_registry.deregister_all_actions_for_extension(extension_id)


def create_menu():
    extension_id = "omni.replicator.core"
    menu = omni.kit.menu.utils
    orchestrator = _Orchestrator()
    menu_items = [
        menu.MenuItemDescription(
            name="Start", onclick_action=(extension_id, "start"), show_fn=lambda: orchestrator.status == Status.STOPPED
        ),
        menu.MenuItemDescription(
            name="Resume",
            onclick_action=(extension_id, "resume"),
            show_fn=lambda: orchestrator.status in [Status.PAUSED, Status.STEPPED, Status.STEPPING],
        ),
        menu.MenuItemDescription(
            name="Pause", onclick_action=(extension_id, "pause"), show_fn=lambda: orchestrator.status == Status.STARTED
        ),
        menu.MenuItemDescription(
            name="Starting...", enabled=False, show_fn=lambda: orchestrator.status == Status.STARTING
        ),
        menu.MenuItemDescription(
            name="Step",
            onclick_action=(extension_id, "step"),
            show_fn=lambda: orchestrator.status in [Status.STOPPED, Status.PAUSED, Status.STEPPED, Status.STEPPING],
        ),
        menu.MenuItemDescription(
            name="Stop",
            onclick_action=(extension_id, "stop"),
            show_fn=lambda: orchestrator.status in [Status.STARTED, Status.PAUSED, Status.STEPPED, Status.STEPPING],
        ),
        menu.MenuItemDescription(
            name="Stopping...", enabled=False, show_fn=lambda: orchestrator.status == Status.STOPPING
        ),
        menu.MenuItemDescription(
            name="Preview",
            onclick_action=(extension_id, "preview"),
            show_fn=lambda: orchestrator.status == Status.STOPPED,
        ),
        menu.MenuItemDescription(),  # Divider
        menu.MenuItemDescription(
            name="Capture On Play",
            onclick_action=(extension_id, "capture_on_play"),
            ticked_fn=lambda x="/omni/replicator/captureOnPlay": carb.settings.get_settings().get_as_bool(x),
        ),
    ]
    menu.add_menu_items(menu_items, "Replicator")
    return menu_items
