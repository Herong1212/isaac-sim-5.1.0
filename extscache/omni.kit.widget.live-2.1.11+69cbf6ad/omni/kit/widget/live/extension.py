# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.usd
import omni.ext
import omni.kit.app

from .live_state_menu import LiveStateMenu
from .icons import Icons
from .style import Styles


class OmniLiveWidgetExtension(omni.ext.IExt):

    def on_startup(self, ext_id):
        extension_path = omni.kit.app.get_app_interface().get_extension_manager().get_extension_path(ext_id)
        Icons.on_startup(extension_path)
        Styles.on_startup()

        usd_context = omni.usd.get_context()
        self._live_state_menu = LiveStateMenu(usd_context)
        self._live_state_menu.register_menu_widgets()

    def on_shutdown(self):
        self._live_state_menu.unregister_menu_widgets()
        Icons.on_shutdown()
