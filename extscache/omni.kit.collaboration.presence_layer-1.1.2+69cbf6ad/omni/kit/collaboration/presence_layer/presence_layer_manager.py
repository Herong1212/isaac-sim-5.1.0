# Copyright (c) 2018-2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["PresenceLayerAPI"]

import asyncio
import carb
from carb.eventdispatcher import get_eventdispatcher
import omni.client
import omni.usd
import omni.kit.usd.layers as layers
import omni.kit.app

from omni.kit.async_engine import run_coroutine

from pxr import Sdf, Usd, UsdGeom, Tf
from typing import Dict, List, Union, Set

from .utils import (
    get_user_id_from_path, get_bound_camera_property_path, get_following_user_property_path,
    get_selection_property_path, get_user_shared_root_path, get_or_create_property_spec,
    is_local_builtin_camera
)
from .event import PresenceLayerEventType, EVENT_PAYLOAD_KEY

from .constants import *
from .peer_user_shared_data import PeerUserSharedData


class PresenceLayerChanges:
    def __init__(self) -> None:
        self.clear()

    def clear(self):
        self.bound_camera_changed_ids = set()
        self.selection_changed_ids = set()
        self.following_user_changed_ids = set()
        self.camera_info_changes = {}
        self.resynced_camera_ids = set()

    def is_empty(self):
        return (
            not self.bound_camera_changed_ids and
            not self.selection_changed_ids and
            not self.following_user_changed_ids and
            not self.camera_info_changes and
            not self.resynced_camera_ids
        )

    def add_camera_info_change(self, user_id, path):
        changes = self.camera_info_changes.get(user_id, None)
        if changes is None:
            self.camera_info_changes[user_id] = set()

        # Changed property name
        self.camera_info_changes[user_id].add(path.name)

    def __str__(self):
        return (f"Bound Camera Changed: {self.bound_camera_changed_ids}, "
            f"Seletion Changed: {self.selection_changed_ids}, "
            f"Following User Changed: {self.following_user_changed_ids}, "
            f"Camera Info Changed: {self.camera_info_changes}, "
            f"Camera Resynced: {self.resynced_camera_ids}")


