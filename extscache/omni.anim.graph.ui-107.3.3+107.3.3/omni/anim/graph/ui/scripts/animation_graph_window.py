import carb
import omni.kit.ui
import omni.ui as ui
from omni.kit.graph.editor.core.graph_editor_core_tree_delegate import GraphEditorCoreTreeDelegate
from omni.kit.window.quicksearch import QuickSearchRegistry
from pxr import Usd, Sdf
from .animation_graph_manager import AnimationGraphManager
from .animation_graph_widget import AnimationGraphWidget
from .animation_graph_catalog_model import AnimationGraphCatalogModel, AnimationGraphQuickSearchModel
from .create_animation_graph_dialog import CreateAnimationGraphDialog
from .config import Settings
from typing import Optional
import asyncio


WINDOW_MENU = "Window/Animation/Animation Graph"


class AnimationGraphWindow:
    def __init__(self, graph_manager: AnimationGraphManager, create_graph_dialog: CreateAnimationGraphDialog):
        Settings.set_default_settings()
        window_flags = ui.WINDOW_FLAGS_NO_SCROLLBAR | ui.WINDOW_FLAGS_NO_SCROLL_WITH_MOUSE
        self._window = ui.Window("Animation Graph", width=640, height=600, flags=window_flags, visible=Settings.get_show_window())
        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(WINDOW_MENU, self._on_click, toggle=True, value=Settings.get_show_window())
        self._window.set_visibility_changed_fn(self._visibility_changed_fn)
        self._window.deferred_dock_in("Content")

        self._graph_manager = graph_manager
        self._create_graph_dialog = create_graph_dialog
        self._main_widget: Optional[AnimationGraphWidget] = None

        def can_show_search():
            return self._window.focused and self._main_widget

        def is_blend_tree_catalog():
            return can_show_search() and \
                self._main_widget.catalog_model.graph_type == AnimationGraphCatalogModel.GraphType.BLEND_TREE

        class BlendTreeQuickSearchModel(AnimationGraphQuickSearchModel):
            def __init__(cls):
                super().__init__(self, AnimationGraphCatalogModel.GraphType.BLEND_TREE)

        self._blend_tree_search_sub = QuickSearchRegistry().register_quick_search_model(
            "Blend Tree Nodes",
            BlendTreeQuickSearchModel,
            GraphEditorCoreTreeDelegate,
            accept_fn=is_blend_tree_catalog,
            exclusive_fn=lambda: True
        )

        def is_state_machine_catalog():
            return can_show_search() and \
                self._main_widget.catalog_model.graph_type == AnimationGraphCatalogModel.GraphType.STATE_MACHINE

        class StateMachineQuickSearchModel(AnimationGraphQuickSearchModel):
            def __init__(cls):
                super().__init__(self, AnimationGraphCatalogModel.GraphType.STATE_MACHINE)

        self._state_machine_search_sub = QuickSearchRegistry().register_quick_search_model(
            "State Machine Nodes",
            StateMachineQuickSearchModel,
            GraphEditorCoreTreeDelegate,
            accept_fn=is_state_machine_catalog,
            exclusive_fn=lambda: True
        )

        def is_condition_catalog():
            return can_show_search() and \
                self._main_widget.catalog_model.graph_type == AnimationGraphCatalogModel.GraphType.CONDITION

        class ConditionQuickSearchModel(AnimationGraphQuickSearchModel):
            def __init__(cls):
                super().__init__(self, AnimationGraphCatalogModel.GraphType.CONDITION)

        self._condition_search_sub = QuickSearchRegistry().register_quick_search_model(
            "Condition Nodes",
            ConditionQuickSearchModel,
            GraphEditorCoreTreeDelegate,
            accept_fn=is_condition_catalog,
            exclusive_fn=lambda: True
        )
        self._window.frame.set_build_fn(self._on_build_window)
        self._window.set_key_pressed_fn(self._on_key_pressed)

    def _on_click(self, *args):
        self._window.visible = not self._window.visible

    def _visibility_changed_fn(self, visible):
        omni.kit.ui.get_editor_menu().set_value(WINDOW_MENU, visible)

    @property
    def graph_widget(self):
        return self._main_widget

    def open_graph(self, graph_prim: Usd.Prim, focus_graph_path: Sdf.Path = None):
        self._window.visible = True
        self._window.focus()

        async def open_graph_async(graph_prim: Usd.Prim, focus_graph_path: Sdf.Path = None):
            while(self._main_widget is None):
                await omni.kit.app.get_app().next_update_async()

            self._main_widget.open_graph(graph_prim, focus_graph_path)

        asyncio.ensure_future(open_graph_async(graph_prim, focus_graph_path))

    def destroy(self):
        if self._main_widget:
            self._main_widget.destroy()
        self._main_widget = None
        del self._blend_tree_search_sub
        self._blend_tree_search_sub = None
        del self._state_machine_search_sub
        self._state_machine_search_sub = None
        del self._condition_search_sub
        self._condition_search_sub = None
        self._menu = None
        self._window.destroy()
        self._window = None

    def _on_build_window(self):
        self._main_widget = AnimationGraphWidget(self._graph_manager, self._create_graph_dialog)

    def _on_key_pressed(self, key, mod, pressed):
        """Called when the user presses a key"""
        if not pressed or (mod & ui.Widget.FLAG_WANT_CAPTURE_KEYBOARD):
            return
