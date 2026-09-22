# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module provides the GraphView class for visualizing nodes and their connections in omni.kit.widget.graph."""


__all__ = [
    "GraphView",
]

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
import asyncio
import carb
import carb.input
import carb.settings
import functools
import traceback

import omni.kit.app
import omni.ui as ui

from .abstract_graph_node_delegate import AbstractGraphNodeDelegate
from .abstract_graph_node_delegate import GraphConnectionDescription
from .graph_layout import SugiyamaLayout
from .graph_model import GraphModel
from .graph_node import GraphNode
from .graph_node_index import GraphNodeDiff, GraphNodeIndex

CONNECTION_CURVE = 60
FLOATING_DELTA = 0.00001


def handle_exception(func):
    """
    Decorator to print exception in async functions

    TODO: The alternative way would be better, but we want to use traceback.format_exc for better error message.
        result = await asyncio.gather(*[func(*args)], return_exceptions=True)
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            # We always cancel the task. It's not a problem.
            pass
        except Exception as e:
            carb.log_error(f"Exception when async '{func}'")
            carb.log_error(f"{e}")
            carb.log_error(f"{traceback.format_exc()}")

    return wrapper


class GraphView:
    """The visualisation layer of omni.kit.widget.graph. It behaves like a
    regular widget and displays nodes and their connections.

    Attributes:
        DEFAULT_DISTANCE_BETWEEN_NODES (float): Default space between graph nodes.

    Args:
        kwargs (dict): Arbitrary keyword arguments for widget initialization.
        settings (Any): Settings related to graph visualization and interaction.
        rect_corner_start (Any): Starting corner for a selection rectangle.
        rect_corner_end (Any): Ending corner for a selection rectangle.
    """

    DEFAULT_DISTANCE_BETWEEN_NODES = 50.0

    class _Proxy:
        """
        A service proxy object to keep the given object in a central
        location. It's used to keep the delegate and this object is passed to
        the nodes, so when the delegate is changed, it's automatically
        updated in all the nodes.

        TODO: Add `set_delegate`. Otherwise it's useless.
        """

        def __init__(self, reference=None):
            self.set_object(reference)

        def __getattr__(self, attr):
            """
            Called when the default attribute access fails with an
            AttributeError.
            """
            return getattr(self._ref, attr)

        def __setattr__(self, attr, value):
            """
            Called when an attribute assignment is attempted. This is called
            instead of the normal mechanism (i.e. store the value in the
            instance dictionary).
            """
            setattr(self._ref, attr, value)

        def set_object(self, reference):
            """Replace the object this proxy holds with the new one"""
            super().__setattr__("_ref", reference)

    class _Event(set):
        """
        A list of callable objects. Calling an instance of this will cause a
        call to each item in the list in ascending order by index.
        """

        def __call__(self, *args, **kwargs):
            """Called when the instance is “called” as a function"""
            # Call all the saved functions
            for f in self:
                f(*args, **kwargs)

        def __repr__(self):
            """
            Called by the repr() built-in function to compute the “official”
            string representation of an object.
            """
            return f"Event({set.__repr__(self)})"

    class _EventSubscription:
        """
        Event subscription.

        _Event has callback while this object exists.
        """

        def __init__(self, event, fn):
            """
            Save the function, the event, and add the function to the event.
            """
            self._fn = fn
            self._event = event
            event.add(self._fn)

        def __del__(self):
            """Called by GC."""
            self._event.remove(self._fn)

    class _ConnectionDragHandler:

        def __init__(self, start_port):
            self.on_start = []
            self.on_abort = []
            self.on_empty_complete = []
            self.on_target_complete = []
            self.on_hover_begin = []
            self.on_hover_end = []
            self.on_can_connect = []
            self.on_completed = []

            self.__start_port = start_port
            self.__hover_port = None

        def destroy(self):
            self.on_start = None
            self.on_target_complete = None
            self.on_empty_complete = None
            self.on_abort = None
            self.on_hover_begin = None
            self.on_hover_end = None
            self.on_can_connect = None
            self.on_completed = None

            self.__hover_port = None

        def start(self):
            for call in self.on_start:
                call()

        def complete(self):

            if self.__start_port == self.__hover_port:
                self.abort()
                return
            with omni.kit.undo.group():
                if self.__hover_port is not None:
                    for call in self.on_target_complete:
                        call(self.__hover_port)
                    self.__hover_port = None
                else:
                    for call in self.on_empty_complete:
                        call()

                self.__completed()

        def abort(self):
            for call in self.on_abort:
                call()
            self.__completed()

        def __completed(self):
            for call in self.on_completed:
                call()

        def hover_begin(self, hover_node, hover_port, hover_widget):
            if self.__hover_port is not None:
                self.hover_end()

            self.__hover_port = hover_port
            if hover_port is None:
                return

            for call in self.on_hover_begin:
                call(hover_node, hover_port, hover_widget)

        def hover_end(self, port=None):
            if self.__hover_port is None:
                return
            if port is None or self.__hover_port == port:
                for call in self.on_hover_end:
                    call()
                self.__hover_port = None

        def can_connect(self, target_port):
            r = True
            for call in self.on_can_connect:
                r &= call(target_port)
                if not r:
                    return r
            return r

    def __init__(self, **kwargs):
        """
        Initialize a GraphView widget.

        Keyword Arguments:
            `model : GraphModel`
                Model to display the node graph

            `delegate : AbstractGraphNodeDelegate`
                Delegate to draw the node

            `virtual_ports : bool`
                True when the model should use reversed output for better look
                of the graph.

            `port_grouping : bool`
                True when the widget should use sub-ports for port grouping.

            `draw_curve_top_layer : bool`
                When True, connections are drawn in 2 passes.  The "under" layer is for the
                opaque curve, and the "top" or "over" layer is meant for floating curve anchor
                decorations that need to be on top of all nodes, like a value display. Its curve
                should be drawn transparent. False by default, so both layers are not drawn.

            `allow_same_side_connections : bool`
                When True, connections can happen between two input ports or two output ports. This is only used within
                one node. We don't support same side connection between different nodes yet.

            All other kwargs are passed to CanvasFrame which is the root widget.
        """
        # Selected nodes
        self.__selection = []

        self.__build_task = None
        self._node_widgets = {}
        # _connection_widgets are the ones that are "under" the nodes,
        # while _connection_over_widgets are "over" the nodes
        self._connection_widgets = {}
        self._connection_over_widgets = {}
        self._node_placers = {}
        self._delegate = self._Proxy()

        # Regenerate the cache index when true
        self._force_regenerate = True

        self.__reference_style = kwargs.get("style", None)

        self._model = None
        self.set_model(kwargs.pop("model", None))
        self.set_delegate(kwargs.pop("delegate", None))
        self.__virtual_ports = kwargs.pop("virtual_ports", False)
        self.__port_grouping = kwargs.pop("port_grouping", False)
        self.__rectangle_selection = kwargs.pop("rectangle_selection", False)
        self.__draw_curve_top_layer = kwargs.pop("draw_curve_top_layer", False)
        self.__allow_same_side_connections = kwargs.pop("allow_same_side_connections", False)
        self.__enable_snapping_for_connection = kwargs.pop("enable_snapping_for_connection", False)
        self.__always_force_regenerate = kwargs.pop("always_force_regenerate", True)

        # The variable raster_nodes is an experimental feature that can improve
        # performance by rasterizing all the nodes when it is set to true.
        # However, it is important to note that this feature may not always
        # behave as expected and may cause issues with the editor. It is
        # recommended to use this feature with caution and thoroughly test any
        # changes before deploying them.
        settings = carb.settings.get_settings()
        self.__raster_nodes = kwargs.pop("raster_nodes", False) or settings.get(
            "/exts/omni.kit.widget.graph/raster_nodes"
        )

        if self.__raster_nodes:
            kwargs["compatibility"] = False

        self._graph_node_index = GraphNodeIndex(None, self.__port_grouping)

        if "style_type_name_override" not in kwargs:
            kwargs["style_type_name_override"] = "Graph"

        # The nodes for filtering upstrem.
        self._filtering_nodes = None

        # Nodes & Connections to force draw
        self._force_draw_nodes = []

        with ui.ZStack():
            # Capturing selection
            if self.__rectangle_selection:
                ui.Spacer(
                    mouse_pressed_fn=self.__rectangle_selection_begin,
                    mouse_released_fn=self.__rectangle_selection_end,
                    mouse_moved_fn=self.__rectangle_selection_moved,
                )

            # The graph canvas
            self.__root_frame = ui.CanvasFrame(**kwargs)
            self.__root_stack = None

            # Drawing selection
            self.__selection_layer = ui.Frame(separate_window=True, visible=False)
            with self.__selection_layer:
                with ui.ZStack():
                    self.__selection_placer_start = ui.Placer(draggable=True)
                    self.__selection_placer_end = ui.Placer(draggable=True)
                    with self.__selection_placer_start:
                        rect_corner_start = ui.Spacer(width=1, height=1)
                    with self.__selection_placer_end:
                        rect_corner_end = ui.Spacer(width=1, height=1)
                    # The rectangle that is drawn when selection with the rectangle
                    ui.FreeRectangle(rect_corner_start, rect_corner_end, style_type_name_override="Graph.Selecion.Rect")

        # Build the network
        self.__on_item_changed(None)

        # ZStack for backdrops to be able to add backdrops without redrawing entire graph
        self.__backdrops_stack = None
        # ZStack for connection curves (in front of backdrops but behind nodes)
        self.__connections_under_stack = None
        # ZStack for nodes to be able to add nodes without covering connections
        self.__nodes_stack = None
        # ZStack for connection anchor_fn displays to be able to be on top of nodes
        # only used when self.__draw_curve_top_layer is True
        self.__connections_over_stack = None
        # The frame that follows mouse cursor when the user creates a new connection
        self.__user_drag_connection_frame = None
        # The frame with the temporary connection that is sticky to the port.
        # We need it to demonstrate that the connection is valid.
        self.__user_drag_connection_accepted_frame = None

        # The drag handler object.
        self.__drag_connection_handler = None

        # Dict that has a port as a key and two frames with port widgets
        self.__port_to_frames = {}
        self.__ports_to_node = {}

        # Nodes that will be dragged once the mouse is moved
        self.__nodes_to_drag = []
        # Nodes that are currently dragged
        self.__nodes_dragging = []
        self.__can_connect = False
        self.__position_changed = False

        self.__on_post_delayed_build_layout = self._Event()
        self.__on_pre_delayed_build_layout = self._Event()

        # This event is triggered when the user "drops" a connection on the empty canvas rather than a port.
        self.__on_empty_connection_drop = self._Event()

        # Selection caches
        # Position when the user started selection
        self.__rectangle_selection_start_position = None
        # Positions of the nodes for selection caches
        self.__positions_cache = None
        # Selection when the user started rectangle
        self.__selection_cache = []
        # Flag for async method to deselect all. See
        # `_clear_selection_next_frame_async` for details.
        self.__need_clear_selection = False

    def __getattr__(self, attr):
        """Pretend it's self.__root_frame"""
        return getattr(self.__root_frame, attr)

    def _post_delayed_build_layout(self):
        """Call the event object that has the list of functions"""
        self.__on_post_delayed_build_layout()

    def subscribe_post_delayed_build_layout(self, fn):
        """Subscribe to the event triggered after a delayed layout build.

        Args:
            fn (callable): The function to call when the event is triggered.

        Returns:
            An _EventSubscription object that will unsubscribe when destroyed.
        """
        return self._EventSubscription(self.__on_post_delayed_build_layout, fn)

    def _pre_delayed_build_layout(self):
        """Call the event object that has the list of functions"""
        self.__on_pre_delayed_build_layout()

    def subscribe_pre_delayed_build_layout(self, fn):
        """Subscribe to the event triggered before a delayed layout build.

        Args:
            fn (callable): The function to call when the event is triggered.

        Returns:
            An _EventSubscription object that will unsubscribe when destroyed.
        """
        return self._EventSubscription(self.__on_pre_delayed_build_layout, fn)

    def subscribe_empty_connection_drop(self, fn):
        """Subscribe to the event triggered when a connection is dropped on an empty area.

        Args:
            fn (callable): The function to call when the event is triggered.

        Returns:
            An _EventSubscription object that will unsubscribe when destroyed.
        """
        return self._EventSubscription(self.__on_empty_connection_drop, fn)

    def layout_all(self):
        """Reset positions of all the nodes in the model"""
        # Turn force_regenerate on whenever calling layout_all, so it doesn't always
        # need to be called right before the layout_all call.
        self._force_regenerate = True
        for node in self._model.nodes:
            self._model[node].position = None
        self.__on_item_changed(None)

    def set_expansion(self, state: GraphModel.ExpansionState):
        """Open, close or minimize all the nodes in the model.

        Args:
            state (GraphModel.ExpansionState): The expansion state to set for all nodes.
        """
        for node in self._model.nodes:
            self._model[node].expansion_state = state

    @property
    def raster_nodes(self):
        """Gets whether node rasterization is enabled.

        Returns:
            A boolean indicating if rasterization is enabled.
        """
        # Read only
        return self.__raster_nodes

    @property
    def model(self):
        """Gets the current graph model.

        Returns:
            The current GraphModel instance.
        """
        return self._model

    @model.setter
    def model(self, model):
        """Sets the graph model.

        Args:
            model (GraphModel): The GraphModel instance to set.
        """
        self._force_regenerate = True
        self.set_model(model)

    @property
    def virtual_ports(self):
        """Gets whether virtual ports are enabled.

        Returns:
            A boolean indicating if virtual ports are enabled.
        """
        return self.__virtual_ports

    @virtual_ports.setter
    def virtual_ports(self, value):
        """Sets whether virtual ports should be enabled.

        Args:
            value (bool): The value to set for virtual ports.
        """
        self.__virtual_ports = not not value
        self.__on_item_changed(None)

    def set_model(self, model: GraphModel):
        """Set the graph model for the view. It will refresh all the content.

        Args:
            model (GraphModel): The graph model to display.
        """
        self._filtering_nodes = None

        if self._model:
            self._model.destroy()

        self._model = model

        # Re-subscribe
        if self._model:
            self._model_subscription = self._model.subscribe_item_changed(self.__on_item_changed)
            self._selection_subscription = self._model.subscribe_selection_changed(self.__on_selection_changed)
            self._node_subscription = self._model.subscribe_node_changed(self.__rebuild_node)
        else:
            self._model_subscription = None
            self._selection_subscription = None
            self._node_subscription = None

        self.__on_item_changed(None)
        self.__on_selection_changed()

    def set_delegate(self, delegate: AbstractGraphNodeDelegate):
        """Set the delegate responsible for drawing nodes.

        Args:
            delegate (AbstractGraphNodeDelegate): The delegate to use for drawing nodes.
        """
        self._force_regenerate = True
        self._delegate.set_object(delegate)
        self.__on_item_changed(None)

    def filter_upstream(self, nodes: list):
        """Filter the graph to show only nodes upstream of the specified nodes.

        Args:
            nodes (list): A list of nodes to filter by.
        """
        self._filtering_nodes = nodes
        self.__on_item_changed(None)

    def get_bbox_of_nodes(self, nodes: list):
        """Get the bounding box that encompasses the specified nodes.

        Args:
            nodes (list): A list of nodes to calculate the bounding box for.

        Returns:
            A tuple containing the width, height, and position (x, y) of the bounding box.
        """
        if not nodes:
            nodes = self._model.nodes
        if not nodes:
            return

        min_pos_x = None
        min_pos_x_node = None
        min_pos_y = None
        min_pos_y_node = None
        max_pos_x = None
        max_pos_x_node = None
        max_pos_y = None
        max_pos_y_node = None
        for node in nodes:
            if node not in self._node_widgets:
                continue
            pos = self._model[node].position
            if pos is None:
                continue
            if min_pos_x is None:
                min_pos_x = pos[0]
                min_pos_x_node = node
                min_pos_y = pos[1]
                min_pos_y_node = node
                max_pos_x = pos[0]
                max_pos_x_node = node
                max_pos_y = pos[1]
                max_pos_y_node = node
                continue
            if pos[0] < min_pos_x:
                min_pos_x = pos[0]
                min_pos_x_node = node
            previous_max_max_x = max_pos_x + self._node_widgets[max_pos_x_node].computed_width
            if pos[0] + self._node_widgets[node].computed_width < previous_max_max_x:
                pass
            else:
                max_pos_x = pos[0]
                max_pos_x_node = node
            if pos[1] < min_pos_y:
                min_pos_y = pos[1]
                min_pos_y_node = node
            previous_max_max_y = max_pos_y + self._node_widgets[max_pos_y_node].computed_height
            if pos[1] + self._node_widgets[node].computed_height < previous_max_max_y:
                pass
            else:
                max_pos_y = pos[1]
                max_pos_y_node = node

        if max_pos_x_node in self._node_widgets:
            computed_width = (max_pos_x + self._node_widgets[max_pos_x_node].computed_width) - min_pos_x
            computed_height = (max_pos_y + self._node_widgets[max_pos_y_node].computed_height) - min_pos_y
        else:
            min_pos_x = 0
            min_pos_y = 0
            computed_height = 500
            computed_width = 500

        return computed_width, computed_height, min_pos_x, min_pos_y

    def focus_on_nodes(self, nodes: Optional[List[Any]] = None):
        """Center the view on the specified nodes.

        Args:
            nodes (Optional[List[Any]]): A list of nodes to focus on. Defaults to None, which will focus on all nodes.
        """
        if not self._model:
            return
        if not nodes:
            nodes = self._model.nodes
        if not nodes:
            return

        computed_width, computed_height, min_pos_x, min_pos_y = self.get_bbox_of_nodes(nodes)

        # TODO: Looks like it's a bug of ui.CanvasFrame.computed_width. But it works for now.
        if self.__raster_nodes:
            canvas_computed_width = self.__root_frame.computed_width
            canvas_computed_height = self.__root_frame.computed_height
        else:
            canvas_computed_width = self.__root_frame.computed_width * self.zoom
            canvas_computed_height = self.__root_frame.computed_height * self.zoom
        zoom = min([canvas_computed_width / computed_width, canvas_computed_height / computed_height])

        # We need to clamp the zoom with zoom_min and zoom_max here since we need to update the zoom of graphView and
        # use the clamped zoom to compute self.pan_x and self.pan_y
        # this FLOATING_DELTA is needed to avoid floating issue
        zoom = max(min(zoom, self.zoom_max - FLOATING_DELTA), self.zoom_min + FLOATING_DELTA)

        self.zoom = zoom
        self.pan_x = -min_pos_x * zoom + canvas_computed_width / 2 - computed_width * zoom / 2
        self.pan_y = -min_pos_y * zoom + canvas_computed_height / 2 - computed_height * zoom / 2

        async def restore_smooth_async():
            """Set smooth_zoom to True"""
            await omni.kit.app.get_app().next_update_async()
            self.__root_frame.smooth_zoom = True

        if self.smooth_zoom:
            # Temporarly disable smooth_zoom
            self.__root_frame.smooth_zoom = False
            asyncio.ensure_future(restore_smooth_async())

    @property
    def selection(self):
        """Gets the currently selected nodes in the graph.

        Returns:
            A list of the currently selected nodes.
        """
        return self.__selection

    @selection.setter
    def selection(self, value):
        """Sets the currently selected nodes in the graph.

        Args:
            value (list): A list of nodes to set as selected.
        """
        if self._model:
            self._model.selection = value

    def __rebuild_node(self, item, full=False):
        """Rebuild the delegate of the node, this could be used to just update the look of one node"""
        if item:
            if full:
                self._force_draw_nodes.append(item)
                omni.kit.async_engine.run_coroutine(self.__delayed_build_layout())
                return

            node = self._node_widgets[item]
            if node:
                # Doesn't rebuild ports or connections
                node.rebuild_layout()

    def __on_item_changed(self, item):
        """Called by the model when something is changed"""
        if item is not None:
            # Only one item is changed. Not necessary to rebuild the whole network.
            placer = self._node_placers.get(item, None)
            if placer:
                position = self._model[item].position
                if position:
                    placer.offset_x = position[0]
                    placer.offset_y = position[1]

                placer.invalidate_raster()

            # TODO: Rebuild the node
            return

        # The whole graph is changed. Rebuild
        if self.__build_task:
            self.__build_task.cancel()

        # Build the layout in the next frame because it's possible that
        # multiple items is changed and in this case we still need to execute
        # __build_layouts once.
        self.__build_task = asyncio.ensure_future(self.__delayed_build_layout())

    def __on_selection_changed(self):
        """Called by the model when selection is changed"""
        if not self._model:
            return

        # Deselect existing selection
        for node in self.__selection:
            widget = self._node_widgets.get(node, None)
            if not widget:
                continue

            widget.selected = False

        # Keep only nodes if we have a widget for them. We need it to skip
        # nodes that are selected in model but they are filtered out here
        self.__selection = []
        for model_selection_node in self._model.selection or []:
            for widget_node in self._node_widgets:
                if model_selection_node == widget_node:
                    self.__selection.append(widget_node)

        # Select new selection
        for node in self.__selection:
            widget = self._node_widgets.get(node, None)
            if not widget:
                continue

            widget.selected = True

    def __cache_positions(self):
        """Creates cache for all the positions of all the nodes"""
        if self.__positions_cache is not None:
            return

        class PositionCache:
            def __init__(self, node: Any, pos: List[float], size: List[float]):
                self.node = node
                self.__x0 = pos[0]
                self.__y0 = pos[1]
                self.__x1 = pos[0] + size[0]
                self.__y1 = pos[1] + size[1]

            def __repr__(self):
                return f"<PositionCache {self.node} {self.__x0} {self.__y0} {self.__x1} {self.__y1}"

            def is_in_rect(self, x_min: float, y_min: float, x_max: float, y_max: float):
                return not (x_max < self.__x0 or x_min > self.__x1 or y_max < self.__y0 or y_min > self.__y1)

        self.__positions_cache = []
        for node in self._model.nodes or []:
            # NOTE: If we ever have selection objects that aren't positioned in the top left corner of the
            #       node (like the header), we will need to get the select_widget's position instead, here.
            pos = self._model[node].position
            if pos:
                widget = self._node_widgets.get(node, None)
                if not widget:
                    continue
                select_widget = self._model.special_select_widget(node, widget) or widget

                size = [select_widget.computed_width, select_widget.computed_height]
                self.__positions_cache.append(PositionCache(node, pos, size))

        self.__selection_cache = self.model.selection or []

    async def _clear_selection_next_frame_async(self, model):
        """
        Called by background layer to clear selection. The idea is that if no
        node cancels it, then the yser clicked in the background and we need
        to deselect all.
        """
        await omni.kit.app.get_app().next_update_async()

        if self.__need_clear_selection:
            model.selection = []

    def _on_rectangle_select(self, model, start, end, modifier=0):
        """Called when the user is performing the rectangle selection"""
        # this function could be triggered when we multi-selected nodes and move one of them too quickly.
        # in this case, we don't want to update the selection.
        if start == end:
            return

        # Don't clear selection frame after
        self.__need_clear_selection = False

        self.__cache_positions()

        x_min = min(start[0], end[0])
        x_max = max(start[0], end[0])
        y_min = min(start[1], end[1])
        y_max = max(start[1], end[1])

        selection = []
        for position_cache in self.__positions_cache:
            if position_cache.is_in_rect(x_min, y_min, x_max, y_max):
                selection.append(position_cache.node)

        if modifier & carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT:
            # Add to the current selection
            selection = self.__selection_cache + [s for s in selection if s not in self.__selection_cache]

        elif modifier & carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL:
            # Subtract from the current selection
            selection = [s for s in self.__selection_cache if s not in selection]

        model.selection = selection

    def _on_node_selected(self, model, node, modifier=0, pressed=True):
        """Called when the user is picking to select nodes"""
        # Stop rectangle selection
        self.__rectangle_selection_start_position = None
        # Don't clear selection frame after
        self.__need_clear_selection = False

        selection = model.selection
        if selection is None:
            return

        # Copy
        selection = selection[:]

        if modifier & carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT:
            if not pressed:
                return

            # Add
            if node not in selection:
                selection.append(node)

        elif modifier & carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL:
            if not pressed:
                return

            # Add / Remove
            if node in selection:
                selection.remove(node)
            else:
                selection.append(node)

        else:
            if pressed and node in selection:
                return

            # Set
            selection = [node]

        model.selection = selection

    @handle_exception
    async def __delayed_build_layout(self):
        """
        Rebuild all the nodes and connections in the next update cycle. It's
        delayed because it's possible that it's called multiple times a
        frame. And we need to create all the widgets only one.

        The challenge here is the ability of USD making input-to-input and output-to-output connections. In USD it's
        perfectly fine to have the following network:

        A.out --> B.out
        A.in  <-- B.in

        So it doesn't matter if the port is input or output. To draw such connections properly and to know which side
        of the node it should connect, we need to find out the direction of the flow in this node network. This is the
        overview of the algorithm to trace the nodes and compute the direction of the flow.

        STEP 1. Create the cache of the model and indices to be able to access the cache fast.

        STEP 2. Scan all the nodes and find roots. A root is a node that doesn't have an output connected to another
        node.

        STEP 3. Trace connections of roots and assign them level. Level is the distance of the node from the root.
        The root has level 0. The nodes connected to root has level one. The next connected nodes have level 2 etc.
        We assume that level is the flow direction. The flow goes from nodes to root.

        STEP 4. It's easy to check if the connection goes to the direction opposite to flow. Such connections have
        virtual ports.
        """
        self._pre_delayed_build_layout()
        await omni.kit.app.get_app().next_update_async()

        regenerate_all = self.__always_force_regenerate or self._force_regenerate
        if not regenerate_all:
            # OM-115286: wait one more frame here, since self.__build_task.cancel() will probably cancel
            # the job before building all the connections, which will cause random connection disappears.
            await omni.kit.app.get_app().next_update_async()

        # STEP 1
        # Small explanation on input/output, source/target. Input and output is
        # just a USD tag. We inherit this terminology to be USD compliant.
        # Input/output is not the direction of the data flow. To express the
        # data flow direction we use source/target. In USD it's possible to
        # have input-to-input and output-to-output connections.
        graph_node_index = GraphNodeIndex(self._model, self.__port_grouping)

        if regenerate_all:
            self._force_regenerate = False
        else:
            # Diff
            diff = self._graph_node_index.get_diff(graph_node_index)
            regenerate_all = not diff.valid

        nodes_add = nodes_del = connections_add = connections_del = set()
        if regenerate_all:
            self._graph_node_index = graph_node_index

            # Clean up the previous nodes
            for _, node_widget in self._node_widgets.items():
                node_widget.destroy()
            for _, connection_widget in self._connection_widgets.items():
                connection_widget.destroy()
            for _, connection_widget in self._connection_over_widgets.items():
                connection_widget.destroy()
            self._node_widgets = {}
            self._connection_widgets = {}
            self._connection_over_widgets = {}

            self.__port_to_frames = {}
            self.__ports_to_node = {}
        else:
            if self._force_draw_nodes:
                self.__add_force_redraws_to_diff(diff, graph_node_index)
            nodes_add, nodes_del, connections_add, connections_del = self._graph_node_index.mutate(diff)

        # Utility to access the index
        def get_node_level_from_port(port, port_to_id, all_cached_nodes):
            if port is None:
                return 0

            node_id = port_to_id.get(port, None)
            if node_id is None:
                return 0

            return all_cached_nodes[node_id].level

        # List of all the nodes from the model. Members are CacheNode objects
        all_cached_nodes = self._graph_node_index.cached_nodes
        all_cached_connections = self._graph_node_index.cached_connections
        # Dictionary that has a port from the model as a key and the index of the parent node in all_cached_nodes.
        port_to_id = self._graph_node_index.port_to_id
        # Dictionary that has a port from the model as a key and a flag if this port is output. We need it to detect
        # the flow direction.
        ports_used_as_output = self._graph_node_index.ports_used_as_output
        # All the connections. Usded to determine if we need to draw output circle.
        source_to_target = self._graph_node_index.source_to_target
        # Dict[child port: parent port]
        port_child_to_parent: Dict[Any, Any] = self._graph_node_index.port_child_to_parent

        if not self._model:
            return

        # STEP 2
        # True if the node in all_cached_nodes is a root node. The node A is a root node if other nodes are not
        # connected to outputs of A.
        is_root_node = [True] * len(all_cached_nodes)
        for cache_node in all_cached_nodes:
            if not cache_node:
                continue

            if not regenerate_all and cache_node.node not in nodes_add:
                continue

            for source in cache_node.inputs + cache_node.outputs:
                if source not in ports_used_as_output:
                    continue

                # The source node is not root because it has output connected to this node
                source_node_id = port_to_id.get(source, None)
                if source_node_id is None:
                    continue

                is_root_node[source_node_id] = False

        if self._filtering_nodes:
            root_nodes = [cached_node for cached_node in all_cached_nodes if cached_node.node in self._filtering_nodes]
        else:
            root_nodes = [cached_node for cached_node, is_root in zip(all_cached_nodes, is_root_node) if is_root]

        if not root_nodes and all_cached_nodes:
            # We have a circular connected network. In this way it doesn't matter which node to pick, but we assume that
            # the first node of the model will be the root node.
            root_nodes = [all_cached_nodes[0]]

        # STEP 3
        # Create the list of edges. We need to put them into layout.
        edges = []
        edges_sorted = []
        for i, cache_node in enumerate(all_cached_nodes):
            if not cache_node:
                continue

            if not regenerate_all and cache_node.node not in nodes_add:
                continue

            for source in cache_node.inputs + cache_node.outputs:
                source_node_id = port_to_id.get(source, None)
                if source_node_id is None:
                    # try to resolve id of parent instead
                    parent_source = port_child_to_parent.get(source, None)
                    if parent_source is not None:
                        source_node_id = port_to_id.get(parent_source, None)
                if source_node_id is None:
                    continue

                v1 = source_node_id
                v2 = i

                edge_sorted = (v1, v2) if v1 < v2 else (v2, v1)
                if v1 != v2 and edge_sorted not in edges_sorted:
                    edges.append((v2, v1))
                    edges_sorted.append(edge_sorted)

        if regenerate_all:
            self.layout = SugiyamaLayout(edges=edges, vertical_distance=20.0, horizontal_distance=200.0)

        for i, cache_node in enumerate(all_cached_nodes):
            if not cache_node:
                continue

            if not regenerate_all and cache_node.node not in nodes_add:
                continue

            level = self.layout.get_layer(i)
            # If level is None, it means the node is not connected to anything. We assume its level is 0.
            cache_node.level = level or 0

        # STEP 4. Generate widgets.
        node_and_level = []

        if self.__root_stack is None or regenerate_all:
            with self.__root_frame:
                self.__root_stack = ui.ZStack()

        if regenerate_all:
            self.__backdrops_stack = None
            self.__connections_under_stack = None
            self.__nodes_stack = None
            self.__connections_over_stack = None

        if not regenerate_all:
            # Delete nodes
            for node in nodes_del:
                self._node_widgets[node].visible = False
                self._node_widgets[node].destroy()

            # Delete connections
            for connection in connections_del:
                connection_under_widget = self._connection_widgets.get(connection)
                if connection_under_widget:
                    connection_under_widget.visible = False
                    connection_under_widget.clear()
                    connection_under_widget.destroy()
                connection_over_widget = self._connection_over_widgets.get(connection)
                if connection_over_widget:
                    connection_over_widget.visible = False
                    connection_over_widget.clear()
                    connection_over_widget.destroy()

        # If 1 to keep indentation. Otherwise indentation is changed, it's bad
        # for code review.
        if 1:
            with self.__root_stack:
                # Create ZStack for backdrops with stacking order < -1. It allows
                # us to add backdrops or rearrange them without having to redraw the entire graph.
                # We need to create it even if there are no backdrops yet, so they can be added later.
                if not self.__backdrops_stack:
                    self.__backdrops_stack = ui.ZStack()

                # Create ZStack for connections.  This layer is for drawing the curve part of the connections,
                # which go under the Nodes, but over backdrops.
                if not self.__connections_under_stack:
                    self.__connections_under_stack = ui.ZStack()

                # Create ZStack for nodes with stacking order >= 1. It allows us to add nodes
                # or rearrange them without having to redraw the entire graph, and also to have
                # all nodes be drawn on top of any connections.
                # We need to create it even if there are no nodes yet, so they can be added later.
                if not self.__nodes_stack:
                    self.__nodes_stack = ui.ZStack()

                # Create 2nd ZStack for connections.  This layer is for drawing the floating anchor_fn part
                # of the connections, which go over all of the Nodes.  If no floating anchor_fn widgets need
                # to be drawn, draw_curve_top_layer can be set to False so this layer doesn't have to draw.
                if self.__draw_curve_top_layer and not self.__connections_over_stack:
                    self.__connections_over_stack = ui.ZStack()

                # Save the connections. It's the list of tuples (target_port, source_port)
                for node_id, cached_node in sorted(
                    enumerate(n for n in all_cached_nodes if n), key=lambda a: a[1].stacking_order
                ):
                    if not regenerate_all and cached_node.node not in nodes_add:
                        continue

                    stacking_order = cached_node.stacking_order

                    expansion_state = self._model[cached_node.node].expansion_state
                    # Filtered ports
                    ports = []
                    # Two bools per port:
                    # (True if it's target, True if it's source)
                    # So the connection can have four states: input/output and
                    # source/target. They can be mixed every possible way.
                    port_input = []
                    # Two bools per port
                    # (True if it's target, True if it's source)
                    port_output = []
                    port_levels: List[int] = []
                    port_position: List[int] = []
                    port_siblings_below = []
                    parent_child_count: List[int] = []

                    node_input = (False, False)
                    node_output = (False, False)

                    # Save connections and check if the node has virtual input/output
                    for cached_port in cached_node.cached_ports:
                        if not cached_port.visibile:
                            continue

                        target_port = cached_port.port

                        # Or it happens when the node is minimized
                        # TODO: compute it when computing port_visibility
                        if (
                            expansion_state == GraphModel.ExpansionState.MINIMIZED
                            or expansion_state == GraphModel.ExpansionState.CLOSED
                        ):
                            if not cached_port.inputs and not cached_port.outputs:
                                if target_port not in source_to_target:
                                    # Filter out ports with no connections
                                    continue

                        # True if the port has input (left side) connection
                        # from this port to another
                        input_is_source_connection = False
                        # True if the port has input (left side) connection
                        # from another port to this port
                        input_is_target_connection = False
                        # True if the port has output (right side) connection
                        # from this port to another
                        output_is_source_connection = False
                        # True if the port has output (right side) connection
                        # from another port to this port
                        output_is_target_connection = False

                        if cached_port.inputs:
                            for source_port in cached_port.inputs:
                                if source_port not in port_to_id:
                                    carb.log_warn(
                                        f"[Graph UI] The port {target_port} can't be connected to the port "
                                        f"{source_port} because it doesn't exist in the model"
                                    )
                                    continue

                                if (
                                    self.virtual_ports
                                    and get_node_level_from_port(source_port, port_to_id, all_cached_nodes)
                                    < cached_node.level
                                ):
                                    # The input port is connected from the downflow node
                                    #
                                    # Example:
                                    # A.out  -------------------------> B.surface
                                    # A.color [checking this option] <- B.color
                                    output_is_target_connection = True
                                else:
                                    # Example:
                                    # A.out -> [checking this option] B.in
                                    input_is_target_connection = True

                        if cached_port.outputs:
                            for source_port in cached_port.outputs:
                                if source_port not in port_to_id:
                                    carb.log_warn(
                                        f"[Graph UI] The port {target_port} can't be connected to the port "
                                        f"{source_port} because it doesn't exist in the model"
                                    )
                                    continue

                                if (
                                    self.virtual_ports
                                    and get_node_level_from_port(source_port, port_to_id, all_cached_nodes)
                                    < cached_node.level
                                ):
                                    output_is_target_connection = True
                                else:
                                    input_is_target_connection = True
                            # The output port has input connection. A.out -> [checking this option] B.out

                        if target_port in source_to_target:
                            for t in source_to_target[target_port]:
                                compare_level = get_node_level_from_port(t, port_to_id, all_cached_nodes)
                                if (
                                    self.virtual_ports
                                    and compare_level is not None
                                    and cached_node.level < compare_level
                                ):
                                    # Example:
                                    # A.out  -------------------------> B.surface
                                    # A.color <- [checking this option] B.color
                                    input_is_source_connection = True
                                else:
                                    # A.out [checking this option] -> B.in
                                    output_is_source_connection = True

                        node_input = (
                            node_input[0] or input_is_source_connection,
                            node_input[1] or input_is_target_connection,
                        )
                        node_output = (
                            node_output[0] or output_is_source_connection,
                            node_output[1] or output_is_target_connection,
                        )

                        if expansion_state == GraphModel.ExpansionState.CLOSED:
                            continue

                        # Ports
                        ports.append(target_port)
                        port_input.append((input_is_source_connection, input_is_target_connection))
                        port_output.append((output_is_source_connection, output_is_target_connection))
                        port_levels.append(cached_port.level)
                        port_position.append(cached_port.relative_position)
                        port_siblings_below.append(cached_port.siblings_below)
                        parent_child_count.append(cached_port.parent_child_count)

                    # Rasterize the nodes. This is an experimental feature that
                    # can improve performance.
                    raster_policy = ui.RasterPolicy.AUTO if self.__raster_nodes else ui.RasterPolicy.NEVER

                    if stacking_order > -1:
                        # For nodes
                        layer_stack = self.__nodes_stack
                    else:
                        # If this is a backdrop
                        layer_stack = self.__backdrops_stack

                    with layer_stack:
                        # The side effect of having level, is the possibility to put the node to the correct position.
                        placer = ui.Placer(
                            draggable=True, frames_to_start_drag=2, name="node_graph", raster_policy=raster_policy
                        )

                    # Set position if possible
                    position = self._model[cached_node.node].position
                    if position:
                        placer.offset_x = position[0]
                        placer.offset_y = position[1]

                    def save_position(placer, model, node, is_x):
                        if self.__nodes_to_drag:
                            for drag_node in self.__nodes_to_drag:
                                model.position_begin_edit(drag_node)
                            self.__nodes_dragging[:] = self.__nodes_to_drag[:]
                            self.__nodes_to_drag[:] = []

                        # Without this, unselected backdrops can still be dragged by their placer
                        if not self.__nodes_dragging:
                            if model[node].position:
                                if is_x:
                                    placer.offset_x.value = model[node].position[0]
                                else:
                                    placer.offset_y.value = model[node].position[1]
                            return

                        node_position = (placer.offset_x.value, placer.offset_y.value)
                        model[node].position = node_position
                        self.__position_changed = True

                    placer.set_offset_x_changed_fn(
                        lambda _, p=placer, m=self._model, n=cached_node.node: save_position(p, m, n, True)
                    )
                    placer.set_offset_y_changed_fn(
                        lambda _, p=placer, m=self._model, n=cached_node.node: save_position(p, m, n, False)
                    )

                    with placer:
                        # The node widget
                        node_widget = GraphNode(
                            self._model,
                            cached_node.node,
                            node_input,
                            node_output,
                            list(
                                zip(
                                    ports,
                                    port_input,
                                    port_output,
                                    port_levels,
                                    port_position,
                                    parent_child_count,
                                    port_siblings_below,
                                )
                            ),
                            self._delegate,
                        )

                        def position_begin_edit(model, node, modifier):
                            self.__nodes_to_drag[:] = [node]
                            self.__nodes_dragging[:] = []
                            self.__position_changed = False

                        def position_end_edit(model, node, modifier):
                            self.__nodes_to_drag[:] = []
                            for drag_node in self.__nodes_dragging:
                                model.position_end_edit(drag_node)
                            self.__nodes_dragging[:] = []

                            return self.__position_changed

                        select_widget = self._model.special_select_widget(cached_node.node, node_widget) or node_widget

                        # Select node
                        select_widget.set_mouse_pressed_fn(
                            lambda x, y, b, modifier, model=self._model, node=cached_node.node: b == 0
                            and (
                                position_begin_edit(model, node, modifier)
                                or self._on_node_selected(model, node, modifier, True)
                            )
                        )
                        select_widget.set_mouse_released_fn(
                            lambda x, y, b, modifier, model=self._model, node=cached_node.node: b == 0
                            and (
                                position_end_edit(model, node, modifier)
                                or self._on_node_selected(model, node, modifier, False)
                            )
                        )

                        # Save the node so it's not removed
                        self._node_widgets[cached_node.node] = node_widget
                        self._node_placers[cached_node.node] = placer

                        node_and_level.append((cached_node.node, node_widget, placer, node_id))

                        # Save the ports for fast access
                        if expansion_state == GraphModel.ExpansionState.CLOSED:
                            for cached_port in cached_node.cached_ports:
                                self.__port_to_frames[cached_port.port] = (
                                    node_widget.header_input_frame,
                                    node_widget.header_output_frame,
                                )
                        else:
                            self.__port_to_frames.update(node_widget.ports)
                            for port, input_output in node_widget.ports.items():
                                input_port_widget, output_port_widget = input_output
                                input_snapping_widget, output_snapping_widget = node_widget.snapping_widgets.get(
                                    port, (None, None)
                                )
                                if input_port_widget:
                                    # Callback when mouse enters/leaves the port widget
                                    input_port_widget.set_mouse_hovered_fn(
                                        lambda h, n=cached_node.node, p=port, w=input_port_widget: self.__on_port_hovered(
                                            n, p, w, h
                                        )
                                    )
                                    input_port_widget.set_mouse_pressed_fn(
                                        lambda x, y, b, m, n=cached_node.node, p=port: (
                                            self._on_port_context_menu(n, p) if b == 1 else None
                                        )
                                    )

                                    if self.__enable_snapping_for_connection and input_snapping_widget:
                                        # Callback when mouse enters/leaves the port widget
                                        input_snapping_widget.set_mouse_hovered_fn(
                                            lambda h, n=cached_node.node, p=port, w=input_port_widget: self.__on_port_hovered(
                                                n, p, w, h
                                            )
                                        )
                                        input_snapping_widget.set_mouse_pressed_fn(
                                            lambda x, y, b, m, n=cached_node.node, p=port: (
                                                self._on_port_context_menu(n, p) if b == 1 else None
                                            )
                                        )

                                if output_port_widget:
                                    # Callback when mouse enters/leaves the port widget
                                    output_port_widget.set_mouse_hovered_fn(
                                        lambda h, n=cached_node.node, p=port, w=output_port_widget: self.__on_port_hovered(
                                            n, p, w, h
                                        )
                                    )
                                    output_port_widget.set_mouse_pressed_fn(
                                        lambda x, y, b, m, n=cached_node.node, p=port: (
                                            self._on_port_context_menu(n, p) if b == 1 else None
                                        )
                                    )
                                    if self.__enable_snapping_for_connection and output_snapping_widget:
                                        # Callback when mouse enters/leaves the port widget
                                        output_snapping_widget.set_mouse_hovered_fn(
                                            lambda h, n=cached_node.node, p=port, w=output_port_widget: self.__on_port_hovered(
                                                n, p, w, h
                                            )
                                        )

                        for port, input_output in node_widget.user_drag.items():
                            _, drag_widget = input_output
                            inout_port_widget = self.__port_to_frames.get(port, (None, None))
                            self.__ports_to_node[port] = (node_widget, cached_node.node)
                            if self._model[port].inputs is not None:
                                port_widget = inout_port_widget[0]
                                from_widget_is_input = True
                            elif self._model[port].outputs is not None:
                                port_widget = inout_port_widget[1]
                                from_widget_is_input = False
                            else:
                                continue

                            # Callback when user starts doing a new connection
                            drag_widget.set_mouse_pressed_fn(
                                lambda x, y, button, modifier, f=port_widget, i=from_widget_is_input, t=drag_widget, n=cached_node.node, p=port: self.__on_start_connection(
                                    n, p, i, f, t, modifier
                                )
                            )
                            # Callback when user finishes doing a new connection
                            drag_widget.set_mouse_released_fn(lambda *_: self._on_finish_connection())

                # OM-115286: wait one frame to build connection after the nodes. Otherwise, we see the connection flickering
                if not regenerate_all:
                    await omni.kit.app.get_app().next_update_async()

                # Buffer to keep the lines already built. We use it for filtering.
                built_lines = set()

                # Build all the connections
                for connection in all_cached_connections:
                    if not connection:
                        continue

                    if not regenerate_all and connection not in connections_add:
                        continue

                    target = connection.target_port
                    source = connection.source_port

                    target_node_id = port_to_id.get(target, None)
                    target_cached_node = all_cached_nodes[target_node_id]
                    target_level = target_cached_node.level

                    source_node_id = port_to_id.get(source, None)
                    source_cached_node = all_cached_nodes[source_node_id]
                    source_level = source_cached_node.level

                    # Check if the direction of this connection is the same as flow
                    if self.virtual_ports:
                        is_reversed_connection = source_level < target_level
                    else:
                        is_reversed_connection = False

                    target_node = target_cached_node.node
                    source_node = source_cached_node.node

                    # 0 means the frame from input (left side). 1 is output (right side).
                    target_frames = self.__port_to_frames.get(target, None)
                    source_frames = self.__port_to_frames.get(source, None)

                    if self.__allow_same_side_connections and target_node == source_node:
                        if self._model[source].inputs is not None:  # input ports
                            is_reversed_target = False
                            is_reversed_source = True
                            f1 = target_frames[0]
                            f2 = source_frames[0]
                        if self._model[source].outputs is not None:  # output ports
                            is_reversed_target = True
                            is_reversed_source = False
                            f1 = target_frames[1]
                            f2 = source_frames[1]
                    else:
                        is_reversed_target = is_reversed_connection
                        is_reversed_source = is_reversed_connection
                        f1 = target_frames[1 if is_reversed_connection else 0]
                        f2 = source_frames[0 if is_reversed_connection else 1]

                    # Filter out lines already built.
                    line1 = (f1, f2)
                    line2 = (f2, f1)
                    if line1 in built_lines or line2 in built_lines:
                        continue

                    built_lines.add(line1)

                    # Objects passed to the delegate
                    source_connection_description = GraphConnectionDescription(
                        source_node, source, f2, source_level, is_reversed_source
                    )
                    target_connection_description = GraphConnectionDescription(
                        target_node, target, f1, target_level, is_reversed_target
                    )

                    # Draw the connection curves, and any "background" parts of the anchor_fn, such
                    # as the "dot" that sticks to the connection curve.
                    with self.__connections_under_stack:
                        connection_under_frame = ui.Frame(separate_window=1)
                        self._connection_widgets[connection] = connection_under_frame
                        with connection_under_frame:
                            try:
                                self._delegate.connection(
                                    self._model, source_connection_description, target_connection_description, False
                                )
                            except TypeError:
                                # Fallback for older versions of connection
                                self._delegate.connection(
                                    self._model, source_connection_description, target_connection_description
                                )

                    if self.__draw_curve_top_layer:
                        # Draw the floating part of the anchor_fn, such as a value display, that should
                        # be on top of all nodes.  Typically the curve will be drawn transparent on this layer.
                        with self.__connections_over_stack:
                            connection_over_frame = ui.Frame()
                            self._connection_over_widgets[connection] = connection_over_frame
                            with connection_over_frame:
                                try:
                                    self._delegate.connection(
                                        self._model, source_connection_description, target_connection_description, True
                                    )
                                except TypeError:
                                    # Fallback for older versions of connection
                                    self._delegate.connection(
                                        self._model, source_connection_description, target_connection_description
                                    )

                # As long as dragging connections don't require an anchor display, we should only need
                # to draw these on the "under" stack and not also the "over" stack.
                with self.__connections_under_stack:
                    # Using separate_window=1 here to prevent clipping and also to keep the dragging connections
                    # in front of backdrops
                    self.__user_drag_connection_frame = ui.Frame(separate_window=1)
                    self.__user_drag_connection_accepted_frame = ui.Frame(separate_window=1)

        # Init selection state
        self.__on_selection_changed()

        # Arrange node position in the next frame because now the node is not
        # created and it's not possible to get its size.
        if not node_and_level:
            self._post_delayed_build_layout()
            return

        await self.__arrange_nodes(node_and_level)
        self._post_delayed_build_layout()

    def __add_force_redraws_to_diff(self, diff: GraphNodeDiff, graph_node_index: GraphNodeIndex):
        """
        Add the force_redraw_nodes, if any, by adding them to both the nodes_to_add and nodes_to_del sides.
        Also do the same with any connections to the node(s).  By deleting and then adding, it forces a redraw.
        """
        cached_add_connections = set()
        cached_del_connections = set()
        for force_node in self._force_draw_nodes:
            # Add node to nodes_to_add
            if force_node in graph_node_index.node_to_id:
                force_add_cache_node = graph_node_index.cached_nodes[graph_node_index.node_to_id[force_node]]
                if force_add_cache_node not in diff.nodes_to_add:
                    diff.nodes_to_add.append(force_add_cache_node)

                # Add any inputs or outputs
                for c_port in force_add_cache_node.cached_ports:
                    # Check for outputs
                    source = c_port.port
                    targets = graph_node_index.source_to_target.get(c_port.port, [])
                    for t in targets:
                        if (source, t) in graph_node_index.connection_to_id:
                            cached_add_connection = graph_node_index.cached_connections[
                                graph_node_index.connection_to_id[(source, t)]
                            ]
                            cached_add_connections.add(cached_add_connection)
                        if (source, t) in self._graph_node_index.connection_to_id:
                            cached_del_connection = self._graph_node_index.cached_connections[
                                self._graph_node_index.connection_to_id[(source, t)]
                            ]
                            cached_del_connections.add(cached_del_connection)

                    # Check for inputs
                    if not targets:
                        target = source
                        if c_port.inputs:
                            for inp in c_port.inputs:
                                source = inp
                                if (source, target) in graph_node_index.connection_to_id:
                                    cached_add_connection = graph_node_index.cached_connections[
                                        graph_node_index.connection_to_id[(source, target)]
                                    ]
                                    cached_add_connections.add(cached_add_connection)
                                if (source, target) in self._graph_node_index.connection_to_id:
                                    cached_del_connection = self._graph_node_index.cached_connections[
                                        self._graph_node_index.connection_to_id[(source, target)]
                                    ]
                                    cached_del_connections.add(cached_del_connection)

            # Add node to nodes_to_del
            if force_node in self._graph_node_index.node_to_id:
                force_del_cache_node = self._graph_node_index.cached_nodes[
                    self._graph_node_index.node_to_id[force_node]
                ]
                if force_del_cache_node not in diff.nodes_to_del:
                    diff.nodes_to_del.append(force_del_cache_node)

        # Add all connections to the diff
        for c_connection in cached_add_connections:
            if c_connection not in diff.connections_to_add:
                diff.connections_to_add.append(c_connection)
        for c_connection in cached_del_connections:
            if c_connection not in diff.connections_to_del:
                diff.connections_to_del.append(c_connection)

        self._force_draw_nodes = []

    async def __arrange_nodes(self, node_and_level):
        """
        Set the the position of the nodes. If the node doesn't have a
        predefined position (TODO), the position is assigned automatically.
        It's async because it waits until the node is created to get its size.
        """
        # Wait until the node appears on the screen.
        while node_and_level[0][1].computed_width == 0.0:
            await omni.kit.app.get_app().next_update_async()

        # Set size
        for _, node_widget, _, layout_node_id in node_and_level:
            self.layout.set_size(layout_node_id, node_widget.computed_width, node_widget.computed_height)

        # Recompute positions
        self.layout.update_positions()

        # Set positions in graph view
        for node, node_widget, placer, layout_node_id in node_and_level:
            model_position = self._model[node].position
            self._model[node].size = (node_widget.computed_width, node_widget.computed_height)
            if not model_position:
                # The model doesn't have the position. Set it.
                model_position = self.layout.get_position(layout_node_id)
                if model_position:
                    self._model[node].position = model_position

                    placer.offset_x = model_position[0]
                    placer.offset_y = model_position[1]

    def __on_start_connection(self, node, port, from_is_input, from_widget, to_widget, modifier=None):
        """Called when the user starts creating connection"""
        # Keep the source port
        if self.__drag_connection_handler is not None:
            self.__drag_connection_handler.abort()
            self.__drag_connection_handler.destroy()
            self.__drag_connection_handler = None

        if not from_widget or not to_widget:
            return
        drag_handler = self._ConnectionDragHandler(port)

        def toggle_visible(w, v):
            if w is not None:
                w.visible = v

        def clear_inputs(model, port):
            model[port].inputs = []

        def draw_connection(delegate, model, source, target):
            delegate.connection(model, source, target)

        def can_connect_test(model, inport, outport):
            from_is_input = model[inport].inputs is not None
            to_is_input = model[outport].inputs is not None

            if not self.__allow_same_side_connections:
                # same side connection, early return
                if to_is_input == from_is_input:
                    return False
            else:
                if to_is_input == from_is_input:
                    # make sure also the same node
                    input_node = self.__ports_to_node.get(inport, (None, None))
                    output_node = self.__ports_to_node.get(outport, (None, None))

                    if input_node != output_node:
                        return False

            return model.can_connect(outport, inport)

        def hover_connection(target_node, target_port, target_widget, delegate, model, source_description, flipped):
            target_description = GraphConnectionDescription(
                target_node,
                target_port,
                target_widget,
                0,
                flipped,
            )
            delegate.connection(model, source_description, target_description)

        def set_inputs(model, port, inputs):
            model[port].inputs = inputs

        def clear_frame(frame):
            with frame:
                ui.Spacer()

        def remove_connection_to(model, port, remove_this):
            model[port].inputs = [x for x in model[port].inputs if x != remove_this]

        def empty_drop(view, ports, flipped):
            view.__on_empty_connection_drop(ports, flipped)

        # If holding CTRL down when click-dragging on a port, rewire rather than start a new connection
        if modifier == carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL:
            if from_is_input:
                inputs = self._model[port].inputs
                node_index = self._graph_node_index
                if not inputs:
                    return

                drag_handler.on_target_complete.append(lambda *_, m=self._model, p=port: clear_inputs(m, p))
                drag_handler.on_target_complete.append(
                    lambda target_port, i=inputs, m=self._model: set_inputs(m, target_port, i)
                )
                drag_handler.on_empty_complete.append(lambda m=self._model, p=port: clear_inputs(m, p))
                drag_handler.on_empty_complete.append(lambda v=self, p=inputs: empty_drop(v, p, False))

                pickup_port = port
                for connected_output in inputs:
                    connection_index = node_index.connection_to_id.get((connected_output, pickup_port), None)
                    if connection_index is not None:
                        connection = node_index.cached_connections[connection_index]
                        connection_widget = self._connection_widgets.get(connection, None)

                        drag_handler.on_start.append(lambda w=connection_widget: toggle_visible(w, False))
                        drag_handler.on_abort.append(lambda w=connection_widget: toggle_visible(w, True))

                        if self.__draw_curve_top_layer:
                            connection_over_widget = self._connection_over_widgets.get(connection, None)
                            drag_handler.on_start.append(lambda w=connection_over_widget: toggle_visible(w, False))
                            drag_handler.on_abort.append(lambda w=connection_over_widget: toggle_visible(w, True))

                    inout_port_widget = self.__port_to_frames.get(connected_output, (None, None))
                    widget_node = self.__ports_to_node.get(connected_output, (None, None))
                    node = widget_node[1]
                    port = connected_output
                    from_widget = inout_port_widget[1]
                    source_connection_description = GraphConnectionDescription(node, port, from_widget, 0, False)
                    target_connection_description = GraphConnectionDescription(None, None, to_widget, 0, False)
                    drag_handler.on_start.append(
                        lambda d=self._delegate, m=self._model, s=source_connection_description, t=target_connection_description: draw_connection(
                            d, m, s, t
                        )
                    )
                    drag_handler.on_hover_begin.append(
                        lambda target_node, target_port, target_widget, d=self._delegate, m=self._model, s=source_connection_description: hover_connection(
                            target_node, target_port, target_widget, d, m, s, False
                        )
                    )
                    drag_handler.on_can_connect.append(
                        lambda inport, outport=connected_output, m=self._model: can_connect_test(m, inport, outport)
                    )
            else:
                node_index = self._graph_node_index
                # Check for outputs
                connected_inputs = node_index.source_to_target.get(port, [])
                if not connected_inputs:
                    return

                pickup_port = port
                drag_handler.on_empty_complete.append(lambda v=self, p=connected_inputs: empty_drop(v, p, True))

                for connected_input in connected_inputs:
                    drag_handler.on_target_complete.append(
                        lambda *_, m=self._model, p=connected_input, r=pickup_port: remove_connection_to(m, p, r)
                    )
                    drag_handler.on_empty_complete.append(
                        lambda *_, m=self._model, p=connected_input, r=pickup_port: remove_connection_to(m, p, r)
                    )
                    drag_handler.on_target_complete.append(
                        lambda target_port, i=connected_input, m=self._model: set_inputs(m, i, [target_port])
                    )

                    connection_index = node_index.connection_to_id.get((pickup_port, connected_input), None)
                    if connection_index is not None:
                        connection = node_index.cached_connections[connection_index]
                        connection_widget = self._connection_widgets.get(connection, None)

                        drag_handler.on_start.append(lambda w=connection_widget: toggle_visible(w, False))
                        drag_handler.on_abort.append(lambda w=connection_widget: toggle_visible(w, True))

                        if self.__draw_curve_top_layer:
                            connection_over_widget = self._connection_over_widgets.get(connection, None)
                            drag_handler.on_start.append(lambda w=connection_over_widget: toggle_visible(w, False))
                            drag_handler.on_abort.append(lambda w=connection_over_widget: toggle_visible(w, True))

                    inout_port_widget = self.__port_to_frames.get(connected_input, (None, None))
                    widget_node = self.__ports_to_node.get(connected_input, (None, None))
                    node = widget_node[1]
                    port = connected_input
                    from_widget = inout_port_widget[0]
                    source_connection_description = GraphConnectionDescription(node, port, from_widget, 0, True)
                    target_connection_description = GraphConnectionDescription(None, None, to_widget, 0, True)
                    drag_handler.on_start.append(
                        lambda d=self._delegate, m=self._model, s=source_connection_description, t=target_connection_description: draw_connection(
                            d, m, s, t
                        )
                    )
                    drag_handler.on_hover_begin.append(
                        lambda target_node, target_port, target_widget, d=self._delegate, m=self._model, s=source_connection_description: hover_connection(
                            target_node, target_port, target_widget, d, m, s, True
                        )
                    )
                    drag_handler.on_can_connect.append(
                        lambda inport, outport=connected_input, m=self._model: can_connect_test(m, outport, inport)
                    )
        else:
            source_connection_description = GraphConnectionDescription(node, port, from_widget, 0, from_is_input)
            target_connection_description = GraphConnectionDescription(None, None, to_widget, 0, from_is_input)
            drag_handler.on_start.append(
                lambda d=self._delegate, m=self._model, s=source_connection_description, t=target_connection_description: draw_connection(
                    d, m, s, t
                )
            )
            drag_handler.on_hover_begin.append(
                lambda target_node, target_port, target_widget, d=self._delegate, m=self._model, s=source_connection_description, flip=from_is_input: hover_connection(
                    target_node, target_port, target_widget, d, m, s, flip
                )
            )
            drag_handler.on_empty_complete.append(lambda v=self, p=[port], f=from_is_input: empty_drop(v, p, f))
            if from_is_input:
                drag_handler.on_target_complete.append(
                    lambda target_port, p=port, m=self._model: set_inputs(m, p, [target_port])
                )
                drag_handler.on_can_connect.append(
                    lambda outport, inport=port, m=self._model: can_connect_test(m, inport, outport)
                )
            else:
                drag_handler.on_target_complete.append(
                    lambda target_port, p=port, m=self._model: set_inputs(m, target_port, [p])
                )
                drag_handler.on_can_connect.append(
                    lambda inport, outport=port, m=self._model: can_connect_test(m, inport, outport)
                )

        drag_handler.on_start.append(lambda w=self.__user_drag_connection_frame: toggle_visible(w, True))

        drag_handler.on_hover_begin.append(lambda *_, w=self.__user_drag_connection_frame: toggle_visible(w, False))
        drag_handler.on_hover_begin.append(
            lambda *_, w=self.__user_drag_connection_accepted_frame: toggle_visible(w, True)
        )

        drag_handler.on_hover_end.append(lambda *_, w=self.__user_drag_connection_frame: toggle_visible(w, True))
        drag_handler.on_hover_end.append(
            lambda *_, w=self.__user_drag_connection_accepted_frame: toggle_visible(w, False)
        )

        drag_handler.on_completed.append(lambda *_, w=self.__user_drag_connection_frame: clear_frame(w))
        drag_handler.on_completed.append(lambda *_, w=self.__user_drag_connection_accepted_frame: clear_frame(w))

        with self.__user_drag_connection_frame:
            with ui.ZStack():
                ui.Spacer()
                drag_handler.start()

        self.__drag_connection_handler = drag_handler

    def __on_port_hovered(self, node, port, widget, hovered):
        """Called when the mouse pointer enters the area of the port"""
        if self.__drag_connection_handler is None:
            # We are not in connection mode, return
            return

        # We are here because the user is trying to connect ports
        if hovered:
            # The user entered the port widget
            self.__can_connect = self.__drag_connection_handler.can_connect(port)

            # Replace connection with the sticky one
            if self.__can_connect:
                # Show sticky connection and hide the one that follows the mouse
                with self.__user_drag_connection_accepted_frame:
                    with ui.ZStack():
                        ui.Spacer()
                        self.__drag_connection_handler.hover_begin(node, port, widget)
        else:
            self.__drag_connection_handler.hover_end(port)

    def __disconnect_inputs(self, port):
        """Remove connections from port"""
        self._model[port].inputs = []

    def __canvas_space(self, x: float, y: float):
        """Convert mouse to canvas space"""
        if self.__raster_nodes:
            return self.__root_frame.screen_to_canvas_x(x), self.__root_frame.screen_to_canvas_y(y)

        offset_x = x - self.__root_frame.screen_position_x * self.zoom
        offset_y = y - self.__root_frame.screen_position_y * self.zoom
        offset_x = (offset_x - self.pan_x) / self.zoom
        offset_y = (offset_y - self.pan_y) / self.zoom
        return offset_x, offset_y

    def __rectangle_selection_begin(self, x: float, y: float, button: int, modifier: int):
        """Mouse pressed callback"""
        if not self._model or button != 0:
            return

        if (
            not modifier & carb.input.KEYBOARD_MODIFIER_FLAG_SHIFT
            and not modifier & carb.input.KEYBOARD_MODIFIER_FLAG_CONTROL
        ):
            self.__need_clear_selection = True
            asyncio.ensure_future(self._clear_selection_next_frame_async(self._model))

            # if there is modifier, but the modifier is not shift or control, we skip drawing the selection
            # so that users are free use other modifier for other actions
            if modifier:
                return

        self.__rectangle_selection_start_position = self.__canvas_space(x, y)

        # Mouse position in widget space
        x_w = x - self.__selection_layer.screen_position_x
        y_w = y - self.__selection_layer.screen_position_y

        self.__selection_placer_start.offset_x = x_w
        self.__selection_placer_start.offset_y = y_w
        self.__selection_placer_end.offset_x = x_w
        self.__selection_placer_end.offset_y = y_w

    def __rectangle_selection_end(self, x: float, y: float, button: int, modifier: int):
        """Mouse released callback"""
        if self.__rectangle_selection_start_position is None:
            return

        # Clean up selection caches
        self.__selection_placer_start.offset_x = 0
        self.__selection_placer_start.offset_y = 0
        self.__selection_placer_end.offset_x = 0
        self.__selection_placer_end.offset_y = 0
        self.__selection_layer.visible = False
        self.__rectangle_selection_start_position = None
        self.__positions_cache = None
        self.__selection_cache = []

    def __rectangle_selection_moved(self, x: float, y: float, modifier: int, pressed: bool):
        """Mouse moved callback"""
        if self.__rectangle_selection_start_position is None:
            # No rectangle selection
            return

        self._on_rectangle_select(
            self._model, self.__rectangle_selection_start_position, self.__canvas_space(x, y), modifier
        )

        # Mouse position in widget space
        x_w = x - self.__selection_layer.screen_position_x
        y_w = y - self.__selection_layer.screen_position_y

        self.__selection_layer.visible = True
        self.__selection_placer_end.offset_x = x_w
        self.__selection_placer_end.offset_y = y_w

    def _on_finish_connection(self):
        """Called when the user finishes creating a connection."""

        if self.__drag_connection_handler:
            self.__drag_connection_handler.complete()
            self.__drag_connection_handler.destroy()
            self.__drag_connection_handler = None

    def _on_port_context_menu(self, node, port):
        """Open context menu for specific port"""
        self.__port_context_menu = ui.Menu("Port Context Menu", visible=False)

        with self.__port_context_menu:
            if self._model[port].inputs:
                self.__port_context_menu.visible = True
                ui.MenuItem("Disconnect", triggered_fn=lambda p=port: self.__disconnect_inputs(p))

        self.__port_context_menu.show()

    def _on_set_zoom_key_shortcut(self, mouse_button, key):
        """allow user to set the key shortcut for the graphView zoom"""
        self.__root_frame.set_zoom_key_shortcut(mouse_button, key)

    def destroy(self):
        """Destroy the GraphView and clean up associated resources.

        Called by extension before destroying this object. It doesn't happen automatically.
        Without this hot reloading doesn't work."""
        self.set_model(None)
        self.__root_frame = None
        self._delegate = None

        # Destroy each node
        for _, node_widget in self._node_widgets.items():
            node_widget.destroy()
        for _, connection_widget in self._connection_widgets.items():
            connection_widget.destroy()
        for _, connection_widget in self._connection_over_widgets.items():
            connection_widget.destroy()
        self._node_widgets = {}
        self._connection_widgets = {}
        self._connection_over_widgets = {}
        self._node_placers = {}

        self.__port_context_menu = None

        self.__backdrops_stack = None
        self.__connections_under_stack = None
        self.__nodes_stack = None
        self.__connections_over_stack = None
        self.__port_to_frames = {}
        self.__ports_to_node = {}

        self.__user_drag_connection_frame = None
        self.__user_drag_connection_accepted_frame = None

        if self.__drag_connection_handler:
            self.__drag_connection_handler.abort()
            self.__drag_connection_handler.destroy()
            self.__drag_connection_handler = None

        # Destroy the graph index
        self._graph_node_index = GraphNodeIndex(None, self.__port_grouping)

    @property
    def zoom(self):
        """Gets the current zoom level of the graph.

        Returns:
            The current zoom level.
        """
        return self.__root_frame.zoom

    @zoom.setter
    def zoom(self, value):
        """Sets the zoom level of the graph.

        Args:
            value (float): The new zoom level.
        """
        self.__root_frame.zoom = value

    @property
    def zoom_min(self):
        """Gets the minimum zoom level of the graph.

        Returns:
            The minimum zoom level.
        """
        return self.__root_frame.zoom_min

    @zoom_min.setter
    def zoom_min(self, value):
        """Sets the minimum zoom level of the graph.

        Args:
            value (float): The new minimum zoom level.
        """
        self.__root_frame.zoom_min = value

    @property
    def zoom_max(self):
        """Gets the maximum zoom level of the graph.

        Returns:
            The maximum zoom level.
        """
        return self.__root_frame.zoom_max

    @zoom_max.setter
    def zoom_max(self, value):
        """Sets the maximum zoom level of the graph.

        Args:
            value (float): The new maximum zoom level.
        """
        self.__root_frame.zoom_max = value

    @property
    def pan_x(self):
        """Gets the current horizontal pan position of the graph.

        Returns:
            The horizontal pan position.
        """
        return self.__root_frame.pan_x

    @pan_x.setter
    def pan_x(self, value):
        """Sets the horizontal pan position of the graph.

        Args:
            value (float): The new horizontal pan position.
        """
        self.__root_frame.pan_x = value

    @property
    def pan_y(self):
        """Gets the current vertical pan position of the graph.

        Returns:
            The vertical pan position.
        """
        return self.__root_frame.pan_y

    @pan_y.setter
    def pan_y(self, value):
        """Sets the vertical pan position of the graph.

        Args:
            value (float): The new vertical pan position.
        """
        self.__root_frame.pan_y = value
