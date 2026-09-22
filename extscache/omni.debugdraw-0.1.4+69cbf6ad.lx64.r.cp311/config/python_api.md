# Public API for module omni.debugdraw:

## Classes

- class IDebugDraw
  - def draw_box(self, box_pos: carb._carb.Float3, box_rotation: carb._carb.Float4, box_size: carb._carb.Float3, color: int, line_width: float = 1.0)
  - def draw_line(self, start_pos: carb._carb.Float3, start_color: int, start_width: float, end_pos: carb._carb.Float3, end_color: int, end_width: float)
  - def draw_line(self, start_pos: carb._carb.Float3, start_color: int, end_pos: carb._carb.Float3, end_color: int)
  - def draw_lines(self, lines_list: list)
  - def draw_point(self, pos: carb._carb.Float3, color: int, width: float = 1.0)
  - def draw_points(self, points_list: list)
  - def draw_sphere(self, sphere_pos: carb._carb.Float3, sphere_radius: float, color: int, line_width: float = 1.0, tesselation: int = 32)

- class SimplexPoint
  - def __init__(self)
  - [property] def color(self) -> int
  - [color.setter] def color(self, arg0: int)
  - [property] def position(self) -> carb._carb.Float3
  - [position.setter] def position(self, arg0: carb._carb.Float3)
  - [property] def width(self) -> float
  - [width.setter] def width(self, arg0: float)

## Functions

- def get_debug_draw_interface() -> IDebugDraw
- def acquire_debug_draw_interface(plugin_name: str = None, library_path: str = None) -> IDebugDraw
- def release_debug_draw_interface(arg0: IDebugDraw)
