import carb
import json
import omni.kit.app
import omni.kit.commands
import omni.anim.graph.ui.scripts.command
import omni.ui as ui
import omni.usd
from omni.kit.graph.editor.core import GraphEditorCoreWidget
from omni.kit.graph.widget.variables import GraphEditorVariablesWidget
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
from pxr import Usd, Sdf, Tf
import AnimGraphSchema
from .animation_graph_catalog_model import AnimationGraphCatalogModel
from .animation_graph_catalog_delegate import AnimationGraphCatalogTreeDelegate
from .animation_graph_manager import AnimationGraphManager
from .animation_graph_view import AnimationGraphView
from .animation_graph_model import AnimationGraphModel
from .animation_graph_node_delegate import AnimationGraphNodeDelegate
from .animation_graph_selector import AnimationGraphSelector
from .animation_graph_variables_model import AnimationGraphVariablesModel, VariableItem
from .create_animation_graph_dialog import CreateAnimationGraphDialog
from .node_graph import (NodeGraph,
                         NodeGraphRoot,
                         NodeGraphStateMachine)
from .config import Paths, Settings
from .config import (
    get_blend_tree_node_types,
    get_state_machine_node_types,
    get_condition_graph_node_types
)
from omni.kit.widget.graph import GraphModel, GraphView
from .stage_picker_dialog import StagePickerDialog
from typing import Tuple, Optional, List
from functools import partial
import traceback
import weakref
import webbrowser
import asyncio

DOCS_URL = "https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_animation-graph.html"


