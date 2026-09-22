# Public API for module omni.kit.menu.core:

## Classes

- class DictReadOnly(collections.abc.Mapping)
  - def __init__(self, data)
  - def copy(self)
  - def merge_dict(self, other)

- class IconMenuBaseDelegate(ui.MenuDelegate)
  - def __init__(self, **kwargs)
  - def get_style(self)
  - def load_settings(self, extension)
  - def build_title(self, item)
  - def build_status(self, item)
  - def build_item(self, item: ui.Widget)

- class uiMenu(ui.Menu)
  - def __init__(self, *args, **kwargs)

- class uiMenuItem(ui.MenuItem)
  - def __init__(self, *args, **kwargs)

- class MenuEventType
  - ACTIVATE: int

## Functions

- def has_delegate_func(delegate, func_name)
