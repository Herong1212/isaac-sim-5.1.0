# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["Channel", "ChannelSubscriber"]

import asyncio
import concurrent.futures
import weakref
import json
import carb
import carb.settings
import omni.client
import omni.kit.app
import time

import omni.kit.collaboration.telemetry
import zlib

from typing import Callable, Dict, List
from .types import Message, MessageType, PeerUser


CHANNEL_PING_TIME_IN_SECONDS = 60   # Period to ping.

KIT_OMNIVERSE_CHANNEL_MESSAGE_HEADER = b'__OVUM__'
KIT_CHANNEL_MESSAGE_VERSION = "3.0"
OMNIVERSE_CHANNEL_URL_SUFFIX = ".__omni_channel__"
OMNIVERSE_CHANNEL_NEW_URL_SUFFIX = ".channel"
MESSAGE_VERSION_KEY = "version"
MESSAGE_FROM_USER_NAME_KEY = "from_user_name"
MESSAGE_CONTENT_KEY = "content"
MESSAGE_TYPE_KEY = "message_type"
MESSAGE_APP_KEY = "app"


def _get_app():  # pragma: no cover
    settings = carb.settings.get_settings()
    app_name = settings.get("/app/name") or "Kit"
    if app_name.lower().endswith(".next"):
        # FIXME: OM-55917: temp hack for Create.
        return app_name[:-5]

    return app_name


def _build_message_in_bytes(from_user, message_type, content):    # pragma: no cover
    content = {
        MESSAGE_VERSION_KEY: KIT_CHANNEL_MESSAGE_VERSION,
        MESSAGE_TYPE_KEY: message_type,
        MESSAGE_FROM_USER_NAME_KEY: from_user,
        MESSAGE_CONTENT_KEY: content,
        MESSAGE_APP_KEY: _get_app(),
    }

    content_bytes = json.dumps(content).encode()
    return KIT_OMNIVERSE_CHANNEL_MESSAGE_HEADER + content_bytes


class ChannelSubscriber:  # pragma: no cover
    """Handler of subscription to a channel."""

    def __init__(self, message_handler: Callable[[Message], None], channel: weakref) -> None:
        """
        Constructor. Internal only.

        Args:
            message_handler (Callable[[Message], None]): Message handler to handle message.
            channel (weakref): Weak holder of channel.
        """

        self._channel = channel
        self._message_handler = message_handler

    def __del__(self):
        self.unsubscribe()

    def unsubscribe(self):
        """Stop subscribe."""

        self._message_handler = None
        if self._channel and self._channel():
            self._channel()._remove_subscriber(self)

    def _on_message(self, message: Message):
        if self._message_handler:
            self._message_handler(message)


