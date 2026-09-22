# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from __future__ import annotations

import weakref
from collections import defaultdict
from typing import TYPE_CHECKING
from weakref import ProxyType

if TYPE_CHECKING:
    from .model import AbstractTransformManipulatorModel
    from .toolbar_registry import ToolbarRegistry
    from .toolbar_tool import ToolbarTool

from pathlib import Path
from typing import Any, DefaultDict, Dict, List, Type

import carb.dictionary
import carb.settings
import omni.kit.app
import omni.ui as ui
from omni.ui import color as cl
from omni.ui import scene as sc

from .gestures import (
    DummyClickGesture,
    DummyGesture,
    HighlightControl,
    HighlightGesture,
    RotationGesture,
    ScaleGesture,
    TranslateGesture,
)
from .settings_constants import c
from .simple_transform_model import SimpleTransformModel
from .style import abgr_to_color, get_default_style, get_default_toolbar_style, update_style
from .types import Axis, Operation

ARROW_WIDTH = 4
ARROW_HEIGHT = 14
ARROW_P = [
    [ARROW_WIDTH, ARROW_WIDTH, 0],
    [-ARROW_WIDTH, ARROW_WIDTH, 0],
    [0, 0, ARROW_HEIGHT],
    #
    [ARROW_WIDTH, -ARROW_WIDTH, 0],
    [-ARROW_WIDTH, -ARROW_WIDTH, 0],
    [0, 0, ARROW_HEIGHT],
    #
    [ARROW_WIDTH, ARROW_WIDTH, 0],
    [ARROW_WIDTH, -ARROW_WIDTH, 0],
    [0, 0, ARROW_HEIGHT],
    #
    [-ARROW_WIDTH, ARROW_WIDTH, 0],
    [-ARROW_WIDTH, -ARROW_WIDTH, 0],
    [0, 0, ARROW_HEIGHT],
    #
    [ARROW_WIDTH, ARROW_WIDTH, 0],
    [-ARROW_WIDTH, ARROW_WIDTH, 0],
    [-ARROW_WIDTH, -ARROW_WIDTH, 0],
    [ARROW_WIDTH, -ARROW_WIDTH, 0],
]

ARROW_VC = [3, 3, 3, 3, 4]
ARROW_VI = [i for i in range(sum(ARROW_VC))]

LINE_THICKNESS = 2

TOOLBAR_WIDGET_HEIGHT = 114


