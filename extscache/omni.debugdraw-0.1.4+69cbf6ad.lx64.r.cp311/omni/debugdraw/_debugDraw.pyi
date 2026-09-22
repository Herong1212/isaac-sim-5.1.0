"""pybind11 omni.debugdraw bindings"""
from __future__ import annotations
import omni.debugdraw._debugDraw
import typing
import carb._carb

__all__ = [
    "IDebugDraw",
    "SimplexPoint",
    "acquire_debug_draw_interface",
    "release_debug_draw_interface"
]


class IDebugDraw():
    def draw_box(self, box_pos: carb._carb.Float3, box_rotation: carb._carb.Float4, box_size: carb._carb.Float3, color: int, line_width: float = 1.0) -> None: ...
    @typing.overload
    def draw_line(self, start_pos: carb._carb.Float3, start_color: int, start_width: float, end_pos: carb._carb.Float3, end_color: int, end_width: float) -> None: ...
    @typing.overload
    def draw_line(self, start_pos: carb._carb.Float3, start_color: int, end_pos: carb._carb.Float3, end_color: int) -> None: ...
    def draw_lines(self, lines_list: list) -> None: ...
    def draw_point(self, pos: carb._carb.Float3, color: int, width: float = 1.0) -> None: ...
    def draw_points(self, points_list: list) -> None: ...
    def draw_sphere(self, sphere_pos: carb._carb.Float3, sphere_radius: float, color: int, line_width: float = 1.0, tesselation: int = 32) -> None: ...
    pass
class SimplexPoint():
    """
    SimplexPoint structure.
    """
    def __init__(self) -> None: ...
    @property
    def color(self) -> int:
        """
        :type: int
        """
    @color.setter
    def color(self, arg0: int) -> None:
        pass
    @property
    def position(self) -> carb._carb.Float3:
        """
        :type: carb._carb.Float3
        """
    @position.setter
    def position(self, arg0: carb._carb.Float3) -> None:
        pass
    @property
    def width(self) -> float:
        """
        :type: float
        """
    @width.setter
    def width(self, arg0: float) -> None:
        pass
    pass
def acquire_debug_draw_interface(plugin_name: str = None, library_path: str = None) -> IDebugDraw:
    pass
def release_debug_draw_interface(arg0: IDebugDraw) -> None:
    pass
