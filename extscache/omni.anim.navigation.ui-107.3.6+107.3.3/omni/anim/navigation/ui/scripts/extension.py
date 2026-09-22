# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
from .menu import Menu
from .property_widget import NavigationProperties
from .navmesh_menu import NavMeshMenu, NavMeshViewportMenu
from .settings import NavMeshPreferencePage
from omni.kit.window.preferences import register_page, unregister_page

import carb
import omni.ext
import omni.kit.browser.sample
import omni.kit.commands
import omni.usd


class Extension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        self._scene = None

    def on_startup(self, ext_id):
        self._navmesh_menu = NavMeshMenu()
        self._menu = Menu(self._navmesh_menu, ext_id)
        self._navmesh_viewport_menu = NavMeshViewportMenu()
        self._navmesh_viewport_menu.register_with_viewport()
        self._properties = NavigationProperties(self._navmesh_menu, ext_id)
        self._settings = register_page(NavMeshPreferencePage())

        self._sample_folder = carb.settings.get_settings().get_as_string("/exts/omni.anim.navigation/sample_folder")
        if (self._sample_folder):
            omni.kit.browser.sample.register_sample_folder(self._sample_folder, "Animation/Navigation")

    def on_shutdown(self):
        self._navpath_event_queue = None
        self._properties = None

        if self._menu:
            self._menu.on_shutdown()
            self._menu = None

        if self._navmesh_menu:
            self._navmesh_menu.destroy()
            self._navmesh_menu = None
        if self._navmesh_viewport_menu:
            self._navmesh_viewport_menu.unregister_from_viewport()

        if self._settings:
            unregister_page(self._settings)
            self._settings = None

        if self._sample_folder:
            omni.kit.browser.sample.unregister_sample_folder(self._sample_folder)
