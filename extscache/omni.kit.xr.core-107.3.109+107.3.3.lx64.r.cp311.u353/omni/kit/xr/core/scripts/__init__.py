# Copyright (c) 2021-2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

# fmt: off
__all__ = [
    # from _xrcore
    "XRAnchorMode",
    "XRCoordinateSystem",
    "XRCoreEventType",
    "XROrientationAlignment",
    "XRRay",
    "XRSystem",
    "XRRayQueryResult",
    "XRTargetInfo",
    "XRTransformType",
    "XRToken",
    "XRAssetManager",
    "XRAssetPackageInfo",

    # from xr_class_wrappers
    "XRCore",
    "XRProfile",
    "XRUsdLayer",
    "XRUtils",
    "XRInputDevice",
    "XREventGenerator",
    "XRInputDeviceModel",
    "XRActionMap",
    "XRPoseDesc",
    "XRPoseValidityFlags",
    "XR_INPUT_DEVICE_HAND_TRACKING_POSE_NAMES",

    # from xr_preferences
    "INTERACT_FREEZE_DELAY_SETTING_KEY",

    # from xr_shutdown
    "XRShutdown",

    # from xr_singleton
    "XRSingleton",
    "XRSingletonType",

    # from xr_weak_method
    "XRWeakMethod",

    # from xr_editor_menu_util
    "XREditorMenuToggleItem",

    # the actual extension
    "XRCoreExtension",

    "XRUsdLayerManager",

    # component base
    "XRComponentBase",
    "XRGuiLayerComponentBase",
    "XRToolComponentBase",
    "printXRException",
    "XRGuiLayerEvent",
    "XRInputDeviceEvent",
    "XRToolEvent",
    "XRActionMapEvent",
    "XRProfileEvent",
    "XRProfileListEvent",
    "XRSystemEvent",
    "XRSystemListEvent",
    "XRTooltipEvent",
    "XRInputDeviceGeneratorEvent",
    "XRSelectionManager",
    "XRSelectionBeam",
    "XRSelectionEvent",
    "XRSelectionEventGeneratorSubscription",
    "XRTooltip",
    "XRTooltipManager"
]
# fmt: on

# import C++ defined classes that don't need a wrapper
from .._xrcore import (
    XRAnchorMode,
    XRAssetPackageInfo,
    XRCoordinateSystem,
    XRCoreEventType,
    XROrientationAlignment,
    XRRay,
    XRRayQueryResult,
    XRToken,
    XRTransformType,
)

# import wrapped C++ defined classes
from .xr_class_wrappers import *

# component bases classes
from .xr_components import *

# Extension python class
from .xr_core_extension import XRCoreExtension

# utility to add menu items
from .xr_editor_menu_util import *

# preference
from .xr_preferences import INTERACT_FREEZE_DELAY_SETTING_KEY

# selection manager
from .xr_selection_manager import *

# shutdown functionality so xr can clean up
from .xr_shutdown import *

# singleton decorators
from .xr_singleton import *

# selection manager
from .xr_tooltip_manager import *

# weak method functionality
from .xr_weak_method import *
