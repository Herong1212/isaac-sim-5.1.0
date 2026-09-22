# Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["PresenceLayerEventType", "PresenceLayerEventPayload", "get_presence_layer_event_payload"]
import carb

from enum import IntEnum
from typing import Set, List


EVENT_PAYLOAD_KEY = "payload"


class PresenceLayerEventType(IntEnum):
    """Events emitted from Presence Layer module."""

    LOCAL_FOLLOW_MODE_CHANGED = carb.events.type_from_string("omni.kit.collaboration.presence_layer@local_follow_mode")
    """Emitted when local user enters/quits follow mode to other peer users."""

    BOUND_CAMERA_CHANGED = carb.events.type_from_string("omni.kit.collaboration.presence_layer@bound_camera")
    """Emitted when peer user switched its bound camera or the the user that is following switches the bound camera."""

    SELECTIONS_CHANGED = carb.events.type_from_string("omni.kit.collaboration.presence_layer@selections")
    """Emitted when peer user switched its selections."""

    BOUND_CAMERA_PROPERTIES_CHANGED = carb.events.type_from_string("omni.kit.collaboration.presence_layer@bound_camera_properties")
    """Emitted when the bound camera of peer user is builtin camera, and its properties are changed."""

    BOUND_CAMERA_RESYNCED = carb.events.type_from_string("omni.kit.collaboration.presence_layer@bound_camera_resynced")
    """Emitted when the bound camera of peer user is resynced. This is the same as prim resync of USD."""


class PresenceLayerEventPayload:
    """Payload of Presence Layer Event."""

    def __init__(self, event: carb.events.IEvent) -> None:
        carb_dict = carb.dictionary.get_dictionary()
        if event.type and event.type in iter(PresenceLayerEventType):
            self.event_type = PresenceLayerEventType(event.type)
            if self.event_type == PresenceLayerEventType.BOUND_CAMERA_PROPERTIES_CHANGED:
                self.__changed_users = carb_dict.get_dict_copy(event.payload)
            elif EVENT_PAYLOAD_KEY in event.payload:
                self.__changed_users = {}.fromkeys(event.payload[EVENT_PAYLOAD_KEY])
            else:
                self.__changed_users = {}
        else:
            self.event_type = None
            self.__changed_users = {}

    @property
    def changed_user_ids(self) -> List[str]:
        """Returns all user ids that have new updates."""

        return self.__changed_users.keys()

    def get_changed_camera_properties(self, user_id: str) -> Set[str]:
        """Gets the changed properties of bound builtin camera if event_type is BOUND_CAMERA_PROPERTIES_CHANGED."""

        return self.__changed_users.get(user_id, set())

    def __str__(self):
        return f"Event Type: {str(self.event_type)}, Changes: {self.__changed_users}"


def get_presence_layer_event_payload(event: carb.events.IEvent) -> PresenceLayerEventPayload:
    """Utility to convert carb.events.IEvent into PresenceLayerEventPayload."""

    try:
        return PresenceLayerEventPayload(event)
    except Exception as e:
        carb.log_error(f"Failed to convert event: {str(e)}")
        return None
