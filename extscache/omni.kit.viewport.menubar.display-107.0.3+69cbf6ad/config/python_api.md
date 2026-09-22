# Public API for module omni.kit.viewport.menubar.display:

## Classes

- class ViewportDisplayMenuBarExtension(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def register_custom_setting(self, text: str, setting_path: str)
  - def deregister_custom_setting(self, text: str)
  - def register_custom_category_item(self, category: str, item: BaseCategoryItem, section: str = DEFAULT_SECTION)
  - def deregister_custom_category_item(self, category: str, item: BaseCategoryItem)

## Functions

- def get_instance() -> Optional[ViewportDisplayMenuBarExtension]
