# Copyright (c) 2021-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["get_live_session_name_from_shared_link", "LiveSession", "LiveSyncing", "LiveSessionUser"]

import asyncio
import weakref
import carb
from carb.eventdispatcher import get_eventdispatcher
import carb.settings
import carb.dictionary
import omni.kit.app
import omni.kit.commands
import omni.usd
import urllib

from functools import partial
from typing import List, Callable, Awaitable, Dict, Tuple, Union, Optional
from .layer_utils import LayerUtils
from .interface_utils import get_layer_event_payload, post_notification
from .live_session_channel_manager import LiveSessionChannelManager, LiveSessionUser

from pxr import Sdf, Usd
from .._omni_kit_usd_layers import (
    acquire_live_syncing_interface,
    release_live_syncing_interface,
    ILayersInstance
)
from .event import LayerEventType


def _get_app():  # pragma: no cover
    settings = carb.settings.get_settings()
    app_name = settings.get("/app/name") or "Kit"
    if app_name.lower().endswith(".next"):
        # FIXME: OM-55917: temp hack for Create.
        return app_name[:-5]

    return app_name


def get_live_session_name_from_shared_link(shared_session_link: str) -> str:
    """Gets the name of Live Session from the url."""

    url = omni.client.break_url(shared_session_link)
    session_name = None
    if url.query:
        queries = urllib.parse.parse_qs(url.query)
        values = queries.get("live_session_name", None)
        if values:
            session_name = values[0]

    return session_name


class LiveSession:
    """
    Python instance of ILayersInstance for the convenience of accessing
    and querying properties and states of a Live Session.
    """

    def __init__(self, handle, session_channel, live_syncing):
        """Internal constructor."""

        if session_channel:
            self._session_channel = weakref.ref(session_channel)
        else:
            self._session_channel = None
        self._live_syncing = weakref.ref(live_syncing)
        self._session_handle = None
        self._set_session_handle(handle)

    def _set_session_handle(self, session_handle):
        if self._session_handle == session_handle:
            return

        self._session_handle = session_handle
        interface = self._live_syncing()._live_syncing_interface
        layers_instance = self._live_syncing()._layers_instance
        session_handle = self._session_handle
        self._session_url = interface.get_live_session_url(layers_instance, session_handle)
        self._session_name = interface.get_live_session_name(layers_instance, session_handle)
        self._session_root = interface.get_live_session_root_identifier(layers_instance, session_handle)
        self._channel_url = interface.get_live_session_channel_url(layers_instance, session_handle)
        self._base_layer_identifier = interface.get_live_session_base_layer_identifier(layers_instance, session_handle)
        self._logged_user = None

        url = omni.client.break_url(self._base_layer_identifier)
        self._shared_session_link = omni.client.make_url(
            scheme=url.scheme,
            host=url.host,
            port=url.port,
            user=url.user,
            path=url.path,
            query=f"live_session_name={self._session_name}"
        )

    @property
    def joined(self) -> bool:
        """Returns True if this session is joined locally."""

        if (
            not self._session_handle or
            not self._session_channel or
            not self._session_channel() or
            not self._live_syncing()
        ):
            return False

        interface = self._live_syncing()._live_syncing_interface
        layers_instance = self._live_syncing()._layers_instance
        return interface.is_valid_live_session(layers_instance, self._session_handle)

    @property
    def valid(self) -> bool:
        """Returns true if the session is valid. Or it's removed."""
        live_syncing = self._live_syncing()
        if not live_syncing:
            return False

        interface = live_syncing._live_syncing_interface
        layers_instance = live_syncing._layers_instance
        return interface.is_valid_live_session(layers_instance, self._session_handle)

    @property
    def channel_url(self) -> str:
        """The channel url of the Live Session that shares by all users to do communication."""
        return self._channel_url

    @property
    def base_layer_identifier(self) -> str:
        """The base layer identifier of the Live Session."""
        return self._base_layer_identifier

    @property
    def name(self) -> str:
        """The name of the Live Session."""
        return self._session_name

    @property
    def url(self) -> str:
        """The physical url of the Live Session in the server."""
        return self._session_url

    @property
    def shared_link(self) -> str:
        """
        The session link to be shared. Shared link is different as
        url, so url points to the physical location of the Live Session
        that local user can get access to, while session link is the URL
        that you can share to others, and can be launched from Omniverse launcher
        and other apps could parse it and decide the action from it. The session
        name is passed as the query parameter to the base layer url, for example,
        omniverse://localhost/test/stage.usd?live_session_name=my_session.
        """

        return self._shared_session_link

    @property
    def owner(self) -> str:
        """
        The owner name of the Live Session. It returns the static owner name of the session only.
        If it has multiple instances of the same user join the same session, only one of the owner
        has the real merge_permission.
        """

        if not self.valid:
            return ""

        interface = self._live_syncing()._live_syncing_interface
        layers_instance = self._live_syncing()._layers_instance

        return interface.get_live_session_owner(layers_instance, self._session_handle)

    @property
    def merge_permission(self) -> bool:
        """
        Whether local user has permission to merge the Live Session or not. It's possible that
        the local user is the owner but this returns False as if multiple instances of the same
        user join the same session, only one of them will be the runtime owner.
        """

        if not self.valid:
            return False

        interface = self._live_syncing()._live_syncing_interface
        layers_instance = self._live_syncing()._layers_instance

        return interface.permission_to_merge_session_changes(layers_instance, self._session_handle)

    @property
    def root(self) -> str:
        """The url of the root.live layer for the Live Session in the server."""
        return self._session_root

    @property
    def peer_users(self) -> List[LiveSessionUser]:
        """All peer users in the Live Session if the session is joined."""
        if not self.joined:
            return []

        return list(self._session_channel().peer_users.values())

    @property
    def logged_user_name(self) -> str:
        """The user name that connects the server of base layer. And it's also the user that joins the Live Session."""

        logged_user = self.logged_user

        return logged_user.user_name

    @property
    def logged_user_id(self) -> str:
        """The user id that connects the server of base layer. And it's also the user that joins the Live Session."""

        logged_user = self.logged_user

        return logged_user.user_id

    @property
    def logged_user(self) -> LiveSessionUser:
        """
        The user that connects the server of base layer. It's also the user that joins the Live Session, and
        can be uniquely identified in the Live Session with user id.
        """

        if not self.valid:
            return None

        if self._logged_user is None:
            interface = self._live_syncing()._live_syncing_interface
            layers_instance = self._live_syncing()._layers_instance
            logged_user_name = interface.get_logged_in_user_name_for_layer(layers_instance, self._base_layer_identifier)
            logged_user_id = interface.get_logged_in_user_id_for_layer(layers_instance, self._base_layer_identifier)
            self._logged_user = LiveSessionUser(logged_user_name, logged_user_id, _get_app())

        return self._logged_user

    def get_peer_user_info(self, user_id) -> LiveSessionUser:
        """Gets the info of peer user by user id if this session is joined."""
        if not self.joined:
            return None

        return self._session_channel().peer_users.get(user_id, None)

    def get_last_modified_time(self) -> int:
        """
        Gets the last modified time of the Live Session. The modified time is
        fetched from the session config file. It can be used to sort the Live Session
        list in access order.
        """

        if not self.valid:
            return 0

        interface = self._live_syncing()._live_syncing_interface
        layers_instance = self._live_syncing()._layers_instance

        return interface.get_live_session_last_modified_time_ns(layers_instance, self._session_handle)

    def __str__(self) -> str:
        return f"<root = {self._session_root}, name = {self._session_name}, url = {self._session_url}>"


