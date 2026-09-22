# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = [
    "LayerEventPayload", "get_layer_event_payload", "get_short_user_name",
    "LayerEventType"
]

import carb

from typing import List, Dict, Union
from .event import LayerEventType
from pxr import Sdf


class LayerEventPayload:
    """
    LayerEventPayload is a wrapper to carb.events.IEvent sent from module omni.kit.usd.layers.
    Through which, you can query event payload easier with properties.
    """

    def __init__(self, event: carb.events.IEvent) -> None:
        self.__layer_info_data: Dict[str, List[str]] = {}
        self.__identifiers_or_spec_paths: List[str] = []
        # If any layers are influenced by this event.
        self.__has_influenced_layers = False
        self.__layer_spec_paths: Dict[str, List[str]] = {}
        self.__user_name = None
        self.__user_id = None
        self.__layer_identifier = None
        self.__success = True

        try:
            # Invalid type that's not defined in this module.
            self.__event_type = LayerEventType(event.type)
        except Exception:
            self.__event_type = None
            return

        self.__has_influenced_layers = event.type != int(LayerEventType.SPECS_LOCKING_CHANGED)
        if event.type == int(LayerEventType.INFO_CHANGED):
            layer_identifier = event.payload["layer_identifier"]
            info_data = event.payload["val"]
            self.__layer_info_data[layer_identifier] = list(info_data)
            self.__layer_identifier = layer_identifier
        elif (
            event.type == int(LayerEventType.DIRTY_STATE_CHANGED)
            or event.type == int(LayerEventType.OUTDATE_STATE_CHANGED)
            or event.type == int(LayerEventType.MUTENESS_STATE_CHANGED)
            or event.type == int(LayerEventType.LOCK_STATE_CHANGED)
            or event.type == int(LayerEventType.SPECS_LOCKING_CHANGED)
            or event.type == int(LayerEventType.LAYER_FILE_PERMISSION_CHANGED)
        ):
            self.__identifiers_or_spec_paths = list(event.payload["val"])
        elif event.type == int(LayerEventType.PRIM_SPECS_CHANGED):
            layer_identifier = event.payload["layer_identifier"]
            prim_specs = event.payload["val"]
            self.__layer_spec_paths[layer_identifier] = list(prim_specs)
            self.__layer_identifier = layer_identifier
        elif event.type == int(LayerEventType.SPECS_LINKING_CHANGED):
            for _, value in event.payload["val"].items():
                layer_identifier = value.get("key", "")
                spec_paths = value.get("value", [])
                if layer_identifier and spec_paths:
                    self.__layer_spec_paths[layer_identifier] = spec_paths
            self.__identifiers_or_spec_paths = list(self.__layer_spec_paths.keys())
        elif (
            event.type == int(LayerEventType.LIVE_SESSION_USER_JOINED)
            or event.type == int(LayerEventType.LIVE_SESSION_USER_LEFT)
        ):
            self.__user_name = event.payload["user_name"]
            self.__user_id = event.payload["user_id"]
            self.__layer_identifier = event.payload["layer_identifier"]
        elif (
            event.type == int(LayerEventType.LIVE_SESSION_STATE_CHANGED) or
            event.type == int(LayerEventType.LIVE_SESSION_JOINING)
        ):
            self.__identifiers_or_spec_paths = list(event.payload["val"])
        elif event.type == int(LayerEventType.LIVE_SESSION_LIST_CHANGED):
            self.__layer_identifier = event.payload["val"]
        elif (
            event.type == int(LayerEventType.LIVE_SESSION_MERGE_STARTED) or
            event.type == int(LayerEventType.LIVE_SESSION_MERGE_ENDED)
        ):
            self.__layer_identifier = event.payload["layer_identifier"]
            self.__success = event.payload["success"]
        elif event.type == int(LayerEventType.AUTO_RELOAD_LAYERS_CHANGED):
            self.__layer_identifier = event.payload["layer_identifier"]

        if not self.__layer_identifier and len(self.__identifiers_or_spec_paths) > 0 and self.__has_influenced_layers:
            self.__layer_identifier = self.__identifiers_or_spec_paths[0]
        elif not self.__identifiers_or_spec_paths and self.__layer_identifier:
            self.__identifiers_or_spec_paths = [self.__layer_identifier]

    @property
    def event_type(self) -> LayerEventType:
        """Layer event type, it's None when the event type is unknown."""

        return self.__event_type

    @property
    def layer_info_data(self) -> Dict[str, List[str]]:
        """
        It is non-empty if event type is INFO_CHANGED, of which key is the layer identifier
        that its metadata has changed, and value is the set of strings that represent the metadata tokens
        that's modified. Currently, only the following tokens are notified when they are modified:

        UsdGeom.Tokens.upAxis

        UsdGeom.Tokens.metersPerUnit

        Sdf.Layer.StartTimeCodeKey

        Sdf.Layer.EndTimeCodeKey

        Sdf.Layer.FramesPerSecond

        Sdf.Layer.TimeCodesPerSecond

        Sdf.Layer.CommentKey

        Sdf.Layer.Documentation

        "subLayerOffsets_offset"  # String as there is no python binding from USD.

        "subLayerOffsets_scale"
        """

        return self.__layer_info_data

    @property
    def identifiers_or_spec_paths(self) -> List[str]:
        """
        The influenced layers or prim specs if any. When event type is LayerEventType.SPECS_LOCKING_CHANGED,
        it hosts all influenced prim specs. Otherwise, it hosts all influenced layers for the event.
        """

        return self.__identifiers_or_spec_paths

    @property
    def layer_spec_paths(self) -> Dict[str, List[str]]:
        """
        The influenced spec paths for each layer.
        It's non-empty if event type is PRIM_SPECS_CHANGED or SPECS_LINKING_CHANGED,
        of which, the key is the layer identifier, and value is the list of spec paths.
        """

        return self.__layer_spec_paths

    @property
    def user_name(self) -> str:
        """It's non-empty if event type is LIVE_SESSION_USER_JOINED or LIVE_SESSION_USER_LEFT."""

        return self.__user_name

    @property
    def user_id(self) -> str:
        """It's non-empty if event type is LIVE_SESSION_USER_JOINED or LIVE_SESSION_USER_LEFT."""

        return self.__user_id

    @property
    def success(self) -> bool:
        """
        It's useful if event type is LIVE_SESSION_MERGE_STARTED or LIVE_SESSION_MERGE_ENDED, which
        means if merge of a Live Session is successful or not.
        """

        return self.__success

    @property
    def layer_identifier(self) -> str:
        """
        This property is non-empty when any layers are influenced. If multiple layers are influenced,
        it's the first one of identifiers_or_spec_paths to keep compatibility.
        """

        return self.__layer_identifier

    def is_layer_influenced(self, layer_identifier_or_handle: Union[str, Sdf.Layer]) -> bool:
        """Checks if specific layer is influenced by the event."""

        if not self.__identifiers_or_spec_paths or not self.__has_influenced_layers:
            return False

        if isinstance(layer_identifier_or_handle, str):
            layer_handle = Sdf.Find(layer_identifier_or_handle)
        else:
            layer_handle = layer_identifier_or_handle

        if not layer_handle:
            return False

        for layer_identifier in self.__identifiers_or_spec_paths:
            if layer_handle == Sdf.Find(layer_identifier):
                return True

        return False


def get_layer_event_payload(event: carb.events.IEvent) -> LayerEventPayload:
    """Gets the payload of layer events by populating them into an instance of LayerEventPayload."""

    try:
        return LayerEventPayload(event)
    except Exception as e:
        carb.log_error(f"Failed to convert event: {str(e)}")
        return None


def get_short_user_name(user_name: str) -> str:
    """Gets short name with capitalized first letters of each word."""

    words = user_name.split()
    if not words:
        name = "NA"
    else:
        if len(words) == 1 and len(words[0]) > 1:
            name = words[0][0:2].upper()
        else:
            name = words[0][0:1].upper()

    return name


def post_notification(message: str, info=True):
    try:
        import omni.kit.notification_manager as nm
        if info:
            status = nm.NotificationStatus.INFO
        else:
            status = nm.NotificationStatus.WARNING
        nm.post_notification(message, status=status)
    except Exception:
        pass
