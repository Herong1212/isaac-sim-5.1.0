# pylint: disable=attribute-defined-outside-init, unused-private-member, relative-beyond-top-level, superfluous-parens

__all__ = ["TriggerPressOption", "TriggerPressWindow", "KeyEditor"]
import asyncio
from typing import Optional, Union, Callable
import carb
import carb.input
import omni.kit.app
import omni.ui as ui
from omni.kit.hotkeys.core import Hotkey, HotkeyRegistry, KeyCombination, get_hotkey_registry
from ..model.hotkey_item import HotkeyDetailItem, EmptyHotkeyItem
from ..model.hotkeys_model import HotkeysModel
from ..window.warning_window import WarningWindow, WarningMessage
from ..style import HOTKEYS_WINDOW_STYLE

_key_capture_instances = 0


class TriggerPressOption:
    def __init__(self, collection: ui.RadioCollection, text):
        with ui.ZStack(width=0):
            ui.Rectangle(style_type_name_override="TriggerPressOption.Background")
            ui.RadioButton(
                text=text,
                radio_collection=collection,
                width=100,
                height=24,
                image_width=14,
                spacing=4,
                alignment=ui.Alignment.LEFT,
                style_type_name_override="TriggerPressOption",
            )


class TriggerPressWindow(ui.Window):
    PADDING = 4

    def __init__(self, model: ui.SimpleIntModel):
        self.__model = model

        flags = ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_MOVE | ui.WINDOW_FLAGS_POPUP
        super().__init__("Hotkey Trigger", flags=flags, auto_resize=True)

        self.frame.set_style(HOTKEYS_WINDOW_STYLE)
        self.frame.set_build_fn(self.__build_ui)

    def destroy(self):
        self.__sub = None

    def __del__(self):
        self.destroy()

    def __build_ui(self):
        collection = ui.RadioCollection(self.__model)
        with self.frame:
            with ui.VStack(style={"padding": self.PADDING}):
                TriggerPressOption(collection, "On Press")
                TriggerPressOption(collection, "On Release")

        self.__sub = collection.model.add_value_changed_fn(self.__on_value_changed)

    def __on_value_changed(self, model: ui.AbstractValueModel):
        self.visible = False


