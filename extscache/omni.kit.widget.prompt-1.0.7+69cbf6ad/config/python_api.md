# Public API for module omni.kit.widget.prompt:

## Classes

- class Prompt
  - def __init__(self, title, text, ok_button_text = 'OK', cancel_button_text = None, middle_button_text = None, middle_2_button_text = None, ok_button_fn = None, cancel_button_fn = None, middle_button_fn = None, middle_2_button_fn = None, modal = False, on_closed_fn = None, shortcut_keys = True, no_title_bar = False, width = None, height = None, callback_addons: List = [])
  - def destroy(self)
  - [property] def visible(self)
  - [visible.setter] def visible(self, value: bool)
  - def show(self)
  - def hide(self)
  - def is_visible(self) -> bool
  - def set_text(self, text)
  - def set_confirm_fn(self, on_ok_button_clicked)
  - def set_cancel_fn(self, on_cancel_button_clicked)
  - def set_middle_button_fn(self, on_middle_button_clicked)
  - def set_middle_2_button_fn(self, on_middle_2_button_clicked)
  - def set_on_closed_fn(self, on_on_closed)

- class PromptManager
  - static def on_startup()
  - static def on_shutdown()
  - static def query_prompt_by_title(title: str)
  - static def add_prompt(prompt: Prompt)
  - static def remove_prompt(prompt: Prompt)
  - static def post_simple_prompt(title: str, message: str, ok_button_info: PromptButtonInfo = PromptButtonInfo('OK', None), cancel_button_info: PromptButtonInfo = None, middle_button_info: PromptButtonInfo = None, middle_2_button_info: PromptButtonInfo = None, on_window_closed_fn: Callable[[], None] = None, modal = True, shortcut_keys = True, standalone = True, no_title_bar = False, width = None, height = None, callback_addons: List = [])

- class PromptButtonInfo
  - def __init__(self, name: str, on_button_clicked_fn: Callable[[], None] = None)
  - [property] def name(self) -> str
  - [property] def on_button_clicked_fn(self) -> Callable[[], None]
