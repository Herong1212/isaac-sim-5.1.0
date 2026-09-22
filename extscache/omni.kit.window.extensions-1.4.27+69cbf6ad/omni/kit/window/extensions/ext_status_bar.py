# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""This module defines the ExtStatusBar class which provides a custom status bar for the Omniverse application, displaying messages and colors based on application events such as syncing the registry and installing extensions."""

__all__ = ["ExtStatusBar"]

from datetime import datetime

import omni.ext
import omni.kit.app
import omni.ui as ui
from carb.eventdispatcher import get_eventdispatcher
from omni.ui import color as cl

NEUTRAL = cl("#FFFFFF")
SUCCESS = cl("#3794ff")
FAILURE = cl("#CC0000")


class ExtStatusBar:
    """A custom status bar extension for the Omniverse application.

    This class creates a status bar that listens to specific events in the Omniverse application and updates its display message and color accordingly. It subscribes to events related to the syncing of the registry and the installation of extensions, and it displays success or failure messages with corresponding colors based on the event outcomes.

    The status bar can be destroyed when it is no longer needed, which cleans up any subscriptions it has made to the application's message bus.
    """

    def __init__(self):
        """Initializes the status bar with subscriptions to various events."""
        self._label = ui.Label("", height=8)

        self._subs = []

        self._set_status("")

        def sub(e, message, color):
            self._subs.append(
                get_eventdispatcher().observe_event(
                    event_name=e, on_event=lambda e: self._set_status(message, color, e)
                )
            )

        sub(omni.ext.GLOBAL_EVENT_REGISTRY_REFRESH_BEGIN_DEFERRED, "Syncing Registry...", NEUTRAL)
        sub(
            omni.ext.GLOBAL_EVENT_REGISTRY_REFRESH_END_SUCCESS,
            "Registry Synced: " + datetime.now().strftime("%H:%M:%S"),
            SUCCESS,
        )
        sub(omni.ext.GLOBAL_EVENT_REGISTRY_REFRESH_END_FAILURE, "Registry Sync Failed.", FAILURE)
        sub(omni.ext.GLOBAL_EVENT_EXTENSION_PULL_BEGIN_DEFERRED, "Installing: {}...", NEUTRAL)
        sub(omni.ext.GLOBAL_EVENT_EXTENSION_PULL_END_SUCCESS, "Installed successfully: {}", SUCCESS)
        sub(omni.ext.GLOBAL_EVENT_EXTENSION_PULL_END_FAILURE, "Install failed: {}", FAILURE)

    def destroy(self):
        """Cleans up the subscriptions."""
        self._subs = None

    def _set_status(self, status, color=NEUTRAL, evt=None):
        if evt and "packageId" in evt:
            status = status.format(evt["packageId"])
        self._status = status
        self._status_color = color
        self._refresh_ui()

    def _refresh_ui(self):
        self._label.style = {"font_size": 14, "color": self._status_color}
        self._label.text = self._status
