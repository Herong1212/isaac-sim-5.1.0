# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["MenuBarViewportLayer"]

import weakref
import omni.ui as ui
from .viewport_menu_model import ViewportMenuModel
from .menu_item.viewport_menu_item import ViewportMenuItem
from .menu_item.viewport_menubar_item import ViewportMenubar


class MenuBarViewportLayer:
    def __init__(self, factory_args, *ui_args, **ui_kwargs):
        self._model = ViewportMenuModel()
        self._sub = self._model.subscribe_item_changed_fn(self._menu_changed)
        super().__init__()

        # Store the factory arguments (we are passed a unique copy that is ours to mutate)
        self.__factory_args = factory_args
        ui_kwargs["build_fn"] = self._build_fn

        # Remove height = 0 to make bottom alignment work
        self.__ui_frame = ui.Frame(*ui_args, **ui_kwargs)
        self.__factory_args['root_menu_layer'] = weakref.proxy(self.__ui_frame)

    def destroy(self):
        if self.__ui_frame:
            self.__ui_frame.destroy()
            self.__ui_frame = None

        self._sub = None

    def _build_fn(self):
        menubar_items = self._model.get_item_children()
        with ui.ZStack():
            # Create menubars
            for item in menubar_items:
                if isinstance(item, ViewportMenubar):
                    if not item.visible_model.as_bool:
                        continue

                    menu_items = self._model.get_item_children(item)
                    item.build_fn(menu_items, self.__factory_args)

    def _menu_changed(self, model: ViewportMenuModel, item: ViewportMenuItem) -> None:
        if self.__ui_frame is not None:
            self.__ui_frame.rebuild()

    @property
    def name(self):
        return "Menubar"

    @property
    def categories(self):
        return ("menubar", "menu")

    @property
    def layers(self):
        return ()

    @property
    def visible(self):
        return self.__ui_frame.visible if self.__ui_frame else False

    @visible.setter
    def visible(self, visible: bool):
        if self.__ui_frame:
            self.__ui_frame.visible = bool(visible)
