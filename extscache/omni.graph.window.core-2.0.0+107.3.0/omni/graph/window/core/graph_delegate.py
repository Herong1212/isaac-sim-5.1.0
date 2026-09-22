# noqa: too-many-lines

# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["OmniGraphNodeDelegate"]
import asyncio
import importlib
import weakref
from contextlib import suppress
from functools import partial
from typing import Callable, Dict, List, Optional, Tuple, Union

import omni.graph.core as og
import omni.graph.tools as ogt
import omni.ui as ui
from omni.kit.graph.delegate.modern import (
    HEADER,
    HIGHLIGHT_THICKNESS,
    ICON,
    NODE_WIDTH_MARGIN,
    PORT_VISIBLE_MIN,
    STATE_TOGGER,
    TEXT_VISIBLE_MIN,
)
from omni.kit.graph.delegate.modern import GraphNodeDelegate as GraphNodeDelegateBase
from omni.kit.graph.delegate.modern import GraphNodeDelegateFull
from omni.kit.graph.delegate.modern.compound_node_delegate import CompoundInputOutputNodeDelegate
from omni.kit.graph.editor.core import GraphEditorCoreWidget
from omni.kit.widget.graph import GraphNodeLayout, IsolationGraphModel
from omni.kit.widget.graph.abstract_graph_node_delegate import (
    GraphConnectionDescription,
    GraphNodeDescription,
    GraphPortDescription,
)
from omni.kit.widget.graph.graph_model import GraphModel
from pxr import Sdf, Usd

from . import graph_config
from .compounds import CompoundUtils
from .graph_context_menu import ClearTargetMenuFunctor, MapToTargetMenuFunctor, OmniGraphEmptyPortContextMenu
from .graph_model import OmniGraphModel
from .graph_operations import (
    can_convert_type,
    can_promote_to_constant,
    can_promote_to_variable,
    can_rename_port,
    get_compatible_variables,
    is_help_available_for_node_type,
    promote_attribute_to_compound,
    promote_to_constant,
    promote_to_existing_variable,
    promote_to_variable,
    remove_subgraph_port,
    show_help_for_node_type,
)
from .multifield_dialog import MultiFieldDialog
from .virtual_node_helper import VirtualNodeHelper

CONNECTION = 0xFF9A9A9A


class _DelayedAction:
    # Helper class to asynchronously perform a start function after a delay. The stop function is performed
    # immediately and cancels the start function if it hasn't been executed yet. Handles all of the asyncio
    # task management so you don't have to.
    def __init__(self, delay: float, start_fn: Callable, stop_fn: Callable = None):
        self._delay = delay
        self._start_fn = start_fn
        self._stop_fn = stop_fn
        self._task = None

    def __del__(self):
        if self._task:
            self._task.cancel()

    def start(self):
        if self._task:
            self._task.cancel()

        async def do_action():
            await asyncio.sleep(self._delay)
            self._start_fn()

        self._task = asyncio.ensure_future(do_action())

    def stop(self):
        if self._task:
            self._task.cancel()
            self._task = None
        self._stop_fn()


