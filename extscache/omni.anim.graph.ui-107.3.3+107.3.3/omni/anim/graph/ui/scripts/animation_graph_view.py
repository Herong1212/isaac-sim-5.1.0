# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from typing import Tuple

import carb.input
from omni.kit.widget.graph import GraphView


class AnimationGraphView(GraphView):
    def __init__(self, **kwargs):
        new_kwargs = kwargs.copy()
        new_kwargs["zoom_min"] = 0.3
        new_kwargs["zoom_max"] = 3
        new_kwargs["always_force_regenerate"] = False
        new_kwargs["raster_nodes"] = True
        super().__init__(**new_kwargs)
        # add ALT+RMB+Drag for graph zoom
        self._on_set_zoom_key_shortcut(1, carb.input.KEYBOARD_MODIFIER_FLAG_ALT)

    def screen_to_view(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """
        Returns the view-relative position corresponding to the given screen coordinates. The
        resulting position can be used to position children of the view's internal canvas.

        Args:
            screen_x: X screen coordinate
            screen_y: Y screen coordinate
        """
        return self.screen_to_canvas(screen_x, screen_y)

    def mouse_to_view(self, mouse_x: float, mouse_y: float) -> Tuple[float, float]:
        """
        Returns the view-relative position corresponding to the coordinates from a mouse
        event over the view, taking into account the view's current zoom and offset. The
        resulting position can be used to position children of the view's internal canvas.

        Args:
            mouse_x: X coordinate from a mouse event over the view
            mouse_y: Y coordinate from a mouse event over the view
        """
        return self.screen_to_canvas(mouse_x, mouse_y)

    def mouse_to_screen(self, mouse_x: float, mouse_y: float) -> Tuple[float, float]:
        """
        Returns the screen position corresponding to the coordinates from a mouse
        event over the view. The resulting position can be used to position UI elements
        which are not children of the view's internal canvas.

        Args:
            mouse_x: X coordinate from a mouse event over the view
            mouse_y: Y coordinate from a mouse event over the view
        """
        if getattr(self, 'compatibility', True):
            # When compatibility mode is on the mouse coordinates have already compensated for
            # the graph's zoom. We need to undo that.
            return (mouse_x * self.zoom, mouse_y * self.zoom)

        return (mouse_x, mouse_y)
