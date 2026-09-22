# Public API for module omni.kit.window.popup_dialog:

## Classes

- class MessageDialog(PopupDialog)
  - def __init__(self, width: int = 400, parent: ui.Widget = None, message: str = '', title: str = None, ok_handler: Callable[[AbstractDialog], None] = None, cancel_handler: Callable[[AbstractDialog], None] = None, ok_label: str = 'Ok', cancel_label: str = 'Cancel', disable_okay_button: bool = False, disable_cancel_button: bool = False, warning_message: Optional[str] = None)
  - def set_message(self, message: str)
  - def destroy(self)

- class MessageWidget
  - def __init__(self, message: str = '')
  - def set_message(self, message: str)
  - def destroy(self)

- class InputDialog(PopupDialog)
  - def __init__(self, width: int = 400, parent: ui.Widget = None, message: str = None, title: str = None, ok_handler: Callable[[AbstractDialog], None] = None, cancel_handler: Callable[[AbstractDialog], None] = None, ok_label: str = 'Ok', cancel_label: str = 'Cancel', input_cls: ui.AbstractField = None, pre_label: str = None, post_label: str = None, default_value: str = None, warning_message: Optional[str] = None)
  - def get_value(self) -> Any
  - def destroy(self)

- class InputWidget
  - def __init__(self, message: str = None, input_cls: ui.AbstractField = None, pre_label: str = None, post_label: str = None, default_value: Any = None)
  - def get_value(self) -> Any
  - def destroy(self)

- class FormDialog(PopupDialog)
  - FieldDef: Unknown
  - def __init__(self, width: int = 400, parent: ui.Widget = None, message: str = None, title: str = None, ok_handler: Callable[[AbstractDialog], None] = None, cancel_handler: Callable[[AbstractDialog], None] = None, ok_label: str = 'Ok', cancel_label: str = 'Cancel', field_defs: List[FieldDef] = None, input_width: int = 250)
  - def show(self, offset_x: int = 0, offset_y: int = 0, parent: ui.Widget = None)
  - def get_field(self, name: str) -> ui.AbstractField
  - def get_value(self, name: str) -> Union[str, int, float, bool]
  - def get_values(self) -> dict
  - def reset_values(self)
  - def destroy(self)

- class FormWidget
  - def __init__(self, message: str = None, field_defs: List[FormDialog.FieldDef] = [])
  - def focus(self)
  - def get_field(self, name: str) -> ui.AbstractField
  - def get_value(self, name: str) -> Union[str, int, float, bool]
  - def get_values(self) -> dict
  - def reset_values(self)
  - def destroy(self)

- class OptionsDialog(PopupDialog)
  - FieldDef: Unknown
  - def __init__(self, width: int = 400, parent: ui.Widget = None, message: str = None, title: str = None, ok_handler: Callable[[AbstractDialog], None] = None, cancel_handler: Callable[[AbstractDialog], None] = None, ok_label: str = 'Ok', cancel_label: str = 'Cancel', field_defs: List[FieldDef] = None, value_changed_fn: Callable = None, radio_group: bool = False)
  - def get_value(self, name: str) -> bool
  - def get_values(self) -> Dict
  - def get_choice(self) -> str
  - def destroy(self)

- class OptionsWidget
  - def __init__(self, message: str = None, field_defs: List[OptionsDialog.FieldDef] = [], value_changed_fn: Callable = None, radio_group: bool = False)
  - def get_values(self) -> dict
  - def get_value(self, name: str) -> bool
  - def get_choice(self) -> str
  - def destroy(self)

- class OptionsMenu(PopupDialog)
  - FieldDef: Unknown
  - def __init__(self, width: int = 400, parent: ui.Widget = None, title: str = None, ok_handler: Callable[[AbstractDialog], None] = None, cancel_handler: Callable[[AbstractDialog], None] = None, ok_label: str = 'Ok', cancel_label: str = 'Cancel', field_defs: List[FieldDef] = None, value_changed_fn: Callable = None)
  - def get_values(self) -> dict
  - def get_value(self, name: str) -> bool
  - def set_value(self, name: str, value: bool)
  - def reset_values(self)
  - def destroy(self)

- class OptionsMenuWidget
  - def __init__(self, title: str = None, field_defs: List[OptionsMenu.FieldDef] = [], value_changed_fn: Callable = None, build_ui: bool = True)
  - def build_ui(self)
  - def get_value(self, name: str) -> bool
  - def get_values(self) -> dict
  - def set_value(self, name: str, value: bool)
  - def reset_values(self)
  - def destroy(self)

- class PopupDialog(AbstractDialog)
  - WINDOW_FLAGS: Unknown
  - def __init__(self, width: int = 400, parent: ui.Widget = None, title: str = None, ok_handler: Callable[[AbstractDialog], None] = None, cancel_handler: Callable[[AbstractDialog], None] = None, ok_label: str = 'Ok', cancel_label: str = 'Cancel', hide_title_bar: bool = False, modal: bool = False, warning_message: Optional[str] = None)
  - def show(self, offset_x: int = 0, offset_y: int = 0, parent: ui.Widget = None, recreate_window: bool = False)
  - def hide(self)
  - [property] def position_x(self)
  - [property] def position_y(self)
  - [property] def window(self)
  - def set_okay_clicked_fn(self, ok_handler: Callable[[AbstractDialog], None])
  - def set_cancel_clicked_fn(self, cancel_handler: Callable[[AbstractDialog], None])
  - def destroy(self)
