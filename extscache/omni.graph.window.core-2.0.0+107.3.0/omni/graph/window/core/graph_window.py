# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["OmniGraphWindow"]

import asyncio
from typing import List

import omni.kit.app
import omni.ui as ui
from pxr import Usd

from .graph_widget import OmniGraphWidget


class OmniGraphWindow(ui.Window):
    """The Graph window"""

    def __init__(self, title, **kwargs):
        flags = kwargs.pop("flags", 0) | ui.WINDOW_FLAGS_NO_SCROLLBAR
        if hasattr(ui, "WINDOW_FLAGS_NO_SCROLL_WITH_MOUSE"):
            # Compatibility with old omni.ui
            flags = flags | ui.WINDOW_FLAGS_NO_SCROLL_WITH_MOUSE

        # OM-79384 hack to fix failing tests, see release notes for 1.44.1
        self.createWidgetFunc = kwargs.pop("createWidgetFunc", OmniGraphWidget)
        self._main_widget = None
        self.__import_task = None
        self._filter_fn = kwargs.pop("filter_fn", None)

        super().__init__(title, flags=flags, **kwargs)

        self.frame.set_build_fn(self.on_build_window)

        self.deferred_dock_in("Content")

    def destroy(self):
        if self._main_widget:
            self._main_widget.destroy()
        if self.__import_task:
            self.__import_task.cancel()
        self.__import_task = None
        self._main_widget = None

        super().destroy()

    def on_build_window(self):
        self._main_widget = self.createWidgetFunc()

    def _import_prims(self, _, prims: List[Usd.Prim], focus=True):
        """Create a model and set it to the graph view"""

        async def delayed_import():
            # Wait the window is created. Not more than 5 frames.
            counter = 0
            while self._main_widget is None:
                await omni.kit.app.get_app().next_update_async()
                counter += 1
                if counter > 5:
                    return

            self._main_widget._import_prims(_, prims, focus)  # noqa: protected-access

        self.__import_task = asyncio.ensure_future(delayed_import())