class PresenceLayerManager:
    def __init__(self, usd_context):
        self.__usd_context = usd_context
        self.__live_syncing = layers.get_live_syncing(self.__usd_context)
        self.__layers = layers.get_layers(self.__usd_context)

        self.__shared_data_stage = None

        self.__peer_users: Dict[str, PeerUserSharedData] = {}

        # Fast access to query the follow relationship. Key is the
        # user id that's followed, and values are the user ids that
        # are currently following this user.
        self.__user_following_map: Dict[str, Set[str]] = {}

        self.__layers_event_subscriptions = []
        self.__stage_event_subscription = None
        self.__shared_stage_objects_changed = None

        self.__delayed_changes_handle_task = None
        self.__local_following_user_id = None

        self.__pending_changed_paths = set()

    def start(self):
        for event in [
            layers.LayerEventType.LIVE_SESSION_STATE_CHANGED,
            layers.LayerEventType.LIVE_SESSION_USER_JOINED,
            layers.LayerEventType.LIVE_SESSION_USER_LEFT,
            layers.LayerEventType.LIVE_SESSION_MERGE_ENDED,
        ]:
            layers_event_sub = self.__layers.get_event_stream().create_subscription_to_pop_by_type(
                event, self.__on_layers_event, name=f"Layers event: omni.kit.collaboration.presence_layer {str(event)}",
                order=LAYER_SUBSCRIPTION_ORDER
            )
            self.__layers_event_subscriptions.append(layers_event_sub)

        self.__stage_event_subscription = [
            get_eventdispatcher().observe_event(
                observer_name="omni.kit.collaboration.presence_layer:presence_layer_manager",
                event_name=self.__usd_context.stage_event_name(event),
                on_event=func
            )
            for event, func in (
                (omni.usd.StageEventType.SELECTION_CHANGED, lambda _: self.__on_selection_changed()),
                (omni.usd.StageEventType.CLOSING, lambda _: self.__stop_subscription())
            )
        ]

        stage_url = self.__usd_context.get_stage_url()
        if omni.client.is_omni_objects_enabled(stage_url):
            self.__on_session_state_changed()

    def __on_selection_changed(self):
        if not self.__shared_data_stage:
            return

        selection = self.__usd_context.get_selection()
        selected_prim_paths = selection.get_selected_prim_paths() or []

        current_session = self.__live_syncing.get_current_live_session()
        if not current_session:
            return

        logged_user_id = current_session.logged_user_id
        selection_property_path = get_selection_property_path(logged_user_id)

        with Sdf.ChangeBlock():
            property_spec = get_or_create_property_spec(
                self.__shared_data_stage.GetRootLayer(), selection_property_path,
                Sdf.ValueTypeNames.StringArray
            )
            property_spec.default = selected_prim_paths

    def __start_subscription(self):
        # Skip it if one of its sublayer is in live session already.
        if self.__shared_data_stage:
            return

        current_session = self.__live_syncing.get_current_live_session()
        if not current_session:
            return

        self.__shared_data_stage = self.__create_or_open_shared_stage(current_session)
        if not self.__shared_data_stage:
            return

        self.__shared_stage_objects_changed = Tf.Notice.Register(
            Usd.Notice.ObjectsChanged, self.__on_shared_usd_changed, self.__shared_data_stage
        )

        stage = self.__usd_context.get_stage()
        target_layer = stage.GetSessionLayer()
        with Sdf.ChangeBlock():
            prim_spec = Sdf.CreatePrimInLayer(target_layer, LOCAL_SESSION_LAYER_SHARED_DATA_ROOT_PATH)
            prim_spec.specifier = Sdf.SpecifierDef
            prim_spec.typeName = "Scope"

        with Usd.EditContext(stage, target_layer):
            prim = stage.GetPrimAtPath(LOCAL_SESSION_LAYER_SHARED_DATA_ROOT_PATH)
            omni.usd.editor.set_hide_in_stage_window(prim, True)
            omni.usd.editor.set_hide_in_ui(prim, True)

        for peer_user in current_session.peer_users:
            self.__track_new_user(peer_user.user_id)

    def __stop_subscription(self):
        for peer_user in self.__peer_users.values():
            peer_user.destroy()
        self.__peer_users.clear()
        self.__pending_changed_paths.clear()

        self.__shared_data_stage = None
        if self.__shared_stage_objects_changed:
            self.__shared_stage_objects_changed.Revoke()
            self.__shared_stage_objects_changed = None

        if self.__delayed_changes_handle_task:
            self.__delayed_changes_handle_task.cancel()
            self.__delayed_changes_handle_task = None

        local_stage = self.__usd_context.get_stage()
        if local_stage:
            layers.LayerUtils.remove_prim_spec(
                local_stage.GetSessionLayer(),
                LOCAL_SESSION_LAYER_SHARED_DATA_ROOT_PATH
            )

        self.__user_following_map.clear()

    def stop(self):
        self.__stop_subscription()
        self.__layers_event_subscriptions = []
        self.__stage_event_subscription = None

    @carb.profiler.profile
    def __notify_changes(self, pending_changes):
        if pending_changes.is_empty():
            return

        event_stream = layers.get_layers(self.__usd_context).get_event_stream()
        if not event_stream:
            return

        def __check_and_send_events(event_type, changed_ids, lambda_filter):
            valid_users = []
            for user_id in changed_ids:
                peer_user = self.__peer_users.get(user_id, None)
                if not peer_user or not lambda_filter(peer_user):
                    continue

                valid_users.append(user_id)

            if valid_users:
                event_stream.push(int(event_type), 0, {EVENT_PAYLOAD_KEY: valid_users})

            return valid_users

        all_bound_camera_changed_ids = set()
        for user_id in pending_changes.following_user_changed_ids:
            peer_user = self.__peer_users.get(user_id, None)
            if not peer_user or not peer_user.update_following_user():
                continue

            old_following_user_id = peer_user.following_user_id
            if old_following_user_id:
                self.__remove_following_user(user_id, old_following_user_id)

            new_following_user_id = peer_user.following_user_id
            if new_following_user_id:
                self.__track_following_user(user_id, new_following_user_id)
            all_bound_camera_changed_ids.add(user_id)

        for user_id in pending_changes.bound_camera_changed_ids:
            peer_user = self.__peer_users.get(user_id, None)
            if not peer_user or not peer_user.update_bound_camera():
                continue

            all_bound_camera_changed_ids.add(user_id)
            # Updates all users that are currently following this user also.
            all_bound_camera_changed_ids.update(self.get_all_following_users(user_id))

        if all_bound_camera_changed_ids:
            event_stream.push(
                int(PresenceLayerEventType.BOUND_CAMERA_CHANGED), 0,
                {EVENT_PAYLOAD_KEY: list(all_bound_camera_changed_ids)}
            )

        __check_and_send_events(
            PresenceLayerEventType.BOUND_CAMERA_RESYNCED,
            pending_changes.resynced_camera_ids,
            lambda user: True
        )
        __check_and_send_events(
            PresenceLayerEventType.SELECTIONS_CHANGED,
            pending_changes.selection_changed_ids,
            lambda user: user.update_selections()
        )

        camera_info_changes = pending_changes.camera_info_changes
        if camera_info_changes:
            # FIXME: WA to make sure changes can be serialized to event stream.
            camera_changes_payload = {}
            with Sdf.ChangeBlock():
                for user_id, property_names in camera_info_changes.items():
                    peer_user = self.__peer_users.get(user_id, None)
                    if property_names:
                        peer_user.replicate_bound_camera_to_local(property_names)
                    camera_changes_payload[user_id] = list(property_names)

            event_stream.push(
                int(PresenceLayerEventType.BOUND_CAMERA_PROPERTIES_CHANGED),
                payload=camera_changes_payload
            )

    @carb.profiler.profile
    async def __handling_pending_changes(self):
        pending_changes = PresenceLayerChanges()
        pending_changed_paths = self.__pending_changed_paths
        self.__pending_changed_paths = set()
        for path in pending_changed_paths:
            if path == SESSION_SHARED_LAYER_ROOT_PATH or path == Sdf.Path.absoluteRootPath:
                pending_changes.bound_camera_changed_ids.update(self.__peer_users.keys())
                pending_changes.following_user_changed_ids.update(self.__peer_users.keys())
                pending_changes.selection_changed_ids.update(self.__peer_users.keys())
                pending_changes.resynced_camera_ids.update(self.__peer_users.keys())
                break

            user_id = get_user_id_from_path(path)
            peer_user = self.__peer_users.get(user_id)
            if not peer_user:
                continue

            if path == peer_user.shared_root_path:
                pending_changes.bound_camera_changed_ids.add(user_id)
                pending_changes.following_user_changed_ids.add(user_id)
                pending_changes.selection_changed_ids.add(user_id)
                pending_changes.resynced_camera_ids.add(user_id)
                continue

            # Checks bound_camera property under user root
            if peer_user.is_following_user_property_affected(path):
                pending_changes.following_user_changed_ids.add(user_id)
            elif peer_user.is_selection_property_affected(path):
                pending_changes.selection_changed_ids.add(user_id)
            elif peer_user.is_bound_camera_property_affected(path):
                pending_changes.bound_camera_changed_ids.add(user_id)
            elif peer_user.is_builtin_camera_affected(path):
                # Only sync properties that are under camera prim.
                if path.IsPropertyPath():
                    pending_changes.add_camera_info_change(user_id, path)
                else:
                    pending_changes.resynced_camera_ids.add(user_id)

        self.__notify_changes(pending_changes)
        self.__delayed_changes_handle_task = None

    @carb.profiler.profile
    def __on_shared_usd_changed(self, notice, sender):
        if not sender or sender != self.__shared_data_stage:
            return

        self.__pending_changed_paths.update(notice.GetResyncedPaths())
        self.__pending_changed_paths.update(notice.GetChangedInfoOnlyPaths())
        if not self.__pending_changed_paths:
            return

        if not self.__delayed_changes_handle_task or self.__delayed_changes_handle_task.done():
            self.__delayed_changes_handle_task = run_coroutine(self.__handling_pending_changes())

    def __create_or_open_shared_stage(self, session: layers.LiveSession):
        session_url = session.url
        if not session_url.endswith("/"):
            session_url += "/"

        shared_data_layer_path = omni.client.combine_urls(session_url, SESSION_SHARED_USER_LAYER)
        layer = Sdf.Layer.FindOrOpen(shared_data_layer_path)
        if not layer:
            layer = Sdf.Layer.CreateNew(shared_data_layer_path)

        if not layer:
            carb.log_warn(f"Failed to open shared data layer {shared_data_layer_path}.")
            return None

        Sdf.CreatePrimInLayer(layer, SESSION_SHARED_LAYER_ROOT_PATH)
        stage = Usd.Stage.Open(layer)

        return stage

    @property
    def shared_data_stage(self) -> Usd.Stage:
        return self.__shared_data_stage

    def __on_session_state_changed(self):
        if not self.__live_syncing.is_in_live_session():
            self.__stop_subscription()
        else:
            self.__start_subscription()

    def __track_new_user(self, user_id):
        if user_id in self.__peer_users:
            return

        if not self.__shared_data_stage:
            return

        current_session = self.__live_syncing.get_current_live_session()
        if not current_session:
            return

        user_info = current_session.get_peer_user_info(user_id)
        if not user_info:
            return

        peer_user = PeerUserSharedData(self.__usd_context, self.__shared_data_stage, user_info)
        self.__peer_users[user_id] = peer_user
        following_user_id = peer_user.following_user_id
        if following_user_id:
            self.__track_following_user(user_id, following_user_id)

    def __track_following_user(self, user_id, following_user_id):
        user_ids = self.__user_following_map.get(following_user_id, None)
        if not user_ids:
            user_ids = set()
            self.__user_following_map[following_user_id] = user_ids

        user_ids.add(user_id)

    def __untrack_followed_user(self, user_id):
        for following_users in self.__user_following_map.values():
            following_users.discard(user_id)

        self.__user_following_map.pop(user_id, None)

    def __remove_following_user(self, user_id, followed_user_id):
        """Removes user_id from list that are currently following followed_user_id."""

        user_list = self.__user_following_map.get(followed_user_id, None)
        if not user_list:
            return False

        if user_id in user_list:
            user_list.discard(user_id)
            return True

        return False

    def __untrack_user(self, user_id):
        self.__untrack_followed_user(user_id)
        peer_user = self.__peer_users.pop(user_id, None)
        if peer_user:
            peer_user.destroy()

    def __on_layers_event(self, event):
        payload = layers.get_layer_event_payload(event)
        if not payload:
            return

        interested_events = [
            layers.LayerEventType.LIVE_SESSION_STATE_CHANGED,
            layers.LayerEventType.LIVE_SESSION_USER_JOINED,
            layers.LayerEventType.LIVE_SESSION_USER_LEFT,
            layers.LayerEventType.LIVE_SESSION_MERGE_ENDED
        ]

        if payload.event_type not in interested_events:
            return

        if not payload.is_layer_influenced(self.__usd_context.get_stage_url()):
            return

        if payload.event_type == layers.LayerEventType.LIVE_SESSION_STATE_CHANGED:
            self.__on_session_state_changed()
        elif payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_JOINED:
            # Creates user shared data
            # Try to copy camera info and add widgets for the bound camera.
            self.__track_new_user(payload.user_id)
        elif payload.event_type == layers.LayerEventType.LIVE_SESSION_USER_LEFT:
            self.__untrack_user(payload.user_id)
        elif payload.event_type == layers.LayerEventType.LIVE_SESSION_MERGE_ENDED:
            if payload.success:
                self.__shared_data_stage.GetRootLayer().Clear()

    def get_all_following_users(self, followed_user_id):
        """Get all user ids that are currently following followed_user_id."""

        return self.__user_following_map.get(followed_user_id, set())

    def get_bound_camera_prim(self, user_id) -> Union[Usd.Prim, None]:
        live_syncing = self.__live_syncing
        current_session = live_syncing.get_current_live_session()
        if not current_session:
            return None

        accessed_user_ids = set()
        usd_prim = None

        while True:
            # To avoid A follows B and B follows A
            if user_id in accessed_user_ids:
                break

            accessed_user_ids.add(user_id)

            peer_user = self.__peer_users.get(user_id, None)
            if not peer_user:
                break

            usd_prim = peer_user.get_bound_camera_prim()
            if usd_prim:
                break

            # It's following other users.
            user_id = self.get_following_user_id(user_id)

            # If it's following me.
            if user_id == current_session.logged_user_id:
                accessed_user_ids.add(user_id)

                shared_data_stage = self.__shared_data_stage
                current_stage = self.__usd_context.get_stage()
                my_bound_camera_property_path = get_bound_camera_property_path(user_id)
                camera_path_property = shared_data_stage.GetRootLayer().GetAttributeAtPath(
                    my_bound_camera_property_path
                )
                if camera_path_property:
                    bound_camera_path = str(camera_path_property.default).strip()
                    # Maps builin camera binding to local path or keep it intact.
                    bound_camera_path = SHARED_NAME_TO_LOCAL_BUILT_IN_CAMERA_PATH.get(
                        bound_camera_path, bound_camera_path
                    )
                    if bound_camera_path:
                        usd_prim = current_stage.GetPrimAtPath(bound_camera_path)
                        break

                    # Otherwise, checking local Kit is following other user to pass the ball.
                    my_following_user_property_path = get_following_user_property_path(user_id)
                    following_user_property = shared_data_stage.GetRootLayer().GetAttributeAtPath(
                        my_following_user_property_path
                    )
                    if not following_user_property:
                        break

                    user_id = str(following_user_property.default).strip()

            if not user_id or not current_session.get_peer_user_info(user_id):
                break

        return usd_prim

    def is_bound_to_builtin_camera(self, user_id):
        peer_user = self.__peer_users.get(user_id, None)
        if not peer_user:
            return False

        return peer_user.is_bound_to_builtin_camera()

    def get_following_user_id(self, user_id: str = None) -> str:
        """Gets the user id that the specific user is currently following."""

        live_syncing = self.__live_syncing
        current_session = live_syncing.get_current_live_session()
        if not current_session:
            return None

        if user_id is None:
            user_id = current_session.logged_user_id

        # Local user is handled differently as peer users.
        if user_id == current_session.logged_user_id:
            following_user_property_path = get_following_user_property_path(current_session.logged_user_id)
            following_user_property = self.__shared_data_stage.GetRootLayer().GetAttributeAtPath(
                following_user_property_path
            )
            if following_user_property:
                following_user_id = str(following_user_property.default).strip()
                if following_user_id and following_user_id in self.__peer_users:
                    return following_user_id

        peer_user = self.__peer_users.get(user_id, None)
        if not peer_user:
            return None

        # Ensure the following user id is currently in the live session.
        following_user = self.__peer_users.get(peer_user.following_user_id, None)
        logged_user_id = current_session.logged_user_id
        if following_user or peer_user.following_user_id == logged_user_id:
            return peer_user.following_user_id

        return None

    def is_user_followed_by(self, user_id: str, followed_by_user_id: str) -> str:
        following_user_id = self.get_following_user_id(followed_by_user_id)

        return following_user_id == user_id

    def get_selections(self, user_id: str) -> List[Sdf.Path]:
        peer_user = self.__peer_users.get(user_id, None)
        if not peer_user:
            return None

        return peer_user.selections

    def broadcast_local_bound_camera(self, local_camera_path: Sdf.Path):
        if not local_camera_path:
            local_camera_path = Sdf.Path.emptyPath
        else:
            local_camera_path = Sdf.Path(local_camera_path)

        shared_data_stage = self.__shared_data_stage
        if not shared_data_stage:
            return

        live_syncing = self.__live_syncing
        current_session = live_syncing.get_current_live_session()
        if not current_session:
            return

        # If camera does not exist
        if local_camera_path:
            current_stage = self.__usd_context.get_stage()
            camera_prim = current_stage.GetPrimAtPath(local_camera_path)
            if not camera_prim or not UsdGeom.Camera(camera_prim):
                carb.log_error(f"Cannot sync camera {local_camera_path} to presence layer as it does not exist.")
                return

        logged_user_id = current_session.logged_user_id
        bound_camera_property_path = get_bound_camera_property_path(logged_user_id)
        following_user_property_path = get_following_user_property_path(logged_user_id)

        local_builtin_camera = is_local_builtin_camera(local_camera_path)
        camera_path = local_builtin_camera or local_camera_path   # It's local builtin camera path or stage camera.
        camera_path = str(camera_path) if camera_path else ""

        with Sdf.ChangeBlock():
            # Only synchronizes builtin camera as non-builtin cameras are visible to all users already.
            if local_builtin_camera:
                user_shared_root = get_user_shared_root_path(logged_user_id)
                shared_camera_prim_path = user_shared_root.AppendElementString(local_builtin_camera)
                Sdf.CreatePrimInLayer(shared_data_stage.GetRootLayer(), shared_camera_prim_path)
                Sdf.CopySpec(
                    current_stage.GetSessionLayer(), local_camera_path,
                    shared_data_stage.GetRootLayer(), shared_camera_prim_path
                )

            property_spec = get_or_create_property_spec(
                shared_data_stage.GetRootLayer(), bound_camera_property_path,
                Sdf.ValueTypeNames.String
            )
            property_spec.default = camera_path

            property_spec = get_or_create_property_spec(
                shared_data_stage.GetRootLayer(), following_user_property_path,
                Sdf.ValueTypeNames.String
            )
            property_spec.default = ""

        # Notify all users that are currently following the local user.
        event_stream = layers.get_layers(self.__usd_context).get_event_stream()
        all_bound_camera_changed_ids = set()
        all_bound_camera_changed_ids.update(self.get_all_following_users(logged_user_id))
        if all_bound_camera_changed_ids:
            event_stream.push(
                int(PresenceLayerEventType.BOUND_CAMERA_CHANGED), 0,
                {EVENT_PAYLOAD_KEY: list(all_bound_camera_changed_ids)}
            )

    def __set_following_user_id_property(self, following_user_id):
        """Broadcasts local user's following id."""

        shared_data_stage = self.__shared_data_stage
        if not shared_data_stage:
            return False

        live_syncing = self.__live_syncing
        current_session = live_syncing.get_current_live_session()
        if not current_session:
            return False

        logged_user_id = current_session.logged_user_id
        following_user_property_path = get_following_user_property_path(logged_user_id)
        bound_camera_property_path = get_bound_camera_property_path(logged_user_id)

        with Sdf.ChangeBlock():
            property_spec = get_or_create_property_spec(
                shared_data_stage.GetRootLayer(), bound_camera_property_path,
                Sdf.ValueTypeNames.String
            )
            if following_user_id:
                property_spec.default = ""
            else:
                # Quits to perspective camera by default.
                property_spec.default = "/OmniverseKit_Persp"

            property_spec = get_or_create_property_spec(
                shared_data_stage.GetRootLayer(), following_user_property_path,
                Sdf.ValueTypeNames.String
            )
            property_spec.default = following_user_id

        if self.__local_following_user_id:
            self.__remove_following_user(logged_user_id, self.__local_following_user_id)

        self.__local_following_user_id = following_user_id
        if following_user_id:
            self.__track_following_user(logged_user_id, following_user_id)

        return True

    def enter_follow_mode(self, following_user_id: str):
        live_syncing = self.__live_syncing
        current_session = live_syncing.get_current_live_session()
        if not current_session:
            carb.log_warn(f"Cannot follow user {following_user_id} as it's not in a live session.")
            return False

        if current_session.logged_user_id == following_user_id:
            carb.log_warn("Cannot follow myself.")
            return False

        following_user = self.__peer_users.get(following_user_id, None)
        if not following_user:
            carb.log_warn(f"Cannot follow user {following_user_id} as the user does not exist in the session.")

            return False

        if not self.get_bound_camera_prim(following_user.user_id):
            message = f"Cannot follow user {following_user.user_name} as the user does not share bound camera."
            try:
                import omni.kit.notification_manager as nm
                nm.post_notification(message, status=nm.NotificationStatus.WARNING)
            except ImportError:
                pass
            finally:
                carb.log_warn(message)

            return False

        # If user is already following me or other users, reports errors.
        if (
            following_user.following_user_id and
            (
                following_user.following_user_id == current_session.logged_user_id or
                following_user.following_user_id in self.__peer_users
            )
        ):
            carb.log_warn(f"Cannot follow user {following_user.user_name} as the user is in following mode.")

            return False

        if self.get_following_user_id() == following_user_id:
            return True

        event_stream = layers.get_layers(self.__usd_context).get_event_stream()
        if self.__set_following_user_id_property(following_user_id):
            event_stream.dispatch(PresenceLayerEventType.LOCAL_FOLLOW_MODE_CHANGED)
            return True

        return False

    def quit_follow_mode(self):
        live_syncing = self.__live_syncing
        current_session = live_syncing.get_current_live_session()
        if not current_session:
            return False

        if self.is_in_following_mode(current_session.logged_user_id):
            event_stream = layers.get_layers(self.__usd_context).get_event_stream()
            if self.__set_following_user_id_property(""):
                event_stream.dispatch(PresenceLayerEventType.LOCAL_FOLLOW_MODE_CHANGED)

    def can_follow(self, user_id):
        following_user = self.__peer_users.get(user_id, None)

        return not following_user or following_user.following_user_id

    def is_in_following_mode(self, user_id: str = None) -> bool:
        """
        Checks if the user is following other user.

        user_id (str): The user id to check. By default, it's None, which means to check if local user is in follow mode.
        """

        live_syncing = self.__live_syncing
        current_session = live_syncing.get_current_live_session()
        if not current_session:
            return False

        if user_id is None:
            user_id = current_session.logged_user_id

        following_user_id = self.get_following_user_id(user_id)
        if following_user_id:
            return True
        else:
            return False


