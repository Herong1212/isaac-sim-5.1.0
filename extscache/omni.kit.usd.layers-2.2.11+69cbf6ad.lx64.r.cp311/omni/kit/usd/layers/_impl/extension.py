# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "get_layers", "get_auto_authoring",
    "get_layers_state", "get_live_syncing", "get_last_error_type",
    "get_last_error_string", "LayerEditMode",
    "LayerErrorType", "active_authoring_layer_context", "Layers"
]

import carb
import omni.ext
import omni.usd

from typing import List, Union, Dict
from .layers_interface import Layers, LiveSyncing, LayersState, AutoAuthoring
from .._omni_kit_usd_layers import acquire_layers_interface, release_layers_interface, LayerEditMode, LayerErrorType
from pxr import Sdf, Usd

_all_layers_instances: Dict[omni.usd.UsdContext, Layers] = {}
_layers_interface = None


def _get_layers_interface():
    global _layers_interface
    if not _layers_interface:
        _layers_interface = acquire_layers_interface()

    return _layers_interface


def get_layers(context_name_or_instance: Union[str, omni.usd.UsdContext] = "") -> Union[Layers, None]:
    """
    Gets Layers instance bound to the context. For each UsdContext, it has unique Layers instance,
    through which, you can access all the interfaces supported.
    """

    global _all_layers_instances
    if not context_name_or_instance:
        context_name_or_instance = ""

    if isinstance(context_name_or_instance, str):
        usd_context = omni.usd.get_context(context_name_or_instance)
    elif isinstance(context_name_or_instance, omni.usd.UsdContext):
        usd_context = context_name_or_instance
    else:
        carb.log_warn("Failed to get layers instance since the param must be name or instance of UsdContext.")
        return None

    if not usd_context:
        carb.log_warn("Failed to query layers instance since UsdContext cannot be found.")
        return None

    layers_instance = _all_layers_instances.get(usd_context, None)
    if not layers_instance:
        instance_native = _get_layers_interface().get_layers_instance_by_context(usd_context)
        if instance_native:
            layers_instance = Layers(instance_native, usd_context)
            _all_layers_instances[usd_context] = layers_instance
        else:
            layers_instance = None
            carb.log_warn("Failed to query layers instance.")

    return layers_instance


def get_layers_state(context_name_or_instance: Union[str, omni.usd.UsdContext] = "") -> Union[LayersState, None]:
    """
    Gets the Layers State interface from Layers instance bound to the specified UsdContext.
    Layers State interface extends the USD interfaces to access more states of layers, and provides
    utilities for layer operations and event subscription.
    """

    layers = get_layers(context_name_or_instance)
    if layers:
        return layers.get_layers_state()

    return None


def get_live_syncing(context_name_or_instance: Union[str, omni.usd.UsdContext] = "") -> Union[LiveSyncing, None]:
    """
    Gets the Live Syncing interface from Layers instance bound to the specified UsdContext.
    Live Syncing interface is the core of supporting Live Session in Kit, which provides all functionalities to
    manage Live Sessions.
    """

    layers = get_layers(context_name_or_instance)
    if layers:
        return layers.get_live_syncing()

    return None


def get_auto_authoring(context_name_or_instance: Union[str, omni.usd.UsdContext] = "") -> Union[AutoAuthoring, None]:
    """
    Gets the Auto Authoring interface from Layers instance bound to the specified UsdContext.
    REMINDER: Auto Authoring interface is still in experimental stage, which is used to reduce the burden of
    managing deltas inside multi-sublayers, so authoring to stage will be auto-targeted to the layers that
    has its strongest opinions.
    """

    layers = get_layers(context_name_or_instance)
    if layers:
        return layers.get_auto_authoring()

    return None


def get_last_error_type(context_name_or_instance: Union[str, omni.usd.UsdContext] = "") -> LayerErrorType:
    """
    Gets the error status of the API call bound to specified UsdContext. Any API calls to Layers interface will change
    the error state. When you want to get the detailed error of your last call, you can use this function to fetch the
    detailed error type.
    """

    layers = get_layers(context_name_or_instance)
    if layers:
        return layers.get_last_error_type()

    return LayerErrorType.SUCCESS


def get_last_error_string(context_name_or_instance: Union[str, omni.usd.UsdContext] = "") -> str:
    """Gets the error string of the API call bound to specified UsdContext."""

    layers = get_layers(context_name_or_instance)
    if layers:
        return layers.get_last_error_string()

    return ""


def active_authoring_layer_context(usd_context) -> Usd.EditContext:
    """
    Gets the edit context for edit target if it's in non-auto authoring mode,
    or edit context for default edit layer if it's in auto authoring mode.
    """

    stage = usd_context.get_stage()
    layers = get_layers(usd_context)
    auto_authoring = layers.get_auto_authoring()
    edit_mode = layers.get_edit_mode()
    if edit_mode == LayerEditMode.NORMAL:
        edit_target_layer = stage.GetEditTarget().GetLayer()
    else:
        default_edit_layer_identifier = auto_authoring.get_default_layer()
        edit_target_layer = Sdf.Find(default_edit_layer_identifier)

    if not edit_target_layer:
        edit_target_layer = stage.GetRootLayer()

    return Usd.EditContext(stage, edit_target_layer)


# Use extension entry points to acquire and release interface.
class Extension(omni.ext.IExt):
    """Extension Class."""

    def on_startup(self):
        # Load layers for default context
        get_layers()

    def on_shutdown(self):
        global _all_layers_instances

        for _, instance in _all_layers_instances.items():
            instance._destroy()
        _all_layers_instances.clear()

        global _layers_interface
        if _layers_interface:
            release_layers_interface(_layers_interface)
