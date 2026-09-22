# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = []

import carb
from omni import ui

from .prim_selection_payload import PrimSelectionPayload


class ContextMenuEvent:
    """The object compatible with ContextMenu"""

    def __init__(self, payload: PrimSelectionPayload, menu_items: list, xpos: int, ypos: int, delegate=None):
        self.menu_items = menu_items
        self.payload = payload
        self.type = 0
        self.xpos = xpos
        self.ypos = ypos
        self.delegate = delegate


class ContextMenu:
    """
    Context menu.
    """

    def __init__(self):
        """
        Initialize the context menu.
        """
        self._menu_delegate = ui.MenuDelegate()

    def on_mouse_event(self, event: ContextMenuEvent):
        """
        On mouse event.

        Args:
            event (ContextMenuEvent): The event.
        """
        # pylint: disable=protected-access
        import omni.kit.menu.core

        # check its expected event
        if event.type != int(omni.kit.menu.core.MenuEventType.ACTIVATE):  # pragma: no cover
            return

        # setup objects, this is passed to all functions
        objects = {
            "stage": event.payload.get_stage(),
            "prim_list": event.payload,
            "menu_xpos": event.xpos,
            "menu_ypos": event.ypos,
        }

        menu_list = []

        for item in event.menu_items:
            parts = item.path.split("/")
            if len(parts) < 2:
                menu_list.append(item.get_dict(event.payload))
            else:
                last_name = parts.pop()
                first_name = parts.pop(0)

                menu_sublist = None
                for menu_item in menu_list:
                    if first_name in menu_item["name"]:
                        menu_sublist = menu_item["name"][first_name]
                        break

                if menu_sublist is None:
                    menu_list.append({"glyph": item.glyph, "name": {first_name: []}})
                    menu_sublist = menu_list[-1]["name"][first_name]

                for part in parts:
                    sublist = None
                    for menu_item in menu_sublist:
                        if part in menu_item["name"]:
                            sublist = menu_item["name"][part]
                            break

                    if sublist is None:
                        menu_sublist.append({"glyph": item.glyph, "name": {part: []}})
                        menu_sublist = menu_sublist[-1]["name"][part]
                    else:
                        menu_sublist = sublist

                menu_sublist.append(item.get_dict(event.payload, last_name))

        # show menu
        self.show_context_menu(objects=objects, menu_list=menu_list, delegate=event.delegate)

    def show_context_menu(self, objects: dict = None, menu_list: list = None, delegate=None):
        """
        Shows the context menu.

        Args:
            objects (dict): The objects to pass to the context menu.
            menu_list (list): The menu list to pass to the context menu.
        """
        import omni.kit.widget.context_menu

        # get context menu core functionality & check its enabled
        context_menu = omni.kit.widget.context_menu.get_instance()
        if context_menu is None:  # pragma: no cover
            carb.log_warn("context_menu is disabled!")
            return
        context_menu.show_context_menu(
            "prim_path_widget",
            objects if objects else {},
            menu_list if menu_list else [],
            delegate=delegate if delegate else self._menu_delegate,
        )
