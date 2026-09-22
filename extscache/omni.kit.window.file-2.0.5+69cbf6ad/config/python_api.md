# Public API for module omni.kit.window.file:

## Classes

- class DialogOptions(Enum)
  - NONE: Tuple
  - FORCE: Tuple
  - HIDE: Tuple

- class ReadOnlyOptionsWindow
  - def __init__(self, open_with_new_edit_fn: Callable[[], None], open_original_fn: Callable[[], None], modal = False)
  - def destroy(self)
  - def show(self)
  - def hide(self)
  - def is_visible(self)

- class Prompt
  - def __init__(self, title: str, text: str, button_text: List[str], button_fn: List[Callable[[], None]], modal: bool = False, callback_addons: List[Callable[[], None]] = [], callback_destroy: List[Callable[[], None]] = [], decode_text: bool = True)
  - def destroy(self)
  - def show(self)
  - def hide(self)
  - def is_visible(self)
  - def set_text(self, text)

- class StageSaveDialog
  - def __init__(self, on_save_fn: Optional[Callable[[], None]] = None, on_dont_save_fn: Optional[Callable[[], None]] = None, on_cancel_fn: Optional[Callable[[], None]] = None, enable_dont_save = False)
  - def destroy(self)
  - def show(self, layer_identifiers: List[str] = [])
  - def is_visible(self)

## Functions

- def get_instance()
- def new(template = None)
- def open(open_loadset = omni.usd.UsdContextInitialLoadSet.LOAD_ALL)
- def open_stage(path: str, open_loadset = omni.usd.UsdContextInitialLoadSet.LOAD_ALL)
- def open_with_new_edit_layer(path: str, open_loadset = omni.usd.UsdContextInitialLoadSet.LOAD_ALL, callback: Callable[[], None] = None)
- def reopen()
- def save(on_save_done: Optional[Callable[[bool, str], None]] = None, exit = False, dialog_options = DialogOptions.NONE)
- def save_as(flatten, on_save_done: Optional[Callable[[bool, str], None]] = None)
- def close(on_closed: Optional[Callable[[], None]] = None)
- def save_layers(new_root_path, dirty_layers, on_save_done, create_checkpoint = True, checkpoint_comment = '')
- def prompt_if_unsaved_stage(job: Callable[[], None])
- def add_reference(is_payload = False)
- def register_open_stage_addon(callback)
- def register_open_stage_complete(callback)

## Variables

- IGNORE_UNSAVED_STAGE: str
