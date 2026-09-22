import carb
import carb.input
import omni.kit.app
import omni.ui as ui
import carb.windowing
import omni.appwindow

from carb.input import MouseEventType, KeyboardEventType, KeyboardInput

import logging

from functools import lru_cache
from itertools import chain

from .vec2 import Vec2
from .common import human_delay, wait_n_updates_internal

logger = logging.getLogger(__name__)


@lru_cache()
def _get_windowing() -> carb.windowing.IWindowing:
    try:
        return carb.windowing.acquire_windowing_interface()
    except RuntimeError:
        # OVC: RuntimeError: Failed to acquire interface: card::windowing::IWindowing
        return None


@lru_cache()
def _get_input_provider() -> carb.input.InputProvider:
    return carb.input.acquire_input_provider()


async def emulate_mouse(event_type: MouseEventType, pos: Vec2 = Vec2(), modifiers: int | None = None):
    app_window = omni.appwindow.get_default_app_window()
    mouse = app_window.get_mouse()
    window_width = ui.Workspace.get_main_window_width()
    window_height = ui.Workspace.get_main_window_height()
    pos = pos * ui.Workspace.get_dpi_scale()
    if modifiers is None:
        if False:
            # Needs OVCC-1499 to work
            modifiers = carb.input.acquire_input_interface().get_global_modifier_flags(mouse_buttons=[])
        else:
            modifiers = carb.input.acquire_input_interface().get_modifier_flags(device_types=[carb.input.DeviceType.KEYBOARD])

    _get_input_provider().buffer_mouse_event(
        mouse, event_type, (pos.x / window_width, pos.y / window_height),
        modifiers,
        pos.to_tuple()
    )
    if event_type == MouseEventType.MOVE:
        windowing = _get_windowing()
        if windowing:
            windowing.set_cursor_position(app_window.get_window(), (int(pos.x), int(pos.y)))


async def emulate_mouse_click(right_click=False, double=False, modifiers: int | None = None):
    """Emulate Mouse single or double click."""
    for _ in range(2 if double else 1):
        await emulate_mouse(MouseEventType.RIGHT_BUTTON_DOWN if right_click else MouseEventType.LEFT_BUTTON_DOWN)
        await wait_n_updates_internal()
        await emulate_mouse(MouseEventType.RIGHT_BUTTON_UP if right_click else MouseEventType.LEFT_BUTTON_UP)
        await wait_n_updates_internal()


async def emulate_mouse_move(pos: Vec2, human_delay_speed: int = 2):
    """Emulate Mouse move into position."""
    logger.info(f"emulate_mouse_move to: {pos}")
    await emulate_mouse(MouseEventType.MOVE, pos)
    await human_delay(human_delay_speed)


async def emulate_mouse_move_and_click(pos: Vec2, right_click=False, double=False, human_delay_speed: int = 2):
    """Emulate Mouse move into position and click."""
    logger.info(f"emulate_mouse_move_and_click pos: {pos} (right_click: {right_click}, double: {double})")
    await emulate_mouse(MouseEventType.MOVE, pos)
    await emulate_mouse_click(right_click=right_click, double=double)
    await human_delay(human_delay_speed)


async def emulate_mouse_slow_move(start_pos, end_pos, num_steps=8, human_delay_speed: int = 4):
    """Emulate Mouse slow move. Mouse is moved in steps between start and end with the human delay between each step."""
    step = (end_pos - start_pos) / num_steps
    for i in range(0, num_steps + 1):
        await emulate_mouse(MouseEventType.MOVE, start_pos + step * i)
        await human_delay(human_delay_speed)


async def emulate_mouse_drag_and_drop(start_pos, end_pos, right_click=False, human_delay_speed: int = 4):
    """Emulate Mouse Drag & Drop. Click at start position and slowly move to end position."""
    logger.info(f"emulate_mouse_drag_and_drop pos: {start_pos} -> {end_pos} (right_click: {right_click})")
    await emulate_mouse(MouseEventType.MOVE, start_pos)
    await emulate_mouse(MouseEventType.RIGHT_BUTTON_DOWN if right_click else MouseEventType.LEFT_BUTTON_DOWN)
    await human_delay(human_delay_speed)
    await emulate_mouse_slow_move(start_pos, end_pos, human_delay_speed=human_delay_speed)
    await human_delay(human_delay_speed)
    await emulate_mouse(MouseEventType.RIGHT_BUTTON_UP if right_click else MouseEventType.LEFT_BUTTON_UP)
    await human_delay(human_delay_speed)


async def emulate_mouse_scroll(delta: Vec2, human_delay_speed: int = 2):
    """Emulate Mouse scroll by delta."""
    logger.info(f"emulate_mouse_scroll: {delta}")
    await emulate_mouse(MouseEventType.SCROLL, delta)
    await human_delay(human_delay_speed)


async def emulate_keyboard(event_type: KeyboardEventType, key: KeyboardInput, modifier: carb.input.KeyboardInput = 0):
    logger.info(f"emulate_keyboard event_type: {event_type}, key: {key} modifier:{modifier}")
    keyboard = omni.appwindow.get_default_app_window().get_keyboard()
    _get_input_provider().buffer_keyboard_key_event(keyboard, event_type, key, modifier)


