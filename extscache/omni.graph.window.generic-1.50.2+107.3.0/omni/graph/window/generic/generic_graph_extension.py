# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["GenericGraphExtension"]

import asyncio
from contextlib import suppress
from functools import lru_cache, partial
from typing import List

import carb.windowing
import omni.appwindow
import omni.client
import omni.ext
import omni.graph.core as og
import omni.kit.app
import omni.kit.notification_manager as nm
import omni.kit.ui
import omni.ui as ui
from omni.graph.ui import add_create_menu_type, remove_create_menu_type
from omni.graph.window.core import (
    OmniGraphActions,
    OmniGraphCatalogTreeDelegate,
    OmniGraphHotkeys,
    graph_config,
    register_stage_graph_opener,
)
from pxr import Sdf, Usd

from .generic_catalog_model import OmniGraphNodeQuickSearchModel
from .generic_graph_window import GenericGraphWindow

_extension_instance = None


@lru_cache
def _get_windowing() -> carb.windowing.IWindowing:
    return carb.windowing.acquire_windowing_interface()


class GenericGraphExtension(omni.ext.IExt):
    """The entry point for the extension"""

    WINDOW_NAME = "Generic Graph"
    MENU_PATH = "Window/Visual Scripting/Generic Graph"

    def __init__(self):
        super().__init__()
        self._window = None
        self._menu = None
        self._actions = None
        self._hotkeys = None
        self.__extensions_subscription = None

        # Position of cursor when Quick Search window was launched
        self._quicksearch_pos = None
        # Quick Search subscription
        self._quicksearch_sub = None
        # Stage Opener subscription
        self._stage_opener_sub = None

    def on_startup(self, ext_id: str):
        global _extension_instance
        _extension_instance = self
        self._window = None
        self._menu = None
        self._quicksearch_sub = None
        self._quicksearch_pos = (None, None)
        self._stage_opener_sub = None

        # Use the default OG actions and hotkeys, unmodified.
        self._actions = OmniGraphActions(ext_id, filter_fn=self._make_paste_filter())
        self._hotkeys = OmniGraphHotkeys(ext_id, GenericGraphExtension.WINDOW_NAME)

        add_create_menu_type("Push Graph", "push", "PushGraph", "push_graph.svg", GenericGraphExtension.show_graph)
        add_create_menu_type(
            "Lazy Graph", "dirty_push", "LazyGraph", "lazy_graph.svg", GenericGraphExtension.show_graph
        )
        ui.Workspace.set_show_window_fn(GenericGraphExtension.WINDOW_NAME, partial(self._menu_show_window, None))

        editor_menu = omni.kit.ui.get_editor_menu()
        if editor_menu:
            self._menu = editor_menu.add_item(
                GenericGraphExtension.MENU_PATH, self._menu_show_window, toggle=True, value=False
            )

        app = omni.kit.app.get_app_interface()
        ext_manager = app.get_extension_manager()
        self.__extensions_subscription = []

        self.__extensions_subscription.append(
            ext_manager.subscribe_to_extension_enable(
                partial(self._on_extensions_changed, True),
                partial(self._on_extensions_changed, False),
                ext_name="omni.kit.window.quicksearch",
                hook_name="omni.graph.window.generic listener",
            )
        )

        self._stage_opener_sub = self._register_for_stage_open()

    def on_shutdown(self):
        global _extension_instance
        _extension_instance = None

        remove_create_menu_type("Push Graph")
        remove_create_menu_type("Lazy Graph")

        ui.Workspace.set_show_window_fn(GenericGraphExtension.WINDOW_NAME, None)
        self.__extensions_subscription = None

        if self._hotkeys:
            self._hotkeys.destroy()
            self._hotkeys = None

        if self._actions:
            self._actions.destroy()
            self._actions = None

        self._menu = None
        if self._window is not None:
            self._window.destroy()
            self._window = None

        # deregister quick search model
        if self._quicksearch_sub is not None:
            self._quicksearch_sub = None

        self._stage_opener_sub = None

    def _menu_show_window(self, menu, value):
        self.show_window(menu, value)

    async def _show_window_async(self):
        # It takes 2 ticks before the window is ready to receive focus.
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        self._window.focus()

    async def _destroy_window_async(self):
        # wait one frame, this is due to the one frame defer in Window::_moveToMainOSWindow()
        await omni.kit.app.get_app().next_update_async()
        if self._window:
            self._window.destroy()
            self._window = None
        if self._actions:
            self._actions.set_window(None)

    def _visibility_changed_fn(self, visible):
        if self._menu:
            omni.kit.ui.get_editor_menu().set_value(GenericGraphExtension.MENU_PATH, visible)
            self.show_window(None, visible)

    def show_window(self, menu, value):
        """Show/hide the window"""
        if value:
            self._window = GenericGraphWindow(
                GenericGraphExtension.WINDOW_NAME,
                width=600,
                height=800,
                filter_fn=self._make_paste_filter(),
            )
            if self._actions:
                self._actions.set_window(self._window)
            self._window.set_visibility_changed_fn(self._visibility_changed_fn)
            asyncio.ensure_future(self._show_window_async())
        else:
            asyncio.ensure_future(self._destroy_window_async())

        # update menu state
        if self._menu:
            omni.kit.ui.get_editor_menu().set_value(GenericGraphExtension.MENU_PATH, value)

    @staticmethod
    def show_graph(prim_list: List[Usd.Prim]):
        """Show graph in Omni Graph window"""
        if not _extension_instance:
            return

        self = _extension_instance

        async def import_prims():
            if not self._window:  # noqa: protected-access
                self.show_window(None, True)
            else:
                self._window.focus()  # noqa: protected-access

            if prim_list:
                self._window._import_prims(None, prim_list)  # noqa: protected-access

        asyncio.ensure_future(import_prims())

    def _on_extensions_changed(self, loaded: bool, ext_id: str):
        """Called when the Quick Search extension is loaded/unloaded"""
        if loaded:
            from omni.kit.window.quicksearch import QuickSearchRegistry

            # create the tree item style for the quick search
            def specialized_color_style(name, color):
                nstyle = {f"Graph.Node.Category::{name}": {"background_color": color}}
                return nstyle

            style = {
                # default node color
                "Graph.Node.Category": {"background_color": 0xFFADFB47},
                # background color
                "Graph.Node.Icon.Background": {"background_color": 0xFF31291E},
            }
            # node color by category
            for name, info in graph_config.CategoryStyles.STYLE_BY_CATEGORY.items():
                style.update(specialized_color_style(name, info[0]))
            with suppress(TypeError):  # FIXME: can remove when quicksearch 2.1 is published
                # Register Omni Graph Generic nodes in Quick Search
                self._quicksearch_sub = QuickSearchRegistry().register_quick_search_model(
                    "Omni Graph Generic nodes",
                    OmniGraphNodeQuickSearchModel,
                    OmniGraphCatalogTreeDelegate,
                    accept_fn=self._is_window_focused,
                    exclusive_fn=lambda: True,
                    priority=0,
                    flat_search=False,
                    style=style,
                )
        else:
            # Deregister Omni Graph Generic nodes in Quick Search
            self._quicksearch_sub = None

    def _make_paste_filter(self):
        return lambda graph_path, prim_spec: self._filter_paste_nodes(graph_path, prim_spec)  # noqa:PLW0108

    def _filter_paste_nodes(self, graph_path: Sdf.Path, prim_spec: Sdf.PrimSpec) -> bool:
        """Return True for nodes that are valid to paste into this graph, False if they aren't valid.

        Args:
            graph_path (Sdf.Path): Path to the target graph
            prim_spec (Sdf.PrimSpec): PrimSpec to check for validity.

        Returns:
            bool: True for Valid, False for Invalid.
        """
        if prim_spec.typeName != "OmniGraphNode":
            return False

        graph = omni.graph.core.get_graph_by_path(str(graph_path))
        if graph is None:
            nm.post_notification(
                f"Pasting error: Graph {str(graph_path)} does not exist",
                status=nm.NotificationStatus.WARNING,
                duration=5,
            )
            return False

        # TODO: When pasting a lot of nodes at once, the variables should be cached
        varnames = {var.name for var in graph.get_variables()}
        if "inputs:variableName" in prim_spec.properties:
            depvar = prim_spec.properties["inputs:variableName"].default
            if depvar is not None and depvar != "" and depvar not in varnames:
                nm.post_notification(
                    f'Variable "{depvar}" does not exist in the pasted graph. Graph will not work until this is fixed',
                    status=nm.NotificationStatus.WARNING,
                    duration=5,
                )

        catalog = self._window._main_widget._catalog_model  # noqa: protected-access
        node_type = prim_spec.properties["node:type"].default
        if catalog.allow_node_type(node_type):
            return True

        nm.post_notification(
            f"Cannot paste incompatible node {prim_spec.path} (type {node_type}) into Generic Graph",
            status=nm.NotificationStatus.WARNING,
            duration=5,
        )
        return False

    def _is_window_focused(self) -> bool:
        """Returns True if the OmniGraph generic graph window exists and has focus"""
        if self._window and self._window.focused:
            # Save the position of the pointer so that we can put the created node there.
            windowing = _get_windowing()
            app_window = omni.appwindow.get_default_app_window()
            self._quicksearch_pos = windowing.get_cursor_position(app_window.get_window())

            # Workaround for OM-99274. See note in action_catalog_model.py.
            OmniGraphNodeQuickSearchModel._node_created = False  # noqa: protected-access
            return True

        self._quicksearch_pos = (None, None)
        return False

    @staticmethod
    def add_node(mime_data: str, is_drop: bool = True):
        """Adds a node to the current Graph window"""
        if not _extension_instance:
            return

        self = _extension_instance
        if not self._window:  # noqa: protected-access
            return

        class CustomEvent:
            def __init__(self, mime_data):
                self.mime_data = mime_data
                # If this is a drop from an actual drag, use the current pointer position. Otherwise this has been
                # triggered by selecting a QuickSearch entry, in which case we want to use the position of the
                # pointer when the QuickSearch window was summoned.
                if is_drop:
                    self.x = None
                    self.y = None
                else:
                    self.x = _extension_instance._quicksearch_pos[0]
                    self.y = _extension_instance._quicksearch_pos[1]

        if self._window._main_widget:  # noqa: protected-access
            self._window._main_widget.on_drop(CustomEvent(mime_data))  # noqa: protected-access

    @staticmethod
    def _register_for_stage_open():
        """Register ourselves as an opener for any graphs"""

        def can_open(prims: List[Usd.Prim]):
            if prims:
                first_prim = prims[0]
                graph = og.get_graph_by_path(first_prim.GetPrimPath().pathString)
                return bool(graph)
            return False

        return register_stage_graph_opener(can_open, GenericGraphExtension.show_graph, 1000)
