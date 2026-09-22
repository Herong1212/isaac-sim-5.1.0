# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from .layers_menu import layers_available
from .layers_menu import LayersMenu
import omni.ext
import omni.kit.app
from carb.eventdispatcher import get_eventdispatcher


class UsdzExportExtension(omni.ext.IExt):
    """Extension for handling USDZ export operations in Omni UI.

    This extension subscribes to global events to monitor script and folder changes. It manages the lifecycle of a layers menu used for USDZ export. On startup, the extension registers event listeners that trigger the creation or destruction of the layers menu based on the current availability of layers. When layers are available, it creates an instance of the layers menu; when they are not, it destroys any existing instance.

    On shutdown, the extension removes the event subscriptions and ensures that the layers menu is properly cleaned up. This allows the USDZ export functionality to adapt dynamically to changes in the workspace state.
    """

    def on_startup(self, ext_id):
        """Handles extension startup. Sets up event callbacks for global events and initializes Layers menu state.

        Args:
            ext_id (str): Extension identifier.
        """
        # Setup a callback for the event
        app = omni.kit.app.get_app_interface()
        self.__extensions_subscription = [
            get_eventdispatcher().observe_event(
                event_name=omni.ext.GLOBAL_EVENT_SCRIPT_CHANGED,
                on_event=self._on_event,
                observer_name="omni.kit.usdz_export",
            ),
            get_eventdispatcher().observe_event(
                event_name=omni.ext.GLOBAL_EVENT_FOLDER_CHANGED,
                on_event=self._on_event,
                observer_name="omni.kit.usdz_export",
            ),
        ]
        self.__layers_menu = None

        self._on_event(None)

    def _on_event(self, _):
        # Create/destroy the menu in the Layers window
        if self.__layers_menu:
            if not layers_available():
                self.__layers_menu.destroy()
                self.__layers_menu = None
        else:
            if layers_available():
                self.__layers_menu = LayersMenu()

    def on_shutdown(self):
        """Handles extension shutdown. Clears event subscriptions and destroys Layers menu if it exists."""
        self.__extensions_subscription = None

        if self.__layers_menu:
            self.__layers_menu.destroy()
            self.__layers_menu = None
