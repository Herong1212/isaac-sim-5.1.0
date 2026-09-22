import carb
import omni.ui as ui
import omni.kit.commands
from .config import Settings
from omni.kit.graph.delegate.modern.delegate import GraphNodeDelegate, GraphNodeDelegateFull
from omni.kit.graph.delegate.modern.delegate import CONNECTION, NODE_BACKGROUND
from omni.kit.widget.graph.abstract_graph_node_delegate import (
    GraphNodeDescription,
    GraphConnectionDescription,
    GraphPortDescription
)
from pxr import Sdf, Tf, Usd
import AnimGraphSchema

from .node_graph import NodeGraph, NodeGraphStateMachine, NodeGraphRoot
from .node import Port, Node, VariableNode
from .animation_graph_node_delegate_state import AnimationGraphNodeDelegateState
from .animation_graph_node_delegate_variable import AnimationGraphNodeDelegateVariableRouter
from .animation_graph_model import AnimationGraphModel
from typing import Any, Callable, Tuple, Dict, Union
from functools import partial

ERROR_COLOR_CATEGORY = ui.color("#AF4E4E")
ERROR_COLOR_SECONDARY = ui.color("#CB6A6A")

PORT_VISIBLE_MIN = 0.35
HIGHLIGHT_THICKNESS = 8.0
CONNECTION_PORT_WIDTH = 11.0
TEXT_VISIBLE_MIN = 0.65
NODE_WIDTH_MARGIN = max(HIGHLIGHT_THICKNESS, CONNECTION_PORT_WIDTH)
PORT_HEIGHT = 20

HEADER = {
    "margin_to_left": 8,
    "margin_to_left_zoom_in": 14,
    "sec_height": 23,
    "height": 3,
    "margin_to_ports": NODE_WIDTH_MARGIN,
}

STATE_TOGGER = {
    "radius": 2,
    "margin": 4,
    "spacing": 1,
}

ICON = {
    "height": 38,
    "width": 38,
    "border": 1.5,
    "radius": 9,
}


def get_node_secondary_color(category_color: tuple):
    if category_color:
        # 50% lightness from the border color
        # 30% saturation from the border color
        L_MULT = 0.5
        S_MULT = 0.3
        import colorsys
        hls = colorsys.rgb_to_hls(category_color[0], category_color[1], category_color[2])
        rgb = colorsys.hls_to_rgb(hls[0], min(1.0, (hls[1] * L_MULT)), hls[2] * S_MULT)
        if len(category_color) > 3:  # alpha
            rgb = rgb + (category_color[3],)
        return rgb


def lerp_component(color: int, fixed_color: int) -> int:
    """Lerp a value to the fixed color"""
    return int(color + 0.5 * (fixed_color - color))


def lerp_abgr_to_secondary(abgr: int, secondary: int = 0x23211F) -> int:
    """Calculate secondary from primary color, leaving the alpha as is
    This is defined as a desaturation of the primary color. One way to do this is to simply
    lerp the color towards grey. In our case half-way to #1F2123.
    """
    r = abgr & 0xFF
    g = (abgr >> 8) & 0xFF
    b = (abgr >> 16) & 0xFF
    a = (abgr >> 24) & 0xFF

    lr = (secondary) & 0xFF
    lg = (secondary >> 8) & 0xFF
    lb = (secondary >> 16) & 0xFF

    return (a << 24) | (lerp_component(b, lb) << 16) | (lerp_component(g, lg) << 8) | lerp_component(r, lr)


