# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import carb
import omni.ext
import omni.kit.app
import omni.kit.commands
import omni.kit.context_menu
import omni.anim.skelJoint
from .anim_preview_model import AnimPreviewModel
from .anim_preview_window import AnimPreviewWindow
from .preference import build_preview_preferences
from omni.kit.preferences.animation import AnimationPreferences
from .utils import WeakMethod
from . import command

from contextlib import suppress
from functools import partial

__all__ = ['StagePreviewExtension', 'get_preview_window']

WINDOW_NAME = 'Animation Preview'
PREFERENCE_PREVIEW_FRAME = 'Preview'

_extension = None


omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate("omni.kit.widget.searchable_combobox", True)


class StagePreviewExtension(omni.ext.IExt):
    def on_startup(self, this_ext_id):
        global _extension
        _extension = self

        self._context_index:int = 0

        self._preview_context_name:str = f'{this_ext_id} Preview Context'

        self._reg_cmds = omni.kit.commands.register_all_commands_in_module(command)

        self._preview_window:AnimPreviewWindow = None
        self._create_preview_window()

        # editor_menu = omni.kit.ui.get_editor_menu()
        # if editor_menu:
        #     self._menu = editor_menu.add_item(CURVE_EDITOR_MENU_PATH, self._on_click_menu, toggle=True, value=True)
        self._usd_context = omni.usd.get_context()
        events = self._usd_context.get_stage_event_stream()
        self._stage_event_sub = events.create_subscription_to_pop(
            WeakMethod(self._on_stage_event), name="anim preview stage event"
        )
        self._register_menu()
        AnimationPreferences.register_preferences_frame(PREFERENCE_PREVIEW_FRAME, build_preview_preferences)

    def _create_preview_window(self):
        if self._preview_window:
            with suppress(AttributeError):
                self._preview_window.destroy()
            self._preview_window = None

        self._context_index += 1
        self._preview_window = AnimPreviewWindow(title=WINDOW_NAME, preview_context_name=f"{self._preview_context_name} {self._context_index}",
                                                   window_width=640, window_height=480)

    def _register_menu(self):
        context_menu: omni.kit.context_menu.ContextMenuExtension = omni.kit.context_menu.get_instance()
        if context_menu:

            def is_anim_selected(model: AnimPreviewModel, objects):
                # commented parts are redundant with context_menu.is(_one)_prim_selected
                # if not any(item in objects for item in ["prim", "prim_list"]):
                #    return False
                prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
                # if len(prim_list) != 1:
                #    return False
                return model.is_animation(prim_list[0])

            def is_skeleton_selected(model: AnimPreviewModel, objects):
                # commented parts are redundant with context_menu.is(_one)_prim_selected
                prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
                return model.is_skeleton(prim_list[0])

            def on_preview_anim(model: AnimPreviewModel, window: AnimPreviewWindow, objects):
                prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
                window.visible = True
                model.set_preview_anim(prim_list[0].GetPath(), objects["stage"])

            def on_preview_skeleton(model: AnimPreviewModel, window: AnimPreviewWindow, objects):
                prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
                if not len(prim_list):
                    carb.log_warn("Unable to preview prim.")
                    return
                window.visible = True
                omni.kit.commands.execute("AnimationPreviewCommand", prim_path=str(prim_list[0].GetPath()))

            menu_anim = {
                "name": "Preview Animation",
                "glyph": "show.svg",
                "show_fn": [
                    context_menu.is_prim_selected,
                    context_menu.is_one_prim_selected,
                    partial(is_anim_selected, self._preview_window.model)],
                "onclick_fn": partial(on_preview_anim, self._preview_window.model, self._preview_window),
                "appear_after": "Copy Prim Path",
            }
            menu_skeleton = {
                "name": "Send To Animation Preview",
                "glyph": "show.svg",
                "show_fn": [
                    context_menu.is_prim_selected,
                    context_menu.is_one_prim_selected,
                    partial(is_skeleton_selected, self._preview_window.model)],
                "onclick_fn": partial(on_preview_skeleton, self._preview_window.model, self._preview_window),
                "appear_after": "Copy Prim Path",
            }
            self._stage_context_menu_anim_preview = omni.kit.context_menu.add_menu(
                menu_anim,
                "MENU",
                "omni.kit.widget.stage"
            )
            self._stage_context_menu_skel_preview = omni.kit.context_menu.add_menu(
                menu_skeleton,
                "MENU",
                "omni.kit.widget.stage"
            )

    def on_shutdown(self):
        AnimationPreferences.unregister_preferences_frame(PREFERENCE_PREVIEW_FRAME)
        self._stage_event_sub = None
        self._stage_context_menu_anim_preview = None
        self._stage_context_menu_skel_preview = None
        self._preview_window.model.stop()
        self._preview_window.destroy()
        self._preview_window = None
        omni.kit.commands.unregister_module_commands(self._reg_cmds)
        self._reg_cmds = None
        global _extension
        _extension = None
        #TODO: close stage?

    def get_preview_window(self) -> AnimPreviewWindow:
        return self._preview_window

    def _on_stage_event(self, event: carb.events.IEvent):
        if event.type == int(omni.usd.StageEventType.CLOSED):
            if self._preview_window.preview_widget:
                self._preview_window.preview_widget.reset_scene()
                self._preview_window.rebuild()
        elif event.type == int(omni.usd.StageEventType.OPENED):
            if self._preview_window.preview_widget:
                self._preview_window.preview_widget.sync_up_axis_with_current_stage()
                self._preview_window.rebuild()
        elif event.type == int(omni.usd.StageEventType.HIERARCHY_CHANGED):
            self._preview_window._populate_scene_info()


def get_preview_window() -> AnimPreviewWindow:
    global _extension
    return _extension.get_preview_window()
