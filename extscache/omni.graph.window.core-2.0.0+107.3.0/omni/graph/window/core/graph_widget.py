# noqa: too-many-lines

# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["OmniGraphWidget"]

import asyncio
import json
import weakref
from enum import IntEnum
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import carb
import carb.events
import carb.input
import omni.graph.core as og
import omni.graph.tools as ogt
import omni.graph.tools.ogn as ogn
import omni.kit
import omni.kit.app
import omni.ui as ui
import omni.usd
import OmniGraphSchema
from omni.kit.graph.delegate.modern import BackdropDelegate
from omni.kit.graph.delegate.modern import GraphNodeDelegate as GraphNodeDelegateBase
from omni.kit.graph.delegate.modern import NoteDelegate
from omni.kit.graph.editor.core import GraphEditorCoreWidget
from omni.kit.graph.widget.variables import GraphEditorVariablesWidget
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
from omni.kit.widget.graph import BackdropGetter, GraphModel
from omni.kit.window.popup_dialog import InputDialog
from pxr import Sdf, Usd

from . import graph_config
from .catalog_delegate import OmniGraphCatalogTreeDelegate
from .catalog_model import OmniGraphNodeTypeCatalogModel
from .compounds import CompoundUtils
from .graph_context_menu import OmniGraphNodeContextMenu
from .graph_delegate import OmniGraphNodeDelegate
from .graph_model import OmniGraphModel, PrimNodeType
from .graph_selector import OmniGraphSelector
from .graph_view import OmniGraphView
from .omni_graph_editor_variables_tree_delegate import OmniGraphEditorVariablesTreeDelegate
from .read_variable_node_delegate import ReadVariableNodeDelegate, VariableNodeDelegate
from .variables_model import READ_VARIABLE_NODES, WRITE_VARIABLE_NODES, OmniGraphVariablesModel, VariableItem
from .virtual_node_helper import VirtualNodeHelper

ICON_PATH = graph_config.Paths.ICON_PATH
TOOLBAR_ICON_PATH = ICON_PATH.joinpath("toolbar")

DEFAULT_GRAPH_PREFIX = "PushGraph"
DEFAULT_GRAPH_EVALUATOR = "push"

DEFAULT_COMPOUND_INPUT_POS = (-600, 0)
DEFAULT_COMPOUND_OUTPUT_POS = (600, 0)


# ==========================================================================================
# Destroy a window after a delay. Useful for having a widget callback destroy its own
# window without crashing Kit.
#
# One drawback to this approach is that this embeds a reference to the window which may keep it
# alive if it is closed by other means (e.g. using its close icon). This can usually be overcome
# by giving the window a visibility_changed_fn which also calls this.
def _delayed_destroy_window(window: ui.Window, num_ticks=1):
    async def do_destroy(window, num_ticks):
        # The window might be destroyed by other means while we're waiting. Get a weak reference to it.
        window_ref = weakref.ref(window)
        for _ in range(num_ticks):
            await omni.kit.app.get_app().next_update_async()
        window = window_ref()
        if window is not None:
            window.destroy()

    asyncio.ensure_future(do_destroy(window, num_ticks))


# ==========================================================================================
# Helpers to deal with the correct variable node being used for the correct version of
# omni-graph


# ---------------------------------------------------------------------------------------
def get_read_variable_node() -> Optional[str]:
    """Returns the name of the read variable node to be used by the graph view"""
    for node_type_name in READ_VARIABLE_NODES:
        if og.get_node_type(node_type_name):
            return node_type_name
    return None


# ---------------------------------------------------------------------------------------
def get_write_variable_node() -> Optional[str]:
    """Returns the name of the write variable node to be used by the graph view"""
    for node_type_name in WRITE_VARIABLE_NODES:
        if og.get_node_type(node_type_name):
            return node_type_name
    return None


# Helpers for Prim Node Drop-Menu entries
# =======================================================================================


# ---------------------------------------------------------------------------------------
def _on_drop_prim(
    node_type: PrimNodeType,
    graph_model: OmniGraphModel,
    prim_path: Sdf.Path,
    graph_path: str,
    window,
    position: Tuple[float],
):
    """Helper callback factory function for the built-in prim options"""

    def drop_fn():
        graph_model.import_node(prim_path, graph_path, node_type, window, position)

    return drop_fn


def _on_drop_read_prim(
    graph_model: OmniGraphModel, prim_paths: List[Sdf.Path], graph_path: str, window, position: Tuple[float]
):
    """Helper callback factory function for the built-in read bundle option; supports multiple prim paths"""

    def drop_fn():
        graph_model.create_read_prim_node(prim_paths, graph_path, window, position)

    return drop_fn


_prim_node_menu_items = []


# ---------------------------------------------------------------------------------------
def add_prim_drop_menu_item(
    title: str,
    icon_path: str,
    callback: Callable[[OmniGraphModel, Sdf.Path, str, ui.Window, Tuple[float]], None],
    enable_if: Callable[[str, Sdf.Path], bool],
    supports_multi_drop: Optional[bool] = False,
):
    """Called to add a menu option for creating OG nodes for dragged prim nodes

    Args:
    title: The title of the item to remove
    callback: The function to call when the item is selected
    enable_if: Function to call to determine if the menu item should be enabled - takes graph path and prim path
    supports_multi_drop: If True, all the paths will be passed to the drop function rather than just a single path
    """
    _prim_node_menu_items.append((title, icon_path, callback, enable_if, supports_multi_drop))


# ---------------------------------------------------------------------------------------
# Initialize menu with default entries
add_prim_drop_menu_item(
    "Read Attribute",
    f"{ICON_PATH}/dropdown_read_attribute_noBorder_dark.svg",
    partial(_on_drop_prim, PrimNodeType.READ_ATTRIBUTE),
    lambda *args: True,
)
add_prim_drop_menu_item(
    "Write Attribute",
    f"{ICON_PATH}/dropdown_write_attribute_noBorder_dark.svg",
    partial(_on_drop_prim, PrimNodeType.WRITE_ATTRIBUTE),
    lambda *args: True,
)
add_prim_drop_menu_item(
    "Read Bundle",
    f"{ICON_PATH}/dropdown_read_bundle_noBorder_dark.svg",
    partial(_on_drop_read_prim),
    lambda *args: True,
    True,
)
add_prim_drop_menu_item(
    "OG Prim Node", "", partial(_on_drop_prim, PrimNodeType.LEGACY), graph_config.Settings.is_legacy_prim_enabled
)
add_prim_drop_menu_item(
    "Read All Attributes",
    "",
    partial(_on_drop_prim, PrimNodeType.READ_ATTRIBUTES),
    graph_config.Settings.is_all_attributes_drop_enabled,
)
add_prim_drop_menu_item(
    "Write All Attribute",
    "",
    partial(_on_drop_prim, PrimNodeType.WRITE_ATTRIBUTES),
    graph_config.Settings.is_all_attributes_drop_enabled,
)