class OmniGraphCompoundInputOutputNodeDelegate(CompoundInputOutputNodeDelegate):
    """
    Fallback delegate for compound input and output nodes

    This is used to remove the default context menus
    """

    def port_input(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        frame = super().port_input(model, node_desc, port_desc)
        if frame:
            frame.set_mouse_pressed_fn(None)
        return frame

    def port_output(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        frame = super().port_output(model, node_desc, port_desc)
        if frame:
            frame.set_mouse_pressed_fn(None)
        return frame


class OmniGraphNodeDelegate(GraphNodeDelegateBase):
    def __init__(self, graph_widget: GraphEditorCoreWidget):
        super().__init__()
        self._graph_widget: GraphEditorCoreWidget = graph_widget
        self._curve_context_menu = None
        self.show_header_icon = True
        self.show_header_background = True
        self.header_label_alignment = ui.Alignment.LEFT_CENTER
        self.__port_context = None
        self.__selected_compound_candidates = None

        # Weak reference to the top-most widget for which the help icon appears when the mouse hovers over it.
        # Only valid for the node currently being built.
        self.__help_hover_widget: ui.Widget = None

        # store the ui stack for each port
        self.__port_stack = {}

        # Store the editable name widgets. Used to decide whether to allow entering the compound or not
        # key = port/node-name
        # value = string field widget
        self.__edit_widgets = {}

        # override the CompoundInputOutputNodeDelegates
        self.add_route(OmniGraphCompoundInputOutputNodeDelegate(), type="InputNode")
        self.add_route(OmniGraphCompoundInputOutputNodeDelegate(), type="OutputNode")

    def destroy(self):
        super().destroy()
        self.__port_context = None
        self.__help_hover_widget = None

    def get_node_layout(self, model, node_desc: GraphNodeDescription):
        """Called to determine the node layout"""
        return GraphNodeLayout.LIST

    @staticmethod
    def __build_port_tooltip(description: str):
        """Build the tooltip UI for a port"""
        padding = 2
        with ui.VStack():
            ui.Spacer(height=padding)
            with ui.HStack():
                ui.Spacer(width=padding)
                ui.Label(
                    f"{description}\n",
                    style={"font_size": 14, "color": 0xFF23211F},
                )
                ui.Spacer(width=padding)
            ui.Spacer(height=padding)

    def _data_port_input(
        self, model: OmniGraphModel, node_desc: GraphNodeDescription, port_desc: GraphPortDescription
    ) -> Optional[ui.Widget]:
        """Build a standard input data port"""
        # The standard port from the base class
        port = port_desc.port
        style = {"Graph.Connection.Port": {"background_color": CONNECTION}}
        widget = ui.ZStack()
        with widget:
            # Override the default tooltip by building the tooltip again on top of the default
            GraphNodeDelegateFull.build_port_input(model, node_desc, port_desc, style, "Graph.Connection.Port")
            GraphNodeDelegateFull.build_tooltip([model.port_tooltip_text(port)])
        return widget

    def _execution_port_input(
        self, model: OmniGraphModel, node_desc: GraphNodeDescription, port_desc: GraphPortDescription
    ) -> Optional[ui.Widget]:
        """Build a execution port input"""
        port = port_desc.port
        if model[port].inputs is None:
            return None

        # Input execution pin dimensions
        input_exec_width = 12
        input_exec_height = 17
        input_exec_pin_width = 12
        input_exec_pin_height = 19

        widget = ui.ZStack()
        with widget:
            if not port_desc.connected_target:
                ui.Frame(
                    style={"background_color": 0xFF99CCCC},
                    tooltip_fn=lambda: self.__build_port_tooltip(model.port_tooltip_text(port)),
                )
            with ui.HStack():
                ui.Spacer(width=NODE_WIDTH_MARGIN)
                with ui.VStack(visible_min=PORT_VISIBLE_MIN):
                    ui.Spacer()
                    ui.Image(
                        f"{graph_config.Paths.ICON_PATH}/omnigraph_input_exec_dark.svg",
                        width=input_exec_width,
                        height=input_exec_height,
                        fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                        style={"color": 0xFF9A9A9A},
                    )
                    ui.Spacer()
            if port_desc.connected_target:
                with ui.HStack():
                    ui.Spacer(width=HIGHLIGHT_THICKNESS)
                    ui.Image(
                        f"{graph_config.Paths.ICON_PATH}/omnigraph_inputPin_exec_dark.svg",
                        width=input_exec_pin_width,
                        height=input_exec_pin_height,
                        fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                    )
        return widget

    def __get_node_position(self, model: OmniGraphModel, port_desc: GraphPortDescription):
        """Get the position of the node that owns the port"""
        if VirtualNodeHelper.is_virtual_node_port(port_desc.port):
            # the position changes between input and output properties
            return model[port_desc.port].position

        # otherwise the node prim can be used
        return model[port_desc.port.GetPrimPath()].position

    def _on_input_port_context_click(
        self, model: OmniGraphModel, port_desc: GraphPortDescription, x: float, y: float, mod: int
    ):
        """Called when there is a context click on a port"""
        if mod != 0:
            return

        # Add Port on input and output nodes. Support context menu to add new port on the fly
        if isinstance(port_desc.port, IsolationGraphModel.EmptyPort):
            # Note: is_input is false because we are creating an output port on the compound, even though this is an
            # input port on the virtual node
            self.__port_context = OmniGraphEmptyPortContextMenu()
            self.__port_context.build(port_desc.port, is_input=False)
            self.__port_context.show()
            return

        # ignore if it is connected. The "Disconnect" menu has priority, and it's not valid
        connections = model[port_desc.port].inputs
        if connections is None or len(connections) > 0:
            return

        is_virtual_node_port = VirtualNodeHelper.is_virtual_node_port(port_desc.port)
        can_promote_to_var = can_promote_to_variable(model, port_desc.port)
        can_promote_to_const = can_promote_to_constant(model, port_desc.port)
        can_convert_tp = can_convert_type(model, port_desc.port)

        # Offset new nodes to the left of the existing one
        node_pos = self.__get_node_position(model, port_desc)
        pos = model.find_next_position_descending((node_pos[0] - 250, node_pos[1] + 50))

        promote_to_variable_fn = partial(promote_to_variable, model, port_desc.port, pos)
        promote_to_constant_fn = partial(promote_to_constant, model, port_desc.port, pos)

        variables = get_compatible_variables(model, port_desc.port)

        self.__port_context = ui.Menu("Context")
        with self.__port_context:
            separator = False
            if graph_config.Supports.compound_subgraphs():
                if CompoundUtils.is_node_in_a_compound(port_desc.port):
                    separator = True
                    ui.MenuItem(
                        "Promote to Compound",
                        triggered_fn=partial(promote_attribute_to_compound, model, port_desc.port),
                        enabled=CompoundUtils.can_promote_attribute_to_compound_subgraph(port_desc.port),
                    )
                converted_port = VirtualNodeHelper.convert_from(port_desc.port)
                if CompoundUtils.is_compound_subgraph_node(converted_port):
                    separator = True
                    ui.MenuItem("Rename Port", triggered_fn=partial(self._on_rename_port, port_desc.port))
                    ui.Separator()
                    ui.MenuItem("Remove Port", triggered_fn=partial(remove_subgraph_port, model, converted_port))

            # ignore promotion on virtual ports
            if not is_virtual_node_port:
                if separator:
                    ui.Separator()
                if variables:
                    with ui.Menu("Set from Variable"):
                        for var in variables:
                            ui.MenuItem(
                                var.display_name,
                                triggered_fn=partial(
                                    promote_to_existing_variable, model, port_desc.port, var.name, pos
                                ),
                            )
                ui.MenuItem("Promote to Variable", triggered_fn=promote_to_variable_fn, enabled=can_promote_to_var)
                ui.MenuItem("Promote to Constant", triggered_fn=promote_to_constant_fn, enabled=can_promote_to_const)
                if graph_config.Settings.is_target_mapping_enabled():
                    with ui.Menu("Graph Target"):
                        ui.MenuItem("Map to...", triggered_fn=MapToTargetMenuFunctor(model, port_desc.port))
                        if ClearTargetMenuFunctor.should_display(port_desc.port):
                            ui.MenuItem("Clear", triggered_fn=ClearTargetMenuFunctor(model, port_desc.port))

                if can_convert_tp:
                    try:
                        # Skip this if we are working with an old version of kit
                        from omni.graph.ui import build_port_type_convert_menu

                        build_port_type_convert_menu(port_desc.port)
                    except ImportError:
                        pass

        self.__port_context.show()

    def port_input(self, model: OmniGraphModel, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        port = port_desc.port
        widget = None

        # if the node is a virtual node (see IsolationGraphModel.InputNode) the port will be an
        # IsolationGraphModel.EmptyPort rather than a prim, which will be handled by the base implementation. But since
        # we still want to customize the context menu, have it routed to our context click function
        if not isinstance(port_desc.port, Sdf.Path):
            widget = super().port_input(model, node_desc, port_desc)
        elif not model[port].is_execution_pin:
            widget = self._data_port_input(model, node_desc, port_desc)
        else:
            widget = self._execution_port_input(model, node_desc, port_desc)

        if not widget:
            return

        def on_mouse_click(port, x: float, y: float, button, mod):
            if button == 1:
                self._on_input_port_context_click(model, port_desc, x, y, mod)

        widget.set_mouse_pressed_fn(partial(on_mouse_click, port))

    def _data_port_output(
        self, model: OmniGraphModel, node_desc: GraphNodeDescription, port_desc: GraphPortDescription
    ) -> Optional[ui.Widget]:
        """Build a standard data output port"""
        port = port_desc.port
        # The standard port from the base class
        style = {"Graph.Connection.Port": {"background_color": CONNECTION}}
        widget = ui.ZStack()
        with widget:
            # Override the default tooltip by building the tooltip again on top of the default
            GraphNodeDelegateFull.build_port_output(model, node_desc, port_desc, style, "Graph.Connection.Port")
            GraphNodeDelegateFull.build_tooltip([model.port_tooltip_text(port)])
        return widget

    def _execution_port_output(
        self, model: OmniGraphModel, node_desc: GraphNodeDescription, port_desc: GraphPortDescription
    ) -> Optional[ui.Widget]:
        """Build an execution output port"""
        port = port_desc.port
        if model[port].outputs is None:
            return None

        # Output execution pin dimensions
        output_exec_pin_width = 10
        output_exec_pin_height = 11
        output_exec_width = 16
        output_exec_height = 20

        widget = ui.ZStack()
        with widget:
            if not port_desc.connected_source:
                ui.Frame(
                    style={"background_color": 0xFF99CCCC},
                    tooltip_fn=lambda: self.__build_port_tooltip(model.port_tooltip_text(port)),
                )

            with ui.HStack():
                ui.Image(
                    f"{graph_config.Paths.ICON_PATH}/omnigraph_output_exec_dark.svg",
                    width=output_exec_width,
                    height=output_exec_height,
                    fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                    style={"color": 0xFF9A9A9A},
                    visible_min=PORT_VISIBLE_MIN,
                )
                ui.Spacer(width=3)

            if port_desc.connected_source:
                with ui.HStack():
                    ui.Spacer(width=0.5 * (output_exec_width - output_exec_pin_width))
                    with ui.VStack():
                        ui.Spacer(height=0.5 * (output_exec_height - output_exec_pin_height))
                        ui.Image(
                            f"{graph_config.Paths.ICON_PATH}/omnigraph_outputPin_exec_dark.svg",
                            width=output_exec_pin_width,
                            height=output_exec_pin_height,
                            fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                        )

        return widget

    def _on_output_port_context_click(
        self, model: OmniGraphModel, port_desc: GraphPortDescription, x: float, y: float, mod: int
    ):
        """Called when there is a context click on an output port"""
        if mod != 0:
            return

        # Add Port on input and output nodes
        if isinstance(port_desc.port, IsolationGraphModel.EmptyPort):
            # Note: is_input is true because we are creating an input port on the compound, even though this is an
            # output port on the virtual node
            self.__port_context = OmniGraphEmptyPortContextMenu()
            self.__port_context.build(port_desc.port, is_input=True)
            self.__port_context.show()
            return

        # ignore if it is connected. The "Disconnect" menu has priority, and it's not valid
        connections = model[port_desc.port].outputs
        if connections is None or len(connections) > 0:
            return

        is_virtual_node_port = VirtualNodeHelper.is_virtual_node_port(port_desc.port)
        variables = get_compatible_variables(model, port_desc.port)

        # Offset new nodes to the right of the existing one
        node_pos = self.__get_node_position(model, port_desc)
        pos = model.find_next_position_descending((node_pos[0] + 350, node_pos[1] + 50))

        can_promote_to_var = can_promote_to_variable(model, port_desc.port)
        promote_to_variable_fn = partial(promote_to_variable, model, port_desc.port, pos)

        self.__port_context = ui.Menu("Context")
        with self.__port_context:
            separator = False
            if graph_config.Supports.compound_subgraphs():
                if CompoundUtils.is_node_in_a_compound(port_desc.port):
                    separator = True
                    ui.MenuItem(
                        "Promote to Compound",
                        triggered_fn=partial(promote_attribute_to_compound, model, port_desc.port),
                        enabled=CompoundUtils.can_promote_attribute_to_compound_subgraph(port_desc.port),
                    )
                converted_port = VirtualNodeHelper.convert_from(port_desc.port)
                if CompoundUtils.is_compound_subgraph_node(converted_port):
                    separator = True
                    ui.MenuItem("Rename Port", triggered_fn=partial(self._on_rename_port, port_desc.port))
                    ui.Separator()
                    ui.MenuItem("Remove Port", triggered_fn=partial(remove_subgraph_port, model, converted_port))
            if not is_virtual_node_port:
                if separator:
                    ui.Separator()
                if variables:
                    with ui.Menu("Write to Variable"):
                        for var in variables:
                            ui.MenuItem(
                                var.display_name,
                                triggered_fn=partial(
                                    promote_to_existing_variable, model, port_desc.port, var.name, pos
                                ),
                            )
                ui.MenuItem("Promote to Variable", triggered_fn=promote_to_variable_fn, enabled=can_promote_to_var)
                if graph_config.Settings.is_target_mapping_enabled():
                    with ui.Menu("Graph Target"):
                        ui.MenuItem("Map to...", triggered_fn=MapToTargetMenuFunctor(model, port_desc.port))
                        if ClearTargetMenuFunctor.should_display(port_desc.port):
                            ui.MenuItem("Clear", triggered_fn=ClearTargetMenuFunctor(model, port_desc.port))

        self.__port_context.show()

    def port_output(self, model: OmniGraphModel, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        port = port_desc.port
        widget = None
        if not model[port].is_execution_pin:
            widget = self._data_port_output(model, node_desc, port_desc)
        else:
            widget = self._execution_port_output(model, node_desc, port_desc)

        if not widget:
            return

        def on_mouse_click(port, x: float, y: float, button, mod):
            if button == 1:
                self._on_output_port_context_click(model, port_desc, x, y, mod)

        widget.set_mouse_pressed_fn(partial(on_mouse_click, port))

    def port(self, model: OmniGraphModel, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        """Called to create the middle part of the port"""
        port = port_desc.port
        port_name = model[port].nice_name

        if port_name is None:
            port_name = model[port].name

        if graph_config.Settings.are_compounds_enabled() and graph_config.Supports.compound_subgraphs():
            stack = GraphNodeDelegateFull.build_port(
                model, node_desc, port_desc, port_name, partial(can_rename_port, port)
            )
        else:
            stack = GraphNodeDelegateFull.build_port(model, node_desc, port_desc, port_name)

        # find all the string fields
        def get_string_fields(root):
            with suppress(Exception):
                for c in ui.Inspector.get_children(root):
                    if isinstance(c, ui.StringField):
                        self.__edit_widgets[port] = c
                        return
                    get_string_fields(c)

        self.__port_stack[port] = stack
        get_string_fields(stack)
        return stack

    def _on_curve_right_clicked(self, model, target_port, source_port):
        """Open context menu for specific curve"""
        self._curve_context_menu = ui.Menu("Curve Context Menu", visible=False)
        target_item = model[target_port]

        input_ports = target_item.inputs

        def _disconnect():
            model.remove_connections(target_port, [source_port])

        with self._curve_context_menu:
            if input_ports:
                self._curve_context_menu.visible = True
                ui.MenuItem("Disconnect", triggered_fn=_disconnect)
        self._curve_context_menu.show()

    def connection(
        self,
        model: OmniGraphModel,
        source: GraphConnectionDescription,
        target: GraphConnectionDescription,
        foreground: bool = False,
    ) -> Tuple[ui.ZStack, ui.FreeLine, ui.FreeBezierCurve]:
        """Called to create the connection between ports"""

        execution_connection_color = 0xFFF5F5F5
        port_type = str(model[source.port].type)
        style = {
            # make the tooltip style transparent to avoid the artifact while target is not set
            "Tooltip": {"background_color": 0x0, "color": 0xFFAAAAAA, "border_color": 0x0},
            f"Graph.Connection::{port_type}": {
                "color": CONNECTION,
                "background_color": CONNECTION,
                "border_width": 2.0,
            },
            "Graph.Connection.execution": {"color": execution_connection_color, "border_width": 2.0},
            "Graph.Connection.execution:hovered": {"color": execution_connection_color, "border_width": 4.0},
        }
        override_style_name = "Graph.Connection"
        if model[source.port].is_execution_pin:
            override_style_name = "Graph.Connection.execution"
        try:
            curve_container_widget, freeline_widget, curve_widget = GraphNodeDelegateFull.build_connection(
                model, source, target, style, override_style_name, foreground
            )
        except TypeError:
            # Use the old version of build_connection as a fallback
            curve_container_widget, freeline_widget, curve_widget = GraphNodeDelegateFull.build_connection(
                model, source, target, style, override_style_name
            )

        # Only need to call on the background pass, not both.
        # Otherwise we might have 2 context menus pop up together.
        if not foreground:
            if freeline_widget:
                freeline_widget.set_mouse_pressed_fn(
                    lambda x, y, b, m, p=target.port, s=source.port, _model=model: (
                        self._on_curve_right_clicked(_model, p, s) if b == 1 else None
                    )
                )
            if curve_widget:
                curve_widget.set_mouse_pressed_fn(
                    lambda x, y, b, m, p=target.port, s=source.port, _model=model: (
                        self._on_curve_right_clicked(_model, p, s) if b == 1 else None
                    )
                )
        return curve_container_widget, freeline_widget, curve_widget

    # This is a clone of modern delegate's _build_rectangle.
    #
    # TODO: Create a separate delegate which derives from modern delegate's GraphNodeDelegateFull and set up
    #       routing for it so that we can just call methods like these instead of duplicating them.
    def _build_rectangle(self, radius, draw_top, type_name, name, style_override=None):
        """
        Build rectangle of the specific design.

        Args:
            radius: The radius of round corers. The corners are top-left and
                    bottom-right.
            draw_top: When false the top corners are straight.
            type_name: style_type_name_override of each widget
            name: name of each widget
            style_override: the style to apply to the top level node
        """
        stack = ui.VStack(alignment=ui.Alignment.CENTER)
        if style_override:
            stack.set_style(style_override)

        with stack:
            # Top of the rectangle
            if draw_top:
                with ui.HStack(height=0):
                    ui.Circle(
                        radius=radius,
                        width=0,
                        height=0,
                        size_policy=ui.CircleSizePolicy.FIXED,
                        alignment=ui.Alignment.RIGHT_BOTTOM,
                        style_type_name_override=type_name,
                        name=name,
                    )
                    ui.Rectangle(style_type_name_override=type_name, name=name)
            else:
                ui.Rectangle(style_type_name_override=type_name, name=name)

            # Middle of the rectangle
            ui.Rectangle(style_type_name_override=type_name, name=name)

            # Bottom of the rectangle
            with ui.HStack(height=0):
                ui.Rectangle(style_type_name_override=type_name, name=name)
                ui.Circle(
                    radius=radius,
                    width=0,
                    height=0,
                    size_policy=ui.CircleSizePolicy.FIXED,
                    alignment=ui.Alignment.LEFT_TOP,
                    style_type_name_override=type_name,
                    name=name,
                )

    def draw_header_label_center(
        self,
        model: OmniGraphModel,
        node: Union[og.Node, Usd.Prim],
        node_name: str,
        node_category: str,
        bg_style_override: str,
        label_style_override: str,
    ):
        with ui.ZStack(spacing=0, style={"margin_width": 0}):
            label = ui.Label(
                node_name,
                visible_min=TEXT_VISIBLE_MIN,
                style_type_name_override=label_style_override,
                style={"margin_width": 0},
                alignment=self.header_label_alignment,
            )
            # If we're displaying the name, as opposed to the type, then allow it to be edited on dbl-click.
            # Also show name of compounds, regardless of the show name as type setting
            if not graph_config.Settings.get_show_name_as_type() or CompoundUtils.is_compound_node(node):
                label_field = ui.StringField()
                label_field.visible = False
                self.__edit_widgets[node_name] = label_field

                def show_edit_field(field, *args):
                    field.model.set_value(node_name)
                    field.visible = True

                label.set_mouse_double_clicked_fn(partial(show_edit_field, label_field))

                def label_edited(field, *args):
                    field.visible = False
                    model[node].name = field.model.as_string

                label_field.model.add_end_edit_fn(partial(label_edited, label_field))

    def draw_header_label_left(
        self,
        model: OmniGraphModel,
        node: Union[og.Node, Usd.Prim],
        node_name: str,
        node_category: str,
        bg_style_override: str,
        label_style_override: str,
    ):
        pass

    def draw_header_label_right(
        self,
        model: OmniGraphModel,
        node: Union[og.Node, Usd.Prim],
        node_name: str,
        node_category: str,
        bg_style_override: str,
        label_style_override: str,
    ):
        pass

    # This is a heavily-modified replacement of modern delegate's _draw_icon.
    def _draw_icon(self, icon_size, node_type_name, border_style: str):
        with ui.HStack(height=icon_size):
            ui.Spacer()
            icon_scale = icon_size / float(ICON["width"])
            with ui.ZStack(width=icon_size):
                # icon border
                outer_icon_radius = ICON["radius"] * icon_scale
                self._build_rectangle(outer_icon_radius, True, border_style, node_type_name)
                # icon image
                icon_border = ICON["border"] * icon_scale
                with ui.HStack():
                    ui.Spacer(width=icon_border)
                    with ui.VStack():
                        ui.Spacer(height=icon_border)
                        with ui.ZStack():
                            self._build_rectangle(
                                outer_icon_radius - icon_border, True, "Graph.Node.Icon.Background", node_type_name
                            )
                            image_width = (ICON["width"] - ICON["border"]) * icon_scale
                            image_height = (ICON["height"] - ICON["border"]) * icon_scale
                            image = ui.ImageWithProvider(
                                style_type_name_override="Graph.Node.Icon",
                                name=node_type_name,
                                width=image_width,
                                height=image_height,
                                fill_policy=ui.IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT,
                            )
                            # Rasterize with big resolution
                            if hasattr(image, "prepare_draw"):
                                image.prepare_draw(1024, 1024)

                            if self.__help_hover_widget and self.__help_hover_widget():
                                hover_widget = self.__help_hover_widget()
                                # OM-87030:
                                # Invisible images under a CanvasWidget do not get scaled properly when the canvas is
                                # zoomed. We can work around this by putting the image in a Placer.
                                with ui.Placer():
                                    help_icon = ui.ImageWithProvider(
                                        style_type_name_override="Graph.Node.Icon",
                                        name=graph_config.CategoryStyles.HELP_TYPE,
                                        width=image_width,
                                        height=image_height,
                                        fill_policy=ui.IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT,
                                    )
                                    # Rasterize with big resolution
                                    if hasattr(help_icon, "prepare_draw"):
                                        help_icon.prepare_draw(1024, 1024)
                                    help_icon.visible = False

                                    def on_mouse_pressed(x, y, button, old_pos):
                                        if button == 0:
                                            old_pos[0] = x
                                            old_pos[1] = y

                                    def on_mouse_released(x, y, button, old_pos, node_type_name):
                                        if button == 0 and old_pos[0] >= 0:  # noqa: SIM102
                                            # If the mouse has moved then a drag is in progress and we don't want to
                                            # pop up help.
                                            if x == old_pos[0] and y == old_pos[1]:  # noqa: SIM102
                                                show_help_for_node_type(node_type_name)

                                    click_pos = [-1, -1]

                                    help_icon.set_mouse_pressed_fn(
                                        lambda x, y, b, m: on_mouse_pressed(x, y, b, click_pos)
                                    )

                                    help_icon.set_mouse_released_fn(
                                        lambda x, y, b, m: on_mouse_released(x, y, b, click_pos, node_type_name)
                                    )

                                    def __set_help_icon_visibility(visible: bool):
                                        help_icon.visible = visible

                                    # Having the help icons switch on and off as the mouse moves across the graph
                                    # can be distracting, so we delay their appearance by half a second, the same as
                                    # with tooltips.
                                    hover_action = _DelayedAction(
                                        0.5,
                                        lambda: __set_help_icon_visibility(True),
                                        lambda: __set_help_icon_visibility(False),
                                    )

                                    def __on_hover(hovering):
                                        if hovering:
                                            hover_action.start()
                                        else:
                                            hover_action.stop()

                                hover_widget.set_mouse_hovered_fn(__on_hover)
                        ui.Spacer(height=icon_border)
                    ui.Spacer(width=icon_border)
            ui.Spacer()

    def __draw_header_icon(self, node_category: str, bg_style_override: str, category_style_override: str):
        """Draws the header icon"""
        with ui.ZStack(height=ICON["height"], width=ICON["width"]):
            with ui.VStack(visible_min=TEXT_VISIBLE_MIN):
                self._draw_icon(ICON["width"], node_category, category_style_override)
            # new header (the part that covers the icon space) when zoomed out
            with ui.VStack(visible_max=TEXT_VISIBLE_MIN, visible_min=PORT_VISIBLE_MIN):
                ui.Rectangle(
                    height=HEADER["sec_height"], name=node_category, style_type_name_override=bg_style_override
                )
                ui.Rectangle(
                    height=HEADER["height"], name=node_category, style_type_name_override=category_style_override
                )

    def __draw_header_label(
        self,
        model: OmniGraphModel,
        node: Union[og.Node, Usd.Prim],
        node_name: str,
        node_category: str,
        bg_style_override: str,
        label_style_override: str,
    ):
        """Draws the label on the header"""
        # the header text with background
        with ui.ZStack(height=HEADER["sec_height"]):
            if self.show_header_background:
                ui.Rectangle(
                    visible_min=PORT_VISIBLE_MIN, name=node_category, style_type_name_override=bg_style_override
                )
            spacing = HEADER["margin_to_left"]
            with ui.HStack(spacing=spacing, style={"margin_width": spacing}):
                self.draw_header_label_left(
                    model, node, node_name, node_category, bg_style_override, label_style_override
                )
                self.draw_header_label_center(
                    model, node, node_name, node_category, bg_style_override, label_style_override
                )
                self.draw_header_label_right(
                    model, node, node_name, node_category, bg_style_override, label_style_override
                )

    def __draw_expansion_button(
        self, model, node: Union[og.Node, Usd.Prim], node_category: str, off_style: str, on_style: str
    ):
        """Draws the expansion button"""

        def switch_expansion(model, node):
            current = model[node].expansion_state
            model[node].expansion_state = GraphModel.ExpansionState((current.value + 1) % 3)

        # 0 == full, 1 == minimized, 2 == closed
        value = model[node].expansion_state.value % 3
        button1 = on_style
        button2 = on_style if value <= 1 else off_style
        button3 = on_style if value == 0 else off_style

        # the expansion button
        ui.Spacer(height=STATE_TOGGER["margin"])
        with ui.HStack():
            ui.Spacer()
            collapse = ui.HStack(width=14, visible_min=PORT_VISIBLE_MIN)
            with collapse:
                ui.Circle(
                    radius=STATE_TOGGER["radius"],
                    size_policy=ui.CircleSizePolicy.FIXED,
                    name=node_category,
                    style_type_name_override=button1,
                )
                ui.Circle(
                    radius=STATE_TOGGER["radius"],
                    size_policy=ui.CircleSizePolicy.FIXED,
                    name=node_category,
                    style_type_name_override=button2,
                )
                ui.Circle(
                    radius=STATE_TOGGER["radius"],
                    size_policy=ui.CircleSizePolicy.FIXED,
                    name=node_category,
                    style_type_name_override=button3,
                )
            collapse.set_mouse_pressed_fn(lambda x, y, b, m, model=model, node=node: switch_expansion(model, node))
            ui.Spacer(width=STATE_TOGGER["margin"])
        ui.Spacer(height=STATE_TOGGER["margin"])

    # This is a clone of the modern delegate's _build_header, modified to change the header colors according
    # to the node's error state, and make the icon drawing optional
    def build_header(
        self, node_name: str, model: OmniGraphModel, node_desc: GraphNodeDescription, error_state: og.Severity
    ):
        header = ui.VStack()
        node = node_desc.node
        node_type_name = str(model[node].type)

        if og.get_kit_version()[0] >= 105 and is_help_available_for_node_type(node_type_name):
            # We want to set a hover function on the header but the function needs access to the help icon widget,
            # which hasn't been created yet. So we save a reference to the zstack for use by _draw_icon().
            self.__help_hover_widget = weakref.ref(header)

        with header:
            if error_state == og.Severity.ERROR:
                bg_style_override = "Graph.Node.Error.Background"
                category_style_override = "Graph.Node.Error.Highlight"
                label_style_override = "Graph.Node.Label"
            elif error_state == og.Severity.WARNING:
                bg_style_override = "Graph.Node.Warning.Background"
                category_style_override = "Graph.Node.Warning.Highlight"
                label_style_override = "Graph.Node.Warning.Label"
            else:
                bg_style_override = "Graph.Node.Secondary"
                category_style_override = "Graph.Node.Category"
                label_style_override = "Graph.Node.Label"

            # set the expansion button styles
            expansion_on = bg_style_override
            expansion_off = category_style_override
            if error_state == og.Severity.INFO:
                expansion_on = "Graph.Node.Expansion.On"
                expansion_off = "Graph.Node.Expansion.Off"

            ui.Spacer(height=NODE_WIDTH_MARGIN)
            with ui.ZStack():
                GraphNodeDelegateFull.build_tooltip([node_name, node_type_name])
                if model[node].expansion_state.value == 2:
                    with ui.VStack(visible_max=PORT_VISIBLE_MIN):
                        self._draw_icon(ICON["width"], node_type_name, category_style_override)

                with ui.HStack():
                    if self.show_header_icon:
                        # icon
                        self.__draw_header_icon(node_type_name, bg_style_override, category_style_override)

                    # label
                    with ui.VStack():
                        self.__draw_header_label(
                            model, node, node_name, node_type_name, bg_style_override, label_style_override
                        )
                        ui.Rectangle(
                            visible_min=PORT_VISIBLE_MIN,
                            height=HEADER["height"],
                            name=node_type_name,
                            style_type_name_override=category_style_override,
                        )
                        self.__draw_expansion_button(model, node, node_type_name, expansion_off, expansion_on)

                # Label to display when we're zoomed out so far that the full header wil no longer work.
                ui.Label(
                    node_name,
                    height=HEADER["sec_height"],
                    visible_max=TEXT_VISIBLE_MIN,
                    visible_min=PORT_VISIBLE_MIN,
                    style_type_name_override="Graph.Node.Label.ZoomIn",
                    style={"margin_width": HEADER["margin_to_left_zoom_in"]},
                    alignment=self.header_label_alignment,
                )
            ui.Spacer(height=NODE_WIDTH_MARGIN)
        self.__help_hover_widget = None
        return header

    def get_error_state(
        self, model: OmniGraphModel, node_desc: GraphNodeDescription
    ) -> Tuple[og.Severity, str, Optional[str], Optional[str]]:
        """
        Retrieves the error state of the omni graph node
        Returns a tuple of (error state, node name, error message, error icon)
        """
        error_state = og.Severity.INFO
        og_node = self.__get_node_from_prim_safe(model, node_desc.node)
        message = None
        error_icon = None
        if og_node:
            node_name = model[og_node].name
            error_icon = None
            msgs = og_node.get_compute_messages(og.Severity.ERROR)
            if msgs:
                error_state = og.Severity.ERROR
                error_icon = f"{graph_config.Paths.ICON_PATH}/error_dark.svg"
                message = msgs[0]
                if not message.lower().startswith("error"):
                    message = "Error: " + message
            else:
                msgs = og_node.get_compute_messages(og.Severity.WARNING)
                if msgs:
                    error_state = og.Severity.WARNING
                    error_icon = f"{graph_config.Paths.ICON_PATH}/warning_dark.svg"
                    message = msgs[0]
                    if not message.lower().startswith("warning"):
                        message = "Warning: " + message
        else:
            node_name = model[node_desc.node].name

        return (error_state, node_name, message, error_icon)

    def node_header(self, model: OmniGraphModel, node_desc: GraphNodeDescription):
        (error_state, error_name, message, error_icon) = self.get_error_state(model, node_desc)
        with ui.ZStack():
            self.build_header(model[node_desc.node].name, model, node_desc, error_state)

            # override the existing tooltip
            node_type_name = model[node_desc.node].node_type_name
            namespace, _, type_name = node_type_name.rpartition(".") if node_type_name else ["", "", "Virtual Node"]
            tips = [error_name, f"{type_name} ({namespace})"]
            if message:
                tips = [message] + tips
            GraphNodeDelegateFull.build_tooltip(tips)
            # Apply an error/warning icon if needed.
            if error_state != og.Severity.INFO:
                with ui.HStack():
                    ui.Spacer()
                    with ui.VStack(alignment=ui.Alignment.RIGHT_CENTER, width=HEADER["sec_height"]):
                        ui.Spacer(height=NODE_WIDTH_MARGIN + ICON["border"])
                        with ui.HStack(width=HEADER["sec_height"] - ICON["border"]):
                            with ui.ZStack(
                                height=HEADER["sec_height"] - 2 * ICON["border"], alignment=ui.Alignment.RIGHT_CENTER
                            ):
                                ui.Rectangle(style_type_name_override="Graph.Node.Icon.Background")
                                ui.Image(
                                    error_icon,
                                    height=HEADER["sec_height"] - 3 * ICON["border"],
                                    fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT,
                                )

    def node_background(self, model: OmniGraphModel, node_desc: GraphNodeDescription):
        def on_mouse_click(button, mod, node_model, node_desc):
            # make sure it's not triggered by other mouse behaviors (e.g., Alt zoom)
            if button == 1 and mod == 0:
                self._on_node_right_clicked(node_model, node_desc)

        def on_mouse_double_click(node, *args):
            def do_it(node):
                # Check and see if any of the node/port rename widgets are visible. If so, don't enter compound, let the
                # rename take precedence
                for widget in self.__edit_widgets.values():
                    if widget.visible:
                        return
                self._graph_widget.enter_compound(node)

            # The double click events for both the string field and the node background are getting triggered (even if
            # send_mouse_events_to_back is false). So just delay the enter compound action a bit to see if the string
            # field widgets have been made visible.
            action = _DelayedAction(0.1, lambda: do_it(node))
            action.start()

        widget = ui.ZStack()
        with widget:
            super().node_background(model, node_desc)

            # override the existing tooltip
            GraphNodeDelegateFull.build_tooltip(
                [model[node_desc.node].name, model[node_desc.node].node_type_name], None, TEXT_VISIBLE_MIN
            )

            widget.set_mouse_pressed_fn(
                lambda x, y, b, modifier, model=model, node_desc=node_desc: on_mouse_click(
                    b, modifier, model, node_desc
                )
            )
            widget.set_mouse_double_clicked_fn(partial(on_mouse_double_click, node_desc.node))

    def _on_node_right_clicked(self, model: OmniGraphModel, node_desc: GraphNodeDescription):  # noqa: C901
        self._graph_widget.show_context_menu(node_desc.node)

    def _on_rename_port(self, port):
        """Trigger display of the edit field for renaming a port"""
        if port in self.__port_stack and self.__port_stack[port]:
            for zs in ui.Inspector.get_children(self.__port_stack[port]):
                if isinstance(zs, ui.ZStack):
                    # trigger the double click behavior that enables the string edit field
                    zs.call_mouse_double_clicked_fn(0, 0, 0, 0)
                    break

    @staticmethod
    def specialized_expansion_style(name: str, color_on: int, color_off: int) -> Dict:
        """
        Return part of the style that customizes the expansion node button colors

        Args:
            name: Node type
            color_on: 'Color of the expansion on' state
            color_off: 'Color of the expansion off' state
        """
        style = {
            # Node
            f"Graph.Node.Expansion.On::{name}": {"background_color": color_on},
            f"Graph.Node.Expansion.Off::{name}": {"background_color": color_off},
        }
        return style

    @staticmethod
    def __get_node_from_prim_safe(model: OmniGraphModel, prim: Usd.Prim) -> og.Node:
        """
        Gets the og.Node from the given prim.
        If the prim is not a valid node, returns None instead of throwing an exception.

        Args:
            model: The graph model
            prim: The node prim

        Returns:
            og.Node: If the prim is a node, returns the og.Node corresponding to the prim, otherwise returns None.
        """
        og_node: og.Node = None
        with suppress(og.OmniGraphValueError):
            og_node = model.get_node_from_prim(prim)
        return og_node

    # ------------------------------------------------------------------
    # Deprecated methods.
    @ogt.deprecated_function("This method is deprecated and will be removed in a future release")
    def _on_create_compound_active(self) -> bool:

        if not self._graph_widget.model:
            return False
        if not self._graph_widget.model.selected_nodes:
            return False

        return self._can_create_compound(self._graph_widget.model.selected_nodes)

    @ogt.deprecated_function("This method is deprecated and will be removed in a future release")
    def _can_create_compound(self, items: List[Usd.Prim]) -> bool:
        """Determines if the on_create_compound_should be active"""

        if not all(isinstance(i, Usd.Prim) for i in items):
            return False

        return CompoundUtils.can_create_compound_from(items)

    @ogt.deprecated_function("This method is deprecated and will be removed in a future release")
    def _can_edit_selected_compound(self, items: List[Usd.Prim]) -> bool:
        """Determines if on_edit_compound should be active"""
        if len(items) != 1:
            return False
        return CompoundUtils.is_compound_node(items[0])

    @ogt.deprecated_function("This method is deprecated and will be removed in a future release")
    def _on_create_compound_dialog_ok(self, dialog: MultiFieldDialog):
        """Callback when the create compound dialog has the ok button click"""
        dialog.hide()
        self._graph_widget.model.create_compound(
            dialog.get_values(0), dialog.get_values(1), self.__selected_compound_candidates
        )
        self.__selected_compound_candidates = None

    @ogt.deprecated_function("This method is deprecated and will be removed in a future release")
    def _on_create_compound_node_type_clicked(self, items: Optional[List[Usd.Prim]]):
        """
        Callback when the create compound from selection is checked.
        If the list of items is not supplied, the current selection is used
        """
        if items is None:
            items = self._graph_widget.model.selected_nodes
        self.__selected_compound_candidates = items

        dialog = MultiFieldDialog(title="Create Compound", ok_handler=self._on_create_compound_dialog_ok)
        dialog.show()

    @ogt.deprecated_function("This method is deprecated and will be removed in a future release")
    def _on_create_subgraph_compound_clicked(self, items: Optional[List[Usd.Prim]]):
        """
        Callback when the create subgraph compound from selection is checked
        If the list of items is not supplied, the current selection is used
        """
        if items is None:
            items = self._graph_widget.model.selected_nodes
        self._graph_widget.model.create_subgraph_compound(items)

    @ogt.deprecated_function("This method is deprecated and will be removed in a future release")
    def _can_create_compound_subgraph_from_selection(self, items: List[Usd.Prim]) -> bool:
        """
        Validation method to determine if the ability to create a compound subgraph
        is available
        """
        return (
            self._can_create_compound(items)
            and importlib.util.find_spec("omni.graph.core._unstable")
            and hasattr(og._unstable, "cmds")  # noqa: protected-access
            and hasattr(og._unstable.cmds, "ReplaceWithCompoundSubgraph")  # noqa: protected-access
        )

    @ogt.deprecated_function("This method is deprecated and will be removed in a future release")
    def _on_edit_compound_clicked(self, items: Optional[List[Usd.Prim]]) -> bool:
        """
        Callback when edit selected compound is clicked.
        If the list of items is not supplied, the first item in the current selection is used
        """
        if items is None:
            items = self._graph_widget.model.selected_nodes
        self._graph_widget.enter_compound(items[0])
