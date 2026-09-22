# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = []

import carb.events

# If refreshing on a USD property path is needed without triggering TfNotice, you can push this event into
# omni.kit.app's message bus. It will trigger a refresh on the widget for that property.
# Example:
#
#    from omni.kit.property.usd import ADDITIONAL_CHANGED_PATH_GLOBAL_EVENT
#    import omni.kit.app
#
#    payload = {
#        "path": "/World/Cube.xformOp:translate",
#        "stage": omni.usd.get_context().get_stage()
#    }
#
#    # If emitting the event from C++, use "stage_id" as payload key instead and value from UsdContext::getStageId()
#
#    omni.kit.app.queue_event(ADDITIONAL_CHANGED_PATH_GLOBAL_EVENT, payload=payload)
ADDITIONAL_CHANGED_PATH_GLOBAL_EVENT: str = "omni.usd.property.usd.additional_changed_path"
ADDITIONAL_CHANGED_PATH_EVENT_TYPE: int = carb.events.type_from_string(ADDITIONAL_CHANGED_PATH_GLOBAL_EVENT)
from omni.kit.app import register_event_alias

register_event_alias(ADDITIONAL_CHANGED_PATH_EVENT_TYPE, ADDITIONAL_CHANGED_PATH_GLOBAL_EVENT)