class KeyEditor:
    def __init__(
        self,
        model: HotkeysModel,
        item: Union[HotkeyDetailItem, EmptyHotkeyItem],
        visible: bool = True,
        on_edit_cancelled_fn: Callable[[str], None] = None
    ):
        self.__model = model
        self.__item = item
        self.__on_edit_cancelled_fn = on_edit_cancelled_fn
        self.__key_text_model = ui.SimpleStringModel(item.hotkey.key_text if item.hotkey else "")
        self.__key_press_model = ui.SimpleIntModel(0 if item.hotkey.key_combination.trigger_press else 1)
        self.__sub_key_text = self.__key_text_model.add_value_changed_fn(self.__on_key_text_changed)
        self.__trigger_window: Optional[TriggerPressWindow] = None
        self.__input_field: Optional[ui.StringField] = None
        self.__input_hint: Optional[ui.Label] = None
        self.__remove_container: Optional[ui.HStack] = None
        self.__input = carb.input.acquire_input_interface()
        self.__input_sub_id = None

        self.__build_ui(visible)

    def __del__(self):
        self.visible = False

    def __build_ui(self, visible):
        # Double click to clean the key input to empty
        self.__container = ui.HStack(visible=visible)
        with self.__container:
            ui.Spacer(width=4)
            with ui.ZStack(width=ui.Fraction(1)):
                self.__input_field = ui.StringField(self.__key_text_model, enabled=False)
                self.__input_hint = ui.Label("Begin Typing to Capture Key Bindings", name="hint", style_type_name_override="Action.Input")
                self.__remove_container = ui.HStack()
                with self.__remove_container:
                    ui.Spacer()
                    ui.Image(name="remove", width=20, mouse_released_fn=lambda x, y, b, f: self.__key_text_model.set_value(""))
                    ui.Spacer(width=4)
            ui.Spacer(width=8)
            ui.Image(name="cancel", width=20, mouse_released_fn=lambda x, y, b, f: self.__hide())
            ui.Spacer(width=4)
            ui.Image(name="save", width=20, mouse_released_fn=lambda x, y, b, f: self.__save())
            ui.Spacer(width=4)
            with ui.ZStack(width=0):
                ui.Rectangle(style_type_name_override="DropDownArrow.background")
                with ui.VStack(width=0):
                    ui.Spacer()
                    self.__arrow = ui.Triangle(
                        width=20,
                        height=16,
                        alignment=ui.Alignment.CENTER_BOTTOM,
                        style_type_name_override="DropDownArrow",
                        mouse_released_fn=lambda x, y, b, f: self.__edit_press()
                    )
                    ui.Spacer()
            ui.Spacer(width=1)

        if visible:
            carb.log_info(f"[Hotkey Editor] Show editor for {self.__item}")
            self.__start_key_capture()

        self.__on_key_text_changed(self.__key_text_model)

    @property
    def visible(self) -> bool:
        return self.__container.visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self.__container.visible = value
        self.__sub_key_text = False
        carb.log_info(f"[Hotkey Editor] Visible change to {value} for {self.__item}")
        if value:
            # Default to capture keyboard for key input
            self.__key_text_model.set_value(self.__item.hotkey.key_text if self.__item.hotkey else "")
            self.__start_key_capture()
        else:
            self.__stop_key_capture()

    def __start_key_capture(self):
        global _key_capture_instances
        _key_capture_instances += 1
        carb.log_info(f"[Hotkey Editor] [{_key_capture_instances}] Start key capture for {self.__item}")
        self.__input_sub_id = self.__input.subscribe_to_input_events(self._on_input_event, order=-100000)

    def __stop_key_capture(self):
        if self.__input_sub_id is not None:
            global _key_capture_instances
            _key_capture_instances -= 1
            carb.log_info(f"[Hotkey Editor] [{_key_capture_instances}] Stop key capture for {self.__item}")
            self.__input.unsubscribe_to_input_events(self.__input_sub_id)
            self.__input_sub_id = None

    def _on_input_event(self, event, *_):
        import carb.input
        if event.deviceType == carb.input.DeviceType.KEYBOARD:
            is_down = event.event.type == carb.input.KeyboardEventType.KEY_PRESS
            if is_down:
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
                key_combination = KeyCombination(key, modifiers=event.event.modifiers)
                self.__key_text_model.set_value(key_combination.as_string)
        # Return False to block key input
        return False

    def __hide(self):
        carb.log_info("[Hotkey Editor] Cancel edit")
        self.visible = False
        if isinstance(self.__item, EmptyHotkeyItem):
            async def __clear_empty_async():
                await omni.kit.app.get_app().next_update_async()
                self.__model.clear_empty_hotkey()

            asyncio.ensure_future(__clear_empty_async())
        if self.__on_edit_cancelled_fn:
            self.__on_edit_cancelled_fn(self.__item.hotkey.key_text)

    def __save(self):
        try:
            result = self.__model.edit_hotkey_item(
                self.__item,
                key_text=self.__key_text_model.as_string,
                trigger_press=self.__key_press_model.as_int == 0
            )
            if result == HotkeyRegistry.Result.OK:
                carb.log_info(f"[Hotkey Editor] Save for {self.__item}")
                self.visible = False
            else:
                if result == HotkeyRegistry.Result.ERROR_NO_ACTION:
                    warn_window = WarningWindow("Action required", ["Please select an action before saving hotkey!"])
                elif result == HotkeyRegistry.Result.ERROR_KEY_INVALID:
                    warn_window = WarningWindow("Key required", ["Please input a valid key binding before saving the hotkey!"])
                elif result == HotkeyRegistry.Result.ERROR_KEY_DUPLICATED:
                    key_combination = KeyCombination(self.__key_text_model.as_string, trigger_press=self.__item.hotkey.key_combination.trigger_press)
                    duplicated_key = get_hotkey_registry().get_hotkey_for_filter(key_combination, self.__item.hotkey.filter)
                    action_display = duplicated_key.action.display_name if duplicated_key.action else "Unknown Action"
                    warn_window = WarningWindow(
                        "Hotkey Conflict Warning",
                        messages=[
                            WarningMessage(f"'{key_combination.id}'", highlight=True),
                            WarningMessage(" is already assigned to "),
                            WarningMessage(f"'{action_display}'", highlight=True),
                            '\n',
                            "Do you want to replace this existing hotkey with your new one?"
                        ],
                        buttons=[
                            ("Replace", lambda k=key_combination, n=self.__item, o=duplicated_key: self.__replace_key(k, n, o)),
                            ("Cancel", None)
                        ]
                    )
                elif result == HotkeyRegistry.Result.ERROR_ACTION_DUPLICATED:
                    action_display = self.__item.action_display
                    warn_window = WarningWindow(
                        "Action Conflict Warning",
                        messages=[
                            WarningMessage(f"'{action_display}'", highlight=True),
                            WarningMessage(" is already defined."),
                        ]
                    )
                else:
                    warn_window = WarningWindow("Unkown Error", [f"Error code: {result}"])
                warn_window.position_x = self.__container.screen_position_x + 4
                warn_window.position_y = self.__container.screen_position_y + self.__container.computed_height + 4
        except Exception as e:  # pylint: disable=broad-except
            carb.log_error(f"Exception when save hotkey: {e}")

    def __edit_press(self):
        if self.__trigger_window is None:
            self.__trigger_window = TriggerPressWindow(self.__key_press_model)

        async def __update_position():
            while self.__trigger_window.width < 10 or self.__trigger_window.width == 400:
                await omni.kit.app.get_app().next_update_async()
            self.__trigger_window.position_x = self.__arrow.screen_position_x + self.__arrow.computed_width - self.__trigger_window.width
            self.__trigger_window.position_y = self.__arrow.screen_position_y + self.__arrow.computed_height + 4

        self.__trigger_window.visible = True
        asyncio.ensure_future(__update_position())

    def __replace_key(self, key_combination: KeyCombination, item: HotkeyDetailItem, duplicated_key: Hotkey):
        carb.log_info(f"[Hotkey Editor] Replace hotkey for {self.__item}")
        self.visible = False
        self.__model.replace_item_key(key_combination, item, duplicated_key)

    def __on_key_text_changed(self, model: ui.SimpleStringModel) -> None:
        if self.__remove_container:
            self.__remove_container.visible = (model.as_string != "")
        if self.__input_hint:
            self.__input_hint.visible = (model.as_string == "")
