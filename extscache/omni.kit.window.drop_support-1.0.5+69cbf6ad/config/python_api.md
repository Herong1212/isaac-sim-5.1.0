# Public API for module omni.kit.window.drop_support:

## Classes

- class ExternalDragDrop
  - def __init__(self, window_name: str, drag_drop_fn: callable)
  - def destroy(self)
  - def get_current_mouse_coords(self)
  - def is_window_hovered(self, pos_x, pos_y, window_name)
  - def expand_payload(self, payload)
