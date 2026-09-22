# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

import weakref
from typing import Any, Callable, Tuple

import omni.ext
import omni.graph.core as og
from pxr import Usd

_extension_instance: omni.ext.IExt = None
_registered_stage_openers = weakref.WeakSet()

# -----------------------------------------------------------------------------


class _StageOpenerEntry:
    """Holder of a stage-open entry"""

    def __init__(self, can_open_fn, open_fn, priority):
        self.can_open_fn = can_open_fn
        self.open_fn = open_fn
        self.priority = priority


def register_stage_graph_opener(
    can_open_fn: Callable[[bool], list[Usd.Prim]], open_fn: Callable[[None], list[Usd.Prim]], priority: int = 0
) -> Any:
    """Register a function that can be used to open Graphs of a particular type
    Args:
        can_open_fn: callable that returns True if the given Prims are openable Graphs
        open_fn: callable that opens the given Graph Prims in the editor
        priority: an integer indicating if the given fn should be tried later than others. For example a generic editor
                  should have a larger number so that other more specific editors are checked first.
    Returns:
        A handle that will unregister the function when GC'd
    """
    fn_entry = _StageOpenerEntry(can_open_fn, open_fn, priority)
    _registered_stage_openers.add(fn_entry)
    return fn_entry


# -----------------------------------------------------------------------------


class OmniGraphWindowCoreExtension(omni.ext.IExt):
    """The entry point for the extension"""

    def __init__(self):
        super().__init__()
        self._ext_id = None
        self._ext_name = None
        self._stage_context_menu = None
        self._thumb_context_menu = None
        self.__extensions_subscription = None

    def on_startup(self, ext_id: str):
        global _extension_instance
        self._ext_name = omni.ext.get_extension_name(ext_id)
        self._ext_id = ext_id
        _extension_instance = self

        from .graph_config import Settings

        Settings.set_default_settings()

        app = omni.kit.app.get_app_interface()
        ext_manager = app.get_extension_manager()
        self.__extensions_subscription = []

        self.__extensions_subscription.append(
            ext_manager.subscribe_to_extension_enable(
                on_enable_fn=lambda _: self._register_stage_menu(),
                on_disable_fn=lambda _: self._unregister_stage_menu(),
                ext_name="omni.kit.widget.stage",
                hook_name="omni.graph.window.action listener",
            )
        )

    def on_shutdown(self):
        global _extension_instance
        _extension_instance = None
        _registered_stage_openers.clear()

    def _register_stage_menu(self):
        def get_parent_global_graph_prim(prim):
            prim_path = prim.GetPrimPath()
            if og.is_global_graph_prim(prim_path.pathString):
                return prim
            if og.get_node_by_path(prim_path.pathString):
                prim_path = prim_path.GetParentPath()
                while prim_path:
                    if og.is_global_graph_prim(prim_path.pathString):
                        return prim.GetStage().GetPrimAtPath(prim_path)
                    prim_path = prim_path.GetParentPath()
            return None

        def open_graph(objects: dict):
            graph_prims = []
            prims = [objects["prim"]] if "prim" in objects else objects["prim_list"]
            for prim in prims:
                graph_prim = get_parent_global_graph_prim(prim)
                if graph_prim:
                    graph_prims.append(graph_prim)
            sorted_entries = list(_registered_stage_openers)
            sorted_entries.sort(key=lambda e: e.priority)
            for entry in sorted_entries:
                if entry.can_open_fn(graph_prims):
                    entry.open_fn(graph_prims)
                    return

        # add context menu to omni.kit.widget.stage
        context_menu = omni.kit.context_menu.get_instance()
        if context_menu:

            def is_global_compute_graph_or_node(objects: dict) -> bool:
                """
                Checks if prims are GlobalComputeGraph or a node within a GlobalComputeGraph
                """
                prim_list = [objects["prim"]] if "prim" in objects else objects["prim_list"]
                return all(get_parent_global_graph_prim(prim) for prim in prim_list)

            menu = {
                "name": "Open Graph",
                "glyph": "folder_open.svg",  # FIXME with a better graph icon
                "show_fn": [
                    context_menu.is_prim_selected,
                    context_menu.is_one_prim_selected,
                    is_global_compute_graph_or_node,
                ],
                "onclick_fn": open_graph,
                "appear_after": "Export Selected",
            }
            _extension_instance._stage_context_menu = omni.kit.context_menu.add_menu(  # noqa: protected-access
                menu, "MENU", "omni.kit.widget.stage"
            )
            _extension_instance._thumb_context_menu = omni.kit.context_menu.add_menu(  # noqa: protected-access
                {"name": "Open in Omni Graph", "onclick_fn": open_graph}, "MENU_THUMBNAIL", ""
            )

    def _unregister_stage_menu(self):
        self._stage_context_menu = None
        self._thumb_context_menu = None


def _is_kit_version_or_greater(version: Tuple[int, int]) -> bool:
    """Compares the running version of Kit to the given version and returns True if the running"""
    kit_version = og.get_kit_version()
    major = version[0]
    minor = version[1]
    return kit_version[0] > major or (kit_version[0] == major and kit_version[1] >= minor)
