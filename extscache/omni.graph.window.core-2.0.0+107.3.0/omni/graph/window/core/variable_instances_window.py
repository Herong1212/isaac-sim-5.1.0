# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["VariableInstancesWindow"]


import omni.ui as ui
import omni.usd

from .singleton import singleton
from .variables_model import READ_VARIABLE_NODES, WRITE_VARIABLE_NODES

TITLEBAR_HEIGHT = 22
BUTTON_IMAGE_SIZE = 18
VARIABLE_INSTANCE_WIN_TITLE = "Variable Instances"
INSTANCE_WINDOW_STYLE = {
    "Label::title": {"font_size": 14},
    "Rectangle::title_rect": {
        "background_color": 0xFF25282A,
        "border_color": 0x0,
        "border_width": 0.5,
        "border_radius": 0,
    },
    "Button:hovered": {
        "background_color": 0x0,
    },
    "Button:pressed": {
        "background_color": 0x0,
    },
}


class OmniGraphVariableInstancesItemDelegate(ui.AbstractItemDelegate):
    def __init__(self, variable_name: str, click_fn: callable):
        super().__init__()
        self._variable_name = variable_name
        self._on_instance_click_fn = click_fn

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per item"""
        ui.Label(
            item.name,
            height=18,
            alignment=ui.Alignment.LEFT_CENTER,
            mouse_released_fn=lambda x, y, b, m: self._on_instance_clicked(item.node),
        )

    def _on_instance_clicked(self, node):
        prim_path = node.get_prim_path()
        omni.usd.get_context().get_selection().set_selected_prim_paths([prim_path], True)
        if self._on_instance_click_fn:
            self._on_instance_click_fn(node)


class OmniGraphVariableInstancesItem(ui.AbstractItem):
    """Single item of the VariableInstances"""

    def __init__(self, node):
        super().__init__()
        self.node = node
        self.name = self._get_node_relative_path(node) + self._get_node_kind(node)

    def _get_name_from_path(self, prim_path: str):
        name = ""
        if prim_path:
            parts = prim_path.rsplit("/", 1)
            name = parts[1] if len(parts) > 1 else prim_path
        return name

    def _get_node_kind(self, node):
        if node.get_type_name() in READ_VARIABLE_NODES:
            return " [READ]"
        if node.get_type_name() in WRITE_VARIABLE_NODES:
            return " [WRITE]"
        return ""

    def _get_node_relative_path(self, node) -> str:
        parent_graph = node.get_graph()
        while parent_graph.is_compound_graph():
            parent_graph = parent_graph.get_parent_graph()
        full_path = node.get_prim_path()
        if full_path and parent_graph:
            graph_path = parent_graph.get_path_to_graph()
            if graph_path and full_path.startswith(graph_path):
                full_path = full_path[len(graph_path) :]
        return full_path


class OmniGraphVariableInstancesModel(ui.AbstractItemModel):
    # List model handling the graph VariableInstances popup
    def __init__(
        self,
        nodes: list,
    ):
        super().__init__()
        self._filter = ""
        self._column_count = 1
        self._items = []
        for node in nodes:
            self._items.append(OmniGraphVariableInstancesItem(node))

    def get_item_children(self, item: OmniGraphVariableInstancesItem) -> list:
        """Returns all the children when the widget asks it."""
        if item is not None:
            # Since we are doing a flat list, we return the children of root only.
            # If it's not root we return.
            return []

        return self._items

    def get_item_value_model_count(self, item) -> int:
        """The number of columns"""
        return self._column_count

    def get_item_value_model(self, item: OmniGraphVariableInstancesItem, column_id: int):
        """Return the model given an item"""
        return item.name


@singleton
class VariableInstancesWindow(ui.Window):
    def __init__(self):
        flags = ui.WINDOW_FLAGS_NO_COLLAPSE | ui.WINDOW_FLAGS_NO_TITLE_BAR | ui.WINDOW_FLAGS_NO_SCROLLBAR
        super().__init__(VARIABLE_INSTANCE_WIN_TITLE, height=100, width=200, flags=flags)
        self._variable_instances = None
        self._origin_x = 0
        self._origin_y = 0
        self._close_btn = None
        self._model = None
        self._delegate = None
        self.position_x = 0
        self.position_y = 0
        self.visible = False
        self.set_focused_changed_fn(self._focus_callback)
        self.set_position_x_changed_fn(self._move_x_callback)
        self.set_position_y_changed_fn(self._move_y_callback)
        self.frame.set_style(INSTANCE_WINDOW_STYLE)
        self.frame.set_build_fn(self._build_ui)

    def destroy(self):
        self._variable_instances = None
        self._model = None
        self._delegate = None
        self._close_btn = None
        super().destroy()

    def setup(self, variable_name: str, nodes: list, click_fn: callable, x_pos: float, y_pos: float):
        self._variable_instances = nodes
        self._origin_x = x_pos
        self._origin_y = y_pos
        self.position_x = x_pos
        self.position_y = y_pos

        self._model = OmniGraphVariableInstancesModel(nodes)
        self._delegate = OmniGraphVariableInstancesItemDelegate(variable_name, click_fn)

        self.visible = True
        self.focus()
        self.frame.rebuild()

    def _build_ui(self):
        with self.frame:
            with ui.VStack(spacing=0):
                self._build_title_bar()
                self._build_content()

    # custom title bar
    def _build_title_bar(self):
        with ui.ZStack(height=TITLEBAR_HEIGHT):
            ui.Rectangle(height=TITLEBAR_HEIGHT, name="title_rect")
            with ui.HStack(height=TITLEBAR_HEIGHT):
                ui.Spacer()
                with ui.VStack(width=0):
                    ui.Spacer(width=0, height=3)
                    ui.Label(VARIABLE_INSTANCE_WIN_TITLE, name="title", alignment=ui.Alignment.CENTER)
                    ui.Spacer(width=0)
                ui.Spacer()
                with ui.ZStack(width=0):
                    ui.Rectangle(width=20, name="title_rect")
                    self._close_btn = ui.Button(
                        "",
                        image_url="resources/icons/Close.png",
                        image_width=BUTTON_IMAGE_SIZE,
                        visible=False,
                        clicked_fn=self._on_close,
                    )

    def _build_content(self):
        if not self._variable_instances:
            ui.Label("No instance", height=20)
            return

        with ui.ScrollingFrame(
            horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
            style_type_name_override="TreeView",
        ):
            ui.TreeView(
                self._model,
                delegate=self._delegate,
                root_visible=False,
                header_visible=False,
            )

    def _focus_callback(self, focus_state: bool):
        if self._close_btn and not self._close_btn.visible and not focus_state:
            self.visible = False

    def _move_x_callback(self, pos: float):
        if self._close_btn and not self._close_btn.visible and abs(self._origin_x - pos) > 1.0:
            self._close_btn.visible = True

    def _move_y_callback(self, pos: float):
        if self._close_btn and not self._close_btn.visible and abs(self._origin_y - pos) > 1.0:
            self._close_btn.visible = True

    def _on_close(self):
        self.visible = False
