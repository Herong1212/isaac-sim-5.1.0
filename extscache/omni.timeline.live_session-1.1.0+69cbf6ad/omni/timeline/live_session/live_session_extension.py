# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from .session_state import SessionState
from .session_watcher import SessionWatcher
from .timeline_session import TimelineSession
from .ui_user_window import UserWindow
import omni.ext


_session_watcher = None
_window = None


class TimelineLiveSessionExtension(omni.ext.IExt):
    def on_startup(self, ext_id):
        usd_context_name = ""
        global _session_watcher
        _session_watcher = SessionWatcher(usd_context_name)
        _session_watcher.start()

        global _window
        _window = UserWindow(_session_watcher.get_session_state())

    def on_shutdown(self):
        global _session_watcher
        if _session_watcher is not None:
            _session_watcher.stop()
            # TODO: _session_watcher.destroy()
        _session_watcher = None

        global _window
        if _window is not None:
            _window.hide()
            _window.destroy()
        _window = None


def get_timeline_session() -> TimelineSession:
    global _session_watcher
    if _session_watcher is None:
        return None
    return _session_watcher.get_timeline_session()

def get_session_state() -> SessionState:
    global _session_watcher
    if _session_watcher is None:
        return None
    return _session_watcher.get_session_state()

def get_session_window() -> UserWindow:
    global _window
    return _window