MODIFIERS_TO_KEY = {
    carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL: KeyboardInput.LEFT_CONTROL,
    carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT: KeyboardInput.LEFT_SHIFT,
    carb.input.KEYBOARD_MODIFIER_FLAG_ALT: KeyboardInput.LEFT_ALT,
}


async def emulate_keyboard_press(
    key: KeyboardInput, modifier: carb.input.KeyboardInput = 0, human_delay_speed: int = 2
):
    """Emulate Keyboard key press. Down and up."""

    # Figure out which modifier keys need to be pressed
    mods = []
    for k in MODIFIERS_TO_KEY.keys():
        if modifier & k:
            mods.append(k)

    modifier = 0
    for k in mods:
        modifier = modifier | k  # modifier is added for the press
        await emulate_keyboard(KeyboardEventType.KEY_PRESS, MODIFIERS_TO_KEY[k], modifier)
        await human_delay(human_delay_speed)

    await emulate_keyboard(KeyboardEventType.KEY_PRESS, key, modifier)
    await human_delay(human_delay_speed)
    await emulate_keyboard(KeyboardEventType.KEY_RELEASE, key, modifier)
    await human_delay(human_delay_speed)

    # Back off the modifiers
    for k in reversed(mods):
        modifier = modifier & ~k  # modifier is removed for the release
        await emulate_keyboard(KeyboardEventType.KEY_RELEASE, MODIFIERS_TO_KEY[k], modifier)
        await human_delay(human_delay_speed)


MODIFIERS_MAP = {
    "CTRL": (KeyboardInput.LEFT_CONTROL, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL),
    "CONTROL": (KeyboardInput.LEFT_CONTROL, carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL),
    "SHIFT": (KeyboardInput.LEFT_SHIFT, carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT),
    "ALT": (KeyboardInput.LEFT_ALT, carb.input.KEYBOARD_MODIFIER_FLAG_ALT),
}


async def emulate_key_combo(combo: str, human_delay_speed: int = 2):
    """Emulate Keyboard key combination.

    Parse string of keys separated by '+' sign and treat as a key combo to emulate.

    Examples: "CTRL+ENTER", "SHIFT+ALT+Y", "Z"
    """
    mods = []
    keys = []
    modifiers = 0
    key_map = KeyboardInput.__members__  # pybind11 way to get enum as dict (name -> value)
    for key in combo.upper().split("+"):
        if key in MODIFIERS_MAP:
            mods.append(MODIFIERS_MAP[key])
            continue
        if key not in key_map:
            carb.log_error(f"Can't parse key: '{key}' in combo: '{combo}'")
            return
        keys.append(key_map[key])

    # press modifier keys first
    for k in mods:
        modifiers = modifiers | k[1]  # modifier is added for the press
        await emulate_keyboard(KeyboardEventType.KEY_PRESS, k[0], modifiers)
        await human_delay(human_delay_speed)
    # press non-modifier keys
    for k in keys:
        await emulate_keyboard(KeyboardEventType.KEY_PRESS, k, modifiers)
        await human_delay(human_delay_speed)

    # release non-modifier keys and modifier keys in reverse order
    for k in reversed(keys):
        await emulate_keyboard(KeyboardEventType.KEY_RELEASE, k, modifiers)
        await human_delay(human_delay_speed)
    for k in reversed(mods):
        modifiers = modifiers & ~k[1]  # modifier is removed for the release
        await emulate_keyboard(KeyboardEventType.KEY_RELEASE, k[0], modifiers)
        await human_delay(human_delay_speed)


async def emulate_char_press(chars: str, delay_every_n_symbols: int = 20, human_delay_speed: int = 2):
    """Emulate Keyboard char input. Type N chars immediately and do a delay, then continue."""
    keyboard = omni.appwindow.get_default_app_window().get_keyboard()
    for i, char in enumerate(chars):
        _get_input_provider().buffer_keyboard_char_event(keyboard, char, 0)
        if (i + 1) % delay_every_n_symbols == 0:
            await human_delay(human_delay_speed)


# Key is down when enter the scope and released when exit
# Usage:
#   async with KeyDownScope(carb.input.KeyboardInput.LEFT_CONTROL):
#       await ui_test.emulate_mouse_drag_and_drop(Vec2(50, 50), Vec2(350, 350))
class KeyDownScope:
    def __init__(
        self, key: carb.input.KeyboardInput, modifier: carb.input.KeyboardInput = 0, human_delay_speed: int = 2
    ):
        self._key = key
        self._modifier = modifier
        self._human_delay_speed = human_delay_speed

    async def __aenter__(self):
        await emulate_keyboard(carb.input.KeyboardEventType.KEY_PRESS, self._key, self._modifier)
        await human_delay(self._human_delay_speed)

    async def __aexit__(self, exc_type, exc, tb):
        await emulate_keyboard(carb.input.KeyboardEventType.KEY_RELEASE, self._key, self._modifier)
        if self._modifier:
            await emulate_keyboard(carb.input.KeyboardEventType.KEY_RELEASE, self._modifier)
        await human_delay(self._human_delay_speed)
