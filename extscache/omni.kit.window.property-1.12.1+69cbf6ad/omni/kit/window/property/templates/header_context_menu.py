"""
Context menu for group header classes.
"""

# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["GroupHeaderContextMenuEvent", "GroupHeaderContextMenuEvent", "GroupHeaderContextMenu"]

from typing import Any


class GroupHeaderContextMenuEvent:
    """
    Right mouse click event sent by SimplePropertyWidget
    """

    def __init__(self, group_id: str, payload: Any):
        """Initialize class function.

        Args:
            group_id (str): Group identifier for event.
            payload (Any): payload for event
        """
        self.group_id = group_id
        self.payload = payload
        self.type = 0


class GroupHeaderContextMenu:
    """
    Context menu for group headers.
    """

    _instance = None

    def __init__(self):
        """Initialize function."""
        GroupHeaderContextMenu._instance = self

    def __del__(self):
        self.destroy()

    def destroy(self):
        """Destroy function. Class cleanup function."""
        GroupHeaderContextMenu._instance = None

    @classmethod
    def on_mouse_event(cls, event: GroupHeaderContextMenuEvent):
        """
        Mouse event received. Used to show context menu.

        Arg:
            event (GroupHeaderContextMenuEvent): Mouse event
        """
        if cls._instance:
            cls._instance._on_mouse_event(event)

    def _on_mouse_event(self, event: GroupHeaderContextMenuEvent):
        import omni.kit.widget.context_menu

        # check its expected event
        if event.type != int(omni.kit.menu.core.MenuEventType.ACTIVATE):
            return

        # setup objects, this is passed to all functions
        objects = {
            "payload": event.payload,
            "stage": None,
        }

        try:
            import omni.usd

            objects["stage"] = omni.usd.get_context().get_stage()
        except ModuleNotFoundError:
            pass

        menu_list = omni.kit.widget.context_menu.get_menu_dict(
            "group_context_menu." + event.group_id, "omni.kit.window.property"
        )
        omni.kit.widget.context_menu.get_instance().show_context_menu(
            "group_context_menu." + event.group_id, objects, menu_list
        )
