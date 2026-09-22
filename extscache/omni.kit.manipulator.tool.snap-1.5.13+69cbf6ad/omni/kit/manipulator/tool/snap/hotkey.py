# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from __future__ import annotations

from typing import Callable

from carb.eventdispatcher import get_eventdispatcher, Event
import carb.input
import omni.appwindow
import omni.kit.actions.core
import omni.kit.app


SNAP_ENABLED_SETTING = "/app/viewport/snapEnabled"


class SnapHotkey:
    """A class that handles the registration, use, and cleanup of a hotkey for toggling snappable manipulators.

    This class provides functionality to register a hotkey that toggles snapping for manipulators in a viewport. It supports fallback registration if the hotkey core extension is not available and ensures that resources are cleaned up appropriately.

    Args:
        on_hotkey_changed_fn (Callable[[str], None], optional): Callback triggered when the hotkey state changes."""

    def __init__(
        self,
        on_hotkey_changed_fn: Callable[[str], None] = None,
    ):
        """Initializes the SnapHotkey instance.

        Args:
            on_hotkey_changed_fn (Callable[[str], None], optional): A callback function that will be called when the hotkey changes.
        """
        self._action_registry = omni.kit.actions.core.get_action_registry()
        self._input = carb.input.acquire_input_interface()
        self._settings = carb.settings.get_settings()
        self._on_hotkey_changed_fn = on_hotkey_changed_fn
        self._registered_hotkey = None
        self._manager = omni.kit.app.get_app().get_extension_manager()
        self._extension_name = omni.ext.get_extension_name(self._manager.get_extension_id_by_module(__name__))
        self._hotkey = carb.input.KeyboardInput.S

        def action_trigger():
            # when RMB is down, it's likely viewport WASD navigation is going on, and don't trigger it if S is pressed
            if self._input.get_mouse_value(None, carb.input.MouseInput.RIGHT_BUTTON) == 0:
                self._settings.set(SNAP_ENABLED_SETTING, not self._settings.get(SNAP_ENABLED_SETTING))

        self._action_name = "manipulator:snap"

        # Register a test action that invokes a Python function.
        self._action = self._action_registry.register_action(
            self._extension_name,
            self._action_name,
            lambda *_: action_trigger(),
            display_name="Manipulator Snap",
            tag="manipulator",
        )

        # for the fallback
        self._input_sub = None
        if not self._manager.is_extension_enabled("omni.kit.hotkeys.core"):
            self._register_hotkey_fallback()

        self._hooks = self._manager.subscribe_to_extension_enable(
            lambda _: self._register_hotkey(),
            lambda _: self._unregister_hotkey(),
            ext_name="omni.kit.hotkeys.core",
            hook_name=f"hotkey {self._action_name} listener",
        )

    def destroy(self):
        """Cleans up the snap hotkey by unregistering the hotkey, deregistering the action, and
        releasing other resources."""
        self._unregister_hotkey()
        self._unregister_hotkey_fallback()
        self._action_registry.deregister_action(self._action)
        self._hooks = None
        self._on_hotkey_changed_fn = None

    def get_as_string(self, default: str):
        """Gets the currently registered hotkey as a string representation.

        Args:
            default (str): The default string to return if no hotkey is registered.

        Returns:
            str: The registered hotkey as a string, or the default string if no hotkey is registered."""
        if self._registered_hotkey:
            return self._registered_hotkey.key_text

        return default

    def _on_hotkey_changed(self, event: Event):
        """Internal callback function that is invoked when the hotkey is changed.

        Args:
            event (carb.eventdispatcher.Event): The event containing the hotkey change information."""
        from omni.kit.hotkeys.core import KeyCombination

        if (
            event["hotkey_ext_id"] == self._extension_name
            and event["action_ext_id"] == self._extension_name
            and event["action_id"] == self._action_name
        ):
            new_key = event["key"]

            # refresh _registered_hotkey with newly registered key?
            hotkey_combo = KeyCombination(new_key)
            self._registered_hotkey = self._hotkey_registry.get_hotkey(self._extension_name, hotkey_combo)

            if self._on_hotkey_changed_fn:
                self._on_hotkey_changed_fn(new_key)

    def _register_hotkey(self):
        """Registers the hotkey using the hotkey core extension if it's available, otherwise,
        it falls back to a manual registration method."""
        try:
            from omni.kit.hotkeys.core import HOTKEY_CHANGED_GLOBAL_EVENT, KeyCombination, get_hotkey_registry

            self._hotkey_registry = get_hotkey_registry()

            hotkey_combo = KeyCombination(self._hotkey)
            self._registered_hotkey = self._hotkey_registry.register_hotkey(
                self._extension_name, hotkey_combo, self._extension_name, self._action_name
            )

            self._change_event_sub = get_eventdispatcher().observe_event(
                event_name=HOTKEY_CHANGED_GLOBAL_EVENT, on_event=self._on_hotkey_changed
            )

            self._unregister_hotkey_fallback()

        except ImportError:
            pass

    def _unregister_hotkey(self):
        """Unregisters the hotkey and falls back to a manual registration method if necessary.

        It also cleans up any subscriptions and references related to hotkey registration."""
        self._register_hotkey_fallback()

        if not self._registered_hotkey or not self._hotkey_registry:
            return

        try:
            self._hotkey_registry.deregister_hotkey(self._registered_hotkey)
            self._registered_hotkey = None
            self._change_event_sub = None

        except Exception:
            pass

    def _register_hotkey_fallback(self):
        """Registers a fallback hotkey manually in case the hotkey core extension is not enabled."""
        if self._input_sub:
            return

        try:
            appwindow = omni.appwindow.get_default_app_window()
            action_mapping_set_path = appwindow.get_action_mapping_set_path()
            action_mapping_set = self._input.get_action_mapping_set_by_path(action_mapping_set_path)

            input_string = carb.input.get_string_from_action_mapping_desc(self._hotkey, 0)
            input_path = action_mapping_set_path + "/" + self._action_name + "/0"
            self._settings.set_default_string(input_path, input_string)

            def on_input_action(evt):
                if not evt.flags & carb.input.BUTTON_FLAG_PRESSED:
                    return

                self._action.execute()

            self._input_sub = self._input.subscribe_to_action_events(
                action_mapping_set, self._action_name, on_input_action
            )
        except Exception:
            pass

    def _unregister_hotkey_fallback(self):
        """Unregisters the fallback hotkey and cleans up any related resources."""
        if self._input_sub:
            self._input.unsubscribe_to_action_events(self._input_sub)
            self._input_sub = None
