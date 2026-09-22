# Public API for module omni.kit.viewport_widgets_manager:

## Classes

- class ViewportWidgetsManagerExtension(omni.ext.IExt)
  - def on_startup(self)
  - def on_shutdown(self)
  - def add_widget(self, prim_path: Sdf.Path, widget: WidgetProvider, alignment = WidgetAlignment.CENTER)
  - def remove_widget(self, widget_id)

- class WidgetAlignment
  - CENTER: int
  - BOTTOM: int
  - TOP: int

- class WidgetProvider
  - def build_widget(self, window)

## Functions

- def add_widget(prim_path: Union[str, Sdf.Path], widget: WidgetProvider, alignment = WidgetAlignment.CENTER)
- def remove_widget(widget_id)
