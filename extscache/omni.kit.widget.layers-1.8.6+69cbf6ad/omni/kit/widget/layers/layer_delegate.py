# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import weakref

from .prim_spec_item import PrimSpecItem
from .layer_item import LayerItem
from .layer_icons import LayerIcons
from .layer_widgets import build_layer_widget, build_prim_spec_widget
from .layer_model_utils import LayerModelUtils
from .context_menu import ContextMenu, ContextMenuEvent
from pathlib import Path
from omni import ui

CURRENT_PATH = Path(__file__).parent
ICON_PATH = CURRENT_PATH.parent.parent.parent.parent.joinpath("icons")


def on_mouse_pressed(button, context_menu: weakref, item: weakref, expanded):
    """Called when the user press the mouse button on the item"""
    if button != 1:
        # It's for context menu only
        return

    if not context_menu() or not item():
        return

    # Form the event
    event = ContextMenuEvent(item, expanded)

    # Show the menu
    context_menu().on_mouse_event(event)


class LayerDelegate(ui.AbstractItemDelegate):
    def __init__(self, usd_context):
        super().__init__()

        self._usd_context = usd_context
        self._context_menu = ContextMenu(self._usd_context)
        self._tree_view = None
        self._initialized = False
        self._last_selected_layer_items = []

    def on_stage_attached(self):
        self._initialized = False

    def destroy(self):
        self._last_selected_layer_items.clear()

    def set_tree_view(self, tree_view: ui.TreeView):
        self._tree_view = weakref.ref(tree_view)
        self._context_menu.tree_view = self._tree_view
        
        def _on_mouse_pressed(x, y, button, c):
            if button != 1:
                # It's for context menu only
                return

            if not self._context_menu:
                return
            
            treeview = self._tree_view()
            if not tree_view:
                return
            
            root_layer_item = treeview.model.root_layer_item
            if not LayerModelUtils.can_edit_sublayer(root_layer_item):
                return

            # Form the event
            event = ContextMenuEvent(None, False)
            self._context_menu.on_mouse_event(event)

        if self._tree_view():
            self.on_selection_changed(self._tree_view().selection)
            self._tree_view().set_mouse_pressed_fn(_on_mouse_pressed)

    def on_selection_changed(self, selection):
        for item in self._last_selected_layer_items:
            if item():
                item().selected = False
        
        self._last_selected_layer_items.clear()
        for item in selection:
            if isinstance(item, LayerItem):
                item.selected = True
                self._last_selected_layer_items.append(weakref.ref(item))

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""
        if not isinstance(item, PrimSpecItem) and not isinstance(item, LayerItem):
            return

        if column_id == 0:
            is_layer_item = isinstance(item, LayerItem)
            if model.can_item_have_children(item):
                if is_layer_item:
                    if not item.is_live_session_layer or not item.is_in_live_session:
                        background_height = 28
                    else:
                        background_height = 30

                    with ui.ZStack(height=32):
                        with ui.VStack():
                            if not item.is_in_live_session:
                                ui.Spacer()

                            with ui.HStack(height=background_height):
                                ui.Spacer(width=4)
                                if item.selected:
                                    ui.Rectangle(name="selected")
                                else:
                                    ui.Rectangle(name="normal")
                                
                            if not item.is_live_session_layer:
                                ui.Spacer()

                        if item.is_live_session_layer:
                            with ui.VStack():
                                ui.Spacer()
                                with ui.HStack(height=1):
                                    ui.Spacer(width=4)
                                    ui.Line(style={"color": 0xFF606060})

                        with ui.VStack(height=32):
                            ui.Spacer()
                            with ui.HStack(width=16 * (level + 2), height=0):
                                ui.Spacer()
                                # Draw the +/- icon
                                image_name = "Minus" if expanded else "Plus"
                                ui.Image(
                                    LayerIcons().get(image_name), width=10, height=10, style_type_name_override="LayerView.Item"
                                )
                                ui.Spacer(width=4)
                            ui.Spacer()
                else:
                    with ui.HStack(width=16 * (level + 2), height=0):
                        ui.Spacer()
                        # Draw the +/- icon
                        image_name = "Minus" if expanded else "Plus"
                        ui.Image(
                            LayerIcons().get(image_name), width=10, height=10, style_type_name_override="LayerView.Item"
                        )
                        ui.Spacer(width=4)
            elif is_layer_item:
                if not item.is_live_session_layer or not item.is_in_live_session:
                    background_height = 28
                else:
                    background_height = 30

                with ui.ZStack(height=32):
                    with ui.VStack():
                        if not item.is_in_live_session:
                            ui.Spacer()

                        with ui.HStack(height=background_height):
                            ui.Spacer(width=4)
                            if item.selected:
                                ui.Rectangle(name="selected")
                            else:
                                ui.Rectangle(name="normal")
                        
                        if not item.is_live_session_layer:
                            ui.Spacer()

                    if item.is_live_session_layer:
                        with ui.VStack():
                            ui.Spacer()
                            with ui.HStack(height=1):
                                ui.Spacer(width=4)
                                ui.Line(style={"color": 0xFF606060})

                    with ui.HStack(width=16 * (level + 2), height=0):
                        ui.Spacer()
            else:
                with ui.HStack(width=16 * (level + 2), height=0):
                    ui.Spacer()

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per item"""
        if isinstance(item, PrimSpecItem):
            widget = ui.ZStack(height=0)
            with widget:
                build_prim_spec_widget(self._context_menu, model, item, column_id, expanded)
        elif isinstance(item, LayerItem):
            if not self._initialized and self._tree_view() and item == model.root_layer_item:
                self._initialized = True
                self._tree_view().set_expanded(item, True, False)
            
            if not item.is_live_session_layer or not item.is_in_live_session:
                background_height = 28
            else:
                background_height = 30

            widget = ui.ZStack(height=32)
            with widget:
                with ui.VStack():
                    if not item.is_in_live_session:
                        ui.Spacer()
                    if item.selected:
                        ui.Rectangle(name="selected", height=background_height)
                    else:
                        ui.Rectangle(name="normal", height=background_height)
                    # TRICK to bound live session layer and base layer together visually
                    if not item.is_live_session_layer:
                        ui.Spacer()
                
                if item.is_live_session_layer:
                    with ui.VStack():
                        ui.Spacer()
                        ui.Line(height=1, style={"color": 0xFF606060})

                with ui.VStack(height=32):
                    ui.Spacer()
                    with ui.HStack(height=20, identifier="layer_widget"):
                        build_layer_widget(self._context_menu, model, item, column_id, expanded)
                    ui.Spacer()
        else:
            widget = None
        
        if widget:
            weakref_menu = weakref.ref(self._context_menu)
            weakref_item = weakref.ref(item)
            widget.set_mouse_pressed_fn(
                lambda x, y, b, _: on_mouse_pressed(b, weakref_menu, weakref_item, expanded)
            )

    def build_header(self, column_id):
        pass

    def set_highlighting(self, enable: bool = None, text: str = None):
        pass