class NativeChannelWrapper:  # pragma: no cover
    """
    Channel is the manager that manages message receive and distribution to MessageSubscriber. It works
    in subscribe/publish pattern.
    """

    def __init__(self, url: str, get_users_only):
        """
        Constructor. Internal only.
        """

        self._url = url
        self._logged_user_name = ""
        self._logged_user_id = ""
        self._peer_users: Dict[str, PeerUser] = {}
        self._channel_handler = None
        self._subscribers = []
        self._message_queue = []
        self._stopped = False
        self._get_users_only = get_users_only
        self._stopping = False
        self._last_ping_time = time.monotonic()
        self._last_user_response_time = {}
        self._all_pending_tasks = []
        self._joining = False
        self._telemetry = omni.kit.collaboration.telemetry.Schema_omni_kit_collaboration_1_0()

    def _track_asyncio_task(self, task):
        self._all_pending_tasks.append(task)

    def _remove_asyncio_task(self, task):
        if task in self._all_pending_tasks:
            self._all_pending_tasks.remove(task)

    def _run_asyncio_task(self, func, *args):
        task = asyncio.ensure_future(func(*args))
        self._track_asyncio_task(task)
        task.add_done_callback(lambda task: self._remove_asyncio_task(task))

        return task

    def _remove_all_tasks(self):
        for task in self._all_pending_tasks:
            task.cancel()

        self._all_pending_tasks = []

    def destroy(self):
        self._remove_all_tasks()
        self._telemetry = None

    @property
    def url(self) -> str:
        """The channel url in Omniverse."""

        return self._url

    @property
    def stopped(self) -> bool:
        """Property. If this channel is stopped already."""
        return self._stopped or not self._channel_handler or self._channel_handler.is_finished()

    @property
    def stopping(self) -> bool:
        return self._stopping

    @property
    def logged_user_name(self) -> str:
        """Property. The logged user name for this channel."""

        return self._logged_user_name

    @property
    def logged_user_id(self) -> str:
        """Property. The unique logged user id."""
        return self._logged_user_id

    @property
    def peer_users(self) -> Dict[str, PeerUser]:
        """Property. All the peer clients that joined to this channel."""

        return self._peer_users

    def _emit_channel_event(self, event_name:str):
        """
        Generates a structured log event noting that a join or leave event has occurred.  This event
        is sent through the 'omni.kit.collaboration.telemetry' extension.

        Args:
            event_name: the name of the event to send.  This must be either 'join' or 'leave'.
        """
        # build up the event data to emit.  Note that the live-edit session's URL will be hashed
        # instead of exposed directly.  This is because the URL contains both the USD stage name
        # and potential PII in the session's name tag itself (ie: "Bob_session".  Both of these
        # are potentially considered either personal information or intellectual property and
        # should not be exposed in telemetry events.  The hashed value will at least be stable
        # for any given URL.
        event = omni.kit.collaboration.telemetry.Struct_liveEdit_liveEdit()
        event.id = str(zlib.crc32(bytes(self.url, "utf-8")))
        event.action = event_name

        settings = carb.settings.get_settings()
        cloud_link_id = settings.get("/cloud/cloudLinkId") or ""

        self._telemetry.liveEdit_sendEvent(cloud_link_id, event)

    async def join_channel_async(self):
        """
        Async function. Join Omniverse Channel.

        Args:
            url: The url to create/join a channel.
            get_users_only: Johns channel as a monitor only or not.
        """

        if self._get_users_only:
            carb.log_info(f"Getting users from channel: {self.url}")
        else:
            carb.log_info(f"Starting to join channel: {self.url}")

        if self._channel_handler:
            self._channel_handler.stop()
            self._channel_handler = None

        # Gets the logged user information.
        try:
            result, server_info = await omni.client.get_server_info_async(self.url)
            if result != omni.client.Result.OK:
                return False

            self._logged_user_name = server_info.username
            self._logged_user_id = server_info.connection_id
        except Exception as e:
            carb.log_error(f"Failed to join channel {self.url} since user token cannot be got: {str(e)}.")
            return False

        channel_connect_future = concurrent.futures.Future()

        # TODO: Should this function be guarded with mutex?
        # since it's called in another native thread.
        def on_channel_message(
            result: omni.client.Result, event_type: omni.client.ChannelEvent, from_user: str, content
        ):
            if not channel_connect_future.done():
                if not self._get_users_only:
                    carb.log_info(f"Join channel {self.url} successfully.")
                    self._emit_channel_event("join")

                channel_connect_future.set_result(result == omni.client.Result.OK)

            if result == omni.client.Result.ERROR_CONNECTION:
                carb.log_warn(f"Underlying channel could be broken.")
            elif result != omni.client.Result.OK:
                carb.log_warn(f"Stop channel since it has errors: {result}.")
                self._stopped = True
                return

            self._on_message(event_type, from_user, content)

        self._joining = True
        self._channel_handler = omni.client.join_channel_with_callback(self.url, on_channel_message)
        result = channel_connect_future.result()
        if result:
            if self._get_users_only:
                await self._send_message_internal_async(MessageType.GET_USERS, {})
            else:
                await self._send_message_internal_async(MessageType.JOIN, {})
        self._joining = False

        return result

    def stop(self):
        """Stop this channel."""
        if self._stopping or self.stopped:
            return

        if not self._get_users_only:
            carb.log_info(f"Stopping channel {self.url}")
            self._emit_channel_event("leave")

        self._stopping = True
        return self._run_asyncio_task(self._stop_async)

    async def _stop_async(self):
        if self._channel_handler and not self._channel_handler.is_finished():
            if not self._get_users_only and not self._joining:
                await self._send_message_internal_async(MessageType.LEFT, {})
            self._channel_handler.stop()
        self._channel_handler = None
        self._stopped = True
        self._stopping = False
        self._subscribers.clear()
        self._peer_users.clear()
        self._last_user_response_time.clear()

    def add_subscriber(self, on_message: Callable[[Message], None]) -> ChannelSubscriber:
        subscriber = ChannelSubscriber(on_message, weakref.ref(self))
        self._subscribers.append(weakref.ref(subscriber))

        return subscriber

    def _remove_subscriber(self, subscriber: ChannelSubscriber):
        to_be_removed = []
        for item in self._subscribers:
            if not item() or item() == subscriber:
                to_be_removed.append(item)

        for item in to_be_removed:
            self._subscribers.remove(item)

    async def send_message_async(self, content: dict) -> omni.client.Request:
        if self.stopped or self.stopping:
            return

        return await self._send_message_internal_async(MessageType.MESSAGE, content)

    async def _send_message_internal_async(self, message_type: MessageType, content: dict):
        carb.log_verbose(f"Send {message_type} message to channel {self.url}, content: {content}")
        message = _build_message_in_bytes(self._logged_user_name, message_type, content)
        return await omni.client.send_message_async(self._channel_handler.id, message)

    def _update(self):
        if self.stopped or self._stopping:
            return

        # FIXME: Is this a must?
        pending_messages, self._message_queue = self._message_queue, []
        for message in pending_messages:
            self._handle_message(message[0], message[1], message[2])

        current_time = time.monotonic()
        duration_in_seconds = current_time - self._last_ping_time
        if duration_in_seconds > CHANNEL_PING_TIME_IN_SECONDS:
            self._last_ping_time = current_time
            carb.log_verbose("Ping all users...")
            self._run_asyncio_task(self._send_message_internal_async, MessageType.GET_USERS, {})

        dropped_users = []
        for user_id, last_response_time in self._last_user_response_time.items():
            duration = current_time - last_response_time
            if duration > CHANNEL_PING_TIME_IN_SECONDS:
                dropped_users.append(user_id)

        for user_id in dropped_users:
            peer_user = self._peer_users.pop(user_id, None)
            if not peer_user:
                continue

            message = Message(peer_user, MessageType.LEFT, {})
            self._broadcast_message(message)

    def _broadcast_message(self, message: Message):
        for subscriber in self._subscribers:
            if subscriber():
                subscriber()._on_message(message)

    def _on_message(self, event_type: omni.client.ChannelEvent, from_user: str, content):
        # Queue message handling to main looper.
        self._message_queue.append((event_type, from_user, content))

    def _handle_message(self, event_type: omni.client.ChannelEvent, from_user: str, content):
        # Skip messages if it's sent from me and not an error event
        if not from_user and event_type != omni.client.ChannelEvent.ERROR:
            return

        if from_user is not None:
            self._last_user_response_time[from_user] = time.monotonic()

        peer_user = None
        payload = {}
        message_type = None
        new_user = False
        if event_type == omni.client.ChannelEvent.JOIN:
            # We don't use JOIN from server
            pass
        elif event_type == omni.client.ChannelEvent.LEFT:
            peer_user = self._peer_users.pop(from_user, None)
            if peer_user:
                message_type = MessageType.LEFT
        elif event_type == omni.client.ChannelEvent.DELETED:
            self._channel_handler.stop()
            self._channel_handler = None
        elif event_type == omni.client.ChannelEvent.MESSAGE:
            carb.log_verbose(f"Message received from user with id {from_user}.")
            try:
                header_len = len(KIT_OMNIVERSE_CHANNEL_MESSAGE_HEADER)
                bytes = memoryview(content).tobytes()
                if len(bytes) < header_len:
                    carb.log_error(f"Unsupported message received from user {from_user}.")
                else:
                    bytes = bytes[header_len:]
                message = json.loads(bytes)
            except Exception:
                carb.log_error(f"Failed to decode message sent from user {from_user}.")
                return

            version = message.get(MESSAGE_VERSION_KEY, None)
            if not version or version != KIT_CHANNEL_MESSAGE_VERSION:
                carb.log_warn(f"Message version sent from user {from_user} does not match expected one: {message}.")
                return

            from_user_name = message.get(MESSAGE_FROM_USER_NAME_KEY, None)
            if not from_user_name:
                carb.log_warn(f"Message sent from unknown user: {message}")
                return

            message_type = message.get(MESSAGE_TYPE_KEY, None)
            if not message_type:
                carb.log_warn(f"Message sent from user {from_user} does not include message type.")
                return

            if message_type == MessageType.GET_USERS:
                carb.log_verbose(f"Fetch message from user with id {from_user}, name {from_user_name}.")
                if not self._get_users_only:
                    self._run_asyncio_task(self._send_message_internal_async, MessageType.HELLO, {})

                return

            peer_user = self._peer_users.get(from_user, None)
            if not peer_user:
                # Don't handle non-recorded user's left.
                if message_type == MessageType.LEFT:
                    carb.log_verbose(f"User {from_user}, name {from_user_name} left channel.")
                    return
                else:
                    from_app = message.get(MESSAGE_APP_KEY, "Unknown")
                    peer_user = PeerUser(from_user, from_user_name, from_app)
                    self._peer_users[from_user] = peer_user
                    new_user = True
            else:
                new_user = False

            if message_type == MessageType.HELLO:
                carb.log_verbose(f"Hello message from user with id {from_user}, name {from_user_name}.")
                if not new_user:
                    return
            elif message_type == MessageType.JOIN:
                carb.log_verbose(f"Join message from user with id {from_user}, name {from_user_name}.")
                if not new_user:
                    return

                if not self._get_users_only:
                    self._run_asyncio_task(self._send_message_internal_async, MessageType.HELLO, {})
            elif message_type == MessageType.LEFT:
                carb.log_verbose(f"Left message from user with id {from_user}, name {from_user_name}.")
                self._peer_users.pop(from_user, None)
            else:
                message_content = message.get(MESSAGE_CONTENT_KEY, None)
                if not message_content or not isinstance(message_content, dict):
                    carb.log_warn(f"Message content sent from user {from_user} is empty or invalid format: {message}.")
                    return

                carb.log_verbose(f"Message received from user with id {from_user}: {message}.")
                payload = message_content
                message_type = MessageType.MESSAGE
        elif event_type == omni.client.ChannelEvent.ERROR:
            message_type = MessageType.ERROR

        if message_type == MessageType.ERROR:
            message = Message(None, message_type, {})
            self._broadcast_message(message)
        elif message_type and peer_user:
            # It's possible that user blocks its main thread and hang over the duration time to reponse ping command.
            # This is to notify user is back again.
            if new_user and message_type != MessageType.HELLO and message_type != MessageType.JOIN:
                message = Message(peer_user, MessageType.HELLO, {})
                self._broadcast_message(message)

            message = Message(peer_user, message_type, payload)
            self._broadcast_message(message)


