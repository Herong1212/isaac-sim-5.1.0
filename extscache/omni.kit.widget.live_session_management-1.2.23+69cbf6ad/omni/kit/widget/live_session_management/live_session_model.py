# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

__all__ = ["LiveSessionModel"]

import itertools
from typing import List

import carb.events
import omni.kit.usd.layers as layers
from omni.kit.widget.live_session_management_ui import LiveSessionInterface, LiveSessionComboBoxModel


# Register layers.LiveSession as a subclass of LiveSessionInterface
LiveSessionInterface.register(layers.LiveSession)


class LiveSessionModel(LiveSessionComboBoxModel):
    """Omni UI model for omni.ui.Combobox, which can be used to build a customized combobox for listing, watching, and selecting Live Sessions for a specific layer.

    Args:
        layers_interface (omni.kit.usd.layers.Layers): Layers instance.
        layer_identifier (str): Layer identifier to query.
        update_users (bool): When True, it will listen for user list updates for the Live Session that is currently selected by this model.
    """

    def __init__(self, layers_interface, layer_identifier, update_users=True) -> None:
        """Initializes a new instance of LiveSessionModel for managing live sessions in Omni UI."""

        super().__init__(
            layer_identifier, self._get_current_live_session, self._get_all_live_sessions, update_users=update_users
        )
        self._layers_interface = layers_interface
        self._layers_event_subscription = layers_interface.get_event_stream().create_subscription_to_pop_by_type(
            layers.LayerEventType.LIVE_SESSION_LIST_CHANGED,
            self._on_layer_event,
            name="Live Session Model Events",
        )

    def destroy(self):
        """Destroys the LiveSessionModel instance by unsubscribing from event streams and cleaning up resources."""
        super().destroy()
        self._layers_event_subscription = None

    def _on_layer_event(self, event: carb.events.IEvent):
        payload = layers.get_layer_event_payload(event)
        if payload.event_type == layers.LayerEventType.LIVE_SESSION_LIST_CHANGED:
            if self._base_layer_identifier not in payload.identifiers_or_spec_paths:
                return

            self.refresh_sessions(force=True)

    def _get_current_live_session(self, layer_identifier: str = None) -> LiveSessionInterface:
        """
        Gets the current Live Session of the base layer joined.

        Args:
            layer_identifier (str): Base layer identifier. It's root layer if it's not provided.
        """
        return self._layers_interface.get_live_syncing().get_current_live_session(layer_identifier)

    def _get_all_live_sessions(self, layer_identifier: str = None) -> List[LiveSessionInterface]:
        """
        Gets all existing Live Sessions for a specific layer.

        Args:
            layer_identifier (str): The base layer to query Live Sessions.
                                    If it's empty, it will be root layer by default.

        Returns:
            A list of Live Sessions.
        """
        return self._layers_interface.get_live_syncing().get_all_live_sessions(layer_identifier)

    def create_new_session_name(self) -> str:
        """Generates a new live session name following a default or user-specific naming convention."""
        live_syncing = self._layers_interface.get_live_syncing()
        # first we attempt creating a "Default" as the first new session.
        default_session_name = "Default"
        if not live_syncing.find_live_session_by_name(self._base_layer_identifier, default_session_name):
            return default_session_name
        # if there already is a `Default`, then we use <username>_01, <username>_02, ...
        layers_instance = live_syncing._layers_instance
        live_syncing_interface = live_syncing._live_syncing_interface
        logged_user_name = live_syncing_interface.get_logged_in_user_name_for_layer(
            layers_instance, self._base_layer_identifier
        )
        if "@" in logged_user_name:
            logged_user_name = logged_user_name.split("@")[0]
        for i in itertools.count(start=1):
            user_session_name = "{}_{:02d}".format(logged_user_name, i)
            if not live_syncing.find_live_session_by_name(self._base_layer_identifier, user_session_name):
                return user_session_name

        return super().create_new_session_name()
