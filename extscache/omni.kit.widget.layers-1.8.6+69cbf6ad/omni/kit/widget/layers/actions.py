import carb
import omni.kit.actions.core
import weakref

from typing import Callable
from .prim_spec_item import PrimSpecItem
from .layer_model_utils import LayerModelUtils


ACTIONS_TAG = "Layers Actions"
ACTION_DELETE_PRIM_SPEC_ITEMS = "delete_deltas"


class Action:
    def __init__(
        self,
        extension_name: str,
        action_name: str,
        action_display_name: str,
        action_description: str,
        on_action_fn: Callable[[], None],
        hotkey: carb.input.KeyboardInput,
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

        try:
            from omni.kit.hotkeys.core import KeyCombination, get_hotkey_registry, filter

            self._hotkey_registry = get_hotkey_registry()

            hotkey_combo = KeyCombination(self._hotkey, self._modifiers)

            hotkey_filter = filter.HotkeyFilter(windows=["Layer"])
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

    def on_startup(self, layer_extension):
        self._manager = omni.kit.app.get_app().get_extension_manager()
        self._extension_name = omni.ext.get_extension_name(self._manager.get_extension_id_by_module(__name__))

        weakref_layer_extension = weakref.ref(layer_extension)

        def on_delete_clicked():
            layers = weakref_layer_extension()
            if not layers:
                return

            items = layers.get_selected_items()

            prim_spec_items = [item for item in items if isinstance(item, PrimSpecItem)]
            LayerModelUtils.remove_prim_spec_items(prim_spec_items)

        remove_prim_spec_items_hotkey = Action(
            extension_name=self._extension_name,
            action_name=ACTION_DELETE_PRIM_SPEC_ITEMS,
            action_display_name="Layer->Delete Prim Specs",
            action_description="Delete selected prim specs.",
            on_action_fn=on_delete_clicked,
            hotkey=carb.input.KeyboardInput.DEL
        )

        self.__all_hotkeys.append(remove_prim_spec_items_hotkey)

        self._hotkey_extension_subscription = self._manager.subscribe_to_extension_enable(
            lambda _: self.__register_hotkeys(),
            lambda _: self.__unregister_hotkeys(),
            ext_name="omni.kit.hotkeys.core",
            hook_name="omni.kit.widget.layers hotkey listener",
        )

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
        self._hotkey_extension_subscription = None
        action_registry = omni.kit.actions.core.get_action_registry()
        action_registry.deregister_all_actions_for_extension(self._extension_name)
        self.__all_hotkeys = []
