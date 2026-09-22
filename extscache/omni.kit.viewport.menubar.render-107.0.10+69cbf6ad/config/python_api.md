# Public API for module omni.kit.viewport.menubar.render:

## Classes

- class ViewportRenderMenuBarExtension(omni.ext.IExt)
  - def on_startup(self, ext_id)
  - def register_menu_item_type(self, menu_item_type: Callable[Ellipsis, SingleRenderMenuItemBase])
  - def on_shutdown(self)

- class SingleRenderMenuItemBase(ui.MenuItem)
  - def __init__(self, display_name: str, engine_name: str, hd_engine_renderer: HdEngineRenderer, hd_renderer: HdRenderer, viewport_api: ViewportAPI, enabled: bool, checked: bool, hide_on_click: bool, triggered_fn: Callable, hotkey_text: str = '', show_hotkey_placeholder: bool = False)
  - def destroy(self)
  - [property] def hd_renderer(self) -> HdRenderer
  - [property] def hd_engine_renderer(self) -> HdEngineRenderer
  - [property] def engine_name(self) -> str
  - [property] def viewport_api(self) -> ViewportAPI
  - def set_checked(self, checked: bool)

- class SingleRenderMenuItem(SingleRenderMenuItemBase)

## Functions

- def get_instance() -> Optional[ViewportRenderMenuBarExtension]
