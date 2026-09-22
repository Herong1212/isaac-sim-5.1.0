# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
import omni.ext
import omni.kit.app
import omni.client

from carb import eventdispatcher, log_warn
from .utils import exec_after_redraw
from .view import (
    BOOKMARK_ADDED_GLOBAL_EVENT, BOOKMARK_DELETED_GLOBAL_EVENT, BOOKMARK_RENAMED_GLOBAL_EVENT,
    NUCLEUS_SERVER_ADDED_GLOBAL_EVENT, NUCLEUS_SERVER_DELETED_GLOBAL_EVENT, NUCLEUS_SERVER_RENAMED_GLOBAL_EVENT
)

g_singleton = None


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class FilePickerExtension(omni.ext.IExt):
    """
    The filepicker extension is not necessarily integral to using the widget.  However, it is useful for handling
    singleton tasks for the class.

    """
    def on_startup(self, ext_id):
        # Save away this instance as singleton
        global g_singleton
        g_singleton = self

        # Listen for bookmark and server connection events in order to update persistent settings
        events = (
            BOOKMARK_ADDED_GLOBAL_EVENT, BOOKMARK_DELETED_GLOBAL_EVENT, BOOKMARK_RENAMED_GLOBAL_EVENT,
            NUCLEUS_SERVER_ADDED_GLOBAL_EVENT, NUCLEUS_SERVER_DELETED_GLOBAL_EVENT, NUCLEUS_SERVER_RENAMED_GLOBAL_EVENT
        )
        ed = eventdispatcher.get_eventdispatcher()
        self._event_stream_subscriptions = [ed.observe_event(event_name=evt, on_event=self._update_persistent_bookmarks) for evt in events]

    def _update_persistent_bookmarks(self, event: eventdispatcher.Event):
        """When a bookmark is updated or deleted, update persistent settings"""

        if event.event_name in [BOOKMARK_ADDED_GLOBAL_EVENT, NUCLEUS_SERVER_ADDED_GLOBAL_EVENT]:
            name = event['name']
            url = event['url']
            if name and url:
                omni.client.add_bookmark(name, url)
        elif event.event_name in [BOOKMARK_DELETED_GLOBAL_EVENT, NUCLEUS_SERVER_DELETED_GLOBAL_EVENT]:
            name = event['name']
            if name:
                omni.client.remove_bookmark(name)
        elif event.event_name in [BOOKMARK_RENAMED_GLOBAL_EVENT, NUCLEUS_SERVER_RENAMED_GLOBAL_EVENT]:
            old_name = event['old_name']
            new_name = event['new_name']
            url = event['url']
            if old_name and new_name and url:
                omni.client.add_bookmark(new_name, url)
                if old_name != new_name:
                    # Wait a few frames for next update to avoid race condition
                    exec_after_redraw(lambda: omni.client.remove_bookmark(old_name), wait_frames=6)

    def on_shutdown(self):
        # Clears the auth callback
        self._event_stream_subscriptions.clear()

        global g_singleton
        g_singleton = None


def get_instance():
    return g_singleton