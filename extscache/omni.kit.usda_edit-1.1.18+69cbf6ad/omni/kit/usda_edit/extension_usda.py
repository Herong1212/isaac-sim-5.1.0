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
from .content_browser_menu import content_browser_available
from .content_browser_menu import ContentBrowserMenu
from .editor import close_all_editors
import omni.ext
import omni.kit.app
from carb.eventdispatcher import get_eventdispatcher


class UsdaEditExtension(omni.ext.IExt):
    """A class for managing the USDA edit extension integration with Omni UI.

    This extension registers callbacks to observe global events and extension state changes in order to create and destroy menus dynamically. The class subscribes to global events such as script changes and folder changes, and registers explicit callbacks for enable and disable events of the content browser extension. Based on availability checks for the Layers menu and Content Browser, the class creates or destroys corresponding menu objects. It also ensures that all resources are properly released during shutdown, including unsubscribing from events and destroying any instantiated menus.

    Methods such as on_startup and on_shutdown manage the lifecycle of the extension, while helper methods respond to specific events from the application framework. The design ensures that the user interface remains responsive to changes in the underlying environment.
    """

    def on_startup(self, ext_id):
        """Initializes the extension on startup and sets up necessary event subscriptions and callbacks.

        Args:
            ext_id (str): The extension identifier to initialize startup tasks.
        """
        # Setup a callback for the event
        app = omni.kit.app.get_app_interface()
        ext_manager = app.get_extension_manager()
        self.__extensions_subscription = [
            get_eventdispatcher().observe_event(
                event_name=omni.ext.GLOBAL_EVENT_SCRIPT_CHANGED,
                on_event=self._on_event,
                observer_name="omni.kit.usda_edit",
            ),
            get_eventdispatcher().observe_event(
                event_name=omni.ext.GLOBAL_EVENT_FOLDER_CHANGED,
                on_event=self._on_event,
                observer_name="omni.kit.usda_edit",
            ),
        ]
        self.__layers_menu = None
        self.__content_browser_menu = None

        self._on_event(None)

        # When kit exits we won't get a change event for content_browser unloading so we need to resort to
        # an explicit subscription to its enable/disable events.
        #
        # If content_browser is already enabled then we will immediately get a callback for it, so we want
        # to do this last.
        self.__content_browser_hook = ext_manager.subscribe_to_extension_enable(
            self._on_browser_enabled, self._on_browser_disabled, "omni.kit.window.content_browser"
        )

    def _on_browser_enabled(self, ext_id: str):
        if not self.__content_browser_menu:
            self.__content_browser_menu = ContentBrowserMenu()

    def _on_browser_disabled(self, ext_id: str):
        if self.__content_browser_menu:
            self.__content_browser_menu.destroy()
            self.__content_browser_menu = None

    def _on_event(self, _):
        # Create/destroy the menu in the Layers window
        if self.__layers_menu:
            if not layers_available():
                self.__layers_menu.destroy()
                self.__layers_menu = None
        else:
            if layers_available():
                self.__layers_menu = LayersMenu()

    def on_shutdown(self):  # pragma: no cover
        """Shuts down the extension by destroying menus, unsubscribing events, and closing all editors."""
        self.__extensions_subscription = None
        self.__content_browser_hook = None

        if self.__layers_menu:
            self.__layers_menu.destroy()
            self.__layers_menu = None

        if self.__content_browser_menu:
            self.__content_browser_menu.destroy()
            self.__content_browser_menu = None

        close_all_editors()
