# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["PresenceLayerAPI", "get_presence_layer_interface", "PresenceLayerExtension"]

import carb
import omni.ext
import omni.usd

from .presence_layer_manager import PresenceLayerManager, PresenceLayerAPI
from typing import Dict, Union, List


__all_presence_layer_apis: Dict[omni.usd.UsdContext, PresenceLayerAPI] = {}
__all_presence_managers: List[PresenceLayerManager] = []


def _shutdown_all():
    global __all_presence_layer_apis
    global __all_presence_managers

    for presence_layer in __all_presence_managers:
        presence_layer.stop()

    __all_presence_layer_apis.clear()
    __all_presence_managers.clear()


def get_presence_layer_interface(
    context_name_or_instance: Union[str, omni.usd.UsdContext] = ""
) -> Union[PresenceLayerAPI, None]:
    """
    Gets PresenceLayerAPI interface bound to the context. For each UsdContext, it has unique PresenceLayerAPI instance,
    through which, you can access all the interfaces supported. PresenceLayerAPI provides the APIs that serve
    for easy access to data of Presence Layer, where Presence Layer is the transport layer that works for exchange
    persistent data for all users in the Live Session of the bound UsdContext. It only supports Live Session of root
    layer for now.
    """

    global __all_presence_layer_apis
    if not context_name_or_instance:
        context_name_or_instance = ""

    if isinstance(context_name_or_instance, str):
        usd_context = omni.usd.get_context(context_name_or_instance)
    elif isinstance(context_name_or_instance, omni.usd.UsdContext):
        usd_context = context_name_or_instance
    else:
        carb.log_warn("Failed to get Presence Layer interface since the param must be name or instance of UsdContext.")
        return None

    if not usd_context:
        carb.log_warn("Failed to query Presence Layer interface since UsdContext cannot be found.")
        return None

    presence_layer_api = __all_presence_layer_apis.get(usd_context, None)
    if not presence_layer_api:
        presence_layer = PresenceLayerManager(usd_context)
        presence_layer.start()
        __all_presence_managers.append(presence_layer)
        presence_layer_api = PresenceLayerAPI(presence_layer)
        __all_presence_layer_apis[usd_context] = presence_layer_api

    return presence_layer_api


class PresenceLayerExtension(omni.ext.IExt):
    def on_startup(self):
        # Initialize Presence Layer for default context.
        get_presence_layer_interface()

    def on_shutdown(self):
        _shutdown_all()