class Channel:  # pragma: no cover
    """Channel represents the instance of an Nucleus Channel."""

    def __init__(self, handler: weakref, channel_manager: weakref) -> None:
        """Internal constructor."""

        self._handler = handler
        self._channel_manager = channel_manager
        if self._handler and self._handler():
            self._url = self._handler().url
            self._logged_user_name = self._handler().logged_user_name
            self._logged_user_id = self._handler().logged_user_id
        else:
            self._url = ""

    @property
    def stopped(self):
        """Whether channel is stopped or not."""

        return not self._handler or not self._handler() or self._handler().stopped

    @property
    def logged_user_name(self):
        """The user name that logs in this channel."""

        return self._logged_user_name

    @property
    def logged_user_id(self):
        """The user id that logs in this channel."""

        return self._logged_user_id

    @property
    def peer_users(self) -> Dict[str, PeerUser]:
        """All the peer clients that joined to this channel."""

        if self._handler and self._handler():
            return self._handler().peer_users

        return None

    @property
    def url(self):
        return self._url

    def stop(self) -> asyncio.Future:
        if not self.stopped and self._channel_manager and self._channel_manager():
            task = self._channel_manager()._stop_channel(self._handler())
        else:
            task = None

        self._handler = None

        return task

    def add_subscriber(self, on_message: Callable[[Message], None]) -> ChannelSubscriber:
        """
        Add subscriber.

        Args:
            on_message (Callable[[Message], None]): The message handler.

        Returns:
            Instance of ChannelSubscriber. The channel will be stopped if instance is release.
            So it needs to hold the instance before it's stopped. You can manually call `stop`
            to stop this channel, or set the returned instance to None.
        """
        if not self.stopped:
            return self._handler().add_subscriber(on_message)

        return None

    async def send_message_async(self, content: dict) -> omni.client.Request:
        """
        Async function. Send message to all peer clients.

        Args:
            content (dict): The message composed in dictionary.

        Return:
            omni.client.Request.
        """
        if not self.stopped:
            return await self._handler().send_message_async(content)

        return None