class AnimationGraphNodeDelegate(GraphNodeDelegate):
    def __init__(self, open_sub_graph_fn: Callable[[Node], None]):
        super().__init__()
        self._open_sub_graph_fn = open_sub_graph_fn
        self._select_node_fn = None
        self._node_context_menu = None
        self._connection_context_menu = None
        self._port_context_menu = None
        self._keyboard = omni.appwindow.get_default_app_window().get_keyboard()
        self._input = carb.input.acquire_input_interface()
        self.show_header_icon = True
        self.show_header_background = True
        self.header_label_alignment = ui.Alignment.LEFT_CENTER

        self.add_route(
            AnimationGraphNodeDelegateState(self._setup_node_widget, self._open_sub_graph_fn),
            expression=self.is_state
        )

        self.add_route(
            AnimationGraphNodeDelegateVariableRouter(),
            expression=self.is_variable
        )

    def is_state(self, model, node):
        graph = node.node_graph
        return graph and isinstance(graph, NodeGraphStateMachine) and node != graph.root_node

    def is_variable(self, model, node):
        return isinstance(node, VariableNode)

    def set_select_node_fn(self, select_node_fn: Callable[[Any, Any, int, bool], None]):
        self._select_node_fn = select_node_fn

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
                        name=name
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
                    name=name
                )

    # This is a clone of modern delegate's _draw_icon, modified to take a specific style for the icon's border.
    def _draw_icon(self, icon_size, node_category, border_style: Dict[str, Any]):
        with ui.HStack(height=icon_size):
            ui.Spacer()
            icon_scale = icon_size / float(ICON["width"])
            with ui.ZStack(width=icon_size):
                # icon border
                outter_icon_radius = ICON["radius"] * icon_scale
                self._build_rectangle(outter_icon_radius, True, border_style, node_category)
                # icon image
                icon_border = ICON["border"] * icon_scale
                with ui.HStack():
                    ui.Spacer(width=icon_border)
                    with ui.VStack():
                        ui.Spacer(height=icon_border)
                        with ui.ZStack():
                            self._build_rectangle(outter_icon_radius - icon_border, True, "Graph.Node.Icon.Background", node_category)
                            image_width = (ICON["width"] - ICON["border"]) * icon_scale
                            image_height = (ICON["height"] - ICON["border"]) * icon_scale
                            image = ui.ImageWithProvider(
                                style_type_name_override="Graph.Node.Icon",
                                name=node_category,
                                width=image_width,
                                height=image_height,
                                fill_policy=ui.IwpFillPolicy.IWP_PRESERVE_ASPECT_FIT)
                            # Rasterize with big resolution
                            if hasattr(image, "prepare_draw"):
                                image.prepare_draw(1024, 1024)
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
                ui.Rectangle(height=HEADER["sec_height"], name=node_category, style_type_name_override=bg_style_override)
                ui.Rectangle(height=HEADER["height"], name=node_category, style_type_name_override=category_style_override)

    def __draw_header_label(self, model: AnimationGraphModel, node: Union[Node, Usd.Prim], node_name: str, node_category: str, bg_style_override: str, label_style_override: str):
        """Draws the label on the header"""
        # the header text with background
        with ui.ZStack(height=HEADER["sec_height"]):
            if self.show_header_background:
                ui.Rectangle(visible_min=PORT_VISIBLE_MIN, name=node_category, style_type_name_override=bg_style_override)
            label = ui.Label(node_name, visible_min=TEXT_VISIBLE_MIN, style_type_name_override=label_style_override, style={"margin_width": HEADER["margin_to_left"]}, alignment=self.header_label_alignment)

            # If we're displaying the name, as opposed to the type, then allow it to be edited on dbl-click.
            if not Settings.get_show_name_as_type():
                label_field = ui.StringField()
                label_field.visible = False

                def show_edit_field(field, *args):
                    field.model.set_value(node_name)
                    field.visible = True

                label.set_mouse_double_clicked_fn(partial(show_edit_field, label_field))

                def label_edited(field, *args):
                    field.visible = False
                    model[node].name = field.model.as_string

                label_field.model.add_end_edit_fn(partial(label_edited, label_field))

    def __draw_expansion_button(self, model, node: Union[Node, Usd.Prim], node_category: str, off_style: str, on_style: str):
        """Draws the expansion button"""
        def switch_expansion(model, node):
            current = model[node].expansion_state
            model[node].expansion_state = AnimationGraphModel.ExpansionState((current.value + 1) % 3)

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
                ui.Circle(radius=STATE_TOGGER["radius"], size_policy=ui.CircleSizePolicy.FIXED, name=node_category, style_type_name_override=button1)
                ui.Circle(radius=STATE_TOGGER["radius"], size_policy=ui.CircleSizePolicy.FIXED, name=node_category, style_type_name_override=button2)
                ui.Circle(radius=STATE_TOGGER["radius"], size_policy=ui.CircleSizePolicy.FIXED, name=node_category, style_type_name_override=button3)
            collapse.set_mouse_pressed_fn(lambda x, y, b, m, model=model, node=node: switch_expansion(model, node))
            ui.Spacer(width=STATE_TOGGER["margin"])
        ui.Spacer(height=STATE_TOGGER["margin"])

    # This is a clone of the modern delegate's _build_header, modified to change the header colors according
    # to the node's error state, and make the icon drawoing optional
    def build_header(self, node_name: str, model: AnimationGraphModel, node_desc: GraphNodeDescription, has_errors):
        header = ui.VStack()
        with header:
            node = node_desc.node
            node_category = str(model[node].type)

            if has_errors:
                bg_style_override = "Graph.Node.Error.Background"
                category_style_override = "Graph.Node.Error.Highlight"
                label_style_override = "Graph.Node.Label"
            else:
                bg_style_override = "Graph.Node.Secondary"
                category_style_override = "Graph.Node.Category"
                label_style_override = "Graph.Node.Label"

            # set the expansion button styles
            expansion_on = bg_style_override
            expansion_off = category_style_override

            ui.Spacer(height=NODE_WIDTH_MARGIN)
            with ui.ZStack():
                GraphNodeDelegateFull.build_tooltip([node_name, node_category])
                if model[node].expansion_state.value == 2:
                    with ui.VStack(visible_max=PORT_VISIBLE_MIN):
                        self._draw_icon(ICON["width"], node_category, category_style_override)

                with ui.HStack():
                    if self.show_header_icon:
                        self.__draw_header_icon(node_category, bg_style_override, category_style_override)
                    # label
                    with ui.VStack():
                        self.__draw_header_label(model, node, node_name, node_category, bg_style_override, label_style_override)
                        ui.Rectangle(visible_min=PORT_VISIBLE_MIN, height=HEADER["height"], name=node_category, style_type_name_override=category_style_override)
                        self.__draw_expansion_button(model, node, node_category, expansion_off, expansion_on)

                # Label to display when we're zoomed out so far that the full header wil no longer work.
                ui.Label(node_name, height=HEADER["sec_height"], visible_max=TEXT_VISIBLE_MIN, visible_min=PORT_VISIBLE_MIN, style_type_name_override="Graph.Node.Label.ZoomIn", style={"margin_width": HEADER["margin_to_left_zoom_in"]}, alignment=self.header_label_alignment)
            ui.Spacer(height=NODE_WIDTH_MARGIN)
        return header

    def node_header(self, model, node_desc: GraphNodeDescription):
        stack = ui.ZStack()
        node = node_desc.node
        path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        node_type = str(model[node].type)
        errors = model[node].errors
        has_errors = errors and len(errors) > 0
        has_custom_header = self.is_variable(model, node) or self.is_state(model, node)
        if not has_custom_header and has_errors:
            style = AnimationGraphNodeDelegate.get_style()
            style[f"Graph.Node.Category::{node_type}"] = {"background_color": ERROR_COLOR_CATEGORY}
            style[f"Graph.Node.Secondary::{node_type}"] = {"background_color": ERROR_COLOR_SECONDARY}
            stack.set_style(style)

        with stack:
            if not has_custom_header:
                self.build_header(model[node_desc.node].name, model, node_desc, has_errors)
            super().node_header(model, node_desc)
            AnimationGraphNodeDelegate.build_tooltip(model, node_desc)
            if not has_custom_header and has_errors:
                with ui.HStack():
                    ui.Spacer()
                    with ui.VStack(alignment=ui.Alignment.RIGHT_CENTER, width=HEADER["sec_height"]):
                        ui.Spacer(height=NODE_WIDTH_MARGIN + ICON["border"])
                        with ui.HStack(width=HEADER["sec_height"] - ICON["border"]):
                            with ui.ZStack(height=HEADER["sec_height"] - 2 * ICON["border"], alignment=ui.Alignment.RIGHT_CENTER):
                                ui.Rectangle(style_type_name_override="Graph.Node.Icon.Background")
                                ui.Image(f"{path}/icons/error_dark.svg", height=HEADER["sec_height"] - 3 * ICON["border"], fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT)

    def node_background(self, model, node_desc: GraphNodeDescription):
        with ui.ZStack():
            widget = self._setup_node_widget(super().node_background(model, node_desc), model, node_desc.node)
            AnimationGraphNodeDelegate.build_tooltip(model, node_desc)
            return widget

    def port_output(self, model, node_desc: GraphNodeDescription, port_desc: GraphPortDescription):
        def on_mouse_pressed(button, modifier):
            if button == 1:
                left_alt_pressed = carb.input.BUTTON_FLAG_DOWN == self._input.get_keyboard_button_flags(self._keyboard, carb.input.KeyboardInput.LEFT_ALT)
                right_alt_pressed = carb.input.BUTTON_FLAG_DOWN == self._input.get_keyboard_button_flags(self._keyboard, carb.input.KeyboardInput.RIGHT_ALT)
                if left_alt_pressed or right_alt_pressed:
                    return

                self._port_context_menu = ui.Menu("Port Context Menu", visible=False)
                with self._port_context_menu:
                    port = port_desc.port
                    if len(port.connected_ports) > 0:
                        self._port_context_menu.visible = True

                        def disconnect():
                            node_graph = port.node_graph
                            with omni.kit.undo.group():
                                for connected_port in port.connected_ports.copy():
                                    node_graph.delete_connection(port, connected_port)

                        ui.MenuItem("Disconnect", triggered_fn=disconnect)

                self._port_context_menu.show()

        widget = super().port_output(model, node_desc, port_desc)
        if widget and not isinstance(node_desc.node.node_graph, NodeGraphStateMachine):
            widget.set_mouse_pressed_fn(lambda x, y, b, m: on_mouse_pressed(b, m))
        return widget

    def connection(self, model, source: GraphConnectionDescription, target: GraphConnectionDescription) -> Tuple[ui.ZStack, ui.FreeLine, ui.FreeBezierCurve]:
        transition_node = None
        if isinstance(target.port, Port):
            transition_node = target.port.transition_nodes.get(source.port, None)

        def on_mouse_pressed(button, modifier):
            if button == 0:
                if not transition_node or not self._select_node_fn:
                    return

                self._select_node_fn(model, transition_node, modifier, True)
            elif button == 1:
                left_alt_pressed = carb.input.BUTTON_FLAG_DOWN == self._input.get_keyboard_button_flags(self._keyboard, carb.input.KeyboardInput.LEFT_ALT)
                right_alt_pressed = carb.input.BUTTON_FLAG_DOWN == self._input.get_keyboard_button_flags(self._keyboard, carb.input.KeyboardInput.RIGHT_ALT)
                if left_alt_pressed or right_alt_pressed:
                    return

                self._connection_context_menu = ui.Menu("Connection Context Menu")
                with self._connection_context_menu:
                    if transition_node:
                        ui.MenuItem(
                            "Open Sub-Graph",
                            triggered_fn=lambda: self._open_sub_graph_fn(transition_node)
                        )
                    ui.MenuItem(
                        "Delete Connection",
                        triggered_fn=lambda: model.current_graph.delete_connection(source.port, target.port)
                    )

                self._connection_context_menu.show()

        def on_mouse_double_clicked(button):
            if button == 0 and transition_node:
                self._open_sub_graph_fn(transition_node)

        curve_container_widget, freeline_widget, curve_widget = super().connection(model, source, target)
        if freeline_widget:
            freeline_widget.set_mouse_pressed_fn(lambda x, y, b, m: on_mouse_pressed(b, m))
            freeline_widget.set_mouse_double_clicked_fn(lambda x, y, b, m: on_mouse_double_clicked(b))
        curve_widget.set_mouse_pressed_fn(lambda x, y, b, m: on_mouse_pressed(b, m))
        curve_widget.set_mouse_double_clicked_fn(lambda x, y, b, m: on_mouse_double_clicked(b))
        return curve_container_widget, freeline_widget, curve_widget

    def destroy(self):
        super().destroy()
        self._open_sub_graph_fn = None
        self._select_node_fn = None
        self._node_context_menu = None
        self._connection_context_menu = None
        self._port_context_menu = None

    def _setup_node_widget(self, widget, model: AnimationGraphModel, node: Node):
        if not widget:
            return

        def on_mouse_pressed(button):
            if button == 1:
                left_alt_pressed = carb.input.BUTTON_FLAG_DOWN == self._input.get_keyboard_button_flags(self._keyboard, carb.input.KeyboardInput.LEFT_ALT)
                right_alt_pressed = carb.input.BUTTON_FLAG_DOWN == self._input.get_keyboard_button_flags(self._keyboard, carb.input.KeyboardInput.RIGHT_ALT)
                if left_alt_pressed or right_alt_pressed:
                    return

                self._node_context_menu = ui.Menu("Node Context Menu")
                with self._node_context_menu:
                    if node.has_sub_graph():
                        ui.MenuItem(
                            "Open Sub-Graph",
                            triggered_fn=lambda: self._open_sub_graph_fn(node)
                        )

                    node_graph = node.node_graph
                    if isinstance(node_graph, NodeGraphStateMachine):
                        start_state = node_graph.get_start_state()
                        if not start_state or start_state != node:
                            ui.MenuItem("Set Start State", triggered_fn=lambda: node_graph.set_start_state(node))

                    is_root_node = node == node_graph.root_node
                    state_machine_root = isinstance(node_graph, NodeGraphStateMachine) and is_root_node
                    if not isinstance(node, VariableNode) and not state_machine_root:
                        ui.MenuItem(
                            "Rename Node" if not isinstance(node_graph, NodeGraphRoot) or not is_root_node else
                            "Rename Graph",
                            triggered_fn=lambda: AnimationGraphNodeDelegate._rename_node_dialog(node)
                        )

                    ui.MenuItem(
                        "Delete Node" if not is_root_node else
                        "Delete Sub-Graph" if not isinstance(node_graph, NodeGraphRoot) else
                        "Delete Graph",
                        triggered_fn=lambda: model.current_graph.delete_node(node)
                    )

                self._node_context_menu.show()

        def on_mouse_double_clicked(button):
            if button == 0 and node.has_sub_graph():
                self._open_sub_graph_fn(node)

        stage = node.prim.GetStage()

        def drop_accept(url):
            prim = stage.GetPrimAtPath(Sdf.Path(url))
            if not prim:
                return False

            return prim.GetTypeName() == "SkelAnimation" and node.prim.IsA(AnimGraphSchema.AnimationClip)

        def drop_fn(e: ui.WidgetMouseDropEvent):
            prim = stage.GetPrimAtPath(e.mime_data)
            if not prim:
                return False

            NodeGraph.set_skel_animation(node.prim, prim)

        widget.set_mouse_pressed_fn(lambda x, y, b, m: on_mouse_pressed(b))
        widget.set_mouse_double_clicked_fn(lambda x, y, b, m: on_mouse_double_clicked(b))
        widget.set_accept_drop_fn(drop_accept)
        widget.set_drop_fn(drop_fn)
        return widget

    @staticmethod
    def _rename_node_dialog(node: Node):
        old_name = node.name
        window = ui.Window(
            "Rename " + old_name,
            width=200,
            height=100,
            flags=ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_MODAL
        )

        def close_window():
            window.visible = False

        def rename_node():
            close_window()
            node.name = new_name_widget.model.get_value_as_string()

        def on_key_pressed(key_index, key_mod, key_down):
            if key_index == int(carb.input.KeyboardInput.ENTER) and key_down:
                rename_node()

        window.set_key_pressed_fn(on_key_pressed)

        with window.frame:
            with ui.VStack(
                height=0,
                spacing=5,
                name="top_level_stack",
                style={"VStack::top_level_stack": {"margin": 5}, "Button": {"margin": 0}},
            ):
                new_name_widget = ui.StringField()
                new_name_widget.model.set_value(old_name)
                new_name_widget.focus_keyboard()
                ui.Spacer(width=5, height=5)
                with ui.HStack(spacing=5):
                    ui.Button("Ok", clicked_fn=rename_node)
                    ui.Button("Cancel", clicked_fn=close_window)

    @staticmethod
    def build_tooltip(model, node_desc: GraphNodeDescription):
        tooltips = []
        errors = model[node_desc.node].errors
        if errors and len(errors) > 0:
            tooltips.append("Errors:")
            tooltips.extend(errors)
            tooltips.append("")
        tooltips.extend([model[node_desc.node].name, model[node_desc.node].description])
        GraphNodeDelegateFull.build_tooltip(tooltips)

    @staticmethod
    def get_style(
        border=None,
        background=None,
        node_background=None,
        icon_background=None,
        border_selected=None,
        node_background_selected=None,
    ):
        graph_background = 0xFF23211F
        style = GraphNodeDelegate.get_style(background=graph_background)
        default_category_color = (0.5, 0.5, 0.5)
        default_secondary_color = get_node_secondary_color(default_category_color)
        path = omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
        style.update(
            {
                "Graph.Node.Category": {"background_color": ui.color(*default_category_color)},
                "Graph.Node.Secondary": {"background_color": ui.color(*default_secondary_color)},
                "Graph.Node.State.Port.Background": {
                    "background_color": NODE_BACKGROUND
                },
                "Graph.Node.State.Port.Background.Hovered": {
                    "background_color": CONNECTION
                },
                "Graph.Node.State.Default": {
                    "background_color": 0xff76b900
                },
                "Graph.Node.Icon": {
                    "image_url": f"{path}/icons/node/type_function_dark.svg"
                }
            }
        )

        type_colors = {
            str(Port.Type.Unknown): 0xFFD79633,
            str(Port.Type.Bool): 0xFF1C1CE2,
            str(Port.Type.BoolArray): 0xFF1C1CE2,
            str(Port.Type.Int): 0xFF5F5FE5,
            str(Port.Type.IntArray): 0xFF5F5FE5,
            str(Port.Type.Float): 0xFF88CF2A,
            str(Port.Type.FloatArray): 0xFF88CF2A,
            str(Port.Type.Token): 0xFF9C3ACC,
            str(Port.Type.TokenArray): 0xFF9C3ACC,
            str(Port.Type.String): 0xFF781FA5,
            str(Port.Type.StringArray): 0xFF781FA5,
            str(Port.Type.Float3): 0xFF88CF2A,
            str(Port.Type.Float3Array): 0xFF88CF2A,
            str(Port.Type.Float4): 0xFF88CF2A,
            str(Port.Type.Float4Array): 0xFF88CF2A,
            str(Port.Type.Object): 0xFFD79633
        }

        def add_port_type_style(name, color):
            style.update(GraphNodeDelegate.specialized_port_style(name, color))
            style.update({f"Graph.Node.Background::{name}": {"background_color": lerp_abgr_to_secondary(color)}})
            style.update(GraphNodeDelegate.specialized_color_style(
                name,
                lerp_abgr_to_secondary(color, 0xA8A8A8),
                "",
                lerp_abgr_to_secondary(color, 0x121110)
            ))

        for type_name, type_color in type_colors.items():
            add_port_type_style(type_name, type_color)

        node_styles = {
            "AnimationGraph": {
                "color": (0.337, 0.651, 0.859),
                "icon": f"{path}/icons/node/type_animation_graph_dark.svg"
            },
            "AnimationClip": {
                "color": (0.337, 0.651, 0.859),
                "icon": f"{path}/icons/node/type_animation_clip_dark.svg"
            },
            "ReadVariable": {
                "color": (0.341, 0.455, 0.486),
                "icon": f"{path}/icons/node/type_variable_dark.svg"
            },
            "StateMachine": {
                "color": (0.463, 0.608, 0.706),
                "icon": f"{path}/icons/node/type_statemachine_dark.svg"
            },
            "State": {
                "color": (0.463, 0.608, 0.706),
                "icon": f"{path}/icons/node/type_state_dark.svg"
            },
            "Transition": {
                "color": (0.635, 0.588, 0.51),
                "icon": f"{path}/icons/node/type_transition_dark.svg"
            },
            "ConditionCompareVariable": {
                "color": (0.29, 0.541, 0.325),
                "icon": f"{path}/icons/node/type_condition_dark.svg"
            },
            "ConditionTimeFractionCrossed": {
                "color": (0.29, 0.541, 0.325),
                "icon": f"{path}/icons/node/type_condition_dark.svg"
            },
            "ConditionSpeed": {
                "color": (0.29, 0.541, 0.325),
                "icon": f"{path}/icons/node/type_condition_dark.svg"
            },
            "ConditionAND": {
                "color": (0.29, 0.541, 0.325),
                "icon": f"{path}/icons/node/type_condition_dark.svg"
            },
            "ConditionOR": {
                "color": (0.29, 0.541, 0.325),
                "icon": f"{path}/icons/node/type_condition_dark.svg"
            },
            "Blend": {
                "color": (0.502, 0.631, 0.561),
                "icon": f"{path}/icons/node/type_blend_dark.svg"
            },
            "LookAtIK": {
                "color": (0.502, 0.631, 0.561),
                "icon": f"{path}/icons/node/type_look_at_ik_dark.svg"
            },
            "TwoBoneIK": {
                "color": (0.502, 0.631, 0.561),
                "icon": f"{path}/icons/node/type_two_bone_ik_dark.svg"
            },
            "MotionMatching": {
                "color": (0.502, 0.631, 0.561),
                "icon": f"{path}/icons/node/type_motion_matching_dark.svg"
            },
            "Filter": {
                "color": (0.502, 0.631, 0.561),
                "icon": f"{path}/icons/node/type_filter_dark.svg"
            },
            "PoseProvider": {
                "color": (0.502, 0.631, 0.561),
                "icon": f"{path}/icons/node/type_pose_provider_dark.svg"
            },
            "FullBodyIK": {
                "color": (0.502, 0.631, 0.561),
                "icon": f"{path}/icons/node/type_full_body_ik_dark.svg"
            },
            "SetEffector": {
                "color": (0.502, 0.631, 0.561),
                "icon": f"{path}/icons/node/type_set_effector_dark.svg"
            }
        }

        def add_node_style(node_type: str, color: tuple, icon: str = ""):
            secondary_color = get_node_secondary_color(color)
            if icon == "":
                icon = style.get("Graph.Node.Icon", {}).get("image_url", "")

            style.update(GraphNodeDelegate.specialized_color_style(
                node_type,
                ui.color(*color),
                icon,
                ui.color(*secondary_color)
            ))

        for type_name, style_data in node_styles.items():
            add_node_style(type_name, style_data.get("color"), style_data.get("icon"))

        return style
