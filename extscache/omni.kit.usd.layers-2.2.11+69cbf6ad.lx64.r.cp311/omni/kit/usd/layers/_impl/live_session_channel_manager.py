# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["LiveSessionUser", "LiveSessionChannelManager"]

import asyncio
import carb

from binascii import crc32
from typing import Dict, List, Tuple
from .interface_utils import post_notification
from .event import LayerEventType


SESSION_MANAGEMENT_VERSION_KEY = "version"
SESSION_MANAGEMENT_VERSION = "1.0"
MESSAGE_GROUP_KEY = "__SESSION_MANAGEMENT__"
MESSAGE_KEY = "message"
MESSAGE_MERGE_STARTED = "MERGE_STARTED"
MESSAGE_MERGE_FINISHED = "MERGE_FINISHED"
MESSAGE_USER_NAME_KEY = "user_name"
MESSAGE_USER_ID_KEY = "user_id"
MESSAGE_LAYER_IDENTIFIER_KEY = "layer_identifier"


class LiveSessionUser:
    """
    LiveSessionUser represents an peer client instance that joins
    the same Live Session.
    """

    def __init__(self, user_name, user_id, from_app):
        self.__user_name = user_name
        self.__user_id = user_id
        self.__from_app = from_app
        self.__user_color = self.__string_to_rgb(self.user_id)

    @property
    def user_name(self) -> str:
        return self.__user_name

    @property
    def user_id(self) -> str:
        return self.__user_id

    @property
    def from_app(self) -> str:
        return self.__from_app

    @property
    def user_color(self) -> Tuple[int, int, int]:
        """Tuple of RGB color with each channel ranging from [0, 255]."""
        return self.__user_color

    def __string_to_rgb(self, user_id):
        """
        The following implement is ported from:
        https://github.com/dimostenis/color-hash-python/blob/main/colorhash/colorhash.py
        """

        lightness = (0.35, 0.5, 0.65)
        saturation = (0.35, 0.5, 0.65)

        bs = str(user_id).encode("utf-8")
        hash = crc32(bs) & 0xFFFFFFFF
        h = hash % 359
        hash //= 360
        s = saturation[hash % len(saturation)]
        hash //= len(saturation)
        l = lightness[hash % len(lightness)]

        rgb = self.__hsl2rgb((h, s, l))

        return rgb

    def __hsl2rgb(self, hsl) -> Tuple[int, int, int]:
        """
        Convert an HSL color value into RGB.
        >>> hsl2rgb((0, 1, 0.5))
        (255, 0, 0)
        """

        try:
            h, s, l = hsl  # noqa, I tolerate "l"
            h /= 360
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
        except TypeError:
            raise ValueError(hsl)

        rgb: list[int] = []
        for c in (h + 1 / 3, h, h - 1 / 3):
            if c < 0:
                c += 1
            elif c > 1:
                c -= 1

            if c < 1 / 6:
                c = p + (q - p) * 6 * c
            elif c < 0.5:
                c = q
            elif c < 2 / 3:
                c = p + (q - p) * 6 * (2 / 3 - c)
            else:
                c = p
            rgb.append(round(c * 255))

        return tuple(rgb)  # noqa


