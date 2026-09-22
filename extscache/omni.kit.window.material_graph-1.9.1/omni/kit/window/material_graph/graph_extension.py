# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["GraphExtension"]

import asyncio
from functools import partial
from pathlib import Path
from typing import Any, List, Optional

import carb
import carb.settings
import omni.client
import omni.ext
import omni.kit.app
import omni.kit.context_menu
import omni.kit.material.library
import omni.ui as ui
from omni.kit.menu.utils import MenuHelperExtensionFull
from omni.kit.widget.graph import GraphModel
from pxr import Sdf, Usd, UsdShade

from . import compound_registry
from .graph_actions import deregister_actions, register_actions
from .graph_hotkeys import deregister_hotkeys, register_hotkeys
from .mdl_node_tree_delegate import MdlNodeTreeDelegate
from .mdl_node_tree_model import MdlNodeTreeQuickSearchModel
from .usdshade_graph_model import UsdShadeGraphModel

CURRENT_PATH = Path(__file__).parent
COMPOUND_DEFAULT_PATH = "${data}/shadergraphs"
MDL_AUTOGEN_PATH = "${data}/shadergraphs/mdl_usd"
# parent.parent.parent.parent is for compatibility with 101
SHADERS_PATH = f"{CURRENT_PATH.parent.parent.parent.parent.joinpath('data/shaders')}"
COMPOUND_PATH_SETTING = "/persistent/exts/omni.kit.window.material_graph/compoundPaths"

_extension_instance = None

from .graph_window import GraphWindow

WINDOW_NAME = "Material Graph"
MENU_GROUP = "Window"


