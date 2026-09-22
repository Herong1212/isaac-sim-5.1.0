# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

# =================================== NOTE ====================================
# The APIs in this file are unfinished and may change in future releases
# Using these is at your own risk, and forward-compatability is not supported

from typing import Iterable, Optional, Union

import carb

from ..xr_class_wrappers import XREventGenerator
from ..xr_selection_manager import XRSelectionEventGeneratorSubscription
from .xr_usd_component_base import XRUsdComponentBase


class XRToolComponentBase(XRUsdComponentBase):

    def __init__(self, name: str):

        super().__init__("xr_tool." + name)

        self.__tool_enabled = True
        self.__tool_name = name

        self.get_settings().set_default("/xr/ui/enabled", True)

        if not self.get_settings().get_as_bool("/xr/ui/enabled"):
            self.__tool_enabled = False

        super().start("xr_tool." + name, self.__tool_enabled)

    def is_enabled(self) -> bool:
        """
        Check if the tool is enabled.

        Return:
            True if tool is enabled
        """

        if not self.__tool_enabled:
            return False

        if self.get_xr_core().is_tool_enabled(self.__tool_name):
            return True

        return False

    def run_enable_if_enabled(self) -> None:
        # A component or python extension can be loaded
        # after the tool has been enabled, in which
        # case we need to manually trigger the enable

        if self.is_enabled():
            self.on_enable()

    def bind_input_event_generator(
        self, event_name: str, event_list: Iterable[str], tooltips: Union[str, dict[str, str]]
    ) -> Optional[XREventGenerator]:
        """
        Bind an input event generator and look up in the action map where it should be bound.

        Args:
            event_name:   base name of the event
            event_list:   events that need to be generated for this base event
            tooltips:     a string with a tooltip or a dictionary with tooltip key/description pairs
        """

        return self.get_xr_core().bind_input_event_generator(event_name, event_list, tooltips)

    def bind_selection_event_generator(
        self, event_name: str, event_list: Iterable[str], usd_path: str, priority: int
    ) -> XRSelectionEventGeneratorSubscription:
        """
        Bind a selection event generator to a specific usd path. If that one gets triggered by a press/release/hover event.
        The given event will be generated on the message_bus

        Args:
            event_name:   base name of the event
            event_list:   events that need to be generated for this base event
            usd_path:     path of prim to bind to
            priority:     priority of handling event, higher priority gets handled first and may block lower priority callbacks.
        """

        return self.get_selection_manager().bind_event_generator(usd_path, priority, event_name, event_list)
