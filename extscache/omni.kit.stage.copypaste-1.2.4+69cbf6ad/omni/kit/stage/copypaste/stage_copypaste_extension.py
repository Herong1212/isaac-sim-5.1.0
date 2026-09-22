# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["StageCopypasteExtension"]

from typing import Optional
# from carb.input import KEYBOARD_MODIFIER_FLAG_CONTROL as CTRL
# from carb.input import KeyboardInput as Key
from pxr import Sdf

import carb
import omni.ext
import omni.kit.context_menu
import omni.usd
from omni.kit.actions.core import get_action_registry

# from .hotkey import Hotkey
from .prim_serializer import get_prim_as_text, text_to_stage

_HOTKEYS_EXT = "omni.kit.hotkeys.core"
_DEFAULT_HOTKEY_MAP = {
    "stage_copy": "CTRL+C",
    "stage_paste": "CTRL+V",
}


class StageCopypasteExtension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        self._ext_name = None
        self._stage_menu = None
        self._stage_context_menu_copy = None
        self._stage_context_menu_paste = None
        self._hotkey_extension_enabled_hook = None
        self._hotkey_extension_disabled_hook = None

    def on_startup(self, ext_id):
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

        self.register_actions(self._ext_name)
        self.register_hotkeys(self._ext_name)

        self._stage_menu = ext_manager.subscribe_to_extension_enable(
            on_enable_fn=lambda _: self._register_stage_menu(),
            on_disable_fn=lambda _: self._unregister_stage_menu(),
            ext_name="omni.kit.widget.stage",
            hook_name="omni.kit.stage.copypaste",
        )

    def on_shutdown(self):
        self._stage_menu = None
        self._stage_context_menu_copy = None
        self._stage_context_menu_paste = None

        self._hotkey_extension_enabled_hook = None
        self._hotkey_extension_disabled_hook = None

        self.deregister_hotkeys(self._ext_name)
        self.deregister_actions(self._ext_name)

    def register_actions(self, extension_id: str):
        action_registry = get_action_registry()
        actions_tag = "Stage Copy/Paste Actions"

        action_registry.register_action(
            extension_id,
            "stage_copy",
            self._on_copy,
            display_name="Copy",
            description="Copy objects in the stage",
            tag=actions_tag,
        )
        action_registry.register_action(
            extension_id,
            "stage_paste",
            self._on_paste,
            display_name="Paste",
            description="Paste objects in the stage",
            tag=actions_tag,
        )

    def deregister_actions(self, extension_id):
        action_registry = get_action_registry()
        action_registry.deregister_all_actions_for_extension(extension_id)

    def register_hotkeys(self, extension_id: str, window_name: Optional[str] = None):
        ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
        if not ext_manager.is_extension_enabled(_HOTKEYS_EXT):
            carb.log_info(f"{_HOTKEYS_EXT} is not enabled. Cannot register hotkeys.")
            return
        import omni.kit.hotkeys.core as hotkeys

        hotkey_registry = hotkeys.get_hotkey_registry()
        action_registry = get_action_registry()
        ext_actions = action_registry.get_all_actions_for_extension(extension_id)
        hotkey_filter = hotkeys.HotkeyFilter(windows=[window_name]) if window_name else None

        for action in ext_actions:
            key = _DEFAULT_HOTKEY_MAP.get(action.id, None)
            # Not all Actions will have default hotkeys
            if not key:
                continue

            hotkey_registry.register_hotkey(
                hotkey_ext_id=extension_id,
                key=key,
                action_ext_id=action.extension_id,
                action_id=action.id,
                filter=hotkey_filter,
            )

    def deregister_hotkeys(self, extension_id: str):
        ext_manager = omni.kit.app.get_app_interface().get_extension_manager()
        if not ext_manager.is_extension_enabled(_HOTKEYS_EXT):
            carb.log_info(f"{_HOTKEYS_EXT} is not enabled. No hotkeys to deregister.")
            return
        import omni.kit.hotkeys.core as hotkeys

        hotkey_registry = hotkeys.get_hotkey_registry()
        hotkey_registry.deregister_all_hotkeys_for_extension(extension_id)

    def _on_hotkey_ext_changed(self, ext_id: str, ext_change_type: omni.ext.ExtensionStateChangeType):
        if ext_change_type == omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_ENABLE:
            self.register_hotkeys(self._ext_name)

        if ext_change_type == omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_DISABLE:
            self.deregister_hotkeys(self._ext_name)

    def _on_copy(self):
        """Called when the user pressed Ctrl-C"""

        # Get the selected paths
        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()
        selection = usd_context.get_selection()
        paths = [Sdf.Path(name) for name in selection.get_selected_prim_paths()]

        prim_as_text = get_prim_as_text(stage, paths)

        if prim_as_text:
            omni.kit.clipboard.copy(prim_as_text)

    def _on_paste(self, keep_inputs=True, root=None, position=None, filter_fn=None):
        """Called when the user pressed Ctrl-V"""

        def get_root_prims(stage):
            """Get the root layer prims visible in the stage window"""
            all_roots = stage.GetPseudoRoot().GetChildren()
            return [p for p in all_roots if p.GetMetadata("hide_in_stage_window") is not True]

        text = omni.kit.clipboard.paste()
        if not text:
            # Silent return
            return

        usd_context = omni.usd.get_context()
        stage = usd_context.get_stage()

        if not root:
            # Pick the root. If we have the only root prim and it's the default
            # one, we need to paste in this prim. For example "/World".
            root = Sdf.Path.absoluteRootPath
            if len(get_root_prims(stage)) == 1:
                default_prim = stage.GetDefaultPrim()
                if default_prim:
                    root = default_prim.GetPath()

        if not text_to_stage(stage, text, root, keep_inputs=keep_inputs, position=position,
                             filter_fn=filter_fn):
            carb.log_warn("The clipboard doesn't have usda")

    def _register_stage_menu(self):
        """Called when "omni.kit.widget.stage" is loaded"""

        def on_copy(objects: dict):
            """Called from the context menu"""

            prims = objects.get("prim_list", None)
            stage = objects.get("stage", None)
            if not prims or not stage:
                return

            paths = [p.GetPath() for p in prims]
            prim_as_text = get_prim_as_text(stage, paths)

            if prim_as_text:
                omni.kit.clipboard.copy(prim_as_text)

        def on_paste(objects: dict):
            """Called from the context menu"""

            text = omni.kit.clipboard.paste()
            if not text:
                # Silent return
                return

            stage = objects.get("stage", None)
            if not stage:
                return

            prims = objects.get("prim_list", None)

            if not prims:
                root = Sdf.Path.absoluteRootPath
            elif len(prims) == 1:
                root = prims[0].GetPath()
            else:
                carb.log_warn("Can't paste to multiple locations")
                return

            if not text_to_stage(stage, text, root):
                carb.log_warn("The clipboard doesn't have usda")

        # Add context menu to omni.kit.widget.stage
        context_menu = omni.kit.context_menu.get_instance()
        if context_menu:
            menu = {
                "name": "Copy Prim",
                "glyph": "menu_link.svg",
                "show_fn": [context_menu.is_prim_selected],
                "onclick_fn": on_copy,
                "appear_after": "Copy Prim Path",
            }
            self._stage_context_menu_copy = omni.kit.context_menu.add_menu(menu, "MENU", "omni.kit.widget.stage")

            menu = {"name": "Paste Prim", "glyph": "menu_link.svg", "onclick_fn": on_paste, "appear_after": "Copy Prim"}
            self._stage_context_menu_paste = omni.kit.context_menu.add_menu(menu, "MENU", "omni.kit.widget.stage")

    def _unregister_stage_menu(self):
        """Called when "omni.kit.widget.stage" is unloaded"""

        self._stage_context_menu_copy = None
        self._stage_context_menu_paste = None
