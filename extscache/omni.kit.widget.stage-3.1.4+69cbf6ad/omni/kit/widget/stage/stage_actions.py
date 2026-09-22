__all__ = ["ActionManager"]

import asyncio
import carb
import omni.kit.actions.core
import omni.kit.hotkeys.core

from typing import Callable
from .export_utils import ExportPrimUSD


ACTIONS_TAG = "Stage Actions"
ACTION_SAVE_PRIM = "save_prim"
ACTION_TOGGLE_PRIMS_ACTIVE_STATE = "toggle_prims_active_state"


def post_notification(message: str, info: bool = False, duration: int = 3):
    try:
        import omni.kit.notification_manager as nm
        if info:
            type = nm.NotificationStatus.INFO
        else:
            type = nm.NotificationStatus.WARNING

        nm.post_notification(message, status=type, duration=duration)
    except ModuleNotFoundError:
        carb.log_warn(message)


def save_prim(objects=None):
    if not objects:
        prim_list = []
        paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        stage = omni.usd.get_context().get_stage()
        for path in paths:
            prim = stage.GetPrimAtPath(path)
            if prim:
                prim_list.append(prim)
        objects = {"prim_list":  prim_list}
    elif isinstance(objects, tuple):
        objects = objects[0]

    if not "prim_list" in objects:
        return False
    prim_list = objects["prim_list"]

    if len(prim_list) == 0:
        post_notification("Cannot save prims as no prims are selected")
    elif len(prim_list) == 1:
        ExportPrimUSD(select_msg=f"Save \"{prim_list[0].GetName()}\" As...").export(prim_list)
    else:
        ExportPrimUSD(select_msg=f"Save Prims As...").export(prim_list)


def toggle_prims_active_state(prim_list=None, stage_model=None):
    if prim_list is None:
        prim_list = []
        paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
        stage = omni.usd.get_context().get_stage()
        for path in paths:
            prim = stage.GetPrimAtPath(path)
            if prim:
                prim_list.append(prim)

    if not prim_list:
        return False

    focus_prim = prim_list[0]
    stage = focus_prim.GetStage()
    path = focus_prim.GetPath()
    prim_paths = set([prim.GetPath() for prim in prim_list])
    if stage_model:
        # OM-111142: Adds all selected stage items as those prims that are inactive are not included in the prim_list.
        selected_stage_items = stage_model.get_selected_stage_items()
        for item in selected_stage_items:
            prim_paths.add(item.path)
    else:
        selected_stage_items = []

    active = focus_prim.IsActive()
    omni.kit.commands.execute("ToggleActivePrims", stage_or_context=stage, prim_paths=list(prim_paths), active=not active)

    if active:
        # TRICK: wait and select stage items after deactivating to avoid deselecting items.
        async def select_items():
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            if stage_model:
                stage_model.set_selected_stage_items(selected_stage_items)

        asyncio.ensure_future(select_items())


class Action:
    def __init__(
        self,
        extension_name: str,
        action_name: str,
        action_display_name: str,
        action_description: str,
        on_action_fn: Callable[[], None],
        hotkey: carb.input.KeyboardInput = None,
        modifiers: int = 0,
    ):
        self._extension_name = extension_name
        self._action_registry = omni.kit.actions.core.get_action_registry()
        self._input = carb.input.acquire_input_interface()
        self._action_name = action_name
        self._action_display_name = action_display_name
        self._action_description = action_description
        self._hotkey = hotkey
        self._modifiers = modifiers
        self._registered_hotkey = None
        self._hotkey_registry = None
        self._on_action_fn = on_action_fn
        self._action = None

        # Register actions and hotkeys
        self._register()

    def _register(self):
        # actions
        self._action = self._action_registry.register_action(
            self._extension_name,
            self._action_name,
            self._on_action_fn,
            display_name=self._action_display_name,
            description=self._action_description,
            tag=ACTIONS_TAG
        )

        self._register_hotkey()

    def destroy(self):
        self._action = None
        self._hotkey_registry = None
        self._registered_hotkey = None
        self._on_action_fn = None

    def _register_hotkey(self):
        if self._registered_hotkey:
            return

        if not self._hotkey:
            return

        try:
            from omni.kit.hotkeys.core import KeyCombination, get_hotkey_registry, filter

            self._hotkey_registry = get_hotkey_registry()

            hotkey_combo = KeyCombination(self._hotkey, self._modifiers)

            hotkey_filter = filter.HotkeyFilter(windows=["Stage"])
            self._registered_hotkey = self._hotkey_registry.register_hotkey(
                self._extension_name, hotkey_combo, self._extension_name, self._action_name,
                filter=hotkey_filter
            )
        except ImportError:
            self._registered_hotkey = None
            pass

    def _unregister_hotkey(self):
        self._registered_hotkey = None


class ActionManager:
    def __init__(self):
        self.__all_hotkeys = []

    def on_startup(self):
        self._manager = omni.kit.app.get_app().get_extension_manager()
        self._extension_name = omni.ext.get_extension_name(self._manager.get_extension_id_by_module(__name__))

        save_prim_hotkey = Action(
            extension_name=self._extension_name,
            action_name=ACTION_SAVE_PRIM,
            action_display_name="Stage->Save Prim",
            action_description="Save Prim.",
            on_action_fn=save_prim
        )

        toggle_prims_active_state_hot_key = Action(
            extension_name=self._extension_name,
            action_name=ACTION_TOGGLE_PRIMS_ACTIVE_STATE,
            action_display_name="Stage->Activate/Deactivate Prim",
            action_description="Activate/Deactivate Prim.",
            on_action_fn=toggle_prims_active_state,
            hotkey=None,
        )

        self.__all_hotkeys.append(save_prim_hotkey)
        self.__all_hotkeys.append(toggle_prims_active_state_hot_key)

        self.__register_hotkeys()

    def __register_hotkeys(self):
        for action in self.__all_hotkeys:
            action._register_hotkey()

    def __unregister_hotkeys(self):
        try:
            from omni.kit.hotkeys.core import get_hotkey_registry

            hotkey_registry = get_hotkey_registry()
            hotkey_registry.deregister_all_hotkeys_for_extension(self._extension_name)
        except Exception:
            pass

        for action in self.__all_hotkeys:
            action._unregister_hotkey()

    def on_shutdown(self):
        for hotkey in self.__all_hotkeys:
            hotkey.destroy()

        self.__unregister_hotkeys()
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_all_actions_for_extension(self._extension_name)
        self.__all_hotkeys = []