class PresenceLayerAPI:
    """
    Presence layer is the transport layer that works for exchange persistent data for
    all users in the same Live Session. PresenceLayerAPI provides the APIs that serve
    for easy access to data of presence layer.
    """

    def __init__(self, presence_layer_instance: PresenceLayerManager) -> None:
        """Internal Constructor."""

        self.__presence_layer_instance = presence_layer_instance

    def is_bound_to_builtin_camera(self, user_id):
        """
        Checks if peer user is bound to builtin camera. If peer user is following other user,
        it will always return False.
        """

        return self.__presence_layer_instance.is_bound_to_builtin_camera(user_id)

    @carb.profiler.profile
    def get_bound_camera_prim(self, user_id) -> Union[Usd.Prim, None]:
        """
        Gets the bound camera of the peer user in the local stage. If peer user is following other user, it will
        return the bound camera of the following user.
        """

        return self.__presence_layer_instance.get_bound_camera_prim(user_id)

    def get_following_user_id(self, user_id: str = None) -> str:
        """
        Gets the user id that the specific user is currently following.

        user_id (str): User id, includes both local and peer users. If it's None, it will return the user id that
            local user is currently following.
        """

        return self.__presence_layer_instance.get_following_user_id(user_id)

    def is_user_followed_by(self, user_id: str, followed_by_user_id: str) -> str:
        """
        Checks if user is followed by other specific user.

        Args:
            user_id (str): The user id to query.
            followed_by_user_id (str): The user that's following the one has user_id.
        """

        return self.__presence_layer_instance.is_user_followed_by(user_id, followed_by_user_id)

    def get_selections(self, user_id: str) -> List[Sdf.Path]:
        """Gets the prim paths that the user selects."""

        return self.__presence_layer_instance.get_selections(user_id)

    @carb.profiler.profile
    def broadcast_local_bound_camera(self, local_camera_path: Sdf.Path):
        """
        Broadcasts local bound camera to presence layer. Local application can be either in
        bound camera mode or following user mode. Switching bound camera will quit
        following user mode.
        """

        return self.__presence_layer_instance.broadcast_local_bound_camera(local_camera_path)

    @carb.profiler.profile
    def enter_follow_mode(self, following_user_id: str):
        """
        Try to follow user from local. Local application can be either in
        bound camera mode or following user mode. Switching bound camera will quit
        following user mode. If the user specified by following_user_id is in following
        mode already, this function will return False.

        Args:
            following_user_id (str): The user id that local user is trying to follow.
        """

        return self.__presence_layer_instance.enter_follow_mode(following_user_id)

    def quit_follow_mode(self):
        """Quits following mode."""

        self.__presence_layer_instance.quit_follow_mode()

    def can_follow(self, user_id):
        """If the specified peer user can be followed."""

        return self.__presence_layer_instance.can_follow(user_id)

    def is_in_following_mode(self, user_id: str = None):
        """
        Checks if the user is following other user.

        user_id (str): User id, including both the local and peer users. By default, it's None, which means to
            check if local user is in follow mode.
        """

        return self.__presence_layer_instance.is_in_following_mode(user_id)

    def get_shared_data_stage(self) -> Usd.Stage:
        """
        Underlying storage. For applications that want to extend the functionality of Presence Layer,
        the raw handle of the stage is exposed for use.
        """

        return self.__presence_layer_instance.shared_data_stage
