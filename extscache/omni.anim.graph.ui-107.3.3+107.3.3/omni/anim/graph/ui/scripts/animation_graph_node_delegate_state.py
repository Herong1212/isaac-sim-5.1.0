import carb
import omni.ui as ui
import omni.kit.commands
from omni.kit.graph.delegate.modern.delegate import GraphNodeDelegate
from omni.kit.graph.delegate.modern.delegate_full import (
    GraphNodeDelegateFull,
    HIGHLIGHT_THICKNESS,
    TEXT_VISIBLE_MIN,
    PORT_VISIBLE_MIN,
    HEADER
)
from omni.kit.widget.graph.abstract_graph_node_delegate import (
    AbstractGraphNodeDelegate,
    GraphNodeLayout,
    GraphNodeDescription,
    GraphPortDescription,
    GraphConnectionDescription
)
from .node_graph import NodeGraphStateMachine
from .node import Node, Port
from .animation_graph_model import AnimationGraphModel
from typing import Any, Callable, Optional, Tuple
from .config import Paths
BACKGROUND_RADIUS = 9.0
HIGHLIGHT_THICKNESS_ZOOM_OUT_MORE = 4.0
HIGHLIGHT_THICKNESS_ZOOM_OUT = 6.0

ERROR_COLOR_CATEGORY = ui.color("#AF4E4E")
ERROR_COLOR_SECONDARY = ui.color("#CB6A6A")
ERROR_COLOR_CONNECTION = ui.color("#CB6A6A")
BUTTON_COLOR_CONNECTION = ui.color("#FFFFFF")


