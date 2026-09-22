# Public API for module omni.kit.hotkeys.core:

## Classes

- class KeyCombination
  - def __init__(self, key: Union[str, carb.input.KeyboardInput], modifiers: int = 0, trigger_press: bool = True)
  - [property] def as_string(self) -> str
  - [property] def id(self) -> str
  - [property] def is_valid(self) -> bool
  - static def from_string(key_string: str) -> Tuple[carb.input.KeyboardInput, int, bool]
  - static def is_valid_key_string(key: str) -> bool

- class Hotkey
  - def __init__(self, hotkey_ext_id: str, key: Union[str, KeyCombination], action_ext_id: str, action_id: str, filter: Optional[HotkeyFilter] = None)
  - [property] def id(self) -> str
  - [property] def key_text(self) -> str
  - [property] def action_text(self) -> str
  - [property] def filter_text(self) -> str
  - [property] def action(self) -> Action
  - def execute(self)

- class HotkeyRegistry
  - class Result
    - OK: str
    - ERROR_NO_ACTION: str
    - ERROR_ACTION_DUPLICATED: str
    - ERROR_KEY_INVALID: str
    - ERROR_KEY_DUPLICATED: str
  - def __init__(self)
  - [property] def last_error(self) -> HotkeyRegistry.Result
  - [property] def keyboard_layout(self) -> Optional[KeyboardLayoutDelegate]
  - def switch_layout(self, layout_name: str)
  - def register_hotkey(self, *args, **kwargs) -> Optional[Hotkey]
  - def edit_hotkey(self, hotkey: Hotkey, key: Union[str, KeyCombination], filter: Optional[HotkeyFilter]) -> HotkeyRegistry.Result
  - def deregister_hotkey(self, *args, **kwargs) -> bool
  - def deregister_hotkeys(self, hotkey_ext_id: str, key: Union[str, KeyCombination])
  - def deregister_all_hotkeys_for_extension(self, hotkey_ext_id: Optional[str])
  - def deregister_all_hotkeys_for_filter(self, filter: HotkeyFilter)
  - def get_hotkey(self, hotkey_ext_id: str, key: Union[str, KeyCombination], filter: Optional[HotkeyFilter] = None) -> Optional[Hotkey]
  - def get_hotkey_for_trigger(self, key: Union[str, KeyCombination], context: Optional[str] = None, window: Optional[str] = None) -> Optional[Hotkey]
  - def get_hotkey_for_filter(self, key: Union[str, KeyCombination], filter: HotkeyFilter) -> Optional[Hotkey]
  - def get_hotkeys(self, hotkey_ext_id: str, key: Union[str, KeyCombination]) -> List[Hotkey]
  - def get_all_hotkeys(self) -> List[Hotkey]
  - def get_all_hotkeys_for_extension(self, hotkey_ext_id: Optional[str]) -> List[Hotkey]
  - def get_all_hotkeys_for_key(self, key: Union[str, KeyCombination]) -> List[Hotkey]
  - def get_all_hotkeys_for_filter(self, filter: HotkeyFilter) -> List[Hotkey]
  - def disable_hotkey(self, hotkey: Hotkey) -> bool
  - def clear_storage(self)
  - def export_storage(self, url: str)
  - def import_storage(self, url: str) -> bool
  - def has_duplicated_hotkey(self, hotkey: Hotkey) -> HotkeyRegistry.Result
  - def verify_hotkey(self, hotkey: Hotkey, key_combination: Optional[KeyCombination] = None, hotkey_filter: Optional[HotkeyFilter] = None) -> HotkeyRegistry.Result
  - def get_hotkey_default(self, hotkey: Hotkey) -> Tuple[str, HotkeyFilter]
  - def restore_defaults(self)
  - def is_user_hotkey(self, hotkey: Hotkey) -> bool

- class HotkeyFilter
  - def __init__(self, context: Optional[str] = None, windows: Optional[List[str]] = None)
  - [property] def windows_text(self)

- class KeyboardLayoutDelegate(abc.ABC)
  - class def get_instances(cls) -> List[KeyboardLayoutDelegate]
  - class def get_instance(cls, name: str) -> Optional[KeyboardLayoutDelegate]
  - def __init__(self)
  - def destroy(self)
  - def get_name(self) -> str
  - def get_maps(self) -> dict
  - def map_key(self, key: KeyCombination) -> Optional[KeyCombination]
  - def restore_key(self, key: KeyCombination) -> Optional[KeyCombination]

## Functions

- def get_hotkey_context() -> HotkeyContext
- def get_hotkey_registry() -> HotkeyRegistry

## Variables

- HOTKEY_REGISTER_EVENT: int
- HOTKEY_REGISTER_GLOBAL_EVENT: str
- HOTKEY_DEREGISTER_EVENT: int
- HOTKEY_DEREGISTER_GLOBAL_EVENT: str
- HOTKEY_CHANGED_EVENT: int
- HOTKEY_CHANGED_GLOBAL_EVENT: str