class AnimationGraphWidget(GraphEditorCoreWidget):
    def __init__(self, graph_manager: AnimationGraphManager, create_graph_dialog: CreateAnimationGraphDialog):
        self._graph_manager = graph_manager
        self._create_graph_dialog = create_graph_dialog
        self._context_menu = ui.Menu("Toolbar Context")
        self._graph_selector = None
        self._graph_selector_task = None

        def on_graph_destroyed(graph: NodeGraphRoot):
            if self._model and graph == self._model.root_graph:
                self.close_graph()

        self._graph_destroyed_callback_id = graph_manager.add_graph_destroy_callback(on_graph_destroyed)

        self._model = None
        self._delegate = AnimationGraphNodeDelegate(lambda n: self.set_current_compound(n))
        self._catalog_frame = None
        self._catalog_model = AnimationGraphCatalogModel()

        self._keyboard = omni.appwindow.get_default_app_window().get_keyboard()
        self._input = carb.input.acquire_input_interface()

        toolbar_items = [
            {"name": "CreateGraph", "icon": f"{Paths.ICON_PATH}/toolbar/create_graph_dark.svg", "on_clicked": self.on_toolbar_create_graph_clicked, "tooltip": "Create a new graph"},
            {"name": "EditGraph", "icon": f"{Paths.ICON_PATH}/toolbar/edit_graph_dark.svg", "on_clicked": self.on_toolbar_edit_graph_clicked, "tooltip": "Edit an existing graph"},
            {"name": "-"},
            {"name": "Expansion_Open", "icon": f"{Paths.ICON_PATH}/toolbar/omnigraph_state_0_toggle_dark.svg", "on_clicked": partial(self.on_toolbar_expansion_state_clicked, GraphModel.ExpansionState.OPEN), "tooltip": "Expand all nodes"},
            {"name": "Expansion_Minimized", "icon": f"{Paths.ICON_PATH}/toolbar/omnigraph_state_1_toggle_dark.svg", "on_clicked": partial(self.on_toolbar_expansion_state_clicked, GraphModel.ExpansionState.MINIMIZED), "tooltip": "Minimize all nodes"},
            {"name": "Expansion_Closed", "icon": f"{Paths.ICON_PATH}/toolbar/omnigraph_state_2_toggle_dark.svg", "on_clicked": partial(self.on_toolbar_expansion_state_clicked, GraphModel.ExpansionState.CLOSED), "tooltip": "Close all nodes"},
            {"name": "-"},
            {"name": "View", "label": "View", "on_clicked": self.on_toolbar_view_clicked},
            {"name": "-"},
            {"name": "Help", "icon": f"{Paths.ICON_PATH}/toolbar/help_dark.svg", "on_clicked": self.on_toolbar_help_clicked, "tooltip": "See Animation Graph Tutorials"},
        ]
        super().__init__(
            delegate=self._delegate,
            view_type=AnimationGraphView,
            style=self._get_default_style(),
            catalog_model=self._catalog_model,
            catalog_delegate=AnimationGraphCatalogTreeDelegate(),
            toolbar_items=toolbar_items)

        self._usd_context = omni.usd.get_context()
        self._selection = None
        self._in_selection = False
        if self._usd_context is not None:
            self._selection = self._usd_context.get_selection()
            self._events = self._usd_context.get_stage_event_stream()
            self._stage_event_sub = self._events.create_subscription_to_pop(
                self.__on_stage_event, name="Animation Graph Selection Update"
            )

        self._selection_changed_sub = None
        self._item_changed_sub = None
        self._last_selected_prim_paths = []

        self._context_menu_created = False
        self._blend_tree_context_menu = None
        self._state_machine_context_menu = None
        self._condition_context_menu = None

        self._context_menu_position: Tuple[float, float] = (0, 0)

        self._new_stage_root_path: Optional[Sdf.Path] = None
        self._new_stage_current_path: Optional[Sdf.Path] = None

        self._stage_picker = None

        self._variables_widget = None
        self._variables_model = AnimationGraphVariablesModel(None)

        self._variable_default_value_models = []
        self._variables_changed_callback_id = None

    def destroy(self):
        def destroy_widget(widget):
            if widget:
                widget.destroy()

        destroy_widget(self._context_menu)
        self._context_menu = None

        self._delegate.destroy()
        self._delegate = None
        self._catalog_model.destroy()
        self._catalog_model = None

        destroy_widget(self._catalog_frame)
        self._catalog_frame = None

        if self._model and self._variables_changed_callback_id:
            self._model.root_graph.remove_variables_changed_callback(self._variables_changed_callback_id)
        self._variables_changed_callback_id = None

        self._model = None
        self._usd_context = None
        self._selection = None
        self._in_selection = None
        self._events = None
        self._stage_event_sub = None
        self._selection_changed_sub = None
        self._item_changed_sub = None
        self._last_selected_prim_paths = None
        self._context_menu_created = None

        destroy_widget(self._blend_tree_context_menu)
        self._blend_tree_context_menu = None

        destroy_widget(self._state_machine_context_menu)
        self._state_machine_context_menu = None

        destroy_widget(self._condition_context_menu)
        self._condition_context_menu = None

        self._context_menu_position = None
        self._new_stage_root_path = None
        self._new_stage_current_path = None

        if self._stage_picker:
            self._stage_picker.clean()
        self._stage_picker = None

        destroy_widget(self._variables_widget)
        self._variables_widget = None

        self._variables_model.destroy()
        self._variables_model = None

        for model in self._variable_default_value_models:
            model.clean()
        self._variable_default_value_models = None

        self._create_graph_dialog = None

        self._graph_manager.remove_graph_destroy_callback(self._graph_destroyed_callback_id)
        self._graph_destroyed_callback_id = None
        self._graph_manager = None
        if self._graph_selector:
            self._graph_selector.destroy()
        self._graph_selector = None

        if self._graph_selector_task and not self._graph_selector_task.done():
            self._graph_selector_task.cancel()
            if self._graph_selector_task and not self._graph_selector_task.done():
                self._graph_selector_task.cancel()
        self._graph_selector_task = None
        super().destroy()

    @property
    def catalog_model(self):
        return self._catalog_model

    def on_toolbar_create_graph_clicked(self):
        self._create_graph_dialog.open(self.open_graph)

    def on_toolbar_edit_graph_clicked(self):
        self._show_graph_picker()

    def on_toolbar_expansion_state_clicked(self, state):
        if self._model:
            nodes = self._model.nodes or []
            if nodes:
                with omni.kit.undo.group():
                    for node in nodes:
                        self._model[node].expansion_state = state

    def on_toolbar_view_clicked(self):
        self._context_menu.clear()
        with self._context_menu:
            ui.MenuItem(
                "Layout Nodes",
                triggered_fn=self.on_layout_clicked,
                enabled=True if self._model else False
            )
            ui.Separator()
            ui.MenuItem(
                "Frame Selected" if self._model and self._model._selected_nodes else "Frame All",
                triggered_fn=self.on_frame_selected_clicked,
                enabled=True if self._model else False
            )  # todo: hotkey_text="F")
            ui.Separator()
            with ui.Menu("Node Header"):
                ui.MenuItem(
                    "Use Prim Name",
                    triggered_fn=partial(self.on_use_prim_name_clicked, False),
                    checkable=True,
                    checked=not Settings.get_show_name_as_type(),
                    enabled=True if self._model else False
                )
                ui.MenuItem(
                    "Use Node Type",
                    triggered_fn=partial(self.on_use_prim_name_clicked, True),
                    checkable=True,
                    checked=Settings.get_show_name_as_type(),
                    enabled=True if self._model else False
                )
        self._context_menu.show()

    def on_toolbar_help_clicked(self):
        webbrowser.open(DOCS_URL)

    def _on_breadcrumbs_open_graph(self, graph: str):
        stage = self._usd_context.get_stage()
        prim = stage.GetPrimAtPath(graph)

        async def open_graph_async():
            self.open_graph(prim)

        self._graph_selector_task = asyncio.ensure_future(open_graph_async())

    def _on_breadcrumbs_get_graphs(self) -> List[str]:
        stage = self._usd_context.get_stage()
        graphs = []
        for prim in stage.Traverse():
            if prim.IsA(AnimGraphSchema.AnimationGraph):
                graphs.append(prim.GetPath().pathString)
        return graphs

    def on_build_breadcrumbs(self):
        with ui.HStack(height=0):
            if self._graph_selector:
                self._graph_selector.destroy()
            self._graph_selector = AnimationGraphSelector(self._on_breadcrumbs_get_graphs, self._on_breadcrumbs_open_graph)
            super().on_build_breadcrumbs()

    def close_graph(self):
        if not self._model:
            return

        if self._variables_changed_callback_id:
            self._model.root_graph.remove_variables_changed_callback(self._variables_changed_callback_id)
            self._variables_changed_callback_id = None

        self.model = None
        self._model = None
        self._selection_changed_sub = None
        self._item_changed_sub = None
        self._last_selected_prim_paths = []
        self._navigation = []
        self._catalog_model.graph_type = AnimationGraphCatalogModel.GraphType.NONE
        self._variables_model.node_graph = None

    def open_graph(self, graph_prim: Usd.Prim, focus_graph_path: Sdf.Path = None):
        if self._model and self._model.root_graph.prim != graph_prim:
            self.close_graph()

        if not graph_prim or not graph_prim.IsA(AnimGraphSchema.AnimationGraph):
            return

        create_new_model = not self._model
        if create_new_model:
            node_graph = self._graph_manager.get_node_graph(graph_prim.GetPath())
            if not node_graph:
                # It is possible for this to be missing, usually if the graph is contained within a reference added this session.
                # However, tracking graphs added via reference results in having to visit many more prims on USD update.
                # Catch this case and generate the model now.
                self._graph_manager._create_node_graph(graph_prim)
                node_graph = self._graph_manager.get_node_graph(graph_prim.GetPath())
                if not node_graph:
                    raise Exception(f"Could not create graph model for {graph_prim.GetPath().pathString}!")

            self._model = AnimationGraphModel(node_graph, self._graph_manager)
            self._variables_model.node_graph = node_graph
            self._selection_changed_sub = self._model.subscribe_selection_changed(self.__on_model_selection_changed)

            def on_item_changed(item):
                if not self._model.current_graph.is_valid():
                    if not item or item.has_sub_graph():
                        self.set_current_compound(item)
                        return

                if not item or item in self._navigation:
                    first_invalid_navigation = 0
                    for i_nav in self._navigation:
                        if i_nav.type is None:
                            break
                        first_invalid_navigation += 1
                    self._navigation = self._navigation[:first_invalid_navigation]
                    self._GraphEditorCoreWidget__build_navigation()

            self._item_changed_sub = self._model.subscribe_item_changed(on_item_changed)

            def on_variable_changed(name):
                for model in self._variable_default_value_models:
                    model._set_dirty()

            self._variables_changed_callback_id = self._model.root_graph.add_variables_changed_callback(
                on_variable_changed
            )

            # Better handling of error messages. The error message from Kit is
            # totally uninformative
            try:
                if self._graph_view:
                    self._graph_view.model = self._model
            except Exception as e:
                carb.log_error("Exception when opening graph")
                carb.log_error(f"{e}")
                carb.log_error(f"{traceback.format_exc()}")

            self.model = self._model

        if focus_graph_path:
            success, graph, node = self._model.root_graph.search_node(focus_graph_path)
            if success:
                focus_graph_node = None
                if node.has_sub_graph():
                    focus_graph_parent = graph
                    focus_graph_node = node
                else:
                    focus_graph_parent = graph.parent_graph
                    if focus_graph_parent:
                        focus_graph_node = focus_graph_parent.get_node(graph.prim.GetPath())

                if focus_graph_node:
                    nav_graph = focus_graph_parent
                    nav_parent_graph = nav_graph.parent_graph
                    self._navigation = []
                    while nav_parent_graph:
                        parent_node = nav_parent_graph.get_node(nav_graph.prim.GetPath())
                        self._navigation.append(parent_node)
                        nav_graph = nav_parent_graph
                        nav_parent_graph = nav_graph.parent_graph

                    self._navigation.append(self._model.root_graph.root_node)
                    self._navigation.reverse()
                    self.set_current_compound(focus_graph_node, not create_new_model)
                    return

        if not create_new_model:
            self.set_current_compound(None)

    def focus_on_nodes(self):
        """Zoom and pan to fit all the nodes"""

        async def focus_on_nodes_async():
            # Adjust the loop count upwards to ensure that computed_width/computed_height are calculated prior to their utilization.
            # Original count is 2 in GraphEditorCoreWidget (omni.kit.graph.editor.core)
            for _ in range(3):
                await omni.kit.app.get_app().next_update_async()
            self._graph_view.focus_on_nodes()

        asyncio.ensure_future(focus_on_nodes_async())

    def focus_on_selection(self):
        if self._model:
            self._graph_view.focus_on_nodes(self._model.selection)

    def on_build_startup(self):
        with ui.ZStack():
            ICON_SIZE = 120
            ui.Rectangle(style_type_name_override="Graph", accept_drop_fn=self.on_accept_drop, drop_fn=self.on_drop)
            with ui.HStack(content_clipping=True):
                with ui.VStack():
                    ui.Spacer()
                    with ui.HStack():
                        ui.Spacer()
                        ui.Button(
                            "Edit Animation Graph",
                            image_url=f"{Paths.ICON_PATH}/canvas_edit.png",
                            style_type_name_override="Graph",
                            width=ICON_SIZE,
                            height=0,
                            image_width=ICON_SIZE,
                            image_height=ICON_SIZE,
                            spacing=5,
                            clicked_fn=self._show_graph_picker
                        )
                        ui.Button(
                            "New Animation Graph",
                            image_url=f"{Paths.ICON_PATH}/canvas_new.png",
                            style_type_name_override="Graph",
                            width=ICON_SIZE,
                            height=0,
                            image_width=ICON_SIZE,
                            image_height=ICON_SIZE,
                            spacing=5,
                            clicked_fn=lambda: self._create_graph_dialog.open(self.open_graph)
                        )
                        ui.Spacer()
                    ui.Spacer()

    def on_build_catalog(self):
        collection = ui.RadioCollection()

        with ui.VStack(spacing=4):
            text_color = ui.color.shade(0xFFA1A1A1, light=0xFFE0E0E0)
            selected_color = ui.color.shade(0xFFFFC734, light=0xFFC5911A)
            with ui.HStack(
                height=0,
                spacing=4,
                style={
                    "GraphPanelTabs.Button": {"background_color": 0x0, "color": text_color},
                    "GraphPanelTabs.Button.Label": {"color": text_color},
                    "GraphPanelTabs.Button.Label:checked": {"color": selected_color},
                    "GraphPanelTabs.Separator": {"color": text_color, "border_width": 2}
                }
            ):
                ui.Spacer()
                ui.RadioButton(
                    text="Nodes",
                    radio_collection=collection,
                    width=0,
                    style_type_name_override="GraphPanelTabs.Button"
                )
                with ui.VStack(width=1):
                    ui.Spacer()
                    ui.Line(
                        height=10, alignment=ui.Alignment.LEFT, style_type_name_override="GraphPanelTabs.Separator"
                    )
                    ui.Spacer()
                ui.RadioButton(
                    text="Variables",
                    radio_collection=collection,
                    width=0,
                    style_type_name_override="GraphPanelTabs.Button"
                )
                ui.Spacer()

            with ui.ZStack():
                self._catalog_frame = ui.Frame()
                with self._catalog_frame:
                    super().on_build_catalog()
                self._variables_widget = GraphEditorVariablesWidget(
                    self._variables_model,
                    on_add_variable=self._on_add_variable_clicked,
                    on_build_variable_value_widget=self._on_build_variable_value_widget,
                    supported_variable_types=[str(type) for type in NodeGraph.get_supported_variable_types()],
                    visible=False
                )

        def on_tab_changed(model: ui.AbstractValueModel, weak_self):
            weak_self = weak_self()
            if not weak_self:
                return

            catalog_selected = model.as_int == 0
            weak_self._catalog_frame.visible = catalog_selected
            weak_self._variables_widget.visible = not catalog_selected

        collection.model.add_value_changed_fn(partial(on_tab_changed, weak_self=weakref.ref(self)))

    def on_accept_drop(self, drop_data: str):
        stage = self._usd_context.get_stage()
        if not stage:
            return False

        json_data = None
        path = None
        try:
            json_data = json.loads(drop_data)
        except json.decoder.JSONDecodeError:
            if Sdf.Path.IsValidPathString(drop_data):
                path = Sdf.Path(drop_data)

        if json_data:
            try:
                return "node_type" in json_data or "variable_name" in json_data
            except KeyError:
                return False

        prim = stage.GetPrimAtPath(path)
        if not prim:
            return False

        prim_type = prim.GetTypeName()
        if prim_type == "AnimationGraph":
            return True

        if prim_type == "SkelAnimation":
            if not self._model:
                return False

            graph = self._model.current_graph
            return \
                graph is not None and \
                not isinstance(graph, NodeGraphStateMachine) and \
                not graph.prim.IsA(AnimGraphSchema.Transition)

        prefixes = prim.GetPath().GetPrefixes()
        for prefix in reversed(prefixes):
            prefix_prim = stage.GetPrimAtPath(prefix)
            if not prefix_prim:
                continue

            prefix_prim_type = prefix_prim.GetTypeName()
            if prefix_prim_type == "AnimationGraph":
                return True

        return False

    def on_drop(self, event: ui.WidgetMouseDropEvent):
        stage = self._usd_context.get_stage()
        if not stage:
            return

        screen_pos = self._graph_view.mouse_to_screen(event.x, event.y)

        drop_data = event.mime_data
        json_data = None
        path = None
        try:
            json_data = json.loads(drop_data) or {}
        except json.decoder.JSONDecodeError:
            if Sdf.Path.IsValidPathString(drop_data):
                path = Sdf.Path(drop_data)

        if json_data:
            if self._model:
                variable_name = json_data.get("variable_name")
                if variable_name:
                    root_graph = self._model.root_graph
                    if root_graph and root_graph.has_variable(variable_name):
                        current_graph = self._model.current_graph
                        if current_graph and not isinstance(current_graph, NodeGraphStateMachine) and not current_graph.prim.IsA(AnimGraphSchema.Transition):

                            self._context_menu_position = screen_pos
                            self.__create_node("ReadVariable", variable_name)
                    return

                node_type_name = json_data.get("node_type")
                if node_type_name:
                    catalog_groups = self._catalog_model.get_item_children(None)
                    for group in catalog_groups:
                        group_items = self._catalog_model.get_item_children(group)
                        for item in group_items:
                            if node_type_name == item.name_model.as_string:
                                self._context_menu_position = screen_pos
                                self.__create_node(node_type_name)
                                return
                    return
            return

        prim = stage.GetPrimAtPath(path)
        if not prim:
            return

        prim_type = prim.GetTypeName()
        if prim_type == "AnimationGraph":
            self.open_graph(prim)
            return

        if prim_type == "SkelAnimation":
            if not self._model:
                return

            graph = self._model.current_graph
            if graph is not None and \
                    not isinstance(graph, NodeGraphStateMachine) and \
                    not graph.prim.IsA(AnimGraphSchema.Transition):

                self._context_menu_position = screen_pos
                node = self.__create_node("AnimationClip", prim.GetName())
                if node:
                    NodeGraph.set_skel_animation(node.prim, prim)
            return

        prefixes = prim.GetPath().GetPrefixes()
        for prefix in reversed(prefixes):
            prefix_prim = stage.GetPrimAtPath(prefix)
            if not prefix_prim:
                continue

            prefix_prim_type = prefix_prim.GetTypeName()
            if prefix_prim_type == "AnimationGraph":
                self.open_graph(prefix_prim, prim.GetPath())
                return

    def on_build_graph(self):
        super().on_build_graph()
        self._delegate.set_select_node_fn(self._graph_view._on_node_selected)

    def on_right_mouse_button_pressed(self, items):
        left_alt_pressed = carb.input.BUTTON_FLAG_DOWN == self._input.get_keyboard_button_flags(self._keyboard, carb.input.KeyboardInput.LEFT_ALT)
        right_alt_pressed = carb.input.BUTTON_FLAG_DOWN == self._input.get_keyboard_button_flags(self._keyboard, carb.input.KeyboardInput.RIGHT_ALT)
        if left_alt_pressed or right_alt_pressed:
            return

        self._create_context_menus()
        self._context_menu_position = self._get_graph_view_hovered_position()
        graph_type = self._catalog_model.graph_type

        if graph_type == AnimationGraphCatalogModel.GraphType.STATE_MACHINE:
            self._state_machine_context_menu.show()
        elif graph_type == AnimationGraphCatalogModel.GraphType.CONDITION:
            self._condition_context_menu.show()
        elif graph_type == AnimationGraphCatalogModel.GraphType.BLEND_TREE:
            self._blend_tree_context_menu.show()

    def on_left_mouse_button_double_clicked(self, items):
        if items and len(items) > 0:
            return

        if len(self._selection.get_selected_prim_paths()) > 0:
            return

        current_graph = self._model.current_graph
        if current_graph:
            parent_graph = current_graph.parent_graph
            if parent_graph:
                graph_node = None
                grand_parent_graph = parent_graph.parent_graph
                if grand_parent_graph:
                    graph_node = grand_parent_graph.get_node(parent_graph.prim.GetPath())

                self.set_current_compound(graph_node)

    def set_current_compound(self, item, focus=True):
        """Changes the current view to show the subgraph of the compound"""
        if item is None:
            if self._model.root_graph:
                self._navigation = [self._model.root_graph.root_node]
            else:
                self._navigation = []

            self._model.current_graph = self._model.root_graph
        else:
            if item.has_sub_graph():
                self._model.current_graph = item.sub_graph
            elif self._model.root_graph and item == self._model.root_graph.root_node:
                self._model.current_graph = self._model.root_graph
            else:
                return

            if item in self._navigation:
                self._navigation = self._navigation[: self._navigation.index(item) + 1]
            else:
                self._navigation.append(item)

        self._GraphEditorCoreWidget__build_navigation()

        graph = self._model.current_graph
        if graph:
            if isinstance(graph, NodeGraphStateMachine):
                self._catalog_model.graph_type = AnimationGraphCatalogModel.GraphType.STATE_MACHINE
            elif graph.prim.IsA(AnimGraphSchema.Transition):
                self._catalog_model.graph_type = AnimationGraphCatalogModel.GraphType.CONDITION
            else:
                self._catalog_model.graph_type = AnimationGraphCatalogModel.GraphType.BLEND_TREE

            if self._usd_context.is_new_stage():
                self._new_stage_root_path = self._model.root_graph.prim.GetPath()
                self._new_stage_current_path = graph.prim.GetPath()
        else:
            self._catalog_model.graph_type = AnimationGraphCatalogModel.GraphType.NONE

        self.__on_kit_selection_changed(True)

        if focus:
            self.focus_on_nodes()

    def _show_graph_picker(self):
        if self._stage_picker:
            self._stage_picker.clean()

        def on_select_graph(weak_self, graph_prim):
            weak_self = weak_self()
            if not weak_self:
                return
            weak_self.open_graph(graph_prim)

        self._stage_picker = StagePickerDialog(
            self._usd_context.get_stage(),
            partial(on_select_graph, weakref.ref(self)),
            "Open Animation Graph",
            "Open",
            [AnimGraphSchema.AnimationGraph]
        )
        self._stage_picker.show()

    def _create_context_menus(self):
        if self._context_menu_created:
            return

        def create_menu_item(name):
            ui.MenuItem(name, triggered_fn=lambda: self.__create_node(name))

        def create_menu(node_type_dict_fn):
            ui.MenuItem("Create Node:")
            node_type_dict = node_type_dict_fn()
            for category, node_types in node_type_dict.items():
                category_menu = ui.Menu(category)
                with category_menu:
                    for type_name in node_types:
                        create_menu_item(type_name)

        self._blend_tree_context_menu = ui.Menu("Blend Tree Context Menu")
        with self._blend_tree_context_menu:
            create_menu(get_blend_tree_node_types)
        self._state_machine_context_menu = ui.Menu("State Machine Context Menu")
        with self._state_machine_context_menu:
            create_menu(get_state_machine_node_types)
        self._condition_context_menu = ui.Menu("Condition Context Menu")
        with self._condition_context_menu:
            create_menu(get_condition_graph_node_types)
        self._context_menu_created = True

    def _get_graph_view_hovered_position(self) -> Tuple[float, float]:
        """Return the position of mouse if self._graph_view is hovered"""
        if not self._graph_view or not self._graph_view.visible:
            return 0, 0
        app_window = omni.appwindow.get_default_app_window()
        mouse_x, mouse_y = carb.input.acquire_input_interface().get_mouse_coords_pixel(app_window.get_mouse())
        return self._graph_view.mouse_to_screen(mouse_x, mouse_y)

    def _on_add_variable_clicked(self):
        self._create_variable(NodeGraph.get_supported_variable_types()[0])

    def _on_build_variable_value_widget(self, item: ui.AbstractItem) -> bool:
        if not isinstance(item, VariableItem) or not self._model.root_graph:
            return False

        root_graph = self._model.root_graph
        variable_prop = root_graph.get_variable_property(item.value_models[0].as_string)
        if not variable_prop:
            return False

        for model in self._variable_default_value_models:
            model.clean()

        self._variable_default_value_models.clear()

        model = UsdPropertiesWidgetBuilder.build(
            self._usd_context.get_stage(),
            variable_prop.GetName(),
            variable_prop.GetAllMetadata(),
            type(variable_prop),
            [variable_prop.GetPrimPath()],
            {"visible": False}
        )

        if isinstance(model, list):
            self._variable_default_value_models.extend(model)
        else:
            self._variable_default_value_models.append(model)

        return True

    def _create_variable(self, variable_type):
        if not self._model or not self._model.root_graph:
            return

        root_graph = self._model.root_graph
        variable_name = Tf.MakeValidIdentifier(root_graph.get_next_variable_name("NewVariable"))
        root_graph.create_variable(variable_name, variable_type, None)

    def _get_default_style(self):
        style = {}

        # variable types
        for tp in ["bool", "bool[]"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFF1C1CE2))

        for tp in ["double", "double[]", "matrix", "matrix2d", "matrix2d[]", "matrix3d", "matrix3d[]", "matrix4d",
                   "matrix4d[]",
                   "quatd", "quatd[]", "double2", "double2[]", "double3", "double3[]", "double4", "double4[]",
                   "normal3d",
                   "normal3d[]", "vector3d", "vector3d[]", "vector4", "color3d", "color3d[]", "color4d", "color4d[]",
                   "frame4d", "frame4d[]",
                   "texCoord2d", "texCoord2d[]", "texCoord3d", "texCoord3d[]", "timecode", "timecode[]", "point3d",
                   "point3d[]"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFF67A515))

        for tp in ["float", "float[]", "quatf", "quatf[]", "float2", "float2[]", "float3", "float3[]", "float4",
                   "float4[]",
                   "point3f", "point3f[]", "normal3f", "normal3f[]", "vector3f", "vector3f[]", "color3f", "color3f[]",
                   "color4f",
                   "color4f[]", "texCoord2f", "texCoord2f[]", "texCoord3f", "texCoord3f[]"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFF88CF2A))

        for tp in ["half", "half[]", "quath", "quath[]", "half2", "half2[]", "half3", "half3[]", "half4", "half4[]",
                   "normal3h", "normal3h[]", "point3h", "point3h[]", "vector3h", "vector3h[]", "color3h", "color3h[]",
                   "color4h",
                   "color4h[]", "texCoord2h", "texCoord2h[]", "texCoord3h", "texCoord3h[]"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFFADFB47))

        for tp in ["int", "int[]", "int2", "int2[]", "int3", "int3[]", "int4", "int4[]"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFF5F5FE5))

        for tp in ["int64", "int64[]"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFF4040D2))

        for tp in ["uint", "uint[]"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFF2525B5))

        for tp in ["uint64", "uint64[]"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFF101081))

        for tp in ["string"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFF781FA5))

        for tp in ["token", "token[]"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFF9C3ACC))

        for tp in ["uchar", "uchar[]"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFFB764E1))

        for tp in ["bundle"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFFCD7A3A))

        for tp in ["unresolved {any}", "unresolved {union}"]:
            style.update(self._delegate.specialized_port_style(tp, 0xFFFFFFFF))

        return style

    def __create_node(self, type_name: str, node_name: str = None):
        graph = self._model.current_graph
        if graph:
            node = graph.create_node(
                type_name,
                self._graph_view.screen_to_canvas(self._context_menu_position[0], self._context_menu_position[1]),
                node_name
            )
            if len(graph.nodes) == 1:
                self.focus_on_nodes()
            return node

    def __on_stage_event(self, event):
        """Called by stage_event_stream"""
        if event.type == int(omni.usd.StageEventType.SELECTION_CHANGED):
            self.__on_kit_selection_changed()
        elif event.type == int(omni.usd.StageEventType.CLOSED):
            self.close_graph()
        elif event.type == int(omni.usd.StageEventType.OPENED):
            if self._new_stage_root_path:
                root_path = self._new_stage_root_path
                current_path = self._new_stage_current_path
                self._new_stage_root_path = None
                self._new_stage_current_path = None
                root_prim = self._usd_context.get_stage().GetPrimAtPath(root_path)
                self.open_graph(root_prim, current_path)
            else:
                self.close_graph()

    def __on_kit_selection_changed(self, force=False):
        """Send the selection from Kit to TreeView"""
        if self._model is None or not self._model.current_graph or self._in_selection:
            return
        prim_paths = self._selection.get_selected_prim_paths()
        if not force and prim_paths == self._last_selected_prim_paths:
            return
        self._last_selected_prim_paths = prim_paths
        selection = []
        for path in prim_paths:
            node = self._model.current_graph.get_node(Sdf.Path(path))
            if node:
                selection.append(node)
        self._in_selection = True
        self._model.selection = selection
        self._in_selection = False

    def __on_model_selection_changed(self):
        if self._in_selection:
            return
        prim_paths = [node.prim.GetPath().pathString for node in self._model.selection if node.prim]
        if prim_paths == self._last_selected_prim_paths:
            return
        self._last_selected_prim_paths = prim_paths
        # send the selection to Kit
        self._in_selection = True
        self._selection.set_selected_prim_paths(prim_paths, False)
        self._in_selection = False

    def on_use_prim_name_clicked(self, Value):
        Settings.set_show_name_as_type(Value)
        self._model._item_changed(None)

    def on_frame_selected_clicked(self):
        self._graph_view.focus_on_nodes(self._model._selected_nodes)

    def on_layout_clicked(self):
        self._graph_view.layout_all()
