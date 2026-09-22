# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ViewportActionsExtension", "get_instance"]

from .actions import register_actions, deregister_actions
from .hotkeys import register_hotkeys, deregister_hotkeys
import omni.ext
import omni.kit.app
from carb.eventdispatcher import get_eventdispatcher

from typing import Callable

_extension_instance = None


def get_instance():
    global _extension_instance
    return _extension_instance


class ViewportActionsExtension(omni.ext.IExt):
    """Actions and Hotkeys related to the Viewport"""
    def __init__(self):
        super().__init__()
        self._ext_name = None
        self._hotkey_extension_enabled_hook = None
        self._hotkey_extension_disabled_hook = None

    def on_startup(self, ext_id):
        global _extension_instance
        _extension_instance = self

        self._ext_name = omni.ext.get_extension_name(ext_id)

        # Hooks to hotkey extension enable/disable
        app = omni.kit.app.get_app_interface()
        ext_manager = app.get_extension_manager()
        hooks: omni.ext.IExtensionManagerHooks = ext_manager.get_hooks()

        self._hotkey_extension_enabled_hook = hooks.create_extension_state_change_hook(
            self._on_hotkey_ext_changed,
            omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_ENABLE,
            ext_name="omni.kit.hotkeys.core",
        )
        self._hotkey_extension_disabled_hook = hooks.create_extension_state_change_hook(
            self._on_hotkey_ext_changed,
            omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_DISABLE,
            ext_name="omni.kit.hotkeys.core",
        )

        register_actions(self._ext_name)
        register_hotkeys(self._ext_name)

    def on_shutdown(self):
        global _extension_instance
        _extension_instance = None

        self._hotkey_extension_enabled_hook = None
        self._hotkey_extension_disabled_hook = None

        deregister_hotkeys(self._ext_name)
        deregister_actions(self._ext_name)

        self._ext_name = None
        del ViewportActionsExtension.__g_usd_context_streams

    def _on_hotkey_ext_changed(self, ext_id: str, ext_change_type: omni.ext.ExtensionStateChangeType):
        if ext_change_type == omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_ENABLE:
            register_hotkeys(self._ext_name)

        if ext_change_type == omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_DISABLE:
            deregister_hotkeys(self._ext_name)


    __g_usd_context_streams = None

    @staticmethod
    def _watch_stage_open(usd_context_name: str, open_callback: Callable):
        if ViewportActionsExtension.__g_usd_context_streams is None:
            ViewportActionsExtension.__g_usd_context_streams = {}

        sub_id = ViewportActionsExtension.__g_usd_context_streams.get(usd_context_name, None)
        if sub_id is not None:
            return

        import omni.usd
        context = omni.usd.get_context(usd_context_name)
        def on_opened(_):
            stage = context.get_stage()
            if stage:
                open_callback(usd_context_name, stage)

        ViewportActionsExtension.__g_usd_context_streams[usd_context_name] = (
            get_eventdispatcher().observe_event(
                observer_name="omni.kit.viewport.actions:extension",
                event_name=context.stage_event_name(omni.usd.StageEventType.OPENED),
                on_event=on_opened
            )
        )
