# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["StageDelegate"]

from .abstract_stage_column_delegate import AbstractStageColumnDelegate
from .abstract_stage_column_delegate import StageColumnItem
from .delegates import NameColumnDelegate
from .context_menu import ContextMenu
from .stage_icons import StageIcons
from .stage_model import StageItem
from typing import List
from functools import partial

import asyncio
import inspect
import weakref
import omni.ui as ui


class AwaitWithFrame:
    """
    A future-like object that runs the given future and makes sure it's
    always in the given frame's scope. It allows creating widgets
    asynchronously.
    """

    def __init__(self, frame: ui.Frame, future: asyncio.Future):
        self._frame = frame
        self._future = future

    def __await__(self):
        # create an iterator object from that iterable
        iter_obj = iter(self._future.__await__())

        # infinite loop
        while True:
            try:
                with self._frame:
                    yield next(iter_obj)
            except StopIteration:
                break

        self._frame = None
        self._future = None


class ContextMenuEvent:
    """The object comatible with ContextMenu"""

    def __init__(self, stage: "pxr.Usd.Stage", path_string, expanded=None):
        self.type = 0
        self.payload = {"stage": stage, "prim_path": path_string, "node_open": expanded}


class ContextMenuHandler:
    """The object that the ContextMenu calls to expand the item"""

    def __init__(self):
        self._expand_fn = None
        self._collapse_fn = None

    @property
    def expand_fn(self):
        return self._expand_fn

    @expand_fn.setter
    def expand_fn(self, value):
        self._expand_fn = value

    @property
    def collapse_fn(self):
        return self._collapse_fn

    @collapse_fn.setter
    def collapse_fn(self, value):
        self._collapse_fn = value

    def _expand(self, path):
        if self._expand_fn:
            self._expand_fn(path)

    def _collapse(self, path):
        if self._collapse_fn:
            self._collapse_fn(path)

    def context_menu_handler(self, cmd, prim_path):
        if cmd == "opentree":
            self._expand(prim_path)
        elif cmd == "closetree":
            self._collapse(prim_path)


