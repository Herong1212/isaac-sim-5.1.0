# Copyright (c) 2020-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from __future__ import annotations

__all__ = ["Hotkey"]

from typing import Callable

from carb.eventdispatcher import get_eventdispatcher, Event
import carb.input
import carb.settings
import omni.appwindow
import omni.ext
import omni.kit.actions.core
import omni.kit.app


class Hotkey:
    """
    A helper class to add hotkey to a Toolbar widget.

    Hotkey registers an Action with `omni.kit.actions.core` and  assigns a hotkey using `omni.kit.hotkeys.core`.
    If `omni.kit.hotkeys.core` is not enabled, hotkey will not be in effect.
    """

    def __init__(
        self,
        action_name: str,
        hotkey: carb.input.KeyboardInput,
        on_action_fn: Callable[[], None],
        hotkey_enabled_fn: Callable[[], bool],
        modifiers: int = 0,
        on_hotkey_changed_fn: Callable[[str], None] = None,
    ):
        """
        Initialize a Hotkey object.

        Args:
            action_name (str): The Action name associated with the hotkey. It needs to be unique.
            hotkey (carb.input.KeyboardInput): The keyboard key binding.
            on_action_fn (Callable[[], None]): Callback function to be called when Action is triggered.
            hotkey_enabled_fn (Callable[[], bool]): Predicate callback function to be called when Action is triggered,
                                                    but before `on_action_fn` to determine if it should be called.
            modifiers (int): Modifier of the hotkey.
            on_hotkey_changed_fn (Callable[[str], None]): Callback function when Hotkey is reassigned by external system
                                                          such as `omni.kit.hotkeys.window`. The parameter will be the
                                                          new key combo.

        """
        self._action_registry = omni.kit.actions.core.get_action_registry()
        self._settings = carb.settings.get_settings()
        self._action_name = action_name
        self._hotkey = hotkey
        self._modifiers = modifiers
        self._on_hotkey_changed_fn = on_hotkey_changed_fn
        self._registered_hotkey = None
        self._manager = omni.kit.app.get_app().get_extension_manager()
        self._extension_name = omni.ext.get_extension_name(self._manager.get_extension_id_by_module(__name__))

        def action_trigger():
            if not hotkey_enabled_fn():
                return

            if on_action_fn:
                on_action_fn()

        # Register a test action that invokes a Python function.
        self._action = self._action_registry.register_action(
            self._extension_name,
            action_name,
            lambda *_: action_trigger(),
            display_name=action_name,
            tag="Toolbar",
        )

        self._hooks = self._manager.subscribe_to_extension_enable(
            lambda _: self._register_hotkey(),
            lambda _: self._unregister_hotkey(),
            ext_name="omni.kit.hotkeys.core",
            hook_name=f"toolbar hotkey {action_name} listener",
        )

    def __del__(self):
        self._hooks = None

    def clean(self):
        """
        Cleanup function to be called before Hotkey object is destroyed.
        """
        self._unregister_hotkey()
        self._action_registry.deregister_action(self._action)
        self._hooks = None
        self._on_hotkey_changed_fn = None

    def get_as_string(self, default: str) -> str:
        """
        Gets the string representation of the hotkey combo. Useful as tooltip.
        """
        if self._registered_hotkey:
            return self._registered_hotkey.key_text

        return default

    def _on_hotkey_changed(self, event: Event):
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
        try:
            from omni.kit.hotkeys.core import HOTKEY_CHANGED_GLOBAL_EVENT, KeyCombination, get_hotkey_registry

            self._hotkey_registry = get_hotkey_registry()

            hotkey_combo = KeyCombination(self._hotkey, self._modifiers)
            self._registered_hotkey = self._hotkey_registry.register_hotkey(
                self._extension_name, hotkey_combo, self._extension_name, self._action_name
            )

            self._change_event_sub = get_eventdispatcher().observe_event(
                event_name=HOTKEY_CHANGED_GLOBAL_EVENT, on_event=self._on_hotkey_changed
            )

        except ImportError:
            pass

    def _unregister_hotkey(self):
        if not self._registered_hotkey or not self._hotkey_registry:
            return

        try:
            self._hotkey_registry.deregister_hotkey(self._registered_hotkey)
            self._registered_hotkey = None
            self._change_event_sub = None

        except Exception:
            pass
