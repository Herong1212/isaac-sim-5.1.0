# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from dataclasses import dataclass, field
from typing import Callable, List, Optional

import omni.kit.menu.utils
from omni.kit.menu.utils import MenuItemDescription

from ..xr_weak_method import XRWeakMethod


@dataclass
class XREditorMenuContext:
    extension_id: str = ""
    action_name: str = ""
    menu_title: str = ""
    menu_location: str = ""
    on_click_fn: Optional[Callable] = None
    menu_item: List[MenuItemDescription] = field(default_factory=list)


class XREditorMenuToggleItem:
    def __init__(self, extension_id: str, menu_location: str, weak_fn: Callable, value: bool):
        self.__menu_context = XREditorMenuContext()
        self.__menu_context.extension_id = extension_id
        self.__menu_context.action_name = menu_location.lower().strip().replace("/", "_")
        self.__menu_context.menu_location = menu_location
        self.__menu_context.on_click_fn = weak_fn

        root_parts = menu_location.split("/")

        self.__editor_menu = MenuItemDescription(
            name=root_parts.pop(-1),
            ticked=True,
            ticked_value=value,
            onclick_action=(self.__menu_context.extension_id, self.__menu_context.action_name),
        )

        sub_menu = [self.__editor_menu]

        # Save the last part as the item that gets added to the menus. All other parts are submenus.
        while len(root_parts) > 1:
            menu_item = root_parts.pop(-1)
            menu = MenuItemDescription(name=menu_item, sub_menu=sub_menu)
            sub_menu = [menu]

        self.__menu_context.menu_item = sub_menu
        self.__menu_context.menu_title = root_parts.pop(-1) if len(root_parts) else self.__editor_menu.name
        omni.kit.menu.utils.add_menu_items(self.__menu_context.menu_item, self.__menu_context.menu_title)

        omni.kit.actions.core.get_action_registry().register_action(
            self.__menu_context.extension_id,
            self.__menu_context.action_name,
            XRWeakMethod(self._on_click_toggle),
            display_name=self.__menu_context.action_name,
            description=self.__menu_context.action_name,
            tag=self.__menu_context.action_name,
        )

    def __del__(self):
        omni.kit.actions.core.get_action_registry().deregister_action(
            self.__menu_context.extension_id, self.__menu_context.action_name
        )

        omni.kit.menu.utils.remove_menu_items(self.__menu_context.menu_item, self.__menu_context.menu_title)

        self.__menu_context = None

    def _on_click_toggle(self):
        self.__editor_menu.ticked_value = not self.__editor_menu.ticked_value
        self.__menu_context.on_click_fn(self.__menu_context.menu_location, self.__editor_menu.ticked_value)

    def refresh_menu(self):
        omni.kit.menu.utils.refresh_menu_items(self.__menu_context.menu_location)

    @property
    def ticked_value(self):
        return self.__editor_menu.ticked_value

    @ticked_value.setter
    def ticked_value(self, value: bool) -> None:
        self.__editor_menu.ticked_value = value
        self.refresh_menu()