class _CallbackRegistrySubscription:
    """
    Simple subscription.

    _Event has callback while this object exists.
    """

    def __init__(self, callback_list: List, callback: Callable):
        """
        Save the callback in the given list.
        """
        self.__callback_list: List = callback_list
        self.__callback = callback
        callback_list.append(callback)

    def __del__(self):
        """Called by GC."""
        self.__callback_list.remove(self.__callback)


class LiveSyncing:
    """
    Live Syncing includes the interfaces to management Live Sessions of all layers in the bound UsdContext.
    A Live Session is a concept that extends non-destructive live workflow for USD layers so all connectors
    can join the session to co-work together.

    Each Live Session is bound to an USD file with unique URL to be identified. And it has only unique instance
    in the same UsdContext for each layer, which means the Live Sessions can be joined multiple times.
    User can only join the Live Sessions that belong to the used layers in the bound UsdContext, either those layers
    are added as sublayers or references/payloads. If a layer is added as both a local sublayer or reference/payload,
    the sublayer and reference/payload cannot join the same Live Session at the same time. However, a Live Session
    can be joined multiple times if the corresponding layer is added as multiple references/payloads.

    Thread Safety: All interfaces of LiveSyncing are not thread-safe. And It's recommended to call
    those interfaces in the same loop thread as UsdContext.
    """

    def __init__(self, layers_instance: ILayersInstance, usd_context, layers_state) -> None:
        self._layers_state = layers_state
        self._layers_instance = layers_instance
        self._usd_context = usd_context
        self._live_syncing_interface = acquire_live_syncing_interface()
        self._dictionary = carb.dictionary.get_dictionary()
        self._layers_event_subs = []
        for event in [
            LayerEventType.LIVE_SESSION_STATE_CHANGED,
            LayerEventType.LIVE_SESSION_LIST_CHANGED,
        ]:
            layers_event_sub = self._layers_instance.get_event_stream().create_subscription_to_pop_by_type(
                event, self._on_layer_event, name=f"omni.kit.usd.layers.LiveSyncing {str(event)}"
            )
            self._layers_event_subs.append(layers_event_sub)
        self._stage_event_sub = [
            get_eventdispatcher().observe_event(
                observer_name="omni.kit.usd.layers:live_syncing",
                event_name=self._usd_context.stage_event_name(event),
                on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.OPENING, lambda _: self._on_stage_opening_or_closing()),
                (omni.usd.StageEventType.CLOSING, lambda _: self._on_stage_opening_or_closing()),
                (omni.usd.StageEventType.SAVING, lambda _: self._on_stage_saving())
            )
        ]
        self._session_channels = {}
        self._merging_live_session = False
        self._joining_session = False
        self._silent_leave_layers = set([])
        self._all_live_sessions: Dict[str, LiveSession] = {}

        self._open_stage_callbacks: List = []

        # Hook move prim command to avoid stiching live layer into the re-named prim.
        # It will stop live session before prim is renamed and re-join the session after that.
        # OMPE-14264: Initialize _saved_prim_sessions to be an empty list to fix issue with it being non-iterable
        self._saved_prim_sessions = []
        self._command_callback_ids = []
        for command in ["MovePrim"]:
            command_callback_id = omni.kit.commands.register_callback(
                command, omni.kit.commands.PRE_DO_CALLBACK, partial(self.__on_pre_move_prim, undo=False)
            )
            self._command_callback_ids.append(command_callback_id)

            command_callback_id = omni.kit.commands.register_callback(
                command, omni.kit.commands.POST_DO_CALLBACK, partial(self.__on_post_move_prim, undo=False)
            )
            self._command_callback_ids.append(command_callback_id)

            command_callback_id = omni.kit.commands.register_callback(
                command, omni.kit.commands.PRE_UNDO_CALLBACK, partial(self.__on_pre_move_prim, undo=True)
            )
            self._command_callback_ids.append(command_callback_id)

            command_callback_id = omni.kit.commands.register_callback(
                command, omni.kit.commands.POST_UNDO_CALLBACK, partial(self.__on_post_move_prim, undo=True)
            )
            self._command_callback_ids.append(command_callback_id)

    def __get_context_and_stage(self, stage_or_context):  # pragma: no cover
        if stage_or_context is None:
            usd_context = omni.usd.get_context()
            stage = usd_context.get_stage()
        elif isinstance(stage_or_context, Usd.Stage):
            usd_context = omni.usd.get_context_from_stage(stage_or_context)
            stage = stage_or_context
        elif isinstance(stage_or_context, omni.usd.UsdContext):
            usd_context = stage_or_context
            stage = usd_context.get_stage()
        elif isinstance(stage_or_context, str):
            usd_context = omni.usd.get_context(stage_or_context)
            if usd_context:
                stage = usd_context.get_stage()
            else:
                stage = None
        else:
            usd_context = None
            stage = None

        return usd_context, stage

    def __on_pre_move_prim(self, params, undo):
        if undo:
            prim_path = params.get("path_to", None)
        else:
            prim_path = params.get("path_from", None)
        if not prim_path:
            return

        prim_path = Sdf.Path(prim_path)

        stage_or_context = params.get("stage_or_context", None)
        usd_context, stage = self.__get_context_and_stage(stage_or_context)
        if not usd_context or usd_context != self.usd_context:
            return

        self._saved_prim_sessions = self.get_all_current_live_sessions(prim_path)
        self.stop_live_session(prim_path=prim_path)

    def __on_post_move_prim(self, params, undo):
        if undo:
            prim_path = params.get("path_from", None)
        else:
            prim_path = params.get("path_to", None)
        if not prim_path:
            return

        prim_path = Sdf.Path(prim_path)

        stage_or_context = params.get("stage_or_context", None)
        usd_context, stage = self.__get_context_and_stage(stage_or_context)
        if not usd_context or usd_context != self.usd_context:
            return

        if not stage.GetPrimAtPath(prim_path):
            return

        for live_session in self._saved_prim_sessions:
            self.join_live_session(live_session, prim_path)

        self._saved_prim_sessions = []

    @property
    def usd_context(self) -> omni.usd.UsdContext:
        """Instance of UsdContext."""

        return self._usd_context

    def _reset(self):
        self._silent_leave_layers.clear()
        self._all_live_sessions.clear()
        for session_channel in self._session_channels.values():
            session_channel.destroy()
        self._session_channels.clear()

    @property
    def layers_instance(self) -> ILayersInstance:
        """Native handle of Layers instance that's bound to an UsdContext."""

        return self._layers_instance

    def _on_stage_opening_or_closing(self):
        self._silent_leave_layers.clear()
        self._all_live_sessions.clear()

    def _on_stage_saving(self):
        # If root layer is in a live session, It will cancel save, and notify.
        current_session = self.get_current_live_session()
        if current_session and not current_session.merge_permission:
            self.usd_context.try_cancel_save()
            error_message = "This stage cannot be saved during a Live Session. "
            error_message += "Please leave the session or contact the owner of the session, "
            error_message += f"<{current_session.owner}>."
            post_notification(error_message, False)
            carb.log_warn(error_message)

    def _on_layer_event(self, event: carb.events.IEvent):
        payload = get_layer_event_payload(event)
        if not payload:
            return

        if payload.event_type == LayerEventType.LIVE_SESSION_STATE_CHANGED:
            if self._joining_session or self._merging_live_session:
                return

            for layer_identifier in payload.identifiers_or_spec_paths:
                current_live_session = self.get_current_live_session(layer_identifier)
                if not current_live_session:
                    session_channel = self._session_channels.pop(layer_identifier, None)
                    if session_channel:
                        session_channel.destroy()
                elif current_live_session and not self._session_channels.get(layer_identifier, None):
                    session_channel = LiveSessionChannelManager(current_live_session, self)
                    session_channel.start_async()
                    self._session_channels[layer_identifier] = session_channel
        elif payload.event_type == LayerEventType.LIVE_SESSION_LIST_CHANGED:
            to_remove_sessions = []
            for session_url, session in self._all_live_sessions.items():
                if session.valid:
                    continue

                to_remove_sessions.append(session_url)

            for session_url in to_remove_sessions:
                self._all_live_sessions.pop(session_url)

    def _destroy(self):
        """Destructor. Don't call this manually."""

        self._reset()
        self._stage_event_sub = None
        self._layers_event_subs = []
        self._layers_instance = None
        self._layers_state = None
        self._saved_prim_sessions = []
        release_live_syncing_interface(self._live_syncing_interface)

        for command_callback_id in self._command_callback_ids:
            omni.kit.commands.unregister_callback(command_callback_id)

    def _to_live_session(self, session_handle, base_layer_identifier):
        if not session_handle:
            return None

        session_channel = self._session_channels.get(base_layer_identifier, None)
        session_url = self._live_syncing_interface.get_live_session_url(self._layers_instance, session_handle)
        if not session_url:
            carb.log_error(f"Failed to find session url for the Live Session of layer {base_layer_identifier}.")
            return None

        session = self._all_live_sessions.get(session_url, None)
        if not session:
            session = LiveSession(session_handle, session_channel, self)
            self._all_live_sessions[session_url] = session
        else:
            if session_channel:
                session_channel_weak = weakref.ref(session_channel)
            else:
                session_channel_weak = None
            session._set_session_handle(session_handle)
            session._session_channel = session_channel_weak

        return session

    def get_all_live_sessions(self, layer_identifier: str = None) -> List[LiveSession]:
        """
        Gets all existing Live Sessions on disk (including joined and not joined ones) for a specific layer.
        See `get_current_live_session` to query joined session for a specific layer.

        Args:
            layer_identifier (str): The base layer to query Live Sessions.
                                    If it's empty, it will be root layer by default.

        Returns:
            A list of Live Sessions.
        """

        if not self.usd_context.get_stage():
            return []

        if not layer_identifier:
            layer_identifier = self.usd_context.get_stage().GetRootLayer().identifier

        total_live_sessions = self._live_syncing_interface.get_total_live_sessions(self._layers_instance, layer_identifier)
        all_live_sessions = []
        for i in range(total_live_sessions):
            session_handle = self._live_syncing_interface.get_live_session_at_index(self._layers_instance, layer_identifier, i)
            if not session_handle:
                continue

            all_live_sessions.append(self._to_live_session(session_handle, layer_identifier))

        return all_live_sessions

    def create_live_session(self, name: str, layer_identifier: str = None) -> LiveSession:
        """
        Creates a named Live Session.

        Args:
            name (str): Name of the session. Currently, name should be unique across all Live Sessions.

            layer_identifier (str): The base layer to create a Live Session. If it's not provided,
                                    it will be root layer by default.

        Returns:
            The Live Session handle if it's success, or None otherwise.
            See Layers.get_last_error_type to get more details.
        """

        if not self.usd_context.get_stage():
            return None

        # It's to be compatible with old interface. The second param
        # of old interface is to enable auto_authoring, which is deprecated for now.
        if not layer_identifier or isinstance(layer_identifier, bool):
            layer_identifier = self.usd_context.get_stage().GetRootLayer().identifier

        session_handle = self._live_syncing_interface.create_live_session(self._layers_instance, layer_identifier, name)
        live_session = self._to_live_session(session_handle, layer_identifier)

        return live_session

    def join_live_session(self, live_session: LiveSession, prim_path: Union[Sdf.Path, str] = None) -> bool:
        """
        Joins the Live Session.

        Args:
            live_session (LiveSession): The Live Session to join. The base layer of the Live Session must
                be in the used layers of the current stage.
            prim_path (Union[Sdf.Path, str]): If prim path is provided, it means to join a Live Session for
                a reference or payload prim.

        Returns:
            True if it joins the session successfully. False otherwise.
            See Layers.get_last_error_type to get more details.
        """

        self._joining_session = True
        session_handle = live_session._session_handle
        if not prim_path:
            success = self._live_syncing_interface.join_live_session(self._layers_instance, session_handle)
        else:
            success = self._live_syncing_interface.join_live_session_for_prim(
                self._layers_instance, session_handle, str(prim_path)
            )
        self._joining_session = False

        if success and live_session.base_layer_identifier not in self._session_channels:
            session_channel = LiveSessionChannelManager(live_session, self)
            session_channel.start_async()
            self._session_channels[live_session.base_layer_identifier] = session_channel

        return success

    def join_live_session_by_url(
        self, layer_identifier: str, live_session_url: str, create_if_not_existed: bool = False
    ) -> bool:
        """
        Joins the Live Session specified by the Live Session URL.

        Args:
            layer_identifier (str): The base layer of the Live Session.

            live_session_url (str): The unique URL of the Live Session. The Live Session must be created against
                                    with the base layer, otherwise, it will fail to join.

            create_if_not_existed (bool): Creates the Live Session if it does not exist.

        Returns:
            True if it joins the session successfully. False otherwise.
            See Layers.get_last_error_type to get more details.
        """

        self._joining_session = True
        success = self._live_syncing_interface.join_live_session_by_url(self._layers_instance, layer_identifier, live_session_url, create_if_not_existed)
        self._joining_session = False

        if success and layer_identifier not in self._session_channels:
            live_session = self.get_current_live_session(layer_identifier)
            session_channel = LiveSessionChannelManager(live_session, self)
            session_channel.start_async()
            self._session_channels[live_session.base_layer_identifier] = session_channel

        return success

    def try_cancelling_live_session_join(self, layer_identifier: str) -> Optional[LiveSession]:
        """
        Try to cancel the Live Session when LayerEventType.LIVE_SESSION_JOINING is received.

        Args:
            layer_identifier (str): The base layer to cancel.

        Returns:
            Instance of Live Session if it's cancelled successfully. Or None otherwise.
        """

        session_handle = self._live_syncing_interface.try_cancelling_live_session_join(self._layers_instance, layer_identifier)
        if not session_handle:
            return None

        return self._to_live_session(session_handle, layer_identifier)

    def stop_live_session(self, layer_identifier: str = None, prim_path: Sdf.Path = None):
        """
        Stops the Live Session for specificed layer or prim.

        Args:
            layer_identifier (str): The base layer to stop its current Live Session. If it's None and prim_path is None,
                                    it's root layer by default.
            prim_path (Sdf.Path): The specified prim to stop the Live Session. If prim_path is given, and
                                  layer_identifier is None, it will stop all joined Live Sessions for this prim.
                                  Or if layer_identifier is not None, it will stop only the Live Session for the layer.
        """

        if not self.usd_context.get_stage():
            return

        if not prim_path:
            if not layer_identifier or isinstance(layer_identifier, bool):
                layer_identifier = self.usd_context.get_stage().GetRootLayer().identifier

        self._joining_session = True
        if prim_path:
            self._live_syncing_interface.stop_live_session_for_prim(
                self._layers_instance, str(prim_path), layer_identifier
            )
        else:
            self._live_syncing_interface.stop_live_session(self._layers_instance, layer_identifier)
        self._joining_session = False

        # OMPE-24091
        # If session is stopped due to network error, user information may be altered after re-connecting to server
        # Set logged user as None to force it be updated later
        session_channel = self._session_channels.get(layer_identifier, None)
        session_url = session_channel._session_url if session_channel else None
        session = self._all_live_sessions.get(session_url, None) if session_url else None
        if session:
            session._logged_user = None

        if not self.is_layer_in_live_session(layer_identifier):
            session_channel = self._session_channels.pop(layer_identifier, None)
            if session_channel:
                session_channel.destroy()

    def stop_all_live_sessions(self):
        """Stops all the Live Sessions that are enabled for the current stage."""

        self._joining_session = True
        self._live_syncing_interface.stop_all_live_sessions(self._layers_instance)
        self._joining_session = False

        for session_channel in self._session_channels.values():
            session_channel.destroy()
        self._session_channels.clear()

    def is_stage_in_live_session(self) -> bool:
        """Checks if any layers that are in the used layers of the current stage are in a Live Session."""

        return self._live_syncing_interface.is_stage_in_live_session(self._layers_instance)

    def is_layer_in_live_session(
        self, layer_identifier: str = None, live_prim_only: bool = False
    ) -> bool:
        """
        Checks if the given layer is in a Live Session or not.

        Args:
            layer_identifier (str): Base layer identifier. Root layer by default.
            live_prim_only (bool): When live_prim_only is True, it will only check the Live Sessions
                                   that are bound to reference/payload prims for the base layer.
                                   Otherwise, it will check all. False by default.
        """

        if layer_identifier is None:
            layer_identifier = self.usd_context.get_stage().GetRootLayer().identifier

        if live_prim_only:
            return self._live_syncing_interface.is_layer_in_prim_live_session(self._layers_instance, layer_identifier)
        else:
            return self._live_syncing_interface.is_layer_in_live_session(self._layers_instance, layer_identifier)

    def is_prim_in_live_session(
        self, prim_path: Sdf.Path, layer_identifier: str = None, from_reference_or_payload_only=False,
    ) -> bool:
        """
        If the prim is in any Live Session.

        Args:
            prim_path (Sdf.Path): Prim path to check.
            layer_identifier (str): If layer identifier is specified, it will check if prim is in
                the Live Session of that layer only.
            from_reference_or_payload_only (bool): If it's True, it will check only references and payloads
                to see if the same Live Session is enabled already. Otherwise, it checks both the prim specificed
                by primPath and its references and payloads. This is normally used to check if the Live Session can
                be stopped as the prim that is in the Live Session may not own the Live Session, which is owned by its
                references or payloads, so it cannot stop the Live Session with the specified prim.
        """

        return self._live_syncing_interface.is_prim_in_live_session(
            self._layers_instance, str(prim_path), layer_identifier, from_reference_or_payload_only,
        )

    def is_in_live_session(self) -> bool:
        """[DEPRECATED] If root layer is in a Live Session."""

        if not self.usd_context.get_stage():
            return False

        layer_identifier = self.usd_context.get_stage().GetRootLayer().identifier

        return self.is_layer_in_live_session(layer_identifier)

    def is_live_session_layer(self, layer_identifier: str) -> bool:
        """Checks if the layer is the live layer (.live layer) of a Live Session."""

        return self._live_syncing_interface.is_live_session_layer(self._layers_instance, layer_identifier)

    def get_current_live_session_layers(self, layer_identifier: str = None) -> List[str]:
        """
        [DEPRECATED] Returns the Live Session layers attached to this Live Session of specifc base layer.
        """

        current_live_session = self.get_current_live_session(layer_identifier)
        if current_live_session:
            return [current_live_session.root]

        return []

    def get_current_live_session_peer_users(self, layer_identifier: str = None) -> List[LiveSessionUser]:
        """
        [DEPRECATED] Returns the list of users that joined in this Live Session.

        Args:
            layer_identifier (str): It's root layer if it's not provided.
        """

        current_live_session = self.get_current_live_session(layer_identifier)
        if current_live_session:
            return current_live_session.peer_users

        return []

    def get_live_session_for_live_layer(self, live_layer_identifier: str) -> LiveSession:
        """
        Gets the Live Session that the live layer is attached to.

        Args:
            live_layer_identifier (str): The .live layer that's in the Live Session.
        """

        session_handle = self._live_syncing_interface.get_live_session_for_live_layer(
            self._layers_instance, live_layer_identifier
        )
        if not session_handle:
            return None

        base_layer_identifier = self._live_syncing_interface.get_live_session_base_layer_identifier(
            self._layers_instance, session_handle
        )
        return self._to_live_session(session_handle, base_layer_identifier)

    def get_current_live_session(self, layer_identifier: str = None) -> LiveSession:
        """
        Gets the current Live Session of the base layer joined.

        Args:
            layer_identifier (str): Base layer identifier. It's root layer if it's not provided.
        """

        if not self.usd_context.get_stage():
            return None

        if layer_identifier is None:
            layer_identifier = self.usd_context.get_stage().GetRootLayer().identifier

        session_handle = self._live_syncing_interface.get_current_live_session(self._layers_instance, layer_identifier)
        if not session_handle:
            return None

        return self._to_live_session(session_handle, layer_identifier)

    def get_all_current_live_sessions(self, prim_path: Sdf.Path = None) -> List[LiveSession]:
        """
        Gets all Live Sessions that are joined for all sublayers of the stage or a specific prim.

        Args:
            prim_spec (Sdf.Path): Specified prim to query. If prim_path is not None, it will
                return all live sessions joined for this prim. If it's None, it will return
                the live sessions joined for all sublayers of the current stage.
        """
        all_joined_sessions = []
        if not prim_path:
            layer_identifiers = LayerUtils.get_all_sublayers(self.usd_context.get_stage(), True, True, False)
            for layer_identifier in layer_identifiers:
                if layer_identifier.endswith(".live"):
                    continue

                current_session = self.get_current_live_session(layer_identifier)
                if current_session:
                    all_joined_sessions.append(current_session)
        else:
            prim_path = Sdf.Path(prim_path)
            for layer_identifier in self._session_channels.keys():
                session_handle = self._live_syncing_interface.get_current_live_session(
                    self._layers_instance, layer_identifier
                )
                if not session_handle:
                    continue

                all_prim_paths = self.__get_live_session_prim_paths(session_handle)
                if prim_path in all_prim_paths:
                    all_joined_sessions.append(self._to_live_session(session_handle, layer_identifier))

        return all_joined_sessions

    def __get_live_session_prim_paths(self, session_handle):
        """Gets the prim that joins this Live Session."""

        item = self._live_syncing_interface.get_live_session_prim_paths(
            self._layers_instance, session_handle
        )
        if not item:
            return []

        try:
            all_prim_paths = []
            count = self._dictionary.get_item_child_count(item)

            for i in range(count):
                path_item = self._dictionary.get_item_child_by_index(item, i)
                prim_path = self._dictionary.get_as_string(path_item)
                if not prim_path:
                    continue

                all_prim_paths.append(Sdf.Path(prim_path))
        finally:
            self._dictionary.destroy_item(item)

        return all_prim_paths

    def get_live_session_by_url(self, session_url) -> LiveSession:
        """
        Gets the Live Session by the url. It can only get the Live Session belongs to one of the used layers
        in the current stage.
        """

        session_handle = self._live_syncing_interface.get_live_session_by_url(self._layers_instance, session_url)
        if not session_handle:
            return None

        base_layer_identifier = self._live_syncing_interface.get_live_session_base_layer_identifier(
            self._layers_instance, session_handle
        )

        return self._to_live_session(session_handle, base_layer_identifier)

    def find_live_session_by_name(self, layer_identifier: str, session_name: str) -> LiveSession:
        """
        Finds the Live Session with name specified by `session_name`. If it has multiple sessions that
        has the same name, it will return the first one found.

        Args:
            layer_identifier (str): The base layer to search Live Sessions.
            session_name (str): The session name.
        """

        session_handle = self._live_syncing_interface.find_live_session_by_name(
            self._layers_instance, layer_identifier, session_name
        )

        return self._to_live_session(session_handle, layer_identifier)

    @property
    def permission_to_merge_current_session(self, layer_identifier: str = None) -> bool:
        """
        [DEPRECATED] Checks to see if it can merge the current Live Session of specified layer.

        Args:
            layer_identifier (str): The base layer of the Live Session. It's root layer if it's not provided.
        """

        current_session = self.get_current_live_session(layer_identifier)
        if not current_session:
            return False

        return current_session.merge_permission

    def merge_live_session_changes(self, layer_identifier: str, stop_session: bool) -> bool:
        """
        Merge Live Session for base layer.

        Args:
            layer_identifier (str): The base layer to merge Live Session.
            stop_session (bool): Stops the Live Session or not after merging.

        Returns:
            True if it's successful, or False otherwise. If it returns False,
            it's possible that the layer is not in the used layers of the current stage. Or
            it has no Live Session joined. Or it has not permissions to merge the Live Session.
            See Layers.get_last_error_type to get more details.
        """
        return self._live_syncing_interface.merge_live_session_changes(
            self._layers_instance, layer_identifier, stop_session
        )

    def merge_live_session_changes_to_specific_layer(
        self, layer_identifier: str,
        target_layer_identifier: str,
        stop_session: bool, clear_target_layer: bool
    ) -> bool:
        """
        Merge Live Session for base layer to specified target layer.

        Args:
            layer_identifier (str): The base layer to merge Live Session.
            target_layer_identifier (str): The target layer to merge the Live Session.
            stop_session (bool): Stops the Live Session or not after merging.
            clear_target_layer (bool): If it needs to clear the target layer before merging.

        Returns:
            True if it's successful, or False otherwise. If it returns False,
            it's possible that the layer is not in the used layers of the current stage. Or
            it has no Live Session joined. Or it has not permissions to merge the Live Session.
            See Layers.get_last_error_type to get more details.
        """

        return self._live_syncing_interface.merge_live_session_changes_to_specific_layer(
            self._layers_instance,
            layer_identifier,
            target_layer_identifier,
            stop_session,
            clear_target_layer
        )

    def merge_changes_to_base_layers(self, stop_session: bool) -> bool:
        """
        [DEPRECATED] Merges changes of root layer's Live Session to its base layer.
        """

        if not self.usd_context.get_stage():
            return False

        layer_identifier = self.usd_context.get_stage().GetRootLayer().identifier
        return self.merge_live_session_changes(layer_identifier, stop_session)

    def merge_changes_to_specific_layer(
        self, target_layer_identifier: str, stop_session: bool, clear_target_layer: bool
    ) -> bool:
        """
        [DEPRECATED] Merges changes of root layer's Live Session to specified layer.
        """

        if not self.usd_context.get_stage():
            return False

        base_layer_identifier = self.usd_context.get_stage().GetRootLayer().identifier
        return self.merge_live_session_changes_to_specific_layer(
            base_layer_identifier, target_layer_identifier, stop_session, clear_target_layer
        )

    async def broadcast_merge_started_message_async(self, layer_identifier: str = None):
        """
        Broadcasts merge started message to other peer clients. This is normally
        called before merging the Live Session to its base layer.
        """

        if not self.usd_context.get_stage():
            return

        if not layer_identifier:
            layer_identifier = self.usd_context.get_stage().GetRootLayer().identifier

        session_channel = self._session_channels.get(layer_identifier, None)
        if session_channel:
            await session_channel.broadcast_merge_started_message_async()

    async def broadcast_merge_done_message_async(self, destroy: bool = True, layer_identifier: str = None):
        """
        Broadcasts merge finished message to other peer clients. This is normally
        called after merging the Live Session to its base layer.

        "Args:
            destroy (bool): If it needs to destroy the session channel after merging.

            layer_identifier (str): The base layer of the Live Session.
        """

        if not layer_identifier:
            layer_identifier = self.usd_context.get_stage().GetRootLayer().identifier

        session_channel = self._session_channels.get(layer_identifier, None)
        if session_channel:
            await session_channel.broadcast_merge_done_message_async()
            if destroy and not self.is_layer_in_live_session(layer_identifier):
                session_channel.destroy()
                self._session_channels.pop(layer_identifier, None)

    async def merge_and_stop_live_session_async(
        self, target_layer: str = None, comment="",
        pre_merge: Callable[[LiveSession], Awaitable] = None,
        post_merge: Callable[[bool], Awaitable] = None,
        layer_identifier: str = None
    ) -> bool:
        """Saves chagnes of Live Session to their base layer if it's in live mode.

        Args:
            target_layer (str): Target layer to merge all live changes to.

            comment (str): The checkpoint comments.

            pre_merge (Callable[[LiveSession], Awaitable]): It will be called before merge.

            post_merge (Callable[[bool, str], Awaitable]): It will be called after merge is done. The first
                                                           param means if it's successful, and the second includes
                                                           the error message if it's not.

            layer_identifier (str): The base layer of the Live Session. It's root layer if it's not provided.
        """

        if not self.usd_context.get_stage():
            return False

        if not layer_identifier:
            layer_identifier = self.usd_context.get_stage().GetRootLayer().identifier

        current_session = self.get_current_live_session(layer_identifier)
        if pre_merge:
            await pre_merge(current_session)

        error = None
        success = True
        try:
            import omni.usd_resolver

            if not self.is_layer_in_live_session(layer_identifier):
                error = "Cannot merge live layers since it's not in any Live Sessions."
                success = False
                return False

            if self.is_layer_in_live_session(layer_identifier, True):
                error = "Cannot merge live layers since it's in a prim's Live Session."
                success = False
                return False

            if not current_session.merge_permission:
                error = f"Cannot merge live layers since only owner {current_session.owner} can merge them."
                success = False
                return False

            if self._merging_live_session:
                error = "Current session is already in progress of merging."
                success = False
                return False

            self._merging_live_session = True

            def report_checkpoint_errors(failed_layers):
                nonlocal error
                nonlocal success
                success = False
                if len(failed_layers) == 1:
                    error = f"Failed to create checkpoints for {failed_layers[0]}."
                elif len(failed_layers) > 1:
                    error = "Failed to create checkpoints for several layers. Please check console for more details."

            all_live_layers = [current_session.root]
            _, failed_layers = await LayerUtils.create_checkpoint_async(all_live_layers, comment, True)
            if failed_layers:
                report_checkpoint_errors(failed_layers)
                return False

            comment = f"Merge changes from live {current_session.name}: {comment}"
            omni.usd_resolver.set_checkpoint_message(comment)
            # Clear checkpoint message to ensure comment is not used in future file operations.

            if not target_layer:
                success = self.merge_live_session_changes(layer_identifier, True)
            else:
                target_layer_handle = Sdf.Layer.FindOrOpen(target_layer)
                if not target_layer_handle:
                    error = f"Failed to merge live changes to {target_layer} as target file cannot be found."
                    success = False
                else:
                    clear_target = not self.usd_context.get_stage().HasLocalLayer(target_layer_handle)
                    success = self.merge_live_session_changes_to_specific_layer(
                        layer_identifier, target_layer, True, clear_target
                    )

            if not success:
                error = "Failed to merge live changes due to permission issues."
        finally:
            omni.usd_resolver.set_checkpoint_message("")

            if not success and error:
                carb.log_error(error)
                post_notification(error, False)

            if post_merge:
                await post_merge(success)

            if not self.is_layer_in_live_session(layer_identifier):
                session_channel = self._session_channels.pop(layer_identifier, None)
                if session_channel:
                    session_channel.destroy()

            self._merging_live_session = False

            return success

    def mute_live_session_merge_notice(self, layer_identifier: str):
        """
        By default, when session owner merges the session, it will
        notify peer clients to leave the session by showing a prompt.
        This is used to disable the prompt and stop session directly
        so it will not be disruptive especially for applications that
        don't have layer window and manages all layers' Live Sessions
        with scripting and don't want to receive prompt for leaving
        sessions.
        """

        self._silent_leave_layers.add(layer_identifier)

    def unmute_live_session_merge_notice(self, layer_identifier: str):
        """Remove layer identifier from mute list."""

        self._silent_leave_layers.discard(layer_identifier)

    def is_live_session_merge_notice_muted(self, layer_identifier: str) -> bool:
        """Checks if layer identifier is in the mute list."""

        return layer_identifier in self._silent_leave_layers

    async def open_stage_with_live_session_async(self, stage_url, session_name=None) -> Tuple[bool, str]:
        """
        Opens stage with Live Session joined. This function is used to reduce the composition cost of
        opening a stage, then joining a Live Session by preparing the Live Session in the session layer
        before opening the stage. It supports to pass the name of Live Session as query string, for example,
        `omniverse://localhost/test/stage.usd?live_session_name=my_session`.

        Args:
            stage_url (str): The stage url to open.
            session_name (str): If the session name is not provided in the stage url, this param will be used.
                If both stage url and this param don't include a valid session, it will return false.

        Returns:
            A (bool, str) tutple, where the first element means if it's success, and the error string int the second.
        """

        final_session_name = get_live_session_name_from_shared_link(stage_url)
        if not final_session_name:
            final_session_name = session_name

        if not final_session_name:
            carb.log_error(f"Failed to open stage {stage_url} with live session as live session is not provided.")

            return False, "ERROR: Live Session Not Found"

        url = omni.client.break_url(stage_url)
        stage_url = omni.client.make_url(
            scheme=url.scheme, user=url.user,
            host=url.host, port=url.port,
            path=url.path
        )

        waiting_prompt = None
        try:
            from omni.kit.widget.prompt import PromptManager

            # Waits 2 updates to make sure modal dialog is centered. This is issue from omni.ui that
            # shows a modal dialog when the last modal dialog is shown will not be positioned correctly.
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
            waiting_prompt = PromptManager.post_simple_prompt(
                "Please Wait",
                f"Opening stage {stage_url} with Live Session `{final_session_name}`...",
                None,
                shortcut_keys=False,
                width=500,
                callback_addons=self._open_stage_callbacks,
            )

            # Waits 2 updates to make sure it's shown.
            await omni.kit.app.get_app().next_update_async()
            await omni.kit.app.get_app().next_update_async()
        except Exception:
            pass

        def on_stage_result(future: asyncio.Future, prompt, result: bool, err_msg: str):
            if prompt:
                prompt.hide()

            if not future.done():
                future.set_result((result, err_msg))
        open_stage_thread = None
        try:
            future = asyncio.Future()
            # OMPE-49021: Put open stage in a thread to avoid blocking the main thread.This way when authentication against
            # the server is required, we can take advantage of the registered callback to display connector dialog to
            # cancel the authentication request. Otherwise if auth is cancelled via closing the browser, the app will hang.
            import threading
            def open_stage_task():
                self._live_syncing_interface.open_stage_with_live_session(
                    self._layers_instance, stage_url, final_session_name,
                    partial(on_stage_result, future, waiting_prompt)
                )

            open_stage_thread = threading.Thread(target=open_stage_task)
            open_stage_thread.start()

            return await future
        except Exception:
            waiting_prompt.hide()
        finally:
            open_stage_thread.join()

        return (False, "ERROR: Unknown")

    def register_open_stage_addon(self, callback):
        return _CallbackRegistrySubscription(self._open_stage_callbacks, callback)
