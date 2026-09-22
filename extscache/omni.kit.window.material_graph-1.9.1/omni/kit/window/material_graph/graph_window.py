# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["GraphWindow"]

import asyncio

import omni.kit.app
import omni.ui as ui

from .graph_widget import GraphWidget


class GraphWindow(ui.Window):
    """The Graph window"""

    def __init__(self, title, **kwargs):
        flags = kwargs.pop("flags", 0) | ui.WINDOW_FLAGS_NO_SCROLLBAR
        if hasattr(ui, "WINDOW_FLAGS_NO_SCROLL_WITH_MOUSE"):
            # Compatibility with old omni.ui
            flags = flags | ui.WINDOW_FLAGS_NO_SCROLL_WITH_MOUSE

        self._main_widget = None

        super().__init__(title, flags=flags, **kwargs)

        self.frame.set_build_fn(self.on_build_window)

        self.deferred_dock_in("Content")

    def destroy(self):
        if self._main_widget:
            self._main_widget.destroy()
        self._main_widget = None

        super().destroy()

    def on_build_window(self):
        self._main_widget = GraphWidget()

    def _import_prims(self, _, prims, focus=True):
        """Create a model and set it to the graph view"""

        async def delayed_import():
            # Wait the window is created. Not more than 5 frames.
            counter = 0
            while self._main_widget is None:
                await omni.kit.app.get_app().next_update_async()
                counter += 1
                if counter > 5:
                    return

            await self._main_widget._import_prims(_, prims, focus)

        asyncio.ensure_future(delayed_import())

    def add_node(self, event):
        """Called to create a node that was droppped to the window"""
        if self._main_widget:
            self._main_widget.on_drop(event)
