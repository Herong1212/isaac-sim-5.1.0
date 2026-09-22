# Public API for module omni.kit.window.stats:

## Classes

- class Extension(omni.ext.IExt, MenuHelperExtension)
  - class ComboBoxItem(omni.ui.AbstractItem)
    - def __init__(self, text)
  - class ComboBoxModel(omni.ui.AbstractItemModel)
    - def __init__(self)
    - def destroy(self)
    - def get_item_children(self, item)
    - def get_item_value_model(self, item, column_id)
    - def get_current_scope_index(self)
  - def __init__(self)
  - def get_name(self)
  - def on_startup(self)
  - def on_shutdown(self)