class OmniGraphWidget(GraphEditorCoreWidget):
    class EventType(IntEnum):
        """Types of events dispatched by OmniGraphWidget to its event stream."""

        # Sent when the graph widget is given a new model or has its model removed.
        #
        # Payload:  None
        NEW_MODEL = carb.events.type_from_string("omni.graph.window.core@new_model")

    def __init__(
        self,
        graph_model_class: Optional[Type[OmniGraphModel]] = None,
        graph_delegate: Optional[OmniGraphNodeDelegate] = None,
        catalog_model: Optional[OmniGraphNodeTypeCatalogModel] = None,
        variables_model: Optional[OmniGraphVariablesModel] = None,
        context_menu_class: Optional[Type[OmniGraphNodeContextMenu]] = None,
        filter_fn: Optional[Callable[[Sdf.Path, Sdf.PrimSpec], bool]] = None,
    ):
        if not graph_model_class:
            graph_model_class = OmniGraphModel
        if not graph_delegate:
            graph_delegate = OmniGraphNodeDelegate(self)
        if not catalog_model:
            catalog_model = OmniGraphNodeTypeCatalogModel()
        if not variables_model:
            variables_model = OmniGraphVariablesModel()
        if not context_menu_class:
            context_menu_class = OmniGraphNodeContextMenu

        self._graph_model_class = graph_model_class
        self._graph_delegate = graph_delegate
        self._catalog_model = catalog_model
        self._catalog_frame = None
        self._variables_model = variables_model
        self._variables_widget = None
        self.__event_stream = carb.events.get_events_interface().create_event_stream("OmniGraphWidget")
        self._catalog_selector = None
        self.__context_menu_class = context_menu_class
        self.__filter_fn = filter_fn
        self.__right_click_context_menu = None

        self._supported_variable_types: List[str] = []
        for name in dir(Sdf.ValueTypeNames):
            type_name = getattr(Sdf.ValueTypeNames, name)
            if isinstance(type_name, Sdf.ValueTypeName):
                type_name_str = str(type_name)
                og_type = og.AttributeType.type_from_sdf_type_name(type_name_str)
                if og_type.base_type != og.BaseDataType.UNKNOWN:
                    self._supported_variable_types.append(type_name_str)

        self._graph_selector = None
        self._context_menu = ui.Menu("Toolbar Context")

        toolbar_items = [
            {
                "name": "CreateGraph",
                "icon": f"{TOOLBAR_ICON_PATH}/create_graph_dark.svg",
                "on_clicked": self.on_toolbar_create_graph_clicked,
                "tooltip": "Create a new graph",
            },
            {
                "name": "EditGraph",
                "icon": f"{TOOLBAR_ICON_PATH}/edit_graph_dark.svg",
                "on_clicked": self.on_toolbar_edit_graph_clicked,
                "tooltip": "Edit an existing graph",
            },
            {"name": "-"},
            {
                "name": "Expansion_Open",
                "icon": f"{TOOLBAR_ICON_PATH}/omnigraph_state_0_toggle_dark.svg",
                "on_clicked": partial(self.on_toolbar_expansion_state_clicked, GraphModel.ExpansionState.OPEN),
                "tooltip": "Expand all nodes",
            },
            {
                "name": "Expansion_Minimized",
                "icon": f"{TOOLBAR_ICON_PATH}/omnigraph_state_1_toggle_dark.svg",
                "on_clicked": partial(self.on_toolbar_expansion_state_clicked, GraphModel.ExpansionState.MINIMIZED),
                "tooltip": "Minimize all nodes",
            },
            {
                "name": "Expansion_Closed",
                "icon": f"{TOOLBAR_ICON_PATH}/omnigraph_state_2_toggle_dark.svg",
                "on_clicked": partial(self.on_toolbar_expansion_state_clicked, GraphModel.ExpansionState.CLOSED),
                "tooltip": "Close all nodes",
            },
            {"name": "-"},
            # TODO - OnFrame and AddNote implementations
            # {"name": "OnFrame", "icon": f"{TOOLBAR_ICON_PATH}/omnigraph_frame_dark.svg", "on_clicked": self.on_toolbar_onframe_clicked, "tooltip": "Add Frame"},
            # {"name": "AddNote", "icon": f"{TOOLBAR_ICON_PATH}/notes_dark.svg", "on_clicked": self.on_toolbar_addnote_clicked, "tooltip": "Add Note"},
            # {"name": "-"},
            {"name": "Edit", "label": "Edit", "on_clicked": self.on_toolbar_edit_clicked},
            {"name": "View", "label": "View", "on_clicked": self.on_toolbar_view_clicked},
            {"name": " "},
            {
                "name": "Help",
                "icon": f"{TOOLBAR_ICON_PATH}/help_dark.svg",
                "on_clicked": self.on_toolbar_help_clicked,
                "tooltip": "See OmniGraph Tutorials",
            },
            {"name": " ", "width": 6},
        ]

        # For proper routing, the base delegate cannot override any methods
        # make the graph delegate the fallback to an existing router
        self._router = GraphNodeDelegateBase()
        self._router.add_route(graph_delegate)
        self._router.add_route(BackdropDelegate(), type="Backdrop")
        self._router.add_route(NoteDelegate(), type="OmniNote")

        # custom delegates for Write and Read Variables nodes
        self._write_variable_delegate = VariableNodeDelegate(self)
        self._read_variable_delegate = ReadVariableNodeDelegate(self)
        for node_type in WRITE_VARIABLE_NODES:
            self._router.add_route(self._write_variable_delegate, type=node_type)
        for node_type in READ_VARIABLE_NODES:
            self._router.add_route(self._read_variable_delegate, type=node_type)

        super().__init__(
            delegate=self._router,
            view_type=OmniGraphView,
            style=self.get_specialized_style(),
            catalog_model=self._catalog_model,
            catalog_delegate=OmniGraphCatalogTreeDelegate(),
            toolbar_items=toolbar_items,
        )

        self.__focus_task = None
        self.__import_task = None
        self.__rebuild_style_task = None
        self.__show_prefs_task = None
        self._usd_context = omni.usd.get_context()
        self._selection = self._usd_context.get_selection()
        self._stage_event_sub = (
            omni.usd.get_context()
            .get_stage_event_stream()
            .create_subscription_to_pop(self._on_stage_event, name="Omni Graph stage update")
        )

        self.__registry_subscription = (
            og.GraphRegistry()
            .get_event_stream()
            .create_subscription_to_pop(self.__on_node_library_changed, name="OmniGraphWidget Registry Changes")
        )
        assert self.__registry_subscription  # This is mostly to avoid lint complaints.

    def destroy(self):
        self.__registry_subscription = None
        self._supported_variable_types = None
        self.__event_stream = None

        if self.__right_click_context_menu:
            self.__right_click_context_menu.destroy()
        self.__right_click_context_menu = None

        if self._variables_widget:
            self._variables_widget.destroy()
        self._variables_widget = None

        if self._variables_model:
            self._variables_model.destroy()
        self._variables_model = None

        if self._catalog_frame:
            self._catalog_frame.destroy()
        self._catalog_frame = None

        if self._catalog_model:
            self._catalog_model.destroy()
        self._catalog_model = None

        if self._graph_delegate:
            self._graph_delegate.destroy()
        self._graph_delegate = None

        if self._graph_selector:
            self._graph_selector.destroy()
        self._graph_selector = None

        if self._router:
            self._router.destroy()
        self._router = None

        if self._write_variable_delegate:
            self._write_variable_delegate.destroy()
        self._write_variable_delegate = None

        if self._read_variable_delegate:
            self._read_variable_delegate.destroy()
        self._read_variable_delegate = None

        if self.model:
            self.model.destroy()
            self.model = None

        # Clean up any outstanding async tasks.
        for task_prop in ("__focus_task", "__import_task", "__rebuild_style_task", "__show_prefs_task"):
            task = getattr(self, task_prop, None)
            if task:
                task.cancel()
            setattr(self, task_prop, None)

        self._context_menu = None
        self._selection = None
        self._usd_context = None
        self._stage_event_sub = None
        self._catalog_selector = None
        super().destroy()

    @property
    def model(self):
        return super().model

    @model.setter
    def model(self, model):
        old_model = self.model
        if model != old_model:
            super(OmniGraphWidget, self.__class__).model.fset(self, model)
            if self.__event_stream:
                self.__event_stream.dispatch(self.EventType.NEW_MODEL)
            if old_model:
                old_model.destroy()

    def on_build_graph(self):
        """Override called when to build the graph views"""
        super().on_build_graph()

        # Install a custom mouse release method
        self._graph_view.set_mouse_released_fn(self.__on_mouse_released)

    def __on_mouse_released(self, x, y, button, m):
        if self._graph_view:
            selection = self._graph_view.selection
        else:
            selection = []

        if button == 1:
            self._on_right_mouse_button_released(selection, x, y, m)

    def _on_right_mouse_button_released(self, selection, x, y, modifiers):
        """Handle the context menu on the release so other widgets have a chance to initiate it first"""
        # make sure it's not triggered by other mouse behaviors (e.g., Alt zoom)
        if modifiers == 0:
            self.show_context_menu(None)

    def on_add_variable(self):
        if not self._variables_model.graph or not self._variables_model.graph.is_valid():
            return

        og.cmds.CreateVariable(
            graph=self._variables_model.graph,
            variable_name=self._variables_model.get_next_variable_name("NewVariable"),
            variable_type=og.AttributeType.type_from_sdf_type_name(self._supported_variable_types[0]),
        )

    def on_build_variable_value_widget(self, item: ui.AbstractItem) -> bool:
        if not isinstance(item, VariableItem) or not self.model:
            return False

        variable = self.model.get_graph(None).find_variable(item.value_models[0].as_string)
        if not variable:
            return False

        stage = self._usd_context.get_stage()
        variable_prop = stage.GetPropertyAtPath(Sdf.Path(variable.source_path))
        if not variable_prop:
            return False

        item.default_value_models = UsdPropertiesWidgetBuilder.build(
            stage,
            variable_prop.GetName(),
            variable_prop.GetAllMetadata(),
            type(variable_prop),
            [variable_prop.GetPrimPath()],
            {"visible": False},
        )

        return True

    def on_drag_variable_readwrite(self, item: ui.AbstractItem, operation: str) -> str:
        mime_data = self._variables_model.get_drag_mime_data(item)
        if mime_data:
            json_data = json.loads(mime_data)
            if json_data:
                json_data["operation"] = operation
                return json.dumps(json_data)

        return ""

    def _on_focus_variable_instance(self, node):
        stage = omni.usd.get_context().get_stage()

        # Get a node's OmniGraph Stack all the way to the root graph
        graph_stack = []
        cur_graph = node.get_graph()
        graph_stack.append(cur_graph)
        parent_graph = cur_graph.get_parent_graph()
        while parent_graph is not None:
            cur_graph = parent_graph
            parent_graph = cur_graph.get_parent_graph()
            graph_stack.append(cur_graph)

        # Rebuild the self._navigation to build the breadscrumbs
        for sub_graph in reversed(graph_stack[1:]):
            if sub_graph and sub_graph.is_compound_graph():
                compound_node = sub_graph.get_owning_compound_node()
                if compound_node:
                    compound_prim_path = compound_node.get_prim_path()
                    compound_prim = stage.GetPrimAtPath(compound_prim_path)
            else:
                graph_prim_path = sub_graph.get_path_to_graph()
                graph_prim = stage.GetPrimAtPath(graph_prim_path)

        # focus on the current subgraph or root graph
        parent_graph = node.get_graph()
        if parent_graph and parent_graph.is_compound_graph():
            compound_node = parent_graph.get_owning_compound_node()
            if compound_node:
                compound_prim_path = compound_node.get_prim_path()
                compound_prim = stage.GetPrimAtPath(compound_prim_path)
                self.enter_compound(compound_prim, True)
        else:
            # root graph case
            graph_prim_path = parent_graph.get_path_to_graph()
            graph_prim = stage.GetPrimAtPath(graph_prim_path)
            # Should not use enter_compound here for some reason I don't know
            self.set_current_compound(graph_prim, True)

    def _on_stage_event(self, event):
        """When the current stage is closed, reset the model"""
        if event.type == int(omni.usd.StageEventType.CLOSED):
            self.model = None
            if self._variables_model:
                self._variables_model.graph = None

    def is_graph_editable(self, graph: og.Graph) -> bool:
        """Returns True if the given graph is editable by this widget"""
        return True

    def on_build_startup(self):
        """Build the startup panel UI"""
        raise NotImplementedError("Subclass must implement")

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
                    "GraphPanelTabs.Separator": {"color": text_color, "border_width": 2},
                },
            ):
                ui.Spacer()
                ui.RadioButton(
                    text="Nodes", radio_collection=collection, width=0, style_type_name_override="GraphPanelTabs.Button"
                )
                with ui.VStack(width=1):
                    ui.Spacer()
                    ui.Line(height=10, alignment=ui.Alignment.LEFT, style_type_name_override="GraphPanelTabs.Separator")
                    ui.Spacer()
                ui.RadioButton(
                    text="Variables",
                    radio_collection=collection,
                    width=0,
                    style_type_name_override="GraphPanelTabs.Button",
                )
                ui.Spacer()

            with ui.ZStack():
                self._catalog_frame = ui.Frame()
                with self._catalog_frame:
                    super().on_build_catalog()
                self._variables_widget = GraphEditorVariablesWidget(
                    self._variables_model,
                    delegate=OmniGraphEditorVariablesTreeDelegate(
                        on_drag_variable_read=partial(self.on_drag_variable_readwrite, operation="read"),
                        on_drag_variable_write=partial(self.on_drag_variable_readwrite, operation="write"),
                        on_focus_variable_instance=self._on_focus_variable_instance,
                    ),
                    on_add_variable=self.on_add_variable,
                    on_build_variable_value_widget=self.on_build_variable_value_widget,
                    supported_variable_types=self._supported_variable_types,
                    visible=False,
                )

        def on_tab_changed(model: ui.AbstractValueModel, weak_self):
            weak_self = weak_self()
            if not weak_self:
                return

            catalog_selected = model.as_int == 0
            weak_self._catalog_frame.visible = catalog_selected  # noqa: protected-access
            weak_self._variables_widget.visible = not catalog_selected  # noqa: protected-access

        collection.model.add_value_changed_fn(partial(on_tab_changed, weak_self=weakref.ref(self)))
        self._catalog_selector = collection

    def on_build_breadcrumbs(self):
        with ui.HStack(height=0):
            if self._graph_selector:
                self._graph_selector.destroy()
            self._graph_selector = OmniGraphSelector(self._get_all_graphs, self._on_open_graph)
            super().on_build_breadcrumbs()

    def _get_all_graphs(self) -> List[str]:
        """Provide a list of possible graphs to open"""
        return [g.get_path_to_graph() for g in og.get_all_graphs() if self.is_graph_editable(g)]

    def _on_open_graph(self, graph: str):
        """callback when opening a new graph from the editor"""
        if self.model and graph == self.model._graph.get_path_to_graph():  # noqa: protected-access
            return

        # Delayed open to allow the UI to cleanup before opening the next graph
        async def delayed_import():
            self._open_graph(graph)

        self.__import_task = asyncio.ensure_future(delayed_import())
        assert self.__import_task  # This is mostly to avoid lint complaints.

    def _import_prims(self, _, prims: List[Usd.Prim], focus=True):
        """Reset the model to the first valid selection in the given list
        Returns:
            True on success, False if no change was made
        """
        # We only care about the first graph.
        graph_node_prim_types = self.__get_graph_node_prim_types()
        prim = next((prim for prim in prims if prim.GetTypeName() in graph_node_prim_types), None)
        if prim:
            root_prim = CompoundUtils.get_root_graph_prim(prim) or prim
            compound_prim = CompoundUtils.owning_compound_node(prim) if root_prim != prim else None

            if self.model:
                self.model.destroy()

            # This assignment will trigger a call to set_current_compound() which will start a UI build.
            self.model = self._graph_model_class(root_prim)

            if self.model:
                # handle variable change events
                if hasattr(og.GraphEvent, "VARIABLE_TYPE_CHANGE") and hasattr(og.GraphEvent, "REMOVE_VARIABLE"):
                    self.model.register_graph_event_callback(self._on_graph_event)

                try:
                    # Calling here so we can pass self (the graph widget) through
                    self.model.add_get_moving_items_fn(
                        BackdropGetter(self.model, lambda item: self.model[item].type == "Backdrop", self)
                    )
                except TypeError:
                    # fallback for 105.0, before the 4th arg existed
                    self.model.add_get_moving_items_fn(
                        BackdropGetter(self.model, lambda item: self.model[item].type == "Backdrop")
                    )

            self._variables_model.graph = self.model.get_graph(root_prim.GetPath().pathString)

            # OM-42766 Workaround:
            #
            # Whenever a new model is loaded into the graph widget it sets its zoom level using the canvas's
            # existing computed size. But that size was based on the previously loaded model and may not
            # be correct for the new one, leading to the nodes being draw at the wrong scale and not centered
            # in the view. This is particularly noticeable with the very first model loaded since the canvas was
            # completely empty before that and therefore at its default size.
            #
            # To get around this we give the graph some time to finish drawing, so that the canvas gets its proper
            # size, then reset the graph's top-level prim so that it draws again using the correct size.
            async def delayed_focus():

                if compound_prim:
                    # Setting the current compound to the root first causes the graph to rebuild, and the navigation
                    # to update correctly.
                    self.set_current_compound(root_prim, focus)
                    self.enter_compound(compound_prim, focus)
                    if focus:
                        for _ in range(2):
                            await omni.kit.app.get_app().next_update_async()
                        # calling enter_compound or set_current_compound again will not cause a re-focus
                        self.focus_on_nodes()
                else:
                    for _ in range(2):
                        await omni.kit.app.get_app().next_update_async()
                    self.set_current_compound(prim, focus)

            self.__focus_task = asyncio.ensure_future(delayed_focus())
            assert self.__focus_task  # This is mostly to avoid lint complaints.
            return True
        return False

    def _import_selection(self, focus=True):
        """Import selected prims"""
        selection = self._selection.get_selected_prim_paths()
        if not selection:
            self.model = None
            self._variables_model.graph = None
            return

        stage = self._usd_context.get_stage()

        # We can only import the first selected graph
        prim_path = selection[0]
        graph = og.get_graph_by_path(prim_path)
        if graph and self.is_graph_editable(graph):
            self._import_prims(None, [stage.GetPrimAtPath(prim_path)])
        else:
            self.model = None

    def __make_drop_all_fn(self, make_drop_fn, prim_paths, graph_path, window, position, offset):
        fns = []
        for i, prim_path in enumerate(prim_paths):
            node_offset = i * offset
            if isinstance(prim_path, str):
                prim_path = Sdf.Path(prim_path)
            fns.append(
                make_drop_fn(
                    self.model, prim_path, graph_path, window, (position[0] + node_offset, position[1] + node_offset)
                )
            )

        def drop_all_fn():
            with omni.kit.undo.group():
                for fn in fns:
                    fn()

        return drop_all_fn

    def choose_prim_node_dialog(
        self,
        prim_paths: Union[str, Sdf.Path, List[str], List[Sdf.Path]],
        graph_path: str,
        position: Tuple[float],
        window_position: Optional[Tuple[float]] = None,
    ):
        """Popup to select if you want to import or export a prim

        Args:
            prim_paths: A single full path or an array of full paths to the prims being imported
            graph_path: The full path to the og.Graph to import the prim into
            position: canvas position to put the new node at
            window_position: screen position to place the dialog
        """
        if isinstance(prim_paths, (str, Sdf.Path)):
            prim_paths = [prim_paths]
        if len(prim_paths) <= 0:
            return
        for prim_path in prim_paths:
            if not isinstance(prim_path, (str, Sdf.Path)):
                carb.log_warn("The specified prim paths must be of type str or Sdf.Path")
                return
        n_entries = len([e for e in self.get_prim_drop_menu_items() if e[3](graph_path, prim_paths[0])])
        if n_entries == 0:
            return
        entry_height = 80
        win_width = 200
        win_height = entry_height * n_entries
        window = ui.Window(
            "Create Node for Prim",
            width=win_width,
            height=win_height,
            flags=ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_SCROLLBAR
            | ui.WINDOW_FLAGS_MODAL
            | ui.WINDOW_FLAGS_NO_SCROLL_WITH_MOUSE,
        )

        def close_window():
            _delayed_destroy_window(window)

        # Called when the window's close icon (the 'x' in the upper-right corner) is clicked.
        def visibility_changed(is_visible: bool):
            if not is_visible:
                close_window()

        window.set_visibility_changed_fn(visibility_changed)

        if window_position is not None:
            window.position_x, window.position_y = (
                window_position[0] - win_width // 2,
                (window_position[1] - win_height // 2) + entry_height // 2,
            )

        def on_key_pressed(key, _, pressed):
            if not pressed:
                return
            if key == int(carb.input.KeyboardInput.ESCAPE):
                close_window()

        window.set_key_pressed_fn(on_key_pressed)

        with window.frame:
            with ui.VStack(
                spacing=5,
                name="top_level_stack",
                style={"VStack::top_level_stack": {"margin": 5}, "Button": {"margin": 0}},
            ):
                icon_size = 58
                margin = 2
                offset = 40
                radius = 9
                border = 1.5
                for title, icon_path, make_drop_fn, enabled_fn, supports_multi_drop in self.get_prim_drop_menu_items2():
                    with ui.ZStack(width=180):
                        if enabled_fn(graph_path, prim_paths[0]):
                            fn = self.__make_drop_all_fn(make_drop_fn, prim_paths, graph_path, window, position, offset)
                            if supports_multi_drop:
                                fn = make_drop_fn(self.model, prim_paths, graph_path, window, position)

                            def execute_and_close(fn):
                                fn()
                                close_window()

                            ui.Button(
                                " ",  # Do not want this empty button to display any text, but this field cannot be empty. Otherwise the size of the button will become weird
                                clicked_fn=partial(execute_and_close, fn),
                            )
                            with ui.HStack(
                                spacing=8,
                                name="button_stack",
                                style={"VStack::button_stack": {"margin": 5}},
                            ):
                                ui.Spacer(width=margin)
                                with ui.VStack(width=icon_size, height=icon_size + margin * 2):
                                    ui.Spacer(width=margin)
                                    with ui.ZStack(height=icon_size):
                                        self._graph_delegate._build_rectangle(  # noqa: protected-access
                                            radius, True, "", title, {"background_color": 0xFF57747C}
                                        )
                                        with ui.VStack(width=icon_size, height=icon_size):
                                            ui.Spacer(height=border)
                                            with ui.HStack():
                                                ui.Spacer(width=border)
                                                self._graph_delegate._build_rectangle(  # noqa: protected-access
                                                    radius - border, True, "", title, {"background_color": 0xFF1E2931}
                                                )
                                                ui.Spacer(width=border)
                                            ui.Spacer(height=border)
                                        with ui.HStack():
                                            ui.Spacer()
                                            ui.Image(
                                                f"{icon_path}",
                                                width=icon_size - border * 2,
                                                style_type_name_override="Graph.Node.Icon",
                                                name="Icon",
                                            )
                                            ui.Spacer()
                                        ui.Spacer()
                                    ui.Spacer(height=margin)
                                ui.Spacer(width=margin)
                                ui.Label(
                                    title,
                                    alignment=ui.Alignment.LEFT_CENTER,
                                )

    def _create_variable_node(self, variable_name, node_type_name, canvas_pos, graph_path=None):
        if graph_path is None:
            graph_path = self.get_current_graph_item().GetPath().pathString

        success, node = self.model.create_node(node_type_name, graph_path, canvas_pos)

        if success:
            graph_attr = node.get_attribute("inputs:graph")

            stage = omni.usd.get_context().get_stage()
            if graph_attr:
                # set the relationship target to the parent level graph
                stage.GetRelationshipAtPath(Sdf.Path(graph_attr.get_path())).SetTargets(
                    [Sdf.Path(self.model.get_graph(None).get_path_to_graph())]
                )

            var_name_attr = node.get_attribute("inputs:variableName")
            if var_name_attr:
                stage.GetAttributeAtPath(Sdf.Path(var_name_attr.get_path())).Set(variable_name)

    def create_variable_node_dialog(
        self, variable_name, position: Tuple[float], window_position: Optional[Tuple[float]] = None
    ):
        window = ui.Window(
            "Create Variable Node",
            flags=ui.WINDOW_FLAGS_NO_RESIZE | ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_MODAL,
            auto_resize=True,
        )

        def close_window():
            _delayed_destroy_window(window)

        # Called when the window's close icon (the 'x' in the upper-right corner) is clicked.
        def visibility_changed(is_visible: bool):
            if not is_visible:
                close_window()

        window.set_visibility_changed_fn(visibility_changed)

        graph_prim = self.get_current_graph_item()
        graph_path = graph_prim.GetPath().pathString

        if window_position is not None:
            window.position_x, window.position_y = (window_position[0], window_position[1])

        with window.frame:
            with ui.VStack(
                width=0,
                height=0,
                spacing=5,
                name="top_level_stack",
                style={"VStack::top_level_stack": {"margin_height": 5}, "Button": {"margin": 0}},
            ):

                def build_button(image_url, text, subtitle, clicked_fn):
                    with ui.ZStack():
                        rectangle = ui.Rectangle(style_type_name_override="Button")
                        if clicked_fn:

                            def on_pressed(x, y, button, modifier):
                                if button == 0:
                                    clicked_fn()

                            rectangle.set_mouse_pressed_fn(on_pressed)

                        with ui.HStack(width=0):
                            ui.Spacer(width=2)
                            with ui.VStack():
                                ui.Spacer(height=2)
                                ui.Image(image_url, width=40, height=40)
                                ui.Spacer(height=2)
                            ui.Spacer(width=10)
                            with ui.VStack():
                                ui.Spacer()
                                with ui.VStack(height=0, spacing=2):
                                    ui.Label(text)
                                    ui.Label(subtitle, style={"Label": {"color": 0xFF5C5C5C}})
                                ui.Spacer()
                            ui.Spacer(width=2)

                def on_read_clicked():
                    self._create_variable_node(variable_name, get_read_variable_node(), position, graph_path)
                    close_window()

                build_button(
                    f"{graph_config.Paths.ICON_PATH}/type_get_dark.svg",
                    "READ VARIABLE NODE",
                    "Returns value of a variable",
                    on_read_clicked,
                )

                def on_write_clicked():
                    self._create_variable_node(variable_name, get_write_variable_node(), position, graph_path)
                    close_window()

                build_button(
                    f"{graph_config.Paths.ICON_PATH}/type_set_dark.svg",
                    "WRITE VARIABLE NODE",
                    "Sets value of a variable",
                    on_write_clicked,
                )

                with ui.HStack():
                    ui.Spacer()
                    ui.Button("Cancel", width=0, clicked_fn=close_window)

    def _on_edit_graph_action(self):
        """Edit what is currently selected, or prompt for selection"""
        selection = self._selection.get_selected_prim_paths()
        if selection:
            stage = self._usd_context.get_stage()
            prim_path = selection[0]
            graph = og.get_graph_by_path(prim_path)
            if graph and self.is_graph_editable(graph) and self._import_prims(None, [stage.GetPrimAtPath(prim_path)]):
                return
        # No selection found, prompt for a graph to edit
        self._select_graph_dialog()

    def _select_graph_dialog(self):
        """Present a window for the user to select a graph to open"""
        window = ui.Window("Select Graph To Open", width=400, height=250, flags=ui.WINDOW_FLAGS_MODAL)

        def close():
            if window:
                window.visible = False

        def select_graph(graph: og.Graph):
            if not graph:
                return
            self._open_graph(graph.get_path_to_graph())
            close()

        graphs = [g for g in og.get_all_graphs() if self.is_graph_editable(g)]

        with window.frame:
            with ui.VStack(
                height=0,
                spacing=5,
                name="top_level_stack",
                style={"VStack::top_level_stack": {"margin": 5}, "Button": {"margin": 0}},
            ):
                for graph in graphs:
                    ui.Button(graph.get_path_to_graph(), clicked_fn=partial(select_graph, graph))
                if not graphs:
                    ui.Button("No Graphs Found", clicked_fn=close)

    def _open_graph(self, graph: str):
        # Select the graph
        self._selection.set_prim_path_selected(graph, True, True, True, True)
        self._import_selection()

    def create_graph(self, evaluator_type: str, name_prefix: str, menu_arg=None, value=None, use_dialog=False):
        """Create a new GlobalGraph below the default prim

        Note: USE_IMPLICIT_GLOBAL_GRAPH forces creation of subgraphs only

        Args:
            evaluator_type: the evaluator type to use for the new graph
            name_prefix: the desired name of the GlobalGraph node. Will be made unique
            menu_arg: menu info
            value: menu value
        """
        # FIXME: How to specify USD backing?
        usd_backing = True
        stage = self._usd_context.get_stage()

        if stage.HasDefaultPrim():
            graph_root_path = stage.GetDefaultPrim().GetPath()
        else:
            graph_root_path = Sdf.Path.absoluteRootPath

        graph_path = Sdf.Path(name_prefix).MakeAbsolutePath(graph_root_path)
        graph_path = omni.usd.get_stage_next_free_path(stage, graph_path, True)

        def on_cancel(dialog: omni.kit.window.popup_dialog.dialog.PopupDialog):
            dialog.hide()

        def create_graph_at_path(path: Sdf.Path):
            # FIXME: Just use the first one? We may want a clearer API here.
            graph = og.get_global_orchestration_graphs()[0]

            # Create the global compute graph
            og.cmds.CreateGraphAsNode(
                graph=graph,
                node_name=Sdf.Path(path).name,
                graph_path=path,
                evaluator_name=evaluator_type,
                is_global_graph=True,
                backed_by_usd=usd_backing,
                fc_backing_type=og.GraphBackingType.GRAPH_BACKING_TYPE_FLATCACHE_SHARED,
                pipeline_stage=og.GraphPipelineStage.GRAPH_PIPELINE_STAGE_SIMULATION,
            )

            # select the new prim
            self._selection.set_prim_path_selected(graph_path, True, True, True, True)
            # Import it to the GraphView
            self._import_selection()

        def on_okay(dialog: omni.kit.window.popup_dialog.dialog.PopupDialog):
            input_path = dialog.get_value()
            input_path = omni.usd.get_stage_next_free_path(stage, input_path, True)
            create_graph_at_path(input_path)
            dialog.hide()

        if use_dialog:
            dialog = InputDialog(
                title=f"Create {evaluator_type} Graph",
                message="Enter desired path to graph",
                default_value=graph_path,
                ok_handler=on_okay,
                cancel_handler=on_cancel,
            )
            dialog.show()
        else:
            create_graph_at_path(graph_path)

    @property
    def current_compound(self) -> Usd.Prim | None:
        """
        Return the prim of the current compound, possibly None if the current isolation model is not set
        """
        if self._isolation_model:
            return self._isolation_model._root  # noqa: protected-access
        return None

    # ---------------------------------------------------------------------------------------
    def enter_compound(self, item: Usd.Prim, focus=True):
        """
        If item is a compound, make it the current compound
        """
        # entering a compound requires changes that are only in kit 105.1, so make sure compound subgraphs are fully
        # supported before we enable entering them
        if not graph_config.Supports.compound_subgraphs() or not graph_config.Settings.are_compounds_enabled():
            return

        # This is a compound graph node. Get the compound graph from it.
        if (
            isinstance(item, Usd.Prim)
            and item.IsA(OmniGraphSchema.OmniGraphNode)
            and item.HasAPI(OmniGraphSchema.CompoundNodeAPI)
        ):
            node = og.Controller.node(item)
            if not node.is_compound_node():
                return

            compound_graph = node.get_compound_graph_instance()
            if not compound_graph:
                return

            graph_prim = self._usd_context.get_stage().GetPrimAtPath(compound_graph.get_path_to_graph())
            if not graph_prim:
                return

            def create_virtual_node_port(port_name: str, default_position: Tuple[int, int], is_input: bool):
                faux_port = graph_prim.GetPath().AppendProperty(port_name)
                pos = VirtualNodeHelper.get_virtual_node_position(faux_port, None)
                if pos is None:
                    # for tests in particular the compound nodes may never have had a position set, so this
                    # will make sure there is a reasonable default position
                    pos = VirtualNodeHelper.compute_initial_position(faux_port) or default_position
                    VirtualNodeHelper.set_virtual_node_position(faux_port, pos)
                self._isolation_model.add_input_or_output((pos[0], pos[1]), is_input)

            # recache the model prior to entering the compound. If the compound was just created,
            # the updated connections are not yet cached and no connections will be shown.
            self.model.cache_graph()
            self.set_current_compound(graph_prim, focus)

            # By default the isolation model InputNode and OutputNode only appears if it has ports.
            # This is to make appear even when there are none
            if self._isolation_model:
                if not self._isolation_model._input_nodes:  # noqa: protected-access
                    create_virtual_node_port("inputs:fakeInput", DEFAULT_COMPOUND_INPUT_POS, True)
                if not self._isolation_model._output_nodes:  # noqa: protected-access
                    create_virtual_node_port("outputs:fakeOutput", DEFAULT_COMPOUND_OUTPUT_POS, False)

    # ---------------------------------------------------------------------------------------

    def on_accept_drop(self, drop_data: str):
        """Called to check if drop_data contains data that we can process.
        We currently support:
        - paths to exiting prims (Eg /World/Cube) which are not OG Prims
        - catalog items {"node_type": "omni.graph.nodes.Add",..}
        - special catalog items {"node_type": "SubGraph"|"InputNode"|"OutputNode"}
        """
        try:
            # this is a new compute node
            json_data = json.loads(drop_data)
            try:
                return "node_type" in json_data or "variable_name" in json_data
            except KeyError:
                return False
        except json.decoder.JSONDecodeError:
            if not Sdf.Path.IsValidPathString(drop_data):
                return False
            # this my be an existing prim in the stage
            prim_path = Sdf.Path(drop_data)
            prim = self._usd_context.get_stage().GetPrimAtPath(prim_path)
            # FIXME: Should this act like a cut and paste of a compute node / graph?
            if prim and prim.GetTypeName() in self.__get_prim_types_to_ignore_on_drop():
                return False
        return True

    def get_prim_drop_menu_items(
        self,
    ) -> List[
        Tuple[
            str,
            str,
            Callable[[OmniGraphModel, Sdf.Path, str, ui.Window, Tuple[float]], None],
            Callable[[str, Sdf.Path], bool],
        ]
    ]:
        """Return the list of menu items for the Prim drop menu popup.
        This function is deprecated; use OmniGraphWidget.get_prim_drop_menu_items2 instead.
        Tuple of:
        Title
        Icon Path
        Callback factory function with arguments:
        (graph_model, prim_path, graph_path, window, position)
        Callback function with arguments (graph_path, prim_path) that returns True if that menu item should be shown
        """
        ogt.DeprecateMessage.deprecated("Use OmniGraphWidget.get_prim_drop_menu_items2 instead.")
        prim_node_menu_items = []
        for title, icon_path, make_drop_fn, enabled_fn, _supports_multi_drop in self.get_prim_drop_menu_items2():
            prim_node_menu_items.append((title, icon_path, make_drop_fn, enabled_fn))
        return prim_node_menu_items

    def get_prim_drop_menu_items2(
        self,
    ) -> List[
        Tuple[
            str,
            str,
            Callable[[OmniGraphModel, Sdf.Path, str, ui.Window, Tuple[float]], None],
            Callable[[str, Sdf.Path], bool],
            bool,
        ]
    ]:
        """Return the list of menu items for the Prim drop menu popup
        Tuple of:
        Title
        Icon Path
        Callback factory function with arguments:
        (graph_model, prim_path or list of prim_paths, graph_path, window, position)
        Callback function with arguments (graph_path, prim_path) that returns True if that menu item should be shown
        A Boolean indicating if the factory function takes a single prim path or multiple prim paths
        """
        return _prim_node_menu_items

    def on_drop(self, event: ui.WidgetMouseDropEvent):
        """Called to create a node that was dropped to the window"""
        if event.x is None and event.y is None:
            # put the node at the Middle of the canvas
            event.x = self._graph_view.screen_position_x + self._graph_view.computed_width / 2
            event.y = self._graph_view.screen_position_y + self._graph_view.computed_height / 2

        canvas_pos = self._graph_view.mouse_to_view(event.x, event.y)
        screen_pos = self._graph_view.mouse_to_screen(event.x, event.y)
        data = event.mime_data
        graph_prim = self.get_current_graph_item()
        graph_path = graph_prim.GetPath().pathString
        try:
            # this is a new compute node
            json_data = json.loads(data) or {}
            variable_name = json_data.get("variable_name")
            if variable_name:
                created_node = False
                operation = json_data.get("operation")
                if operation:
                    if operation == "read":
                        self._create_variable_node(
                            variable_name,
                            get_read_variable_node(),
                            canvas_pos,
                            graph_path,
                        )
                        created_node = True
                    elif operation == "write":
                        self._create_variable_node(
                            variable_name,
                            get_write_variable_node(),
                            canvas_pos,
                            graph_path,
                        )
                        created_node = True

                if not created_node:
                    self.create_variable_node_dialog(variable_name, canvas_pos, screen_pos)
            else:
                node_type_name = json_data.get("node_type", "New")
                if node_type_name == "SubGraph":
                    self.model.create_subgraph_node(graph_path, canvas_pos)
                elif node_type_name == "InputNode":
                    self._isolation_model.add_input_or_output(canvas_pos, 1)
                elif node_type_name == "OutputNode":
                    self._isolation_model.add_input_or_output(canvas_pos, 0)
                elif node_type_name == "Backdrop":
                    self.model.create_backdrop(graph_prim.GetPath(), canvas_pos)
                elif node_type_name == "OmniNote":
                    self.model.create_note(graph_prim.GetPath(), canvas_pos)
                else:
                    # Check if this is a registered OG node type
                    node_type = og.get_node_type(node_type_name)
                    if not node_type:
                        carb.log_warn(f"Could not find OmniGraph node type {node_type_name}")
                        return
                    self.model.create_node(node_type_name, graph_path, canvas_pos)
        except json.decoder.JSONDecodeError:
            # this is an existing prim (or prims) in the stage
            prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()
            if len(prim_paths) > 0:
                self.choose_prim_node_dialog(prim_paths, graph_path, canvas_pos, screen_pos)
                # Dialog will trigger the item changed callback on completion
                return
            carb.log_warn("No prims selected!")

        self.model._item_changed(None)  # noqa: protected-access

    # ---------------------------------------------------------------------------------------

    def on_left_mouse_button_double_clicked(self, items: List[Usd.Prim]):
        """Override"""
        if not items:
            # Double clicking with no items selected, in this case we want to select the current Graph
            graph_prim = self.get_current_graph_item()
            graph_path = graph_prim.GetPath().pathString
            old_prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()

            # At this point the selection has already been cleared by the first mouse pressed, and there is an
            # additional graph_view._clear_selection_next_frame_async pending for the second mouse press.
            # So we need to wait for that to finish
            async def async_navigate_up():
                # Wait one tick for _clear_selection_next_frame_async to start
                await omni.kit.app.get_app().next_update_async()
                # Another tick for it to finish, then select
                await omni.kit.app.get_app().next_update_async()
                omni.kit.commands.execute(
                    "SelectPrims",
                    old_selected_paths=old_prim_paths,
                    new_selected_paths=[graph_path],
                    expand_in_stage=True,
                )

            asyncio.ensure_future(async_navigate_up())
            return

    # ---------------------------------------------------------------------------------------

    def get_specialized_style(self):
        # It's optional. It's here in case we have colors different from colors
        # of omni.kit.graph.editor.core.
        style = self._graph_delegate.get_style(background=0xFF23211F)

        # Special colors for error and warning states, and the expansion button
        style.update(
            {
                "Graph.Node.Error.Background": {"background_color": graph_config.ERROR_BACKGROUND_COLOR},
                "Graph.Node.Error.Highlight": {"background_color": graph_config.ERROR_HIGHLIGHT_COLOR},
                "Graph.Node.Warning.Background": {"background_color": graph_config.WARNING_BACKGROUND_COLOR},
                "Graph.Node.Warning.Highlight": {"background_color": graph_config.WARNING_HIGHLIGHT_COLOR},
                "Graph.Node.Warning.Label": {"color": graph_config.WARNING_LABEL_COLOR, "font_size": 15},
                "Graph.Node.Expansion.On": {"background_color": graph_config.EXPANSION_ON_COLOR_ABGR},
                "Graph.Node.Expansion.Off": {"background_color": graph_config.EXPANSION_OFF_COLOR_ABGR},
            }
        )

        # The variable widget uses Graph.Connection with SDF types to determine background color
        # It is already overridden for og.Types, override it for Graph.Connection as well.
        for type_name in self._supported_variable_types:
            og_type = og.AttributeType.type_from_sdf_type_name(type_name)
            color = graph_config.DATA_TYPE_TO_COLOR.get(og_type.base_type, 0xFF000000)
            style.update({f"Graph.Connection::{type_name}": {"background_color": color, "color": color}})

        # pre-load fixed category types
        for name, info in graph_config.CategoryStyles.STYLE_BY_CATEGORY.items():
            color, icon_path, second_color = info
            style.update(self._graph_delegate.specialized_color_style(name, color, icon_path, second_color))
            style.update(
                self._graph_delegate.specialized_expansion_style(
                    name, graph_config.lerp_abgr_to_secondary(color, graph_config.EXPANSION_ON_COLOR_ABGR), second_color
                )
            )

        # Existing registered node types
        self._update_style_for_registered_types(style)

        # Port types are colored by base data type. Update the style dictionary.
        for type_name in ogn.supported_attribute_type_names():
            style.update(self._graph_delegate.specialized_port_style(type_name, graph_config.type_to_color(type_name)))

        return style

    def on_toolbar_create_graph_clicked(self):
        self.create_graph(DEFAULT_GRAPH_EVALUATOR, DEFAULT_GRAPH_PREFIX, use_dialog=False)

    def on_toolbar_edit_graph_clicked(self):
        self._on_edit_graph_action()

    def on_toolbar_expansion_state_clicked(self, state):
        if self.model:
            nodes = self.model.nodes or []
            if nodes:
                with omni.kit.undo.group():
                    for node in nodes:
                        self.model[node].expansion_state = state

    def on_toolbar_onframe_clicked(self):
        pass

    def on_toolbar_addnote_clicked(self):
        pass

    def on_toolbar_view_clicked(self):
        self._context_menu.clear()
        with self._context_menu:
            ui.MenuItem("Layout Nodes", triggered_fn=self.on_layout_clicked, enabled=bool(self.model))
            ui.Separator()
            ui.MenuItem(
                "Frame Selected" if self.model and self._graph_view.selection else "Frame All",
                triggered_fn=self.on_frame_selected_clicked,
                enabled=bool(self.model),
            )  # hotkey_text="F")
            ui.Separator()
            with ui.Menu("Node Header"):
                ui.MenuItem(
                    "Use Prim Name",
                    triggered_fn=partial(self.on_use_prim_name_clicked, False),
                    checkable=True,
                    checked=not graph_config.Settings.get_show_name_as_type(),
                    enabled=bool(self.model),
                )
                ui.MenuItem(
                    "Use Node Type",
                    triggered_fn=partial(self.on_use_prim_name_clicked, True),
                    checkable=True,
                    checked=graph_config.Settings.get_show_name_as_type(),
                    enabled=bool(self.model),
                )
        self._context_menu.show()

    def on_toolbar_edit_clicked(self):
        from omni.graph.ui import SETTING_PAGE_NAME
        from omni.kit.window.preferences import PreferenceBuilder, get_page_list, select_page, show_preferences_window

        def show_visual_scripting_preference():
            pages = get_page_list()
            omni_page = [page for page in pages if page.get_title() == SETTING_PAGE_NAME]
            if len(omni_page) == 1:

                async def show_window_and_focus():
                    select_page(omni_page[0])
                    show_preferences_window()
                    preference_window = ui.Workspace.get_window(PreferenceBuilder.WINDOW_NAME)
                    if preference_window:
                        preference_window.focus()

                self.__show_prefs_task = asyncio.ensure_future(show_window_and_focus())
                assert self.__show_prefs_task  # This is mostly to avoid lint complaints.

        self._context_menu.clear()
        with self._context_menu:
            ui.MenuItem("Preferences...", triggered_fn=show_visual_scripting_preference)
            ui.MenuItem("Delete all unused variables", triggered_fn=self._delete_all_unused_variables)
        self._context_menu.show()

    def _delete_all_unused_variables(self):
        if self._variables_model and hasattr(self._variables_model, "get_variable_instances"):
            for item in self._variables_model.get_item_children(None):
                variable_name = item.value_models[0].as_string
                instances = self._variables_model.get_variable_instances(variable_name)
                if len(instances) == 0:
                    variable = self._variables_model.graph.find_variable(variable_name)
                    og.cmds.RemoveVariable(graph=self._variables_model.graph, variable=variable)

    def on_toolbar_help_clicked(self):
        import webbrowser

        omnigraph_tutorial_url = "https://docs.omniverse.nvidia.com/prod_extensions/prod_extensions/ext_omnigraph.html"
        webbrowser.open(omnigraph_tutorial_url)

    def on_use_prim_name_clicked(self, Value):  # noqa: N803
        graph_config.Settings.set_show_name_as_type(Value)
        self.model._item_changed(None)  # noqa: protected-access

    def on_frame_selected_clicked(self):
        self._graph_view.focus_on_nodes(self._graph_view.selection or [])

    def on_layout_clicked(self):
        with omni.kit.undo.group():
            self._graph_view.layout_all()

    def show_context_menu(self, context_item, pos: Tuple[float, float] | None = None):
        """
        Show the right click context menu. If the context menu is already shown, this will do nothing.

        Args:
            context_item: The item that was right clicked
        """
        current_menu = ui.Menu.get_current()
        if current_menu and current_menu.shown:
            return

        if self.__right_click_context_menu:
            self.__right_click_context_menu.destroy()

        self.__right_click_context_menu = self.__context_menu_class(widget=self, filter_fn=self.__filter_fn)
        self.__right_click_context_menu.build(context_item)
        self.__right_click_context_menu.show(pos)

    def _update_style_for_registered_types(self, style: Dict[str, Any]):
        """Updates the given style dict with information from all registered OG node types
        Args:
            style: The style dict to modify
        """
        for node_type_name in og.get_registered_nodes():
            color, icon_path, second_color = graph_config.CategoryStyles.get_style_for_node_type(node_type_name)
            bg_color = graph_config.CategoryStyles.modify_background_color_for_node_type(node_type_name, color)
            style.update(self._graph_delegate.specialized_color_style(node_type_name, color, icon_path, second_color))
            style.update(
                self._graph_delegate.specialized_expansion_style(
                    node_type_name,
                    graph_config.lerp_abgr_to_secondary(color, graph_config.EXPANSION_ON_COLOR_ABGR),
                    second_color,
                )
            )
            if bg_color is not None:
                style.update({f"Graph.Node.Background::{node_type_name}": {"background_color": bg_color}})

    def __get_graph_node_prim_types(self) -> Tuple[str]:
        """Returns the prim type(s) used to represent OG graphs and subgraphs."""
        if graph_config.Settings.is_schema_prims_enabled():
            return ("OmniGraph",)
        return ("ComputeGraph", "GlobalComputeGraph")

    def __get_prim_types_to_ignore_on_drop(self) -> Tuple[str]:
        """Returns the prim types which should be ignored if dropped onto the OG editor window."""
        if graph_config.Settings.is_schema_prims_enabled():
            return ("OmniGraph", "OmniGraphNode")
        return ("ComputeGraph", "GlobalComputeGraph", "ComputeNode", "ComputeGraphSettings")

    def __on_node_library_changed(self, event: carb.events.IEvent):
        """Callback invoked when node types are added, removed or changed in the node library"""
        # If the node library is changed (e.g. a compound node is added/changed) the node styles are rebuilt
        # to accommodate new styles or category changes
        if self.__rebuild_style_task is None:
            self.__rebuild_style_task = asyncio.ensure_future(self.__delayed_rebuild_style())

    async def __delayed_rebuild_style(self):
        """Rebuilds the style after the next update"""
        await omni.kit.app.get_app().next_update_async()

        style = self.style  # noqa: access-member-before-definition
        self._update_style_for_registered_types(style)
        self.style = style  # noqa: attribute-defined-outside-init

        self.__rebuild_style_task = None

    def _on_graph_event(self, event: og.GraphEvent):
        """Callback that is invoked when omnigraph graph event occurs"""
        if not self.model:
            return

        # If a variable type has changed, or a variable is removed the nodes need to be redrawn.
        # The graph view needs to force-regenerate everything because the data on the nodes
        # has changed, and attempts to detect relevant changes (GraphNodeIndex) will fail
        if event.type in (og.GraphEvent.VARIABLE_TYPE_CHANGE, og.GraphEvent.REMOVE_VARIABLE):
            self._graph_view._force_regenerate = True  # noqa: protected-access
            self.model._item_changed(None)  # noqa: protected-access

    def get_event_stream(self) -> carb.events.IEventStream:
        return self.__event_stream

    # DEPRECATED

    @property
    @ogt.deprecated_function("use 'model' instead")
    def _graph_model(self):
        return self.model

    @_graph_model.setter
    @ogt.deprecated_function("use 'model' instead")
    def _graph_model(self, model):
        self.model = model
