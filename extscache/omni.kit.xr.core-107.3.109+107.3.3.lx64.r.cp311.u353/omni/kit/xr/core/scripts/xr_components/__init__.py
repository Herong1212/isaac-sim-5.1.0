# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.


# These scripts append more functions into C++ defined classes.
# We append classes rather then inherit from them so they can be used as inputs for the C++ classes as well

__all__ = [
    "XRGuiLayerEvent",
    "XRToolEvent",
    "XRActionMapEvent",
    "XRProfileEvent",
    "XRProfileListEvent",
    "XRSystemEvent",
    "XRSystemListEvent",
    "XRInputDeviceEvent",
    "XRSelectionEvent",
    "XRTooltipEvent",
    "XRInputDeviceGeneratorEvent",
    "XRGuiLayerComponentBase",
    "XRToolComponentBase",
    "XRUsdLayerManager",
    "XRUsdComponentBase",
    "XRComponentBase",
    "printXRException",
]

from .xr_component_base import XRComponentBase, printXRException
from .xr_events import (
    XRActionMapEvent,
    XRGuiLayerEvent,
    XRInputDeviceEvent,
    XRInputDeviceGeneratorEvent,
    XRProfileEvent,
    XRProfileListEvent,
    XRSelectionEvent,
    XRSystemEvent,
    XRSystemListEvent,
    XRToolEvent,
    XRTooltipEvent,
)
from .xr_gui_layer_component_base import XRGuiLayerComponentBase
from .xr_tool_component_base import XRToolComponentBase
from .xr_usd_component_base import XRUsdComponentBase, XRUsdLayerManager
