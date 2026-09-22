# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["OmniGraphView"]

from functools import partial
from typing import Tuple

import carb.input
import omni.ui as ui
from omni.kit.widget.graph import GraphView

from . import graph_config
from .compounds import CompoundUtils
from .graph_operations import promote_attribute_to_compound, remove_subgraph_port

# =======================================================================================


class OmniGraphView(GraphView):
    def __init__(self, **kwargs):
        new_kwargs = kwargs.copy()
        new_kwargs["zoom_min"] = 0.3
        new_kwargs["zoom_max"] = 3
        new_kwargs["always_force_regenerate"] = False
        new_kwargs["enable_snapping_for_connection"] = True
        super().__init__(**new_kwargs)
        # add ALT+RMB+Drag for graph zoom
        self._on_set_zoom_key_shortcut(1, carb.input.KEYBOARD_MODIFIER_FLAG_ALT)
        self.__port_context_menu = None

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
        if getattr(self, "compatibility", True):
            # When compatibility mode is on the mouse coordinates have already compensated for
            # the graph's zoom. We need to undo that.
            return (mouse_x * self.zoom, mouse_y * self.zoom)

        return (mouse_x, mouse_y)

    def _get_port_dbl_click_fn(self, node, port):
        """
        Helper function to find the double click to rename function for port names
        """
        widgets = self._node_widgets[node].port_center_widgets

        def find_zstack(root):
            for c in ui.Inspector.get_children(root):
                if isinstance(c, ui.ZStack) and c.has_mouse_double_clicked_fn():
                    return c
                zs = find_zstack(c)
                if zs is not None:
                    return zs
            return None

        # Note: delegate may  not return a widget, if so widget will be None
        zs = find_zstack(widgets[port]) if widgets[port] else None
        return partial(zs.call_mouse_double_clicked_fn, 0, 0, 0, 0) if zs else None

    def _on_port_context_menu(self, node, port):
        """Override context menu for port"""
        self.__port_context_menu = ui.Menu("Port Context Menu", visible=False)

        def disconnect_inputs(port):
            self._model[port].inputs = []

        show_menu = False
        with self.__port_context_menu:
            if self._model[port].inputs:
                ui.MenuItem("Disconnect", triggered_fn=lambda p=port: disconnect_inputs(p))
                show_menu = True
            if graph_config.Supports.compound_subgraphs():
                if CompoundUtils.is_node_in_a_compound(port):
                    ui.MenuItem(
                        "Promote to Compound",
                        triggered_fn=partial(promote_attribute_to_compound, self._model, port),
                        enabled=CompoundUtils.can_promote_attribute_to_compound_subgraph(port),
                    )
                    show_menu = True
                    # NOTE: haven't figured out how to trigger the double click behavior from here
                if CompoundUtils.is_compound_subgraph_node(port):
                    ui.MenuItem("Rename Port", triggered_fn=self._get_port_dbl_click_fn(node, port))
                    ui.Separator()
                    ui.MenuItem("Remove Port", triggered_fn=partial(remove_subgraph_port, self._model, port))
                    show_menu = True
        if show_menu:
            self.__port_context_menu.visible = True
            self.__port_context_menu.show()
