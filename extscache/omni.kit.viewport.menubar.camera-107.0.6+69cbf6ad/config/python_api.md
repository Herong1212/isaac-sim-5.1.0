# Public API for module omni.kit.viewport.menubar.camera:

## Classes

- class AbstractCameraButtonDelegate(AbstractWidgetDelegate)
  - class def get_instances(cls)
  - def __init__(self)
  - def destroy(self)

- class AbstractCameraMenuItemDelegate(AbstractWidgetDelegate)
  - class def get_instances(cls)
  - def __init__(self)
  - def destroy(self)

- class AbstractWidgetDelegate(abc.ABC)
  - def build_widget(self, parent_id: int, viewport_api: ViewportAPI, camera_path: Sdf.Path) -> Optional[ui.Widget]
  - def on_parent_destroyed(self, parent_id: int)
  - def on_camera_path_changed(self, parent_id: int, camera_path: Sdf.Path)
  - def destroy(self)
  - [property] def order(self) -> int

- class ViewportCameraMenuBarExtension(omni.ext.IExt)
  - def __init__(self)
  - def on_startup(self, ext_id)
  - def on_shutdown(self)
  - def register_menu_item_type(self, menu_item_type: Callable[Ellipsis, SingleCameraMenuItemBase])
  - def register_menu_item(self, create_menu_item_fn: Callable[['viewport_context', ui.Menu], None], order: int = 0)
  - def deregister_menu_item(self, create_menu_item_fn: Callable[['viewport_context', ui.Menu], None])

- class SingleCameraMenuItemBase(ui.MenuItem)
  - def __init__(self, camera_path: Sdf.Path, viewport_api: ViewportAPI, lock_model: ui.AbstractValueModel, root: ui.Menu, triggered_fn: Callable, widget_delegate_manager: CameraWidgetDelegateManager, hotkey_text: str = '', show_hotkey_placeholder: bool = False)
  - [property] def camera_path(self) -> Sdf.Path
  - [property] def viewport_api(self) -> ViewportAPI
  - def destroy(self)
  - def set_checked(self, checked: bool)

## Functions

- def get_instance() -> Optional[ViewportCameraMenuBarExtension]