class ChannelManager:   # pragma: no cover
    def __init__(self) -> None:
        self._all_channels: List[NativeChannelWrapper] = []
        self._update_subscription = None

    def on_startup(self):
        carb.log_info("Starting Omniverse Channel Manager...")
        self._all_channels.clear()
        from carb.eventdispatcher import get_eventdispatcher
        self._update_subscription = get_eventdispatcher().observe_event(
            event_name=omni.kit.app.GLOBAL_EVENT_UPDATE,
            on_event=self._on_update,
            observer_name="omni.kit.collaboration.channel_manager update"
        )

    def on_shutdown(self):
        carb.log_info("Shutting down Omniverse Channel Manager...")

        self._update_subscription = None
        for channel in self._all_channels:
            self._stop_channel(channel)
            channel.destroy()
        self._all_channels.clear()

    def _stop_channel(self, channel: NativeChannelWrapper):
        if channel and not channel.stopping:
            task = channel.stop()

            return task

        return None

    def _on_update(self, _):
        to_be_removed = []
        for channel in self._all_channels:
            if channel.stopped:
                to_be_removed.append(channel)
            else:
                channel._update()

        for channel in to_be_removed:
            channel.destroy()
            self._all_channels.remove(channel)

    # Internal interface
    def has_channel(self, url: str):
        for channel in self._all_channels:
            if url == channel:
                return True

        return False

    async def join_channel_async(self, url: str, get_users_only: bool):
        """
        Async function. Join Omniverse Channel.

        Args:
            url: The url to create/join a channel.
            get_users_only: Joins channel as a monitor only or not.
        """
        channel_wrapper = NativeChannelWrapper(url, get_users_only)
        success = await channel_wrapper.join_channel_async()
        if success:
            self._all_channels.append(channel_wrapper)
            channel = Channel(weakref.ref(channel_wrapper), weakref.ref(self))
        else:
            channel = None

        return channel
