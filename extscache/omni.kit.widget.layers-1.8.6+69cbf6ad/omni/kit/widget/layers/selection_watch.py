# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["SelectionWatch"]
from pxr import Trace, Sdf
from .layer_item import LayerItem
from .prim_spec_item import PrimSpecItem
import weakref
import omni.usd
from carb.eventdispatcher import get_eventdispatcher

class SelectionWatch(object):
    """
    The object that update selection in TreeView when the scene selection is
    changed and updated scene selection when TreeView selection is changed.
    """

    def __init__(self, usd_context, tree_view, tree_view_delegate):
        self._usd_context = usd_context
        self._selection = None
        self._in_selection = False
        self._select_with_command = True
        self._current_selected_layer_item = None
        self._last_selected_prim_paths = []
        self._on_layer_selection_changed_listeners = set([])
        if self._usd_context is not None:
            self._selection = self._usd_context.get_selection()
            self._stage_event_sub = get_eventdispatcher().observe_event(
                observer_name="omni.kit.widget.layers:selection_watch",
                event_name=self._usd_context.stage_event_name(omni.usd.StageEventType.SELECTION_CHANGED),
                on_event=lambda _: self._on_kit_selection_changed()
            )

        self.set_tree_view(tree_view, tree_view_delegate)

    def destroy(self):
        for listener in self._on_layer_selection_changed_listeners:
            listener(None)
        self._on_layer_selection_changed_listeners.clear()
        self._current_selected_layer_item = None
        self._tree_view = None
        self._selection = None
        self._stage_event_sub = None

    @property
    def select_with_command(self):
        return self._select_with_command
    
    @select_with_command.setter
    def select_with_command(self, value):
        self._select_with_command = value

    def set_tree_view(self, tree_view, tree_view_delegate):
        """Replace TreeView that should show the selection"""
        self._tree_view = tree_view
        self._tree_view_delegate = tree_view_delegate
        self._tree_view.set_selection_changed_fn(self._on_widget_selection_changed)
        self._on_kit_selection_changed()

    @Trace.TraceFunction
    def _on_kit_selection_changed(self):
        """Send the selection from Kit to TreeView"""
        if not self._tree_view or self._in_selection:
            return

        # Make sure it's a new selection. It happens that omni.usd sends the same selection twice. No sorting because
        # the order of selection is important.
        prim_paths = self._selection.get_selected_prim_paths()
        if prim_paths == self._last_selected_prim_paths:
            return

        self._last_selected_prim_paths = prim_paths
        sdf_paths = [Sdf.Path(path) for path in prim_paths]

        # Get the selected item and its parents. Expand all the parents of the new selection.
        edit_target, selection = self._tree_view.model.find_all_specs(sdf_paths)
        if selection:
            self._tree_view.set_expanded(edit_target, True, False)
            for item in selection:
                if not item:
                    continue

                parent_item = item.parent
                parent_chain = []
                while parent_item and parent_item != edit_target.absolute_root_spec:
                    parent_chain.append(parent_item)
                    parent_item = parent_item.parent
                
                for parent in reversed(parent_chain):
                    self._tree_view.set_expanded(parent, True, False)

        # Send all of this to TreeView
        self._in_selection = True
        self._tree_view.selection = selection
        self._in_selection = False

    @Trace.TraceFunction
    def _on_widget_selection_changed(self, selection):
        """Send the selection from TreeView to Kit"""
        if self._in_selection:
            return

        if self._tree_view_delegate:
            self._tree_view_delegate.on_selection_changed(selection)

        changed = False
        selected_item = None
        if len(selection) == 1 and isinstance(selection[0], LayerItem):
            selected_item = selection[0]

        if (
            not self._current_selected_layer_item
            or not self._current_selected_layer_item()
            or self._current_selected_layer_item() != selected_item
        ):
            changed = True
            if selected_item:
                self._current_selected_layer_item = weakref.ref(selected_item)
            else:
                self._current_selected_layer_item = None

        if changed:
            for listener in self._on_layer_selection_changed_listeners:
                if self._current_selected_layer_item and self._current_selected_layer_item():
                    listener(self._current_selected_layer_item())
                else:
                    listener(None)

        # Send the selection to Kit
        prim_paths = [item.path.pathString for item in selection if isinstance(item, PrimSpecItem)]
        if prim_paths == self._last_selected_prim_paths:
            return

        self._in_selection = True
        if self._select_with_command:
            omni.kit.commands.execute(
                "SelectPrims", old_selected_paths=self._last_selected_prim_paths,
                new_selected_paths=prim_paths, expand_in_stage=True
            )
        else:
            self._selection.set_selected_prim_paths(prim_paths, False)
        self._in_selection = False
        self._last_selected_prim_paths = prim_paths

    def add_layer_selection_changed_fn(self, fn):
        self._on_layer_selection_changed_listeners.add(fn)

    def remove_layer_selection_changed_fn(self, fn):
        self._on_layer_selection_changed_listeners.discard(fn)

    def get_current_focused_layer_item(self):
        return self._current_selected_layer_item() if self._current_selected_layer_item else None

    def set_current_focused_layer_item(self, layer_item):
        if layer_item:
            self._tree_view.selection = [layer_item]