class TransformManipulator(sc.Manipulator):
    """A manipulator for transforming objects in 3D space.

    This manipulator is used to interactively translate, rotate, and scale objects within a 3D scene
    using various gizmos and widgets. It can be customized with different models, styles, and gestures.

    Args:
        size (float): The initial size of the manipulator, affecting its visual representation.
        enabled (bool): If False, the manipulator will be created but disabled (invisible).
        axes (Axis): Specifies which axes to enable for the manipulator. Use this to create 2D or 1D manipulators.
        model (AbstractTransformManipulatorModel): The model for the manipulator. If None, a default SimpleTransformModel will be created.
        style (Dict): Overrides the default style of the manipulator.
        gestures (List[sc.ManipulatorGesture]): The list of gestures associated with the manipulator.
        tool_registry (ToolbarRegistry): The registry holding the toolbar tools associated with the manipulator.
        tool_button_additional_payload (Dict[str, Any]): Additional payload to be passed into the toolbar's context menu.
        tools_default_collapsed (bool | None): Determines whether the toolbar should be collapsed by default."""

    def __init__(
        self,
        size: float = 1.0,
        enabled: bool = True,
        axes: Axis = Axis.ALL,
        model: AbstractTransformManipulatorModel = None,
        style: Dict = {},
        gestures: List[sc.ManipulatorGesture] = [],
        tool_registry: ToolbarRegistry = None,
        tool_button_additional_payload: Dict[str, Any] = {},
        tools_default_collapsed: bool | None = None,
    ):
        """Initializes a new instance of the TransformManipulator."""

        if model is None:
            model = SimpleTransformModel()
        super().__init__(model=model, gestures=gestures)

        self._size: float = size
        self._enabled: bool = enabled
        self._transform = None
        self._transform_screen = None
        self._translate_gizmo = None
        self._rotation_gizmo = None
        self._scale_gizmo = None
        self._toolbar_root = None
        self._toolbar_height_offset_transform = None
        self._toolbar_collapsable_frame = None
        self._toolbars: Dict[Operation, ui.Frame] = {}
        self._toolbar_widget: sc.Widget = None
        self._header_line = None
        self._tools_stacks: Dict[Operation, ui.HStack] = {}
        self._tools: List[ToolbarTool] = []
        self._operation = None

        self._style = get_default_style()
        self._style = update_style(self._style, style)

        self._settings = carb.settings.get_settings()
        self._dict = carb.dictionary.get_dictionary()

        self._scale_sub = self._settings.subscribe_to_node_change_events(
            c.MANIPULATOR_SCALE_SETTING, self._on_scale_changed
        )
        self._scale = self._settings.get(c.MANIPULATOR_SCALE_SETTING)

        self._thickness_sub = self._settings.subscribe_to_node_change_events(
            c.INTERSECTION_THICKNESS_SETTING, self._on_intersection_thickness_changed
        )

        self._free_rotation_enabled_sub = self._settings.subscribe_to_node_change_events(
            c.FREE_ROTATION_ENABLED_SETTING, self._on_free_rotation_enabled_changed
        )

        self._axes = axes

        self._tool_button_additional_payload = tool_button_additional_payload
        self._toolbar_collapsed = (
            tools_default_collapsed
            if tools_default_collapsed is not None
            else self._settings.get(c.TOOLS_DEFAULT_COLLAPSED_SETTING)
        )
        self._tool_registry = tool_registry
        self._tool_registry_sub = None
        if self._tool_registry:
            self._tool_registry_sub = self._tool_registry.subscribe_to_registry_change(self._on_toolbar_changed)

        if self.model:
            if self._enabled:
                self.model.widget_enabled()

    def __del__(self):
        """Releases all resources and subscriptions of the TransformManipulator on deletion."""
        self.destroy()

    def destroy(self):
        """Cleanly destroys the TransformManipulator, unsubscribing from all settings and destroying tools."""
        if self._scale_sub:
            self._settings.unsubscribe_to_change_events(self._scale_sub)
            self._scale_sub = None

        if self._thickness_sub:
            self._settings.unsubscribe_to_change_events(self._thickness_sub)
            self._thickness_sub = None

        if self._free_rotation_enabled_sub:
            self._settings.unsubscribe_to_change_events(self._free_rotation_enabled_sub)
            self._free_rotation_enabled_sub = None

        if self._tool_registry and self._tool_registry_sub:
            self._tool_registry_sub.release()
            self._tool_registry_sub = None

        for tool in self._tools:
            tool.destroy()
        self._tools.clear()

        self._toolbar_widget = None

        for key, stack in self._tools_stacks.items():
            stack.set_computed_content_size_changed_fn(None)
        self._tools_stacks.clear()

        self.enabled = False

    def on_build(self):
        """Builds the TransformManipulator's structure representation. Should be called within a SceneView.scene scope if build_items_on_init is set to False."""
        self._transform = sc.Transform(visible=self.enabled)
        with self._transform:
            final_size = self._get_final_size()
            self._transform_screen = sc.Transform(
                transform=sc.Matrix44.get_scale_matrix(final_size, final_size, final_size), scale_to=sc.Space.SCREEN
            )
            with self._transform_screen:
                self._create_translate_manipulator()
                self._create_rotation_manipulator()
                self._create_scale_manipulator()

            with sc.Transform(scale_to=sc.Space.SCREEN):
                self._create_toolbar()

        self._translate_gizmo.visible = True

        self._update_axes_visibility()
        self._update_from_model()

    @property
    def enabled(self) -> bool:
        """Gets the enabled state of the TransformManipulator.

        Returns:
            bool: The enabled state of the TransformManipulator."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        """Sets the enabled state of the TransformManipulator."""
        if value != self._enabled:
            if self._transform:
                self._transform.visible = value
            self._enabled = value
            if self.model:
                if self._enabled:
                    self.model.widget_enabled()
                else:
                    self.model.widget_disabled()

    @property
    def size(self) -> float:
        """Gets the size of the TransformManipulator.

        Returns:
            float: The current size of the TransformManipulator."""
        return self._size

    @size.setter
    def size(self, value: float):
        """Sets the size of the TransformManipulator."""
        if self._size != value:
            self._size = value
            self._update_manipulator_final_size()

    @property
    def axes(self) -> float:
        """Gets the enabled axes for the TransformManipulator.

        Returns:
            Axis: The enabled axes of the TransformManipulator."""
        return self._axes

    @axes.setter
    def axes(self, value: float):
        """Sets the enabled axes for the TransformManipulator."""
        if self._axes != value:
            self._axes = value
            self._update_axes_visibility()

    @property
    def style(self) -> Dict:
        """Gets the style dictionary for the TransformManipulator.

        Returns:
            Dict: The current style settings of the TransformManipulator."""
        return self._style

    @style.setter
    def style(self, value: Dict):
        """Sets the style dictionary for the TransformManipulator."""
        default_style = get_default_style()
        style = update_style(default_style, value)

        if self._style != style:
            if self._transform:
                self._translate_line_x.color = abgr_to_color(style["Translate.Axis::x"]["color"])
                self._translate_line_y.color = abgr_to_color(style["Translate.Axis::y"]["color"])
                self._translate_line_z.color = abgr_to_color(style["Translate.Axis::z"]["color"])

                vert_count = len(ARROW_VI)
                self._translate_arrow_x.colors = [abgr_to_color(style["Translate.Axis::x"]["color"])] * vert_count
                self._translate_arrow_y.colors = [abgr_to_color(style["Translate.Axis::y"]["color"])] * vert_count
                self._translate_arrow_z.colors = [abgr_to_color(style["Translate.Axis::z"]["color"])] * vert_count

                self._translate_plane_yz.color = abgr_to_color(style["Translate.Axis::x"]["color"])
                self._translate_plane_zx.color = abgr_to_color(style["Translate.Axis::y"]["color"])
                self._translate_plane_xy.color = abgr_to_color(style["Translate.Axis::z"]["color"])

                self._translate_point.color = abgr_to_color(style["Translate.Point"]["color"])
                self._translate_point_square.color = abgr_to_color(style["Translate.Point"]["color"])
                use_point = style["Translate.Point"]["type"] == "point"
                self._translate_point.visible = use_point
                self._translate_point_square.visible = not use_point

                self._translate_point_focal_transform.visible = style["Translate.Focal"]["visible"]

                self._rotation_arc_x.color = abgr_to_color(style["Rotate.Arc::x"]["color"])
                self._rotation_arc_y.color = abgr_to_color(style["Rotate.Arc::y"]["color"])
                self._rotation_arc_z.color = abgr_to_color(style["Rotate.Arc::z"]["color"])
                self._rotation_arc_screen.color = abgr_to_color(style["Rotate.Arc::screen"]["color"])

                self._scale_line_x.color = abgr_to_color(style["Scale.Axis::x"]["color"])
                self._scale_line_y.color = abgr_to_color(style["Scale.Axis::y"]["color"])
                self._scale_line_z.color = abgr_to_color(style["Scale.Axis::z"]["color"])

                self._scale_point_x.color = abgr_to_color(style["Scale.Axis::x"]["color"])
                self._scale_point_y.color = abgr_to_color(style["Scale.Axis::y"]["color"])
                self._scale_point_z.color = abgr_to_color(style["Scale.Axis::z"]["color"])

                self._scale_plane_yz.color = abgr_to_color(style["Scale.Axis::x"]["color"])
                self._scale_plane_zx.color = abgr_to_color(style["Scale.Axis::y"]["color"])
                self._scale_plane_xy.color = abgr_to_color(style["Scale.Axis::z"]["color"])

                self._scale_point.color = abgr_to_color(style["Scale.Point"]["color"])

            self._style = style

    @sc.Manipulator.model.setter
    def model(self, model):
        """Sets the model associated with the TransformManipulator."""
        if self.model is not None and self.enabled:
            self.model.widget_disabled()

        sc.Manipulator.model.fset(self, model)

        if self.model is not None and self.enabled:
            self.model.widget_enabled()

    @property
    def tool_registry(self) -> ToolbarRegistry:
        """Gets the ToolbarRegistry associated with the TransformManipulator.

        Returns:
            ToolbarRegistry: The current ToolbarRegistry associated with the TransformManipulator."""
        return self._tool_registry

    @tool_registry.setter
    def tool_registry(self, value: ToolbarRegistry):
        """Sets the ToolbarRegistry associated with the TransformManipulator."""
        if self._tool_registry != value:
            if self._tool_registry_sub:
                self._tool_registry_sub.release()
                self._tool_registry_sub = None

            self._tool_registry = value
            if self._tool_registry:
                self._tool_registry_sub = self._tool_registry.subscribe_to_registry_change(self._on_toolbar_changed)

    @property
    def toolbar_visible(self) -> bool:
        """Gets the visibility state of the TransformManipulator's toolbar.

        Returns:
            bool: Whether the toolbar is currently visible."""
        if self._toolbar_root:
            return self._toolbar_root.visible
        return False

    @toolbar_visible.setter
    def toolbar_visible(self, value: bool):
        """Sets the visibility state of the TransformManipulator's toolbar."""
        if self._toolbar_root:
            self._toolbar_root.visible = value

    def refresh_toolbar(self):
        """Refreshes the toolbar, forcing it to redraw."""
        if self._toolbar_widget:
            self._toolbar_widget.invalidate()

    #############################################
    # Beginning of internal functions. Do not use.
    #############################################

    def _create_translate_manipulator(self):
        """Internally creates the translation manipulator components within the TransformManipulator's structure"""
        self._translate_gizmo = sc.Transform()
        self._translate_gizmo.visible = False

        AXIS_LEN = 100
        RECT_SIZE = 50
        POINT_RADIUS = 7
        FOCAL_SIZE = 16
        intersection_thickness = self._settings.get(c.INTERSECTION_THICKNESS_SETTING)

        with self._translate_gizmo:
            # Arrows
            def make_arrow(
                rot,
                translate,
                color,
            ):
                vert_count = len(ARROW_VI)
                with sc.Transform(
                    transform=sc.Matrix44.get_translation_matrix(translate[0], translate[1], translate[2])
                    * sc.Matrix44.get_rotation_matrix(rot[0], rot[1], rot[2], True)
                ):
                    return sc.PolygonMesh(ARROW_P, [color] * vert_count, ARROW_VC, ARROW_VI)

            self._translate_arrow_x = make_arrow(
                (0, 90, 0), (AXIS_LEN - ARROW_HEIGHT / 2, 0, 0), abgr_to_color(self.style["Translate.Axis::x"]["color"])
            )
            self._translate_arrow_y = make_arrow(
                (-90, 0, 0),
                (0, AXIS_LEN - ARROW_HEIGHT / 2, 0),
                abgr_to_color(self.style["Translate.Axis::y"]["color"]),
            )
            self._translate_arrow_z = make_arrow(
                (0, 0, 0), (0, 0, AXIS_LEN - ARROW_HEIGHT / 2), abgr_to_color(self.style["Translate.Axis::z"]["color"])
            )

            # Lines
            def make_line(axis, color, arrow):
                line = sc.Line(
                    [v * POINT_RADIUS for v in axis],
                    [v * AXIS_LEN for v in axis],
                    color=color,
                    thickness=LINE_THICKNESS,
                    intersection_thickness=intersection_thickness,
                )

                highlight_ctrl = HighlightControl([line, arrow])
                line.gestures = [
                    TranslateGesture(self, axis, highlight_ctrl),
                    HighlightGesture(highlight_ctrl),
                ]
                return line

            self._translate_line_x = make_line(
                [1, 0, 0], abgr_to_color(self.style["Translate.Axis::x"]["color"]), self._translate_arrow_x
            )
            self._translate_line_y = make_line(
                [0, 1, 0], abgr_to_color(self.style["Translate.Axis::y"]["color"]), self._translate_arrow_y
            )
            self._translate_line_z = make_line(
                [0, 0, 1], abgr_to_color(self.style["Translate.Axis::z"]["color"]), self._translate_arrow_z
            )

            # Rectangles
            def make_plane(axis, color, axis_vec):
                translate = [v * (AXIS_LEN - RECT_SIZE * 0.5) for v in axis_vec]
                with sc.Transform(
                    transform=sc.Matrix44.get_translation_matrix(translate[0], translate[1], translate[2])
                ):
                    highlight_ctrl = HighlightControl()
                    return sc.Rectangle(
                        axis=axis,
                        width=RECT_SIZE / 2,
                        height=RECT_SIZE / 2,
                        color=color,
                        gestures=[TranslateGesture(self, axis_vec, highlight_ctrl), HighlightGesture(highlight_ctrl)],
                    )

            self._translate_plane_yz = make_plane(0, abgr_to_color(self.style["Translate.Axis::x"]["color"]), (0, 1, 1))
            self._translate_plane_zx = make_plane(1, abgr_to_color(self.style["Translate.Axis::y"]["color"]), (1, 0, 1))
            self._translate_plane_xy = make_plane(2, abgr_to_color(self.style["Translate.Axis::z"]["color"]), (1, 1, 0))

            # Points
            with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                use_point = self.style["Translate.Point"]["type"] == "point"
                self._translate_point = sc.Arc(
                    POINT_RADIUS,
                    tesselation=16,
                    color=abgr_to_color(self.style["Translate.Point"]["color"]),
                    visible=use_point,
                )
                highlight_ctrl = HighlightControl(
                    [
                        self._translate_plane_yz,
                        self._translate_plane_zx,
                        self._translate_plane_xy,
                        self._translate_point,
                    ]
                )
                self._translate_point.gestures = [
                    TranslateGesture(self, [1, 1, 1], highlight_ctrl, order=-1),
                    HighlightGesture(highlight_ctrl=highlight_ctrl, order=-1),
                ]

                self._translate_point_square = sc.Rectangle(
                    width=FOCAL_SIZE,
                    height=FOCAL_SIZE,
                    color=abgr_to_color(self.style["Translate.Point"]["color"]),
                    visible=not use_point,
                )

                highlight_ctrl = HighlightControl(
                    [
                        self._translate_plane_yz,
                        self._translate_plane_zx,
                        self._translate_plane_xy,
                        self._translate_point_square,
                    ]
                )
                self._translate_point_square.gestures = [
                    TranslateGesture(self, [1, 1, 1], highlight_ctrl, order=-1),
                    HighlightGesture(highlight_ctrl=highlight_ctrl, order=-1),
                ]

                show_focal = self.style["Translate.Focal"]["visible"]
                self._translate_point_focal_transform = sc.Transform(visible=show_focal)
                with self._translate_point_focal_transform:

                    def create_corner_line(begin, end):
                        sc.Line(
                            begin,
                            end,
                            color=abgr_to_color(self.style["Translate.Focal"]["color"]),
                            thickness=2,
                        )

                    offset_outer = FOCAL_SIZE
                    offset_inner = FOCAL_SIZE * 0.4
                    v_buffer = [
                        [offset_outer, offset_inner, 0],  # 0
                        [offset_outer, offset_outer, 0],
                        [offset_inner, offset_outer, 0],
                        [-offset_outer, offset_inner, 0],  # 1
                        [-offset_outer, offset_outer, 0],
                        [-offset_inner, offset_outer, 0],
                        [offset_outer, -offset_inner, 0],  # 2
                        [offset_outer, -offset_outer, 0],
                        [offset_inner, -offset_outer, 0],
                        [-offset_outer, -offset_inner, 0],  # 3
                        [-offset_outer, -offset_outer, 0],
                        [-offset_inner, -offset_outer, 0],
                    ]

                    i_buffer = [(0, 1), (1, 2), (3, 4), (4, 5), (6, 7), (7, 8), (9, 10), (10, 11)]
                    for i in i_buffer:
                        create_corner_line(v_buffer[i[0]], v_buffer[i[1]])

    def _create_rotation_manipulator(self):
        """Internally creates the rotation manipulator components within the TransformManipulator's structure."""
        self._rotation_gizmo = sc.Transform()
        self._rotation_gizmo.visible = False

        ARC_RADIUS = 100
        intersection_thickness = self._settings.get(c.INTERSECTION_THICKNESS_SETTING)

        with self._rotation_gizmo:

            def make_arc(
                radius, axis_vec, color, culling: sc.Culling, wireframe: bool = True, highlight_color=None, **kwargs
            ):
                viz_color = [1.0, 1.0, 0.0, 0.3]
                viz_arc = sc.Arc(radius, tesselation=36 * 3, color=viz_color, visible=False, **kwargs)
                highlight_ctrl = HighlightControl(color=highlight_color)
                return sc.Arc(
                    radius,
                    wireframe=wireframe,
                    tesselation=36 * 3,
                    thickness=LINE_THICKNESS,
                    intersection_thickness=intersection_thickness,
                    culling=culling,
                    color=color,
                    gestures=[
                        RotationGesture(self, axis_vec, viz_arc, highlight_ctrl),
                        HighlightGesture(highlight_ctrl),
                    ],
                    **kwargs,
                )

            self._rotation_arc_x = make_arc(
                ARC_RADIUS, [1, 0, 0], abgr_to_color(self.style["Rotate.Arc::x"]["color"]), sc.Culling.BACK, axis=0
            )
            self._rotation_arc_y = make_arc(
                ARC_RADIUS, [0, 1, 0], abgr_to_color(self.style["Rotate.Arc::y"]["color"]), sc.Culling.BACK, axis=1
            )
            self._rotation_arc_z = make_arc(
                ARC_RADIUS, [0, 0, 1], abgr_to_color(self.style["Rotate.Arc::z"]["color"]), sc.Culling.BACK, axis=2
            )

            self._screen_space_rotation_transform = sc.Transform(look_at=sc.Transform.LookAt.CAMERA)
            with self._screen_space_rotation_transform:
                self._rotation_arc_screen = make_arc(
                    ARC_RADIUS + 20,
                    [0, 0, 0],
                    abgr_to_color(self.style["Rotate.Arc::screen"]["color"]),
                    sc.Culling.NONE,
                )

                self._rotation_arc_free = make_arc(
                    ARC_RADIUS - 5,
                    None,
                    abgr_to_color(self.style["Rotate.Arc::free"]["color"]),
                    sc.Culling.NONE,
                    False,
                    highlight_color=cl("#8F8F8F8F"),
                )
                self._rotation_arc_free.visible = self._settings.get(c.FREE_ROTATION_ENABLED_SETTING)

    def _create_scale_manipulator(self):
        """Internally creates the scale manipulator components within the TransformManipulator's structure."""
        AXIS_LEN = 100
        RECT_SIZE = 50
        POINT_RADIUS = 7
        intersection_thickness = self._settings.get(c.INTERSECTION_THICKNESS_SETTING)

        self._scale_gizmo = sc.Transform()
        self._scale_gizmo.visible = False

        with self._scale_gizmo:
            # Point
            def make_point(translate, color):
                scale_point_tr = sc.Transform(
                    transform=sc.Matrix44.get_translation_matrix(translate[0], translate[1], translate[2])
                )
                with scale_point_tr:
                    with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                        scale_point = sc.Arc(POINT_RADIUS, tesselation=16, color=color)
                return (scale_point_tr, scale_point)

            (scale_point_tr_x, self._scale_point_x) = make_point(
                (AXIS_LEN, 0, 0), abgr_to_color(self.style["Scale.Axis::x"]["color"])
            )
            (scale_point_tr_y, self._scale_point_y) = make_point(
                (0, AXIS_LEN, 0), abgr_to_color(self.style["Scale.Axis::y"]["color"])
            )
            (scale_point_tr_z, self._scale_point_z) = make_point(
                (0, 0, AXIS_LEN), abgr_to_color(self.style["Scale.Axis::z"]["color"])
            )

            # Line
            def make_line(axis_vec, color, point_tr, point):
                line_begin = [v * POINT_RADIUS for v in axis_vec]
                line_end = [v * AXIS_LEN for v in axis_vec]
                viz_line = sc.Line(line_begin, line_end, color=[0.5, 0.5, 0.5, 0.5], thickness=2)

                scale_line = sc.Line(
                    line_begin,
                    line_end,
                    color=color,
                    thickness=LINE_THICKNESS,
                    intersection_thickness=intersection_thickness,
                )
                highlight_ctrl = HighlightControl([scale_line, point])
                scale_line.gestures = [
                    ScaleGesture(self, axis_vec, highlight_ctrl, [viz_line], [point_tr]),
                    HighlightGesture(highlight_ctrl),
                ]

                return (viz_line, scale_line)

            (line_x, self._scale_line_x) = make_line(
                [1, 0, 0], abgr_to_color(self.style["Scale.Axis::x"]["color"]), scale_point_tr_x, self._scale_point_x
            )
            (line_y, self._scale_line_y) = make_line(
                [0, 1, 0], abgr_to_color(self.style["Scale.Axis::y"]["color"]), scale_point_tr_y, self._scale_point_y
            )
            (line_z, self._scale_line_z) = make_line(
                [0, 0, 1], abgr_to_color(self.style["Scale.Axis::z"]["color"]), scale_point_tr_z, self._scale_point_z
            )

            # Rectangles
            def make_plane(axis, axis_vec, color, lines, points):
                axis_vec_t = [v * (AXIS_LEN - RECT_SIZE * 0.5) for v in axis_vec]
                with sc.Transform(
                    transform=sc.Matrix44.get_translation_matrix(axis_vec_t[0], axis_vec_t[1], axis_vec_t[2])
                ):
                    highlight_ctrl = HighlightControl()
                    return sc.Rectangle(
                        axis=axis,
                        width=RECT_SIZE * 0.5,
                        height=RECT_SIZE * 0.5,
                        color=color,
                        gestures=[
                            ScaleGesture(self, axis_vec, highlight_ctrl, lines, points),
                            HighlightGesture(highlight_ctrl),
                        ],
                    )

            self._scale_plane_yz = make_plane(
                0,
                (0, 1, 1),
                abgr_to_color(self.style["Scale.Axis::x"]["color"]),
                [line_y, line_z],
                [scale_point_tr_y, scale_point_tr_z],
            )
            self._scale_plane_zx = make_plane(
                1,
                (1, 0, 1),
                abgr_to_color(self.style["Scale.Axis::y"]["color"]),
                [line_x, line_z],
                [scale_point_tr_x, scale_point_tr_z],
            )
            self._scale_plane_xy = make_plane(
                2,
                (1, 1, 0),
                abgr_to_color(self.style["Scale.Axis::z"]["color"]),
                [line_x, line_y],
                [scale_point_tr_x, scale_point_tr_y],
            )

            # Points
            with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                highlight_ctrl = HighlightControl()
                self._scale_point = sc.Arc(
                    POINT_RADIUS, tesselation=16, color=abgr_to_color(self.style["Scale.Point"]["color"])
                )

                highlight_ctrl = HighlightControl(
                    [
                        self._scale_plane_yz,
                        self._scale_plane_zx,
                        self._scale_plane_xy,
                        self._scale_point,
                    ]
                )

                self._scale_point.gestures = [
                    ScaleGesture(
                        self,
                        [1, 1, 1],
                        highlight_ctrl,
                        [line_x, line_y, line_z],
                        [scale_point_tr_x, scale_point_tr_y, scale_point_tr_z],
                        order=-1,
                    ),
                    HighlightGesture(highlight_ctrl, order=-1),
                ]

    def _create_toolbar(self):
        """Internally creates the toolbar components within the TransformManipulator's structure."""
        self._toolbar_root = sc.Transform(look_at=sc.Transform.LookAt.CAMERA)
        self._build_tools_widgets(self._toolbar_root)

    def _get_toolbar_height_offset(self):
        """Calculates the height offset for the toolbar based on the current size of the TransformManipulator.

        Returns:
            float: The calculated height offset for the toolbar."""
        final_size = self._get_final_size()

        return -120 * final_size - TOOLBAR_WIDGET_HEIGHT

    def _build_tools_widgets(self, root: sc.Transform):
        """Internally builds the tools widgets for the TransformManipulator."""
        # clear existing widgets under root

        ICON_FOLDER_PATH = Path(f"{omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)}/data/icons")
        root.clear()
        self._toolbar_widget = None

        if self._tool_registry is None:
            return None

        OPERATIONS = [Operation.TRANSLATE, Operation.ROTATE, Operation.SCALE]

        tools = self._tool_registry.tools
        tools_can_build: DefaultDict[Operation, List[Type[ToolbarTool]]] = defaultdict(list)
        for op in OPERATIONS:
            for tool in tools:
                if tool.can_build(self, op):
                    tools_can_build[op].append(tool)

        # Don't build toolbar if there's no tool
        if len(tools_can_build) == 0:
            return

        with root:
            # values for omni.ui inside of sc.Widget
            CARAT_SIZE = 44
            CRATE_SPACING = 10
            TOOLBAR_HEIGHT = 44
            TOOLBAR_SPACING = 5

            height_offset = self._get_toolbar_height_offset()
            toolbar_to_content_scale = 1.4  # a guesstimate

            toolbar_widget_width = (
                max(max([len(t) for t in tools_can_build.values()]), 3)
                * ((TOOLBAR_HEIGHT + TOOLBAR_SPACING) * toolbar_to_content_scale)
                + TOOLBAR_SPACING
            )

            self._toolbar_height_offset_transform = sc.Transform(
                sc.Matrix44.get_translation_matrix(0, height_offset + TOOLBAR_WIDGET_HEIGHT / 2, 0)
            )
            with self._toolbar_height_offset_transform:
                # create a sc.Rectangle behind the widget to stop the click into Viewport with DummyGesture
                dummy_transform = sc.Transform(sc.Matrix44.get_translation_matrix(0, 0, -1))
                with dummy_transform:
                    dummy_rect = sc.Rectangle(
                        width=toolbar_widget_width,
                        height=TOOLBAR_WIDGET_HEIGHT,
                        color=0x0,
                        gestures=[
                            DummyGesture(self),  # needed for VP1 only
                            DummyClickGesture(mouse_button=0),
                            DummyClickGesture(mouse_button=1),
                            DummyClickGesture(mouse_button=2),
                        ],  # hijack left/right/middle mouse click on the toolbar so it doesn't click into viewport
                    )

                # Build a set of scene items to emulate the tooltip for omni.ui item inside of sc.Widget.
                # This is to workaround chopped off tooltip in sc.Widget OM-49626
                tooltip_style = ui.style.default["Tooltip"]
                tooltip_color = tooltip_style["color"]
                tooltip_bg_color = tooltip_style["background_color"]
                tooltip_border_width = tooltip_style["border_width"]
                with sc.Transform(
                    transform=sc.Matrix44.get_translation_matrix(-toolbar_widget_width / 2, TOOLBAR_HEIGHT, 10)
                ):
                    tooltip_transform = sc.Transform(visible=False)
                    with tooltip_transform:
                        tooltip_label = sc.Label("Tooltip", alignment=ui.Alignment.CENTER, color=tooltip_color, size=16)
                        tooltip_bg_outline = sc.Rectangle(
                            color=tooltip_color,
                            height=0,
                            width=0,
                            wireframe=True,
                        )
                        tooltip_bg = sc.Rectangle(
                            color=tooltip_bg_color,
                            height=0,
                            width=0,
                            thickness=tooltip_border_width,
                        )

                    def update_tooltip(label: str, visible: bool, x_offset: float):
                        tooltip_transform.visible = visible
                        if visible:
                            tooltip_transform.transform = sc.Matrix44.get_translation_matrix(
                                x_offset * toolbar_to_content_scale, 0, 0
                            )
                            padding = 10
                            tooltip_label.text = label
                            # / 1.2 due to no way to get a calculated width of string and not each character has same width
                            tooltip_bg.width = (tooltip_label.size * len(tooltip_label.text) + padding * 2) / 1.2
                            tooltip_bg.height = tooltip_label.size + padding * 2
                            tooltip_bg_outline.width = tooltip_bg.width + tooltip_border_width * 2
                            tooltip_bg_outline.height = tooltip_bg.height + tooltip_border_width * 2

                self._toolbar_widget = sc.Widget(
                    toolbar_widget_width, TOOLBAR_WIDGET_HEIGHT, update_policy=sc.Widget.UpdatePolicy.ON_MOUSE_HOVERED
                )
                with self._toolbar_widget.frame:

                    def build_frame_header(manip: ProxyType[TransformManipulator], collapsed: bool, text: str):
                        header_stack = ui.HStack(spacing=8)
                        with header_stack:
                            with ui.VStack(width=0):
                                ui.Spacer()
                                styles = [
                                    {
                                        "": {"image_url": f"{ICON_FOLDER_PATH}/carat_close.svg"},
                                        ":hovered": {"image_url": f"{ICON_FOLDER_PATH}/carat_close_hover.svg"},
                                        ":pressed": {"image_url": f"{ICON_FOLDER_PATH}/carat_close_hover.svg"},
                                    },
                                    {
                                        "": {"image_url": f"{ICON_FOLDER_PATH}/carat_open.svg"},
                                        ":hovered": {"image_url": f"{ICON_FOLDER_PATH}/carat_open_hover.svg"},
                                        ":pressed": {"image_url": f"{ICON_FOLDER_PATH}/carat_open_hover.svg"},
                                    },
                                ]
                                ui.Image(
                                    width=CARAT_SIZE, height=CARAT_SIZE, style=styles[0] if collapsed else styles[1]
                                )
                                ui.Spacer()
                            if not collapsed:
                                operation = self.model.get_operation()
                                tools_stack = self._tools_stacks.get(operation, None)
                                self._header_line = ui.Line(
                                    width=(
                                        ui.Pixel(tools_stack.computed_width - CARAT_SIZE - CRATE_SPACING)
                                        if tools_stack
                                        else ui.Percent(100)
                                    )
                                )
                                dummy_rect.height = TOOLBAR_WIDGET_HEIGHT
                                dummy_transform.transform = sc.Matrix44.get_translation_matrix(0, 0, -1)
                            else:
                                self._header_line = None
                                ui.Spacer(width=ui.Percent(100))
                                dummy_rect.height = TOOLBAR_WIDGET_HEIGHT * 0.4
                                dummy_transform.transform = sc.Matrix44.get_translation_matrix(
                                    0, TOOLBAR_WIDGET_HEIGHT / 4, -1
                                )

                    with ui.HStack(style=get_default_toolbar_style(), content_clipping=True):
                        self._toolbar_collapsable_frame = ui.CollapsableFrame(
                            build_header_fn=lambda collapsed, text, manip=weakref.proxy(self): build_frame_header(
                                manip, collapsed, text
                            ),
                            collapsed=self._toolbar_collapsed,
                        )
                        with self._toolbar_collapsable_frame:
                            with ui.ZStack():

                                def build_toolbar_frame(operation: Operation, visible: bool) -> ui.Frame:
                                    toolbar_frame = ui.Frame(visible=visible)
                                    with toolbar_frame:
                                        with ui.ZStack():
                                            with ui.VStack():
                                                ui.Spacer(height=2)
                                                with ui.ZStack():
                                                    bg = ui.Rectangle()
                                                    self._tools_stacks[operation] = ui.HStack(
                                                        width=0, spacing=TOOLBAR_SPACING
                                                    )
                                                    with self._tools_stacks[operation]:
                                                        ui.Spacer()
                                                        for tool in tools_can_build[operation]:
                                                            t = tool(
                                                                manipulator=weakref.proxy(self),
                                                                operation=operation,
                                                                toolbar_height=TOOLBAR_HEIGHT,
                                                                toolbar_payload=self._tool_button_additional_payload,
                                                                tooltip_update_fn=update_tooltip,
                                                            )
                                                            self._tools.append(t)
                                                        ui.Spacer()

                                                    def update_bg_width():
                                                        bg.width = ui.Pixel(
                                                            self._tools_stacks[operation].computed_width
                                                        )
                                                        if self._header_line:
                                                            self._header_line.width = ui.Pixel(
                                                                self._tools_stacks[operation].computed_width
                                                                - CARAT_SIZE
                                                                - CRATE_SPACING
                                                            )

                                                    self._tools_stacks[operation].set_computed_content_size_changed_fn(
                                                        update_bg_width
                                                    )
                                                ui.Spacer(height=2)
                                    return toolbar_frame

                                for op in OPERATIONS:
                                    self._toolbars[op] = build_toolbar_frame(op, self._operation == op)

    def _on_toolbar_changed(self):
        """Callback for when the ToolbarRegistry associated with the TransformManipulator changes."""
        if not self._toolbar_root:
            return

        for tool in self._tools:
            tool.destroy()
        self._tools.clear()
        self._toolbars.clear()
        self._build_tools_widgets(self._toolbar_root)

    def on_model_updated(self, item):
        """Callback for when the model associated with the TransformManipulator is updated."""
        self._update_from_model()

    def _update_from_model(self):
        """Updates the TransformManipulator's visual representation based on its model."""
        if not self._transform:
            return

        if not self.model:
            return

        self._transform.transform = self.model.get_as_floats(self.model.get_item("transform"))

        operation = self.model.get_operation()
        if operation != self._operation:
            self._operation = operation
            self._translate_gizmo.visible = False
            self._rotation_gizmo.visible = False
            self._scale_gizmo.visible = False
            for op, toolbar_frame in self._toolbars.items():
                toolbar_frame.visible = False

            if operation == Operation.TRANSLATE:
                self._translate_gizmo.visible = True
            elif operation == Operation.ROTATE:
                self._rotation_gizmo.visible = True
            elif operation == Operation.SCALE:
                self._scale_gizmo.visible = True

            if operation == Operation.NONE:
                self._toolbar_root.visible = False
            else:
                self._toolbar_root.visible = True

                if operation in self._toolbars:
                    self._toolbars[operation].visible = True

            # update line width
            if self._toolbar_collapsable_frame:
                self._toolbar_collapsable_frame.rebuild()

            # toolbar render must be manually updated
            self.refresh_toolbar()

    def _on_scale_changed(self, item, event_type):
        """Callback for when the scale setting for the TransformManipulator changes."""
        scale = self._dict.get(item)
        if scale != self._scale:
            self._scale = scale
            self._update_manipulator_final_size()

    def _get_final_size(self):
        """Calculates the final size of the TransformManipulator based on its scale setting.

        Returns:
            float: The calculated final size of the TransformManipulator."""
        return self._size * self._scale

    def _update_manipulator_final_size(self):
        """Updates the visual size of the TransformManipulator based on its scale setting."""
        final_size = self._get_final_size()
        if self._transform_screen:
            self._transform_screen.transform = sc.Matrix44.get_scale_matrix(final_size, final_size, final_size)

        if self._toolbar_height_offset_transform:
            self._toolbar_height_offset_transform.transform = sc.Matrix44.get_translation_matrix(
                0, self._get_toolbar_height_offset(), 0
            )

    def _on_intersection_thickness_changed(self, item, event_type):
        """Callback for when the intersection thickness setting for the TransformManipulator changes."""
        if self._transform:
            thickness = self._dict.get(item)

            self._translate_line_x.intersection_thickness = thickness
            self._translate_line_y.intersection_thickness = thickness
            self._translate_line_z.intersection_thickness = thickness
            self._rotation_arc_x.intersection_thickness = thickness
            self._rotation_arc_y.intersection_thickness = thickness
            self._rotation_arc_z.intersection_thickness = thickness
            self._rotation_arc_screen.intersection_thickness = thickness
            self._scale_line_x.intersection_thickness = thickness
            self._scale_line_y.intersection_thickness = thickness
            self._scale_line_z.intersection_thickness = thickness

    def _on_free_rotation_enabled_changed(self, item, event_type):
        """Callback for when the free rotation setting for the TransformManipulator changes."""
        if self._transform:
            enabled = self._dict.get(item)
            self._rotation_arc_free.visible = enabled

    def _update_axes_visibility(self):
        """Updates the visibility of various axes components based on the axes settings for the TransformManipulator."""
        if self._transform:
            enable_x = bool(self.axes & Axis.X)
            enable_y = bool(self.axes & Axis.Y)
            enable_z = bool(self.axes & Axis.Z)
            enable_screen = bool(self.axes & Axis.SCREEN)

            self._translate_line_x.visible = self._translate_arrow_x.visible = self._rotation_arc_x.visible = (
                self._scale_point_x.visible
            ) = self._scale_line_x.visible = enable_x

            self._translate_line_y.visible = self._translate_arrow_y.visible = self._rotation_arc_y.visible = (
                self._scale_point_y.visible
            ) = self._scale_line_y.visible = enable_y

            self._translate_line_z.visible = self._translate_arrow_z.visible = self._rotation_arc_z.visible = (
                self._scale_point_z.visible
            ) = self._scale_line_z.visible = enable_z

            self._translate_plane_yz.visible = self._scale_plane_yz.visible = enable_y & enable_z
            self._translate_plane_zx.visible = self._scale_plane_zx.visible = enable_z & enable_x
            self._translate_plane_xy.visible = self._scale_plane_xy.visible = enable_x & enable_y

            self._translate_point.visible = self._rotation_arc_screen.visible = self._scale_point.visible = (
                enable_screen
            )

            self._rotation_arc_free.visible = self._settings.get(c.FREE_ROTATION_ENABLED_SETTING) and enable_screen