class AnimationGraphNodeDelegateState(AbstractGraphNodeDelegate):
    def __init__(
        self,
        setup_node_frame_fn: Callable[[Any, AnimationGraphModel, Node], Any],
        open_sub_graph_fn: Callable[[Node], None]
    ):
        super().__init__()
        self._setup_node_frame_fn = setup_node_frame_fn
        self._open_sub_graph_fn = open_sub_graph_fn

    def destroy(self):
        super().destroy()
        self._setup_node_frame_fn = None
        self._open_sub_graph_fn = None

    def get_node_layout(self, model, node_desc: GraphNodeDescription):
        return GraphNodeLayout.HEAP

    def port_output(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        node = node_desc.node
        node_type = str(model[node].type)
        # the node body
        background = ui.ZStack()
        with background:
            # this trick makes min width
            ui.Spacer(width=90)
            # highlight
            with ui.VStack(visible_max=PORT_VISIBLE_MIN):
                self._build_rectangle(
                    BACKGROUND_RADIUS + HIGHLIGHT_THICKNESS,
                    True,
                    "Graph.Node.Border",
                    node_type,
                    False
                )
            # zoomed out highlight
            # this is shown during the zoom in between PORT_VISIBLE_MIN to TEXT_VISIBLE_MIN
            margin = HIGHLIGHT_THICKNESS - HIGHLIGHT_THICKNESS_ZOOM_OUT
            with ui.HStack(visible_max=TEXT_VISIBLE_MIN, visible_min=PORT_VISIBLE_MIN):
                ui.Spacer(width=margin)
                with ui.VStack():
                    ui.Spacer(height=margin)
                    with ui.ZStack():
                        self._build_rectangle(
                            BACKGROUND_RADIUS + HIGHLIGHT_THICKNESS_ZOOM_OUT,
                            False,
                            "Graph.Node.Border",
                            node_type,
                            False
                        )
                    ui.Spacer(height=margin)
                ui.Spacer(width=margin)
            # zoomed out more highlight
            # this is shown when the zoom is > TEXT_VISIBLE_MIN
            margin = HIGHLIGHT_THICKNESS - HIGHLIGHT_THICKNESS_ZOOM_OUT_MORE
            with ui.HStack(visible_min=TEXT_VISIBLE_MIN):
                ui.Spacer(width=margin)
                with ui.VStack():
                    ui.Spacer(height=margin)
                    self._build_rectangle(
                        BACKGROUND_RADIUS + HIGHLIGHT_THICKNESS_ZOOM_OUT_MORE,
                        True,
                        "Graph.Node.Border",
                        node_type,
                        False
                    )
                    ui.Spacer(height=margin)
                ui.Spacer(width=margin)
            # node
            with ui.HStack():
                ui.Spacer(width=HIGHLIGHT_THICKNESS)
                with ui.VStack():
                    ui.Spacer(height=HIGHLIGHT_THICKNESS)
                    with ui.ZStack():
                        hover_widget = ui.Spacer()
                        rectangle_widgets = self._build_rectangle(BACKGROUND_RADIUS, True, "Graph.Node.State.Port.Background", node_type, False)

                        def on_hover(hovered: bool):
                            if hovered:
                                for widget in rectangle_widgets:
                                    widget.style_type_name_override = "Graph.Node.State.Port.Background.Hovered"
                            else:
                                for widget in rectangle_widgets:
                                    widget.style_type_name_override = "Graph.Node.State.Port.Background"

                        hover_widget.set_mouse_hovered_fn(on_hover)
                    ui.Spacer(height=HIGHLIGHT_THICKNESS)
                ui.Spacer(width=HIGHLIGHT_THICKNESS)
        return background

    def port(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        BORDER_SIZE = 15
        node_frame = ui.Frame(skip_draw_when_clipped=True)
        node = node_desc.node
        if port_desc.port.kind == Port.Kind.Input:
            node_frame = self._setup_node_frame_fn(node_frame, model, node)
        with node_frame:
            with ui.HStack():
                ui.Spacer(width=BORDER_SIZE)
                with ui.VStack():
                    ui.Spacer(height=BORDER_SIZE)
                    frame = ui.Frame(separate_window=True)
                    with frame:
                        with ui.ZStack():
                            ui.Spacer(height=45)
                            # highlight
                            with ui.ZStack(visible_max=PORT_VISIBLE_MIN):
                                self._build_inner_port(model, node, HIGHLIGHT_THICKNESS)
                            # zoomed out highlight
                            # this is shown during the zoom in between PORT_VISIBLE_MIN to TEXT_VISIBLE_MIN
                            with ui.ZStack(visible_max=TEXT_VISIBLE_MIN, visible_min=PORT_VISIBLE_MIN):
                                self._build_inner_port(model, node, HIGHLIGHT_THICKNESS_ZOOM_OUT)
                            # zoomed out more highlight
                            # this is shown when the zoom is > TEXT_VISIBLE_MIN
                            with ui.ZStack(visible_min=TEXT_VISIBLE_MIN):
                                self._build_inner_port(model, node, HIGHLIGHT_THICKNESS_ZOOM_OUT_MORE)
                    ui.Spacer(height=BORDER_SIZE)
                ui.Spacer(width=BORDER_SIZE)
        return frame

    def connection(self, model, source: GraphConnectionDescription, target: GraphConnectionDescription) -> Tuple[ui.ZStack, ui.FreeLine, ui.FreeBezierCurve]:
        # path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        transition_node = None
        if target.port and target.port.transition_nodes:
            transition_node = target.port.transition_nodes.get(source.port, None)

        # def on_mouse_pressed(button, modifier):
        #     if button == 0:
        #         if not transition_node or not self._select_node_fn:
        #             return

        #         self._select_node_fn(model, transition_node, modifier, True)
        #     elif button == 1:
        #         left_alt_pressed = carb.input.BUTTON_FLAG_DOWN == self._input.get_keyboard_button_flags(self._keyboard, carb.input.KeyboardInput.LEFT_ALT)
        #         right_alt_pressed = carb.input.BUTTON_FLAG_DOWN == self._input.get_keyboard_button_flags(self._keyboard, carb.input.KeyboardInput.RIGHT_ALT)
        #         if left_alt_pressed or right_alt_pressed:
        #             return

        #         self._connection_context_menu = ui.Menu("Connection Context Menu")
        #         with self._connection_context_menu:
        #             if transition_node:
        #                 ui.MenuItem(
        #                     "Open Sub-Graph",
        #                     triggered_fn=lambda: self._open_sub_graph_fn(transition_node)
        #                 )
        #             ui.MenuItem(
        #                 "Delete Connection",
        #                 triggered_fn=lambda: model.current_graph.delete_connection(source.port, target.port)
        #             )

        #         self._connection_context_menu.show()

        # def on_mouse_double_clicked(button):
        #     if button == 0 and transition_node:
        #         self._open_sub_graph_fn(transition_node)

        # #image = None
        with ui.ZStack():
            offset_line = ui.OffsetLine(
                target.widget,
                source.widget,
                alignment=ui.Alignment.UNDEFINED,
                begin_arrow_type=ui.ArrowType.ARROW,
                offset=7,
                bound_offset=5.5,
                style_type_name_override="Graph.Connection"
            )

            if transition_node:
                errors = model[transition_node].errors
                if errors and len(errors) > 0:
                    offset_line.set_style({"color": ERROR_COLOR_CONNECTION})
                    # image = ui.Image(
                    #     f"{path}/icons/error_dark.svg",
                    #     width=10,
                    #     height=10)
                # else:
                #     image = ui.Image(
                #         f"{path}/icons/transition_dark.svg",
                #         width=16,
                #         height=16)
        # if image:
        #     image.set_mouse_pressed_fn(lambda x, y, b, m: on_mouse_pressed(b, m))
        #     image.set_mouse_double_clicked_fn(lambda x, y, b, m: on_mouse_double_clicked(b))

        return None, None, offset_line

    @staticmethod
    def _build_rectangle(radius, draw_top, style_type_name, name, has_errors):
        """
        Build rectangle of the specific design.

        Args:
            radius: The radius of round corers. The corners are top-left and
                    bottom-right.
            draw_top: When false the top corners are straight.
            style_type_name: style_type_name_override of each widget
            name: name of each widget
            style_override: the style to apply to the top level node
        """
        stack = ui.VStack(alignment=ui.Alignment.CENTER)

        if has_errors:
            style = GraphNodeDelegate.get_style()
            style["Graph.Node.Error.Category"] = {"background_color": ERROR_COLOR_CATEGORY}
            style["Graph.Node.Error.Secondary"] = {"background_color": ERROR_COLOR_SECONDARY}
            stack.set_style(style)

        widgets = list()
        with stack:
            # top of the rectangle
            if draw_top:
                with ui.HStack(height=0):
                    widgets.append(ui.Circle(
                        radius=radius,
                        width=0,
                        height=0,
                        size_policy=ui.CircleSizePolicy.FIXED,
                        alignment=ui.Alignment.RIGHT_BOTTOM,
                        style_type_name_override=style_type_name,
                        name=name
                    ))
                    widgets.append(ui.Rectangle(style_type_name_override=style_type_name, name=name))
            else:
                widgets.append(ui.Rectangle(style_type_name_override=style_type_name, name=name))

            # middle of the rectangle
            widgets.append(ui.Rectangle(style_type_name_override=style_type_name, name=name))

            # bottom of the rectangle
            with ui.HStack(height=0):
                widgets.append(ui.Rectangle(style_type_name_override=style_type_name, name=name))
                widgets.append(ui.Circle(
                    radius=radius,
                    width=0,
                    height=0,
                    size_policy=ui.CircleSizePolicy.FIXED,
                    alignment=ui.Alignment.LEFT_TOP,
                    style_type_name_override=style_type_name,
                    name=name
                ))

        return widgets

    def _build_inner_port(self, model, node, highlight_thickness):
        node_name = model[node].name
        node_type = str(model[node].type)
        errors = model[node].errors
        has_errors = errors and len(errors) > 0

        if has_errors:
            category_style_type = "Graph.Node.Error.Category"
            background_style_type = "Graph.Node.Error.Background"
        else:
            category_style_type = "Graph.Node.Category"
            background_style_type = "Graph.Node.Background"

        self._build_rectangle(
            BACKGROUND_RADIUS + highlight_thickness,
            True,
            category_style_type,
            node_type,
            has_errors
        )
        with ui.HStack():
            ui.Spacer(width=highlight_thickness)
            with ui.VStack():
                ui.Spacer(height=highlight_thickness)
                with ui.ZStack():
                    self._build_rectangle(
                        BACKGROUND_RADIUS,
                        True,
                        background_style_type,
                        node_type,
                        has_errors
                    )
                    with ui.HStack():
                        ui.Label(
                            node_name,
                            visible_min=TEXT_VISIBLE_MIN,
                            style_type_name_override="Graph.Node.Label",
                            style={"margin_width": HEADER["margin_to_left"]},
                            alignment=ui.Alignment.CENTER
                        )
                        node_graph = node.node_graph
                        if isinstance(node_graph, NodeGraphStateMachine):
                            start_state = node_graph.get_start_state()
                            if start_state and start_state == node:
                                with ui.VStack():
                                    ui.Spacer()
                                    ui.Image(f"{Paths.ICON_PATH}/animation_graph_start_state.svg", width=15, height=15)
                                    ui.Spacer()
                            if has_errors:
                                with ui.VStack():
                                    ui.Spacer()
                                    ui.Image(f"{Paths.ICON_PATH}/error_dark.svg", width=15, height=15)
                                    ui.Spacer()
                ui.Spacer(height=highlight_thickness)
            ui.Spacer(width=highlight_thickness)
