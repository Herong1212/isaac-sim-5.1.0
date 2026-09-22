# Copyright (c) 2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

"""Livestream nvcf service extension."""

import os
from typing import Optional

from fastapi import staticfiles

import carb
import carb.settings

import omni.ext
import omni.usd
import omni.kit.app
from omni.services.core import main

from .services.api import router as api_router
import omni.services.livestream.nvcf.services.api


class LivestreamNVCFServiceExtension(omni.ext.IExt):
    """Livestream nvcf service extension."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__()

    def on_startup(self, ext_id: str) -> None:
        router_tags = ["streaming"]
        main.register_router(router=api_router, tags=router_tags)
        omni.services.livestream.nvcf.services.api.quit_on_session_ended = carb.settings.get_settings().get("app/livestream/nvcf/quitOnSessionEnded")
        omni.services.livestream.nvcf.services.api.session_resume_timeout_seconds = carb.settings.get_settings().get("app/livestream/nvcf/sessionResumeTimeoutSeconds")
        omni.services.livestream.nvcf.services.api.wait_for_custom_ready_event = carb.settings.get_settings().get("app/livestream/nvcf/waitForCustomReadyEvent")
        if omni.services.livestream.nvcf.services.api.wait_for_custom_ready_event:
            carb.log_info(f"omni.services.livestream.nvcf `app/livestream/nvcf/waitForCustomReadyEvent` is enabled, app MUST send an `omni.services.livestream.nvcf.custom_ready` event over the message_bus_event_stream once the app is ready to be streamed.")
            if not omni.services.livestream.nvcf.services.api.quit_on_session_ended:
                carb.log_info(f"omni.services.livestream.nvcf `app/livestream/nvcf/quitOnSessionEnded` is also enabled, app MUST listen for `omni.services.livestream.nvcf.session_ended` events sent over the message_bus_event_stream, perform whatever cleanup is necessary to prepare for a new client connection, and then send another `omni.services.livestream.nvcf.custom_ready` event.")

            # Listen for the custom ready event
            message_bus_event_stream = omni.kit.app.get_app().get_message_bus_event_stream()
            custom_ready_event_type = carb.events.type_from_string("omni.services.livestream.nvcf.custom_ready")
            self._custom_ready_sub = message_bus_event_stream.create_subscription_to_pop_by_type(custom_ready_event_type, self._on_custom_ready)

        # Listen for the app ready event
        startup_event_stream = omni.kit.app.get_app().get_startup_event_stream()
        self._app_ready_sub = startup_event_stream.create_subscription_to_pop_by_type(
            omni.kit.app.EVENT_APP_READY, self._on_app_ready, name="Livestream NVCF"
        )

        # Listen for client connection and disconnection events
        message_bus_event_stream = omni.kit.app.get_app().get_message_bus_event_stream()
        self.CLIENT_CONNECTED = carb.events.type_from_string("omni.kit.streamsdk.client_connected")
        self.CLIENT_DISCONNECTED = carb.events.type_from_string("omni.kit.streamsdk.client_disconnected")
        self._client_connection_subs = [
            message_bus_event_stream.create_subscription_to_pop_by_type(self.CLIENT_CONNECTED, self._on_client_connection),
            message_bus_event_stream.create_subscription_to_pop_by_type(self.CLIENT_DISCONNECTED, self._on_client_connection),
        ]

    def on_shutdown(self) -> None:
        self._client_connection_subs.clear()
        self._new_frame_sub = None
        self._app_ready_sub = None
        main.deregister_router(router=api_router)

    def _on_custom_ready(self, event):
        carb.log_info(f"omni.services.livestream.nvcf custom_ready for streaming")
        omni.services.livestream.nvcf.services.api.custom_ready = True

    def _on_app_ready(self, event):
        carb.log_info(f"omni.services.livestream.nvcf app_ready for streaming (waiting for rtx)")
        omni.services.livestream.nvcf.services.api.app_ready = True
        self._app_ready_sub = None

        # Listen for a new frame event
        rendering_event_stream = omni.usd.get_context().get_rendering_event_stream()
        self._new_frame_sub = rendering_event_stream.create_subscription_to_push_by_type(
            omni.usd.StageRenderingEventType.NEW_FRAME, self._on_new_frame, name="Livestream NVCF"
        )

    def _on_new_frame(self, event):
        carb.log_info(f"omni.services.livestream.nvcf rtx_ready for streaming")
        omni.services.livestream.nvcf.services.api.rtx_ready = True
        self._new_frame_sub = None

    def _on_client_connection(self, event):
        if event.type == self.CLIENT_CONNECTED:
            omni.services.livestream.nvcf.services.api.client_connected = True

            # Once a client connects, we must clear any pending session resume timeout.
            if omni.services.livestream.nvcf.services.api.session_resume_timeout_started:
                omni.services.livestream.nvcf.services.api.session_resume_timeout_started = None
                carb.log_warn(f"omni.services.livestream.nvcf client connected while awaiting session resume.")
        elif event.type == self.CLIENT_DISCONNECTED:
            omni.services.livestream.nvcf.services.api.client_connected = False

            # Once a client disconnects, we must clear the flag waiting for this to happen.
            omni.services.livestream.nvcf.services.api.waiting_for_client_disconnect = False
        else:
            carb.log_warn(f"omni.services.livestream.nvcf unknown client connection event received: {event.type}")
