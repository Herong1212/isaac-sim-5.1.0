# Public API for module omni.graph.window.action:

## Classes

- class ActionGraphExtension(omni.ext.IExt)
  - WINDOW_NAME: str
  - MENU_PATH: str
  - def __init__(self)
  - def on_startup(self, ext_id: str)
  - def on_shutdown(self)
  - def show_window(self, menu, value)
  - static def show_graph(prim_list: List[Usd.Prim])
  - static def add_node(mime_data: str, is_drop: bool = True)
