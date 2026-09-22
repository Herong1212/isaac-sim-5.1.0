# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

"""This module defines the GraphNode class, which represents a widget for individual graph nodes in a graphical interface."""


__all__ = ["GraphNode"]

from .abstract_graph_node_delegate import GraphNodeDescription
from .abstract_graph_node_delegate import GraphNodeLayout
from .abstract_graph_node_delegate import GraphPortDescription
from .graph_model import GraphModel
import omni.ui as ui


class GraphNode:
    """Represents the Widget for the single node. Uses the model and the
    delegate to fill up its layout.

    Args:
        model (GraphModel): The graph model associated with this node.
        item: The item data associated with this node.
        has_input_connection: Indicates if the node has input connections.
        has_output_connection: Indicates if the node has output connections.
        ports (list): List of ports associated with the node.
        delegate: The delegate responsible for node appearance and layout."""

    def __init__(self, model: GraphModel, item, has_input_connection, has_output_connection, ports: list, delegate):
        """Initializes a new instance of the GraphNode."""
        # Port to the tuple of two widgets that represent the port
        self._port_to_frames = {}
        self._port_snapping_frames = {}
        # Port to the tuple of two widgets that are used to draw line to show the connection is in process
        self._port_to_user_drag = {}
        self._port_to_user_drag_placer = {}
        # center port widget (i.e. name labels and string edit fields)
        self._port_center_widgets = {}
        self._header_input_widget = None
        self._header_output_widget = None

        self._has_input_connection = has_input_connection
        self._has_output_connection = has_output_connection

        self._header_widget = None
        self._footer_widget = None
        self._node_bg_widget = None

        self.__root_frame = ui.Frame(width=0, height=0, skip_draw_when_clipped=True)
        # TODO: WeakRef for the model?
        self.__model = model
        self.__delegate = delegate
        self.__item = item
        self.__ports = ports

        # Build everything
        self.__build_layout()

    def __getattr__(self, attr):
        """Pretend it's self.__root_frame"""
        return getattr(self.__root_frame, attr)

    def rebuild_layout(self):
        """Rebuilds the layout of the graph node based on the current node description."""
        node_desc = GraphNodeDescription(self.__item, self._has_input_connection[0], self._has_input_connection[1])

        def __build_node_bg():
            self.__delegate.node_background(self.__model, node_desc)

        def __build_footer():
            self.__delegate.node_footer(self.__model, node_desc)

        def __build_header():
            self.__delegate.node_header(self.__model, node_desc)

        if not self._header_widget.has_build_fn():
            self._header_widget.set_build_fn(__build_header)
        self._header_widget.rebuild()

        if not self._node_bg_widget.has_build_fn():
            self._node_bg_widget.set_build_fn(__build_node_bg)
        self._node_bg_widget.rebuild()

        if not self._footer_widget.has_build_fn():
            self._footer_widget.set_build_fn(__build_footer)
        self._footer_widget.rebuild()

    def __build_layout(self):
        """
        Build the Node layout with the delegate. See GraphNodeDelegate for info.
        When it's called, it will replace all the sub-widgets.
        """

        self._port_to_frames.clear()
        self._port_snapping_frames.clear()
        self._port_to_user_drag.clear()
        self._port_to_user_drag_placer.clear()
        self._port_center_widgets.clear()

        # Sorting ports for column layout. If the port has inputs only, it goes
        # to input_ports. IF the port has both inputs and outputs, it goes to
        # mixed_ports.
        mixed_ports = []
        input_ports = []
        output_ports = []

        node_desc = GraphNodeDescription(self.__item, self._has_input_connection[0], self._has_input_connection[1])

        node_layout = self.__delegate.get_node_layout(self.__model, node_desc)
        for port_entry in self.__ports:
            if node_layout == GraphNodeLayout.LIST or node_layout == GraphNodeLayout.HEAP:
                mixed_ports.append(port_entry)
            elif node_layout == GraphNodeLayout.COLUMNS:
                port, port_input_flags, port_output_flags, level, position, parent_child_count, port_siblings_below = (
                    port_entry
                )
                inputs = self.__model[port].inputs
                outputs = self.__model[port].outputs
                if inputs is None and outputs is None:
                    input_ports.append(port_entry)
                elif inputs is not None and outputs is None:
                    input_ports.append(port_entry)
                elif inputs is None and outputs is not None:
                    output_ports.append(port_entry)
                else:
                    mixed_ports.append(port_entry)

        with self.__root_frame:
            # This "extra" ZStack & Spacer helps fix a width calculation bug that can be
            # seen on nodes using the COLUMNS layout.
            with ui.ZStack():
                ui.Spacer(width=ui.Fraction(1))

                # See GraphNodeDelegate for the detailed information on the layout
                with ui.ZStack(height=0):
                    self._node_bg_widget = ui.Frame()
                    with self._node_bg_widget:
                        self.__delegate.node_background(self.__model, node_desc)

                    if node_layout == GraphNodeLayout.HEAP:
                        stack = ui.ZStack(height=0)
                    else:
                        stack = ui.VStack(height=0)

                    with stack:
                        # Header
                        with ui.HStack():
                            self._header_input_widget = ui.Frame(width=0)
                            with self._header_input_widget:
                                port_widget = self.__delegate.node_header_input(self.__model, node_desc)
                                # The way to set the center of connection. If the
                                # port function doesn't return anything, the
                                # connection is centered to the frame. If it
                                # returns a widget, the connection is centered to
                                # the widget returned.
                                if port_widget:
                                    self._header_input_widget = port_widget

                            self._header_widget = ui.Frame()
                            with self._header_widget:
                                self.__delegate.node_header(self.__model, node_desc)

                            self._header_output_widget = ui.Frame(width=0)
                            with self._header_output_widget:
                                port_widget = self.__delegate.node_header_output(self.__model, node_desc)
                                # Set the center of connection.
                                if port_widget:
                                    self._header_output_widget = port_widget

                        # One port per line
                        for (
                            port,
                            port_input_flags,
                            port_output_flags,
                            port_level,
                            pos,
                            siblings,
                            siblings_below,
                        ) in mixed_ports:
                            self.__build_port(
                                node_desc,
                                port,
                                port_input_flags,
                                port_output_flags,
                                port_level,
                                pos,
                                siblings,
                                siblings_below,
                                node_layout == GraphNodeLayout.HEAP,
                            )

                        # Two ports per line
                        with ui.HStack():
                            if len(input_ports) == 0 or len(output_ports) == 0:
                                with ui.VStack(height=0, width=ui.Fraction(0 if len(input_ports) == 0 else 1)):
                                    for (
                                        port,
                                        port_input_flags,
                                        port_output_flags,
                                        port_level,
                                        pos,
                                        siblings,
                                        siblings_below,
                                    ) in input_ports:
                                        self.__build_port(
                                            node_desc,
                                            port,
                                            port_input_flags,
                                            None,
                                            port_level,
                                            pos,
                                            siblings,
                                            siblings_below,
                                            False,
                                        )
                                with ui.VStack(height=0, width=ui.Fraction(0 if len(output_ports) == 0 else 1)):
                                    for (
                                        port,
                                        port_input_flags,
                                        port_output_flags,
                                        port_level,
                                        pos,
                                        siblings,
                                        siblings_below,
                                    ) in output_ports:
                                        self.__build_port(
                                            node_desc,
                                            port,
                                            None,
                                            port_output_flags,
                                            port_level,
                                            pos,
                                            siblings,
                                            siblings_below,
                                            False,
                                        )
                            else:
                                # width=0 lets each column only take up the amount of space it needs
                                with ui.VStack(height=0, width=0):
                                    for (
                                        port,
                                        port_input_flags,
                                        port_output_flags,
                                        port_level,
                                        pos,
                                        siblings,
                                        siblings_below,
                                    ) in input_ports:
                                        self.__build_port(
                                            node_desc,
                                            port,
                                            port_input_flags,
                                            None,
                                            port_level,
                                            pos,
                                            siblings,
                                            siblings_below,
                                            False,
                                        )
                                ui.Spacer()  # spreads the 2 sides apart from each other
                                with ui.VStack(height=0, width=0):
                                    for (
                                        port,
                                        port_input_flags,
                                        port_output_flags,
                                        port_level,
                                        pos,
                                        siblings,
                                        siblings_below,
                                    ) in output_ports:
                                        self.__build_port(
                                            node_desc,
                                            port,
                                            None,
                                            port_output_flags,
                                            port_level,
                                            pos,
                                            siblings,
                                            siblings_below,
                                            False,
                                        )

                        # Footer
                        self._footer_widget = ui.Frame()
                        with self._footer_widget:
                            self.__delegate.node_footer(self.__model, node_desc)

    def __build_port(
        self,
        node_desc: GraphNodeDescription,
        port,
        port_input_flags,
        port_output_flags,
        level: int,
        relative_position: int,
        parent_child_count: int,
        siblings_below: list[int],
        is_heap: bool,
    ):
        """The layout for one single port line."""

        # port_input_flags is a tuple of 2 bools. The first item is the flag
        # that is True if the port is a source in connection to the input (left
        # side). The second item is the flag that is True when this port is a
        # target in the connection to the input. port_output_flags is the same
        # for output (right side). If port_input_flags or port_output_flags is
        # None, it doesn't produce left or right part.

        if is_heap:
            width = ui.Fraction(1)
            stack = ui.ZStack()
        else:
            width = ui.Pixel(0)
            stack = ui.HStack()

        def fit_to_mouse(placer: ui.Placer, x: float, y: float):
            """
            If the port is big we need to make the placer small enough
            and move it to the mouse cursor to make the connection follow
            the mouse
            """
            # The new size
            SIZE = 3.0
            placer.width = ui.Pixel(SIZE)
            placer.height = ui.Pixel(SIZE)
            # Move to the mouse position
            placer.offset_x = x - placer.screen_position_x - SIZE / 2
            placer.offset_y = y - placer.screen_position_y - SIZE / 2

        def reset_offset(placer: ui.Placer):
            # Put it back to the port
            placer.offset_x = 0
            placer.offset_y = 0
            # Restore the size
            placer.width = ui.Fraction(1)
            placer.height = ui.Fraction(1)

        def set_draggable(placer: ui.Placer, draggable: bool):
            placer.draggable = draggable

        with stack:
            if port_input_flags is None:
                input_port_widget = None
            else:
                with ui.ZStack(width=width):
                    # for heap layouted node, since all the input port, port_center_widget, and output port are stacked together,
                    # we don't want the reversed connection from input port, otherwise, port_center_widget's mouse pressed drag and move is not working.
                    if self.__model[port].inputs is not None and not is_heap:
                        # The placer and the widget that follows the
                        # mouse cursor when the user creates a connection
                        input_userconnection_placer = ui.Placer(stable_size=True, draggable=True)
                        input_userconnection_placer.set_mouse_pressed_fn(
                            lambda x, y, b, *_, p=input_userconnection_placer: b == 0 and fit_to_mouse(p, x, y)
                        )
                        input_userconnection_placer.set_mouse_released_fn(
                            lambda x, y, b, *_, p=input_userconnection_placer: b == 0 and reset_offset(p)
                        )

                        self._port_to_user_drag_placer[port] = input_userconnection_placer
                        with input_userconnection_placer:
                            # This widget follows the cursor when the user creates a connection.
                            # Line is stuck to this widget.
                            rect = ui.Spacer()
                            self._port_to_user_drag[port] = (None, rect)

                    input_port_widget = ui.Frame(width=width)
                    with input_port_widget:
                        port_desc = GraphPortDescription(
                            port, level, relative_position, parent_child_count, port_input_flags[0], port_input_flags[1]
                        )
                        port_desc.siblings_below = siblings_below
                        port_widget = self.__delegate.port_input(self.__model, node_desc, port_desc)
                        # Set the center of connection.
                        if port_widget:
                            input_port_widget = port_widget

            port_desc = GraphPortDescription(port, level, relative_position, parent_child_count)
            port_desc.siblings_below = siblings_below

            port_center_frame = ui.Frame()
            with port_center_frame:
                with ui.ZStack():
                    port_center_widget = self.__delegate.port(self.__model, node_desc, port_desc)
                    self._port_center_widgets[port_desc.port] = port_center_widget
                    # make the snapping area as half of the node size
                    port_snapping_frame = ui.Spacer(width=ui.Percent(50))

            # for snapping effect
            if self.__model[port].inputs is None:  # this is an output port
                self._port_snapping_frames[port] = (None, port_snapping_frame)
            else:  # this is an input port
                self._port_snapping_frames[port] = (port_snapping_frame, None)

            if port_output_flags is None:
                output_port_widget = None
            else:
                with ui.ZStack(width=width):
                    if self.__model[port].outputs is not None:
                        # The placer and the widget that follows the
                        # mouse cursor when the user creates a connection
                        output_userconnection_placer = ui.Placer(stable_size=True, draggable=True)
                        output_userconnection_placer.set_mouse_pressed_fn(
                            lambda x, y, b, *_, p=output_userconnection_placer: b == 0 and fit_to_mouse(p, x, y)
                        )
                        output_userconnection_placer.set_mouse_released_fn(
                            lambda x, y, b, *_, p=output_userconnection_placer: b == 0 and reset_offset(p)
                        )

                        if port_center_widget:
                            port_center_widget.set_mouse_pressed_fn(
                                lambda x, y, b, *_, p=output_userconnection_placer: b == 0 and set_draggable(p, False)
                            )
                            port_center_widget.set_mouse_released_fn(
                                lambda x, y, b, *_, p=output_userconnection_placer: b == 0 and set_draggable(p, True)
                            )

                        self._port_to_user_drag_placer[port] = output_userconnection_placer
                        with output_userconnection_placer:
                            # This widget follows the cursor when the
                            # user creates a connection. Line is
                            # stuck to this widget.
                            rect = ui.Spacer()
                            self._port_to_user_drag[port] = (None, rect)

                    # The port widget
                    output_port_widget = ui.Frame()
                    with output_port_widget:
                        port_desc = GraphPortDescription(
                            port,
                            level,
                            relative_position,
                            parent_child_count,
                            port_output_flags[0],
                            port_output_flags[1],
                        )
                        port_desc.siblings_below = siblings_below
                        port_widget = self.__delegate.port_output(self.__model, node_desc, port_desc)
                        # Set the center of connection.
                        if port_widget:
                            output_port_widget = port_widget

        # Save input and output frame for each port
        self._port_to_frames[port] = (input_port_widget, output_port_widget)

    @property
    def ports(self):
        """Gets the dictionary mapping ports to their frames.

        Returns:
            A dictionary where the key is a port and the value is a tuple of two ui.Widget objects representing the port.
        """
        return self._port_to_frames

    @property
    def snapping_widgets(self):
        """Gets the dictionary of widgets used for snapping connections.

        Returns:
            A dictionary where the key is a port and the value is a tuple with ui.Widget objects used for snapping connections.
        """
        return self._port_snapping_frames

    @property
    def port_center_widgets(self):
        """Gets the dictionary for port center widgets which contains the port name label and edit fields.

        Returns:
            A dictionary where the key is the port and the value is a ui.Widget or None if the delegate does not return a widget.
        """
        return self._port_center_widgets

    @property
    def user_drag(self):
        """Gets the dictionary with widgets that follow the mouse cursor when the user creates a connection.

        Returns:
            A dictionary with the port as the key and widget that follows the mouse cursor when the user creates a connection.
        """
        return self._port_to_user_drag

    @property
    def user_drag_placer(self):
        """Gets the dictionary with placers that follow the mouse cursor when the user creates a connection.

        Returns:
            A dictionary with the port as the key and placer that follows the mouse cursor when the user creates a connection.
        """
        return self._port_to_user_drag_placer

    @property
    def header_input_frame(self):
        """Gets the frame that holds the inputs on the left side of the header bar.

        Returns:
            The Frame that holds the inputs on the left side of the header bar."""
        return self._header_input_widget

    @property
    def header_output_frame(self):
        """Gets the frame that holds the outputs on the right side of the header bar.

        Returns:
            The Frame that holds the outputs on the right side of the header bar."""
        return self._header_output_widget

    @property
    def header_frame(self):
        """Gets the frame that holds the entire header bar.

        Returns:
            The Frame that holds the entire header bar."""
        return self._header_widget

    def destroy(self):
        """Called by extension before destroying this object. It doesn't happen automatically.
        Without this hot reloading doesn't work."""
        self._port_to_frames = None
        self._port_snapping_frames = None
        self._port_to_user_drag = None
        self._port_to_user_drag_placer = None
        self._port_center_widgets = None
        if self.__root_frame:
            self.__root_frame.destroy()
        self.__root_frame = None
        self.__model = None
        self.__delegate = None

        self._header_widget = None
        self._footer_widget = None
        self._node_bg_widget = None

    @property
    def skip_draw_clipped(self):
        """Gets the skip_draw_when_clipped property of the root frame.

        Returns:
            The skip_draw_when_clipped property of the root frame."""
        return self.__root_frame.skip_draw_when_clipped

    @skip_draw_clipped.setter
    def skip_draw_clipped(self, value):
        """Sets the skip_draw_when_clipped property of the root frame.

        Args:
            value (bool): The new skip_draw_when_clipped state to be applied to the root frame."""
        self.__root_frame.skip_draw_when_clipped = value

    @property
    def selected(self):
        """Gets the widget selected style state.

        Returns:
            The selected style state of the widget."""
        if self.__root_frame:
            return self.__root_frame.selected

    @selected.setter
    def selected(self, value):
        """Sets the widget selected style state.

        Args:
            value (bool): The new selected state to be applied to the widget."""
        if self.__root_frame:
            self.__root_frame.selected = value

    @property
    def visible(self) -> bool:
        """Gets the visibility state of the graph node.

        Returns:
            The visibility state of the graph node."""
        return self.__root_frame.visible

    @visible.setter
    def visible(self, value: bool):
        """Sets the visibility of the graph node.

        Args:
            value (bool): The new visibility state to be applied to the graph node."""
        self.__root_frame.visible = value
