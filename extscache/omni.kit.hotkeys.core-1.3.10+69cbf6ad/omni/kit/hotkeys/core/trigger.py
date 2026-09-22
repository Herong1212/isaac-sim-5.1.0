__all__ = ["HotkeyTrigger"]
import asyncio
import carb
import carb.input
import omni.appwindow
import omni.kit.app

from .registry import HotkeyRegistry
from .context import HotkeyContext
from .key_combination import KeyCombination
from .hovered_window import get_hovered_window


SETTING_ALLOW_LIST = "/exts/omni.kit.hotkeys.core/allow_list"


class HotkeyTrigger:
    def __init__(self, registry: HotkeyRegistry, context: HotkeyContext):
        """
        Trigger hotkey on keyboard input.

        Args:
            registry (HotkeyRegistry): Hotkey registry.
            context (HotkeyContext): Hotkey context.
        """
        self._registry = registry
        self._context = context

        self._input = carb.input.acquire_input_interface()
        self._input_sub_id = self._input.subscribe_to_input_events(self._on_input_event, order=0)
        self.__app_window = omni.appwindow.get_default_app_window()

        self._stop_event = asyncio.Event()
        self._work_queue = asyncio.Queue()
        self.__run_future = asyncio.ensure_future(self._run())

        self.__settings = carb.settings.get_settings()
        self._allow_list = self.__settings.get(SETTING_ALLOW_LIST)

        def __on_allow_list_change(value, event_type) -> None:
            self._allow_list = self.__settings.get(SETTING_ALLOW_LIST)

        self._sub_allow_list = omni.kit.app.SettingChangeSubscription(SETTING_ALLOW_LIST, __on_allow_list_change)

    def destroy(self):
        self._stop_event.set()
        self._work_queue.put_nowait((None, None, None))
        self.__run_future.cancel()

        self._input.unsubscribe_to_input_events(self._input_sub_id)
        self._input_sub_id = None
        self._input = None

        self._sub_allow_list = None

    def _on_input_event(self, event, *_):
        import carb.input
        if event.deviceType == carb.input.DeviceType.KEYBOARD \
                and event.event.type in [carb.input.KeyboardEventType.KEY_PRESS, carb.input.KeyboardEventType.KEY_RELEASE]:
            is_down = event.event.type == carb.input.KeyboardEventType.KEY_PRESS
            if event.deviceType == carb.input.DeviceType.KEYBOARD:
                key = event.event.input
                try:
                    # no Carb::Windowing on OVC
                    import carb.windowing
                    windowing = carb.windowing.acquire_windowing_interface()
                    if windowing and hasattr(windowing, "translate_key"):
                        key = windowing.translate_key(key)
                except ImportError:
                    pass
                except RuntimeError:
                    # OVC: RuntimeError: Failed to acquire interface: card::windowing::IWindowing
                    pass
                key_combination = KeyCombination(key, modifiers=event.event.modifiers, trigger_press=is_down)
                if not self._allow_list or key_combination.as_string in self._allow_list and self._registry.get_all_hotkeys_for_key(key_combination):
                    (mouse_pos_x, mouse_pos_y) = self._input.get_mouse_coords_pixel(self.__app_window.get_mouse())
                    self._work_queue.put_nowait((key_combination, mouse_pos_x, mouse_pos_y))
        return True

    def __trigger(self, key_combination: KeyCombination, pos_x: float, pos_y: float):
        hotkey = None

        # First: find hotkey assigned to current context
        current_context = self._context.get()
        if current_context:
            hotkey = self._registry.get_hotkey_for_trigger(key_combination, context=current_context)

        if not hotkey:
            current_window = get_hovered_window(pos_x, pos_y)
            if current_window:
                hotkey = self._registry.get_hotkey_for_trigger(key_combination, window=current_window.title)

        if not hotkey:
            # Finally: No context/window hotkey found, find global hotkey
            hotkey = self._registry.get_hotkey_for_trigger(key_combination)

        if hotkey:
            hotkey.execute()

    async def _run(self):
        while not self._stop_event.is_set():
            (key_combination, pos_x, pos_y) = await self._work_queue.get()
            self.__trigger(key_combination, pos_x, pos_y)
