from typing import Callable, List, Optional

import omni.kit.actions.core
from pxr import Sdf, Usd

from .graph_model import OmniGraphModel
from .graph_view import OmniGraphView
from .graph_window import OmniGraphWidget, OmniGraphWindow
from .virtual_node_helper import VirtualNodeHelper


class OmniGraphActions:
    """
    Default actions used in menus and hotkeys by OmniGraph editors.

    Each extension wanting to use these actions must create its own instance
    of the class and call its destroy() method when it is no longer needed.
    """

    # Action names
    LAYOUT_NODES = "og_layout_nodes"
    FRAME_NODES = "og_frame_nodes"
    DUPLICATE_SELECTION = "og_duplicate_selection"
    COPY_NODES = "og_copy_nodes"
    PASTE_NODES = "og_paste_nodes"

    def __init__(self, extension_id: str, filter_fn: Optional[Callable[[Sdf.Path, Sdf.PrimSpec], bool]] = None):
        self._extension_id = extension_id
        self._filter_fn = filter_fn
        self._window = None

        action_registry = omni.kit.actions.core.get_action_registry()
        actions_tag = "OmniGraph Actions"

        action_registry.register_action(
            self._extension_id,
            OmniGraphActions.LAYOUT_NODES,
            self.layout_nodes,
            display_name="Layout Nodes",
            description="Layout all nodes in the graph.",
            tag=actions_tag,
        )

        action_registry.register_action(
            self._extension_id,
            OmniGraphActions.FRAME_NODES,
            self.frame_nodes,
            display_name="Frame Nodes",
            description="Fit graph view to selected nodes, or all nodes if none selected.",
            tag=actions_tag,
        )

        action_registry.register_action(
            self._extension_id,
            OmniGraphActions.DUPLICATE_SELECTION,
            self.duplicate_selection,
            display_name="Duplicate Selection",
            description="Duplicate selected nodes.",
            tag=actions_tag,
        )

        action_registry.register_action(
            self._extension_id,
            OmniGraphActions.COPY_NODES,
            self.graph_copy,
            display_name="Graph Copy",
            description="Copy nodes to the clipboard.",
            tag=actions_tag,
        )

        action_registry.register_action(
            self._extension_id,
            OmniGraphActions.PASTE_NODES,
            self.graph_paste,
            display_name="Graph Paste",
            description="Paste nodes from the clipboard.",
            tag=actions_tag,
        )

    def destroy(self):
        if self._extension_id:
            self._window = None
            action_registry = omni.kit.actions.core.get_action_registry()
            action_registry.deregister_all_actions_for_extension(self._extension_id)
            self._extension_id = None

    def _get_model(self) -> OmniGraphModel:
        view = self._get_view()
        return view._model if view else None  # noqa: protected-access

    def _get_view(self) -> OmniGraphView:
        widget = self._get_widget()
        return widget._graph_view if widget else None  # noqa: protected-access

    def _get_widget(self) -> OmniGraphWidget:
        return (
            self._window._main_widget if self._window and self._window._main_widget else None  # noqa: protected-access
        )

    def set_window(self, window: OmniGraphWindow):
        """Set the graph window instance on which actions should operate. Set to None to disable actions."""
        self._window = window

    # Action Functions

    def layout_nodes(self):
        view = self._get_view()
        if view:
            view.layout_all()

    def frame_nodes(self):
        view = self._get_view()
        if view:
            selection = view.selection
            nodes: List[Usd.Prim] = selection
            view.focus_on_nodes(nodes)

    def duplicate_selection(self):
        view = self._get_view()
        if view:
            selection = view.selection
            selection = [p for p in selection if not VirtualNodeHelper.is_virtual_node(p)]
            paths: List[str] = [prim.GetPath().pathString for prim in selection]
            if paths:
                omni.kit.commands.execute("CopyPrims", paths_from=paths)

    # This is purely a pass-through action, but needed so users can modify hotkeys for a particular window
    def graph_copy(self):
        action = omni.kit.actions.core.get_action_registry().get_action("omni.kit.stage.copypaste", "stage_copy")
        if action:
            action.execute()

    def graph_paste(self):
        model = self._get_model()
        if model:
            parent = model._root.GetPath()  # noqa: protected-access
            action = omni.kit.actions.core.get_action_registry().get_action("omni.kit.stage.copypaste", "stage_paste")
            if action:
                widget = self._get_widget()
                view = self._get_view()

                # Get the mouse position in canvas space
                canvas_pos = None
                if hasattr(widget, "_get_graph_view_hovered_position") and hasattr(view, "screen_to_canvas"):
                    mouse_position = widget._get_graph_view_hovered_position()  # noqa: protected-access
                    canvas_pos = view.screen_to_canvas(*mouse_position)

                params = dict(action.parameters)
                if "keep_inputs" in params:

                    def filter_wrapper(prim_spec):
                        return self._filter_fn(parent, prim_spec) if self._filter_fn else True

                    action.execute(root=parent, keep_inputs=False, position=canvas_pos, filter_fn=filter_wrapper)
                else:
                    # This is just a fallback until we've completely moved to Kit 105.  At that point we shouldn't
                    # need to have this fallback.
                    action.execute()