class LiveSessionChannelManager:
    def __init__(self, current_session, live_syncing_interface):
        self._base_layer_identifier: str = current_session.base_layer_identifier
        self._session_url = current_session.url
        self._session_name: str = current_session.name
        self._channel_url = current_session.channel_url
        self._channel = None
        self._channel_subscriber = None
        self._join_channel_future = None
        self._live_syncing = live_syncing_interface
        self._event_stream = live_syncing_interface._layers_instance.get_event_stream()
        self._peer_users = {}

    def destroy(self):
        self._stop_channel()
        self._live_syncing = None
        self._event_stream = None

    def start_async(self):
        self._join_channel_future = asyncio.ensure_future(self._join_channel_async(self._channel_url))

        return self._join_channel_future

    def stop(self):
        self._stop_channel()

    @property
    def stopped(self):
        return self._channel and self._channel.stopped

    def _send_layer_event(self, event_type: LayerEventType, payload={}):
        payload[MESSAGE_LAYER_IDENTIFIER_KEY] = self._base_layer_identifier
        if payload:
            self._event_stream.push(int(event_type), 0, payload)
        else:
            self._event_stream.push(int(event_type))

    @property
    def peer_users(self) -> Dict[str, LiveSessionUser]:
        return self._peer_users

    async def broadcast_merge_started_message_async(self):
        if self._channel:
            message = {
                MESSAGE_GROUP_KEY: {
                    SESSION_MANAGEMENT_VERSION_KEY: SESSION_MANAGEMENT_VERSION,
                    MESSAGE_KEY: MESSAGE_MERGE_STARTED
                }
            }
            await self._channel.send_message_async(message)

    async def broadcast_merge_done_message_async(self):
        if self._channel:
            message = {
                MESSAGE_GROUP_KEY: {
                    SESSION_MANAGEMENT_VERSION_KEY: SESSION_MANAGEMENT_VERSION,
                    MESSAGE_KEY: MESSAGE_MERGE_FINISHED
                }
            }
            await self._channel.send_message_async(message)

    async def _join_channel_async(self, url):
        # OM-108516: Channel manager needs to be optional.
        try:
            import omni.kit.collaboration.channel_manager as cm
            has_channel_manager = True
        except ImportError:
            has_channel_manager = False

        if has_channel_manager:
            self._channel = await cm.join_channel_async(url)
            if not self._channel:
                post_notification(f"Failed to join channel {url}. Stopping session '{self._session_name}'...", False)
        else:
            self._channel = None
            post_notification(
                f"Failed to start session '{self._session_name}' as Live Session functionality is not supported.", False
            )

        if not self._channel:
            if self._live_syncing:
                self._live_syncing.stop_live_session(self._base_layer_identifier)

            return False

        self._channel_subscriber = self._channel.add_subscriber(self._on_channel_message)

        return True

    def _on_channel_message(self, message):
        try:
            import omni.kit.collaboration.channel_manager as cm
        except ImportError:
            return

        info = None
        from_user = message.from_user
        if message.message_type == cm.MessageType.JOIN:
            if from_user.user_id not in self._peer_users:
                self._peer_users[from_user.user_id] = LiveSessionUser(
                    from_user.user_name, from_user.user_id, from_user.from_app
                )
            info = f"User {message.from_user.user_name} has joined the session '{self._session_name}'."
            self._send_layer_event(
                LayerEventType.LIVE_SESSION_USER_JOINED,
                {
                    MESSAGE_USER_NAME_KEY: from_user.user_name,
                    MESSAGE_USER_ID_KEY: from_user.user_id,
                }
            )
        elif message.message_type == cm.MessageType.LEFT:
            self._peer_users.pop(from_user.user_id, None)
            info = f"User {message.from_user.user_name} has left the session '{self._session_name}."
            self._send_layer_event(
                LayerEventType.LIVE_SESSION_USER_LEFT,
                {
                    MESSAGE_USER_NAME_KEY: from_user.user_name,
                    MESSAGE_USER_ID_KEY: from_user.user_id,
                }
            )
        elif message.message_type == cm.MessageType.HELLO:
            if from_user.user_id not in self._peer_users:
                self._peer_users[from_user.user_id] = LiveSessionUser(
                    from_user.user_name, from_user.user_id, from_user.from_app
                )
            info = f"User {message.from_user.user_name} has joined the session '{self._session_name}'."
            self._send_layer_event(
                LayerEventType.LIVE_SESSION_USER_JOINED,
                {
                    MESSAGE_USER_NAME_KEY: from_user.user_name,
                    MESSAGE_USER_ID_KEY: from_user.user_id,
                }
            )
        elif message.message_type == cm.MessageType.MESSAGE:
            content = message.content.get(MESSAGE_GROUP_KEY, None) or message.content.get(MESSAGE_GROUP_KEY.lower(), None)
            if not content or not isinstance(content, dict):
                return

            message_type = content.get(MESSAGE_KEY, None) or content.get(MESSAGE_KEY.lower(), None)
            if not message_type:
                return

            current_session = self._live_syncing.get_current_live_session(self._base_layer_identifier)
            if not current_session:
                carb.log_error("Invalid state. Live Session is not started but channel is still alive.")
                return

            if message_type.lower() == MESSAGE_MERGE_STARTED.lower():
                if self._live_syncing.is_live_session_merge_notice_muted(self._base_layer_identifier):
                    self._live_syncing.stop_live_session(self._base_layer_identifier)
                else:
                    try:
                        from omni.kit.widget.prompt import PromptButtonInfo, PromptManager
                        PromptManager.post_simple_prompt(
                            "Leave Session",
                            f"`{current_session.owner}' is ending the live session. "
                            "Stop all work and leave the session.",
                            PromptButtonInfo(
                                "LEAVE", lambda: self._live_syncing.stop_live_session(self._base_layer_identifier)
                            ),
                            shortcut_keys=False
                        )
                    except Exception:
                        carb.log_warn("Cannot post prompt as omni.ui is not enabled, stopping live session forcely.")
                        self._live_syncing.stop_live_session(self._base_layer_identifier)
            else:
                return
        elif message.message_type == cm.MessageType.ERROR:
            carb.log_warn(f"Stopping live session: {self._base_layer_identifier} because underlying channel could be broken.")
            self._live_syncing.stop_live_session(self._base_layer_identifier)

        # Don't explicitly make layers backend dependent on notification manager
        if info:
            post_notification(info)
            carb.log_info(info)

    def _stop_channel(self):
        if self._channel_subscriber:
            self._channel_subscriber.unsubscribe()
            self._channel_subscriber = None
        if self._channel:
            self._channel.stop()
        self._channel = None
        self._peer_users = {}
        if self._join_channel_future:
            self._join_channel_future.cancel()
            self._join_channel_future = None
