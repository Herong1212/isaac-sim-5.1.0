# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ext
import omni.kit.actions.core
from omni.kit.menu.utils import MenuItemDescription 
from .quicklayout import QuickLayout


class QuickLayoutExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        self.__quick_layout = QuickLayout()

        # actions
        action_registry = omni.kit.actions.core.get_action_registry()
        actions_tag = "Quicklayout Actions"
        extension_id = "omni.kit.quicklayout"

        omni.kit.actions.core.get_action_registry().register_action(
            extension_id,
            "quick_layout_save",
            lambda: self.__quick_layout.save(None, None),
            display_name="Quicklayout Save",
            description="Save",
            tag=actions_tag,
        )

        omni.kit.actions.core.get_action_registry().register_action(
            extension_id,
            "quick_layout_load",
            lambda: self.__quick_layout.load(None, None),
            display_name="Quicklayout Load",
            description="Load",
            tag=actions_tag,
        )

        omni.kit.actions.core.get_action_registry().register_action(
            extension_id,
            "quick_layout_quicksave",
            lambda: QuickLayout.quick_save(None, None),
            display_name="Quicklayout Quick Save",
            description="Quicksave",
            tag=actions_tag,
        )

        omni.kit.actions.core.get_action_registry().register_action(
            extension_id,
            "quick_layout_quickload",
            lambda: QuickLayout.quick_load(None, None),
            display_name="Quicklayout Quick Load",
            description="Quickload",
            tag=actions_tag,
        )

        # add menus
        submenu_list = [ 
            MenuItemDescription(name="Save Layout...",  onclick_action=(extension_id, "quick_layout_save")),
            MenuItemDescription(name="Load Layout...",  onclick_action=(extension_id, "quick_layout_load")),
            MenuItemDescription(name="Quick Save",  onclick_action=(extension_id, "quick_layout_quicksave")),
            MenuItemDescription(name="Quick Load",  onclick_action=(extension_id, "quick_layout_quickload")),
            ] 
        self._menu_list = [ MenuItemDescription(name="Layout", sub_menu=submenu_list)] 
        omni.kit.menu.utils.add_menu_items(self._menu_list, "Window") 

    def on_shutdown(self): # pragma: no cover
        omni.kit.menu.utils.remove_menu_items(self._menu_list, "Window") 

        action_registry = omni.kit.actions.core.get_action_registry()
        if action_registry:
            action_registry.deregister_all_actions_for_extension("omni.kit.quicklayout")
        self.__quick_layout.destroy()
        self.__quick_layout = None
