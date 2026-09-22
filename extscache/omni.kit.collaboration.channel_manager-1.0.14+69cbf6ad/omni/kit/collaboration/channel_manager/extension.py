# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["ChannelManagerExtension", "join_channel_async", "Channel", "ChannelSubscriber"]

import carb
import omni.ext
import omni.client
from .manager import Channel, ChannelManager, ChannelSubscriber


_global_instance = None


class ChannelManagerExtension(omni.ext.IExt):   # pragma: no cover
    def on_startup(self):
        global _global_instance
        _global_instance = self
        self._channel_manager = ChannelManager()
        self._channel_manager.on_startup()

    def on_shutdown(self):
        global _global_instance
        _global_instance = None
        self._channel_manager.on_shutdown()
        self._channel_manager = None

    async def join_channel_async(self, url, get_users_only) -> Channel:
        channel = await self._channel_manager.join_channel_async(url, get_users_only)
        return channel

    def _has_channel(self, url) -> bool:
        """Internal for testing."""

        return self._channel_manager.has_channel(url)

    @staticmethod
    def _get_instance():
        global _global_instance
        return _global_instance

async def join_channel_async(url: str, get_users_only=False) -> Channel:
    """
    Joins a channel and starts listening. The typical life cycle is as follows of a channel session if get_users_only is False:
    1. User joins and sends a JOIN message to the channel.
    2. Other clients receive JOIN message will respond with HELLO to broadcast its existence.
    3. Clients communicate with each other by sending MESSAGE to each other.
    4. Clients send LEFT before quit this channel.

    Args:
        url (str): The channel url to join. The url could be stage url or url with `.__omni_channel__` or `.channel` suffix.
                   If the suffix is not provided, it will be appended internally with `.__omni_channel__` to be compatible with old
                   version.

        get_users_only (bool): It will join channel without sending JOIN/HELLO/LEFT message but only receives message
                          from other clients. For example, it can be used to fetch user list without broadcasting its
                          existence. After joining, all users inside the channel will respond HELLO message.

    Returns:
        omni.kit.collaboration.channel_manager.Channel. The instance of channel that could be used to publish/subscribe
        channel messages.

    Examples:
        >>> import omni.kit.collaboration.channel_manager as nm
        >>>
        >>> async join_channel_async(url):
        >>>     channel = await nm.join_channel_async(url)
        >>>     if channel:
        >>>         channel.add_subscriber(...)
        >>>         await channel.send_message_async(...)
        >>>     else:
        >>>         # Failed to join
        >>>         pass
    """
    if not omni.client.is_omni_objects_enabled(url):
        carb.log_warn(f"Only omni objects enabled URL supports to create channel: {url}.")
        return None

    if not ChannelManagerExtension._get_instance():
        carb.log_warn("Channel Manager Extension is not enabled.")
        return None

    channel = await ChannelManagerExtension._get_instance().join_channel_async(url, get_users_only=get_users_only)
    return channel
