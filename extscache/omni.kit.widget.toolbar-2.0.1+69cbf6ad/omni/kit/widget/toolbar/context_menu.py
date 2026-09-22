# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ContextMenu", "ContextMenuEvent"]

import carb
from omni import ui
import omni.kit.context_menu


class ContextMenuEvent:
    """The object compatible with ContextMenu"""

    def __init__(self):
        self.type = 0
        self.payload = {}


class ContextMenu:
    def on_mouse_event(self, event):
        import omni.kit.menu.core

        # check its expected event
        if event.type != int(omni.kit.menu.core.MenuEventType.ACTIVATE):
            return

        # get context menu core functionality & check its enabled
        context_menu = omni.kit.context_menu.get_instance()
        if context_menu is None:
            carb.log_error("context_menu is disabled!")
            return

        # setup objects, this is passed to all functions
        objects = {}
        objects.update(event.payload)

        widget_name = objects.get("widget_name", None)

        menu_list = omni.kit.context_menu.get_menu_dict(widget_name, "omni.kit.widget.toolbar")
        # because we moved separated the widget from the window extension, we need to still grab the menu from
        # the window extension
        menu_list_backward_compatible = omni.kit.context_menu.get_menu_dict(widget_name, "omni.kit.window.toolbar")
        for menu_list_backward in menu_list_backward_compatible:
            if menu_list_backward not in menu_list:
                menu_list.append(menu_list_backward)

        # For some tool buttons, the context menu only shows if additional (>1) menu entries are added.
        min_menu_entries = event.payload.get("min_menu_entries", 0)

        # show menu
        context_menu.show_context_menu("toolbar", objects, menu_list, min_menu_entries, delegate=ui.MenuDelegate())
