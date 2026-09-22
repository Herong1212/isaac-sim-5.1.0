# Public API for module omni.kit.ui_test:

## Classes

- class InitExt(omni.ext.IExt)
  - def on_startup(self)

- class Vec2
  - def __init__(self, *args)
  - def to_tuple(self)

- class KeyDownScope
  - def __init__(self, key: carb.input.KeyboardInput, modifier: carb.input.KeyboardInput = 0, human_delay_speed: int = 2)

- class WidgetRef
  - def __init__(self, widget: ui.Widget, path: str, window: ui.Window = None)
  - [property] def widget(self) -> ui.Widget
  - [property] def model(self)
  - [property] def window(self) -> ui.Window
  - [property] def path(self) -> str
  - [property] def realpath(self) -> str
  - [property] def position(self) -> Vec2
  - [property] def size(self) -> Vec2
  - [property] def center(self) -> Vec2
  - def offset(self, *kwargs) -> Vec2
  - async def focus(self)
  - async def undock(self)
  - async def bring_to_front(self)
  - async def click(self, pos: Vec2 = None, right_click = False, double = False, human_delay_speed: int = 2)
  - async def right_click(self, pos = None, human_delay_speed: int = 2)
  - async def double_click(self, pos = None, human_delay_speed: int = 2)
  - async def input(self, text: str, end_key = KeyboardInput.ENTER, human_delay_speed: int = 2, clear_before_input: bool = False)
  - async def drag_and_drop(self, drop_target: Vec2, human_delay_speed: int = 4)
  - def find(self, path: str) -> WidgetRef
  - def find_all(self, path: str) -> List[WidgetRef]
  - def find_first(self, path: str) -> WidgetRef

- class WindowRef(WidgetRef)
  - def __init__(self, widget: ui.WindowHandle, path: str)
  - [property] def position(self) -> Vec2
  - [property] def size(self) -> Vec2

## Functions

- async def human_delay(human_delay_speed: int = 2)
- async def wait_n_updates(update_count = 2)
- async def emulate_mouse_click(right_click = False, double = False, modifiers: int | None = None)
- async def emulate_mouse_move(pos: Vec2, human_delay_speed: int = 2)
- async def emulate_mouse_move_and_click(pos: Vec2, right_click = False, double = False, human_delay_speed: int = 2)
- async def emulate_mouse_drag_and_drop(start_pos, end_pos, right_click = False, human_delay_speed: int = 4)
- async def emulate_mouse_scroll(delta: Vec2, human_delay_speed: int = 2)
- async def emulate_keyboard_press(key: KeyboardInput, modifier: carb.input.KeyboardInput = 0, human_delay_speed: int = 2)
- async def emulate_char_press(chars: str, delay_every_n_symbols: int = 20, human_delay_speed: int = 2)
- async def emulate_key_combo(combo: str, human_delay_speed: int = 2)
- def find(path: str) -> WidgetRef
- def find_all(path: str) -> List[WidgetRef]
- def find_first(path: str) -> List[WidgetRef]
- def get_menubar() -> MenuRef
- async def menu_click(path, separator: str = '/', human_delay_speed: int = 2, show: bool = True)
- async def select_context_menu(menu_path: str, menu_root: ui.Widget = None, offset = Vec2(100, 10), human_delay_speed: int = 4, find_fn = _find_menu_item)
- async def get_context_menu(menu_root: ui.Widget = None, get_all: bool = False)