class StageDelegate(ui.AbstractItemDelegate):
    def __init__(self, **kwargs):
        super().__init__()
        self._context_menu = kwargs.get("context_menu", ContextMenu())
        self._context_menu._stage_win = ContextMenuHandler()
        self._column_delegates: List[AbstractStageColumnDelegate] = []
        self._header_layout = None
        self._header_layout_is_hovered = False
        self._mouse_pressed_task = None
        self._on_stage_items_destroyed_sub = None
        self._name_column_delegate = None

    @property
    def model(self):
        return self._stage_model

    @model.setter
    def model(self, value):
        if self._on_stage_items_destroyed_sub:
            self._on_stage_items_destroyed_sub.destroy()
            self._on_stage_items_destroyed_sub = None

        self._stage_model = value
        self._context_menu._stage_model = value
        if self._stage_model:
            self._on_stage_items_destroyed_sub = self._stage_model.subscribe_stage_items_destroyed(
                self.__on_stage_items_destroyed
            )

    def __on_stage_items_destroyed(self, items: List[StageItem]):
        for delegate in self._column_delegates:
            delegate.on_stage_items_destroyed(items)

    @property
    def expand_fn(self):
        return self._context_menu._stage_win.expand_fn

    @expand_fn.setter
    def expand_fn(self, value):
        self._context_menu._stage_win.expand_fn = value

    @property
    def collapse_fn(self):
        return self._context_menu._stage_win.collapse_fn

    @collapse_fn.setter
    def collapse_fn(self, value):
        self._context_menu._stage_win.collapse_fn = value

    def destroy(self):
        if self._on_stage_items_destroyed_sub:
            self._on_stage_items_destroyed_sub.destroy()
            self._on_stage_items_destroyed_sub = None

        self._stage_model = None
        self._context_menu.function_list.pop("rename_item", None)
        self._context_menu.destroy()
        self._context_menu = None
        self._name_column_delegate = None
        for d in self._column_delegates:
            d.destroy()
        self._column_delegates = []

        if self._header_layout:
            self._header_layout.set_mouse_hovered_fn(None)
            self._header_layout = None

        if self._mouse_pressed_task:
            self._mouse_pressed_task.cancel()
            self._mouse_pressed_task = None

    def build_branch(self, model, item, column_id, level, expanded):
        """Create a branch widget that opens or closes subtree"""
        if column_id == 0:
            with ui.HStack(width=20 * (level + 1), height=0):
                ui.Spacer()
                if model.can_item_have_children(item):
                    # Draw the +/- icon
                    image_name = "Minus" if expanded else "Plus"
                    ui.Image(
                        StageIcons().get(image_name), width=10, height=10, style_type_name_override="TreeView.Item"
                    )
                    ui.Spacer(width=5)

    def on_mouse_pressed(self, button, stage: "pxr.Usd.Stage", item, expanded):
        """Called when the user press the mouse button on the item"""
        if button != 1:
            return

        async def show_context_menu(stage: "pxr.Usd.Stage", item, expanded):
            import omni.kit.app

            await omni.kit.app.get_app().next_update_async()

            # menu is for context menu only but don't check in on_mouse_pressed func as it can be out of date
            # check layout_is_hovered here to make sure its updated for current mouse position
            if self._header_layout_is_hovered:
                return

            # Form the event
            path = item.path if item else None
            event = ContextMenuEvent(stage, path, expanded)

            # Show the menu
            self._context_menu.on_mouse_event(event)
            self._mouse_pressed_task = None

        # this function can get called multiple times sometimes with different item values
        if self._mouse_pressed_task:
            self._mouse_pressed_task.cancel()
            self._mouse_pressed_task = None
        self._mouse_pressed_task = asyncio.ensure_future(show_context_menu(stage, item, expanded))

    def build_widget(self, model, item, column_id, level, expanded):
        """Create a widget per item"""
        if column_id >= len(self._column_delegates):
            return

        if item:
            column_item = StageColumnItem(item.path, model.stage, not item.instance_proxy, expanded)
        else:
            column_item = None

        stage = model.stage
        frame = ui.Frame(mouse_pressed_fn=lambda x, y, b, _: self.on_mouse_pressed(b, stage, item, expanded))
        # Name column needs special treatment to build frame synchronously so all items will not be built
        # in the same line.
        if self._name_column_delegate and self._name_column_delegate == self._column_delegates[column_id]:
            with frame:
                self._name_column_delegate.build_widget_sync(column_item, stage_item=item, stage_model=model)
        else:
            # This is for back compatibility of old interface.
            build_widget_func = self._column_delegates[column_id].build_widget
            argspec = inspect.getfullargspec(build_widget_func)
            if not argspec.varkw:
                future = build_widget_func(column_item)
            else:
                future = build_widget_func(column_item, stage_item=item, stage_model=model)
            asyncio.ensure_future(AwaitWithFrame(frame, future))

    def __on_header_hovered(self, hovered):
        self._header_layout_is_hovered = hovered

    def build_header(self, column_id):
        if column_id >= len(self._column_delegates):
            return

        self._header_layout = ui.ZStack()
        self._header_layout.set_mouse_hovered_fn(self.__on_header_hovered)
        with self._header_layout:
            column_delegate = self._column_delegates[column_id]

            if column_delegate.sortable:
                def on_drop_down_hovered(weakref_delegate, hovered):
                    if not weakref_delegate():
                        return

                    weakref_delegate().on_header_hovered(hovered)

                hovered_area = ui.Rectangle(name="hovering", style_type_name_override="TreeView.Header")
                weakref_delegate = weakref.ref(column_delegate)
                hovered_area.set_mouse_hovered_fn(partial(on_drop_down_hovered, weakref_delegate))

            build_header_func = column_delegate.build_header
            argspec = inspect.getfullargspec(build_header_func)
            # This is for back compatibility of old interface.
            if not argspec.varkw:
                build_header_func()
            else:
                build_header_func(stage_model=self.model)

    def set_highlighting(self, enable: bool = None, text: str = None):
        """
        Specify if the widgets should consider highlighting. Also set the text that should be highlighted in flat mode.
        """
        if self._name_column_delegate:
            self._name_column_delegate.set_highlighting(enable, text)

    def set_column_delegates(self, delegates):
        """Add custom columns"""
        self._name_column_delegate = None
        for d in self._column_delegates:
            d.destroy()

        self._column_delegates = delegates
        self._context_menu.function_list.pop("rename_item", None)

        def rename_item(prim_path):
            if not self.model:
                return

            item = self.model.find(prim_path)
            if not item:
                return

            self._name_column_delegate.rename_item(item)

        for delegate in delegates:
            if isinstance(delegate, NameColumnDelegate):
                self._name_column_delegate = delegate
                self._context_menu.function_list["rename_item"] = rename_item

                break

    def get_name_column_delegate(self):
        return self._name_column_delegate
