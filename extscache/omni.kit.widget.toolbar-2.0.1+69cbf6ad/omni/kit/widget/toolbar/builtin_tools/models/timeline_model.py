# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["TimelinePlayPauseModel"]

import omni.ui as ui
import carb
import omni.timeline
from omni.kit.commands import execute


class TimelinePlayPauseModel(ui.AbstractValueModel):
    """The value model that is reimplemented in Python to watch a bool setting path"""

    def __init__(self):
        super().__init__()

        self._timeline = omni.timeline.get_timeline_interface()
        self._is_playing = self._timeline.is_playing()
        self._is_stopped = self._timeline.is_stopped()

        stream = self._timeline.get_timeline_event_stream()
        self._sub = stream.create_subscription_to_pop(self._on_timeline_event)

    def clean(self):
        self._sub = None

    def get_value_as_bool(self):
        return self._is_playing and not self._is_stopped

    def set_value(self, value):
        """Reimplemented set bool"""
        if value:
            execute("ToolbarPlayButtonClicked")
        else:
            execute("ToolbarPauseButtonClicked")

    def _on_timeline_event(self, e):
        is_playing = self._timeline.is_playing()
        is_stopped = self._timeline.is_stopped()

        if is_playing != self._is_playing or is_stopped != self._is_stopped:
            self._is_playing = self._timeline.is_playing()
            self._is_stopped = self._timeline.is_stopped()
            self._value_changed()