class GraphExtension(omni.ext.IExt, MenuHelperExtensionFull):
    """The entry point for MDL Material Graph"""

    def __init__(self):
        super().__init__()
        self._ext_name = None
        self._hotkey_extension_enabled_hook = None
        self._hotkey_extension_disabled_hook = None

    def on_startup(self, ext_id: str):
        global _extension_instance
        _extension_instance = self

        self._ext_name = omni.ext.get_extension_name(ext_id)

        # Register menu item via menu utils
        self.menu_startup(
            lambda: GraphWindow(WINDOW_NAME, width=600, height=800), WINDOW_NAME, f"MDL {WINDOW_NAME}", MENU_GROUP
        )

        # Register default compounds
        self._compound_subscription = None

        # Register MDLs in Quick Search
        self._sub = None

        self.__extensions_subscription = []
        app = omni.kit.app.get_app_interface()
        ext_manager = app.get_extension_manager()
        quicksearch = "omni.kit.window.quicksearch"
        self.__extensions_subscription.append(
            ext_manager.subscribe_to_extension_enable(
                partial(self._on_extensions_changed, True),
                partial(self._on_extensions_changed, False),
                ext_name=quicksearch,
                hook_name=self._ext_name,
            )
        )

        self.__extensions_subscription.append(
            ext_manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: self._register_stage_menu(),
                on_disable_fn=lambda _: self._unregister_stage_menu(),
                ext_name="omni.kit.widget.stage",
                hook_name=self._ext_name,
            )
        )

        # Hooks to hotkey extension enable/disable
        hooks: omni.ext.IExtensionManagerHooks = ext_manager.get_hooks()

        self._hotkey_extension_enabled_hook = hooks.create_extension_state_change_hook(
            self._on_hotkey_ext_changed,
            omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_ENABLE,
            ext_name="omni.kit.hotkeys.core",
        )
        self._hotkey_extension_disabled_hook = hooks.create_extension_state_change_hook(
            self._on_hotkey_ext_changed,
            omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_DISABLE,
            ext_name="omni.kit.hotkeys.core",
        )

        if hasattr(omni.kit.material.library, "add_material_list_item"):

            def on_create_mdl_graph(mtl_created_list=None, bind_selected_prims=True):
                # don't access self as it causes leaks
                async def create_mdl(extension_instance):
                    bind_prim_paths = omni.usd.get_context().get_selection().get_selected_prim_paths()

                    # show window and wait for widget to be build
                    ui.Workspace.show_window(WINDOW_NAME, True)
                    while True:
                        await omni.kit.app.get_app().next_update_async()
                        if extension_instance._window._main_widget:
                            # ensure that the widget is initialized.
                            await omni.kit.app.get_app().next_update_async()
                            await omni.kit.app.get_app().next_update_async()
                            break

                    extension_instance._window._main_widget._create_new()
                    bind_material = omni.usd.get_context().get_selection().get_selected_prim_paths()
                    if bind_prim_paths:
                        # _create_new() always selects the new material. restore previous selection
                        omni.usd.get_context().get_selection().set_selected_prim_paths(bind_prim_paths, True)
                        if bind_material:
                            for prim_path in bind_prim_paths:
                                omni.kit.commands.execute(
                                    "BindMaterialCommand", prim_path=prim_path, material_path=bind_material
                                )

                asyncio.ensure_future(create_mdl(_extension_instance))

            omni.kit.material.library.add_material_list_item("Create MDL Graph", on_create_mdl_graph)

        register_actions(self._ext_name, _extension_instance)
        register_hotkeys(self._ext_name, WINDOW_NAME)

    def on_shutdown(self):

        global _extension_instance
        _extension_instance = None

        # deregister quick search model
        if self._sub is not None:
            del self._sub
            self._sub = None

        if hasattr(omni.kit.material.library, "remove_material_list_item"):
            omni.kit.material.library.remove_material_list_item("Create MDL Graph")

        self.menu_shutdown()
        self.__extensions_subscription = None
        self._hotkey_extension_enabled_hook = None
        self._hotkey_extension_disabled_hook = None
        self._stage_context_menu = None
        self._thumb_context_menu = None

        if self._sub:
            del self._sub
            self._sub = None

        deregister_hotkeys(self._ext_name)
        deregister_actions(self._ext_name)

        self._compound_subscription = None
        self._ext_name = None

    @staticmethod
    def refresh_compounds():
        """Register default compounds"""

        if not _extension_instance:
            return

        self = _extension_instance
        self._compound_subscription = []

        settings = carb.settings.get_settings()
        compound_custom_paths: List[str] = settings.get(COMPOUND_PATH_SETTING) or []

        paths = [COMPOUND_DEFAULT_PATH, SHADERS_PATH, MDL_AUTOGEN_PATH] + compound_custom_paths
        token = carb.tokens.get_tokens_interface()

        for path in paths:
            compound_path = token.resolve(path)
            (result, entries) = omni.client.list(compound_path)
            if result == omni.client.Result.OK:
                compounds = [
                    e.relative_path
                    for e in entries
                    if e.flags & int(omni.client.ItemFlags.READABLE_FILE)
                    and (e.relative_path.lower().endswith(".usd") or e.relative_path.lower().endswith(".usda"))
                ]
                compounds = [f"{omni.client.combine_urls(compound_path + '/', c)}" for c in compounds]
                self._compound_subscription += [compound_registry.register_compound(c) for c in compounds]

    @staticmethod
    def show_materials(prim_list: List[Usd.Prim]):
        """Show materials in Material Graph window"""
        if not _extension_instance:
            return

        self = _extension_instance

        async def import_prims():
            if self._window == None:
                self.show_window(None, True, 0)
                while True:
                    await omni.kit.app.get_app().next_update_async()
                    if self._window._main_widget:
                        # ensure that the widget is initialized.
                        await omni.kit.app.get_app().next_update_async()
                        await omni.kit.app.get_app().next_update_async()
                        break
            if prim_list:
                self._window._import_prims(UsdShadeGraphModel, prim_list)

        asyncio.ensure_future(import_prims())

    @staticmethod
    def add_node(mime_data: str):
        """Adds a node to the current Material Graph window"""
        if not _extension_instance:
            return

        self = _extension_instance

        if self._window == None:
            return

        class CustomEvent:
            def __init__(self, mime_data):
                self.mime_data = mime_data
                self.x = None
                self.y = None

        self._window.add_node(CustomEvent(mime_data))

    def _on_hotkey_ext_changed(self, ext_id: str, ext_change_type: omni.ext.ExtensionStateChangeType):
        if ext_change_type == omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_ENABLE:
            register_hotkeys(self._ext_name, WINDOW_NAME)

        if ext_change_type == omni.ext.ExtensionStateChangeType.AFTER_EXTENSION_DISABLE:
            deregister_hotkeys(self._ext_name)

    def _visiblity_changed_fn(self, visible):
        # Refresh menu tick state via menu utils helper
        self.menu_refresh()

    def show_window(self, menu, value, index):
        """Show/hide the window"""
        super().show_window(menu, value, index)
        if value:
            self.refresh_compounds()

    def _is_window_focused(self) -> bool:
        """Returns True if the MDL Material Graph window exists and focused"""
        return self._window != None and self._window.focused

    def _on_extensions_changed(self, loaded: bool, ext_id: str):
        """Called when the Quick Search extension is loaded/unloaded"""
        if loaded:
            from omni.kit.window.quicksearch import QuickSearchRegistry

            # Register MDLs in Quick Search
            self._sub = QuickSearchRegistry().register_quick_search_model(
                "MDL Shading Nodes",
                MdlNodeTreeQuickSearchModel,
                MdlNodeTreeDelegate,
                accept_fn=self._is_window_focused,
                exclusive_fn=lambda: True,
                priority=0,
                flat_search=False,
            )
        else:
            # Deregister MDLs in Quick Search
            del self._sub
            self._sub = None

    def _register_stage_menu(self):
        def open_material(objects: dict):
            if not any(item in objects for item in ["prim", "prim_list"]):
                return
            prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]

            # Check if they are material prims, get bound materials if not
            mtl_prim_list = []
            for prim in prim_list:
                if prim.IsA(UsdShade.Material):
                    mtl_prim_list.append(prim)
                else:
                    mb_api = UsdShade.MaterialBindingAPI(prim)
                    mtl_prim, _ = mb_api.ComputeBoundMaterial()
                    mtl_prim_list.append(mtl_prim)

            _extension_instance.show_materials(mtl_prim_list)

        # add context menu to omni.kit.widget.stage
        context_menu = omni.kit.context_menu.get_instance()
        if context_menu:
            menu = {
                "name": "Open in MDL Material Graph",
                "glyph": "menu_material.svg",
                "show_fn": [context_menu.is_prim_selected, context_menu.is_material, context_menu.is_one_prim_selected],
                "onclick_fn": open_material,
                "appear_after": "Select Bound Objects",
            }
            _extension_instance._stage_context_menu = omni.kit.context_menu.add_menu(
                menu, "MENU", "omni.kit.widget.stage"
            )
            _extension_instance._thumb_context_menu = omni.kit.context_menu.add_menu(
                {"name": "Open in MDL Material Graph", "onclick_fn": open_material}, "MENU_THUMBNAIL", ""
            )

    def _unregister_stage_menu(self):
        self._stage_context_menu = None
        self._thumb_context_menu = None

    # Action helper methods

    def layout_all(self):
        if self._window != None:
            self._window._main_widget._graph_view.layout_all()

    def focus_on_nodes(self, nodes: Optional[List[Any]] = None):
        if self._window != None:
            nodes = self._window._main_widget._graph_view.selection
            self._window._main_widget._graph_view.focus_on_nodes(nodes)

    def set_expansion(self, mode: str):
        """Set the expansion mode of all graph nodes to be:
        "open", "minimize", or "close".

        Args:
            mode (str): "open", "minimize", or "close"
        """
        long_mode = None
        if mode == "open":
            long_mode = GraphModel.ExpansionState.OPEN
        elif mode == "minimize":
            long_mode = GraphModel.ExpansionState.MINIMIZED
        elif mode == "close":
            long_mode = GraphModel.ExpansionState.CLOSED
        else:
            carb.log_error("Invalid mode passed to _set_expansion (Options are 'open', 'close' or 'minimize').")

        if self._window != None and long_mode:
            self._window._main_widget._graph_view.set_expansion(long_mode)

    # This is purely a pass-through action, but needed so users can modify hotkeys for a particular window
    def graph_copy(self):
        action = omni.kit.actions.core.get_action_registry().get_action("omni.kit.stage.copypaste", "stage_copy")
        if action:
            action.execute()

    def graph_paste(self):
        if (
            self._window != None
            and self._window._main_widget
            and self._window._main_widget._graph_view
            and self._window._main_widget._graph_view._model
        ):
            parent = self._window._main_widget._graph_view._model._root.GetPath()
            action = omni.kit.actions.core.get_action_registry().get_action("omni.kit.stage.copypaste", "stage_paste")
            if action:
                # Get the mouse position in canvas space
                canvas_pos = None
                if hasattr(self._window._main_widget, "_get_graph_view_hovered_position") and hasattr(
                    self._window._main_widget._graph_view, "screen_to_canvas"
                ):
                    mouse_position = self._window._main_widget._get_graph_view_hovered_position()
                    canvas_pos = self._window._main_widget._graph_view.screen_to_canvas(*mouse_position)

                params = dict(action.parameters)
                if "keep_inputs" in params:
                    action.execute(
                        root=parent, keep_inputs=False, position=canvas_pos, filter_fn=GraphExtension.filter_paste_nodes
                    )
                else:
                    # This is just a fallback until we've completely moved to Kit 105.  At that point we shouldn't
                    # need to have this fallback.
                    action.execute()

    @staticmethod
    def filter_paste_nodes(prim_spec: Sdf.PrimSpec) -> bool:
        """Return True for nodes that are valid to paste into this graph, False if they aren't valid.

        Args:
            prim_spec (Sdf.PrimSpec): PrimSpec to check for validity.

        Returns:
            bool: True for Valid, False for Invalid.
        """
        # Check if it is a graph node
        if prim_spec.typeName in ["OmniGraph", "OmniGraphNode", "ComputeGraph", "NodeGraph", "Shader"]:
            # Then check if it's a graph node that is valid in this graph
            return prim_spec.typeName in ["Shader", "NodeGraph"]

        # Let everything else through, if it's not a Graph node
        return True

    def toggle_material_compilation(self):
        if self._window != None:
            self._window._main_widget.toggle_material_compilation()

    def material_unpause_and_pause(self):
        if self._window != None:
            self._window._main_widget.unpause_and_pause()
